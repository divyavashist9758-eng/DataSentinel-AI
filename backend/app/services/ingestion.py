import os
import re
import hashlib
import uuid
import datetime
from pathlib import Path
from typing import Tuple, Dict, Any, List
import pandas as pd
from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.config import settings
from app.core.exceptions import FileProcessingException, ValidationException
from app.core.logging import logger
from app.models.dataset import Dataset, DatasetVersion, DatasetSchema
from app.models.user import User

ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls", ".json"}

# Executable binary signatures to strictly prohibit
DANGEROUS_MAGIC_HEADERS = [
    b"\x7fELF",               # Linux ELF executable
    b"MZ",                   # Windows DOS/PE executable
    b"\xca\xfe\xba\xbe",     # Java / Mach-O binary
    b"\xfe\xed\xfa\xce",     # Mach-O 32-bit
    b"\xfe\xed\xfa\xcf",     # Mach-O 64-bit
    b"#!",                   # Shell script execution header
]

class IngestionService:
    @staticmethod
    def calculate_file_hash(file_path: str) -> str:
        """Compute SHA-256 cryptographic digest of file."""
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()

    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """Strictly sanitize incoming filename to prevent path traversal and script injection."""
        # Strip all path components
        base = os.path.basename(filename)
        # Strip non-alphanumeric, dot, dash, and underscore characters
        cleaned = re.sub(r'[^a-zA-Z0-9_.-]', '_', base)
        # Prevent hidden files and double dots
        cleaned = cleaned.lstrip('.')
        while '..' in cleaned:
            cleaned = cleaned.replace('..', '_')
        return cleaned or "dataset"

    @classmethod
    def validate_content_signature(cls, first_chunk: bytes, ext: str):
        """Validate content magic bytes against dangerous binaries and verify format compliance."""
        if not first_chunk:
            raise ValidationException("Uploaded file is empty (0 bytes)")

        # Disallow known dangerous executable headers
        for magic in DANGEROUS_MAGIC_HEADERS:
            if first_chunk.startswith(magic):
                raise ValidationException("Security alert: Executable binary or script headers detected. Upload blocked.")

        if ext == ".csv":
            try:
                # Must be decodable as text
                first_chunk.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    first_chunk.decode('latin-1')
                except Exception:
                    raise ValidationException("CSV file must be valid text-encoded data")
        elif ext == ".xlsx":
            # XLSX files are ZIP archives starting with PK\x03\x04
            if not first_chunk.startswith(b"PK\x03\x04"):
                raise ValidationException("Invalid Excel XLSX file: missing ZIP header signature")
        elif ext == ".xls":
            # Legacy XLS files start with OLE header \xd0\xcf\x11\xe0
            if not first_chunk.startswith(b"\xd0\xcf\x11\xe0"):
                raise ValidationException("Invalid Excel XLS file: missing OLE compound header signature")
        elif ext == ".json":
            text_lead = first_chunk.decode('utf-8', errors='ignore').strip()
            if not (text_lead.startswith('{') or text_lead.startswith('[')):
                raise ValidationException("Invalid JSON file: file must begin with '{' or '['")

    @classmethod
    def validate_and_save_upload(cls, upload_file: UploadFile) -> Tuple[str, str, int]:
        """Validate file extension, size, and content signature, then save securely to disk."""
        raw_filename = upload_file.filename or "uploaded_dataset"
        _, ext = os.path.splitext(raw_filename)
        ext = ext.lower()

        if ext not in ALLOWED_EXTENSIONS:
            raise ValidationException(
                f"Unsupported file format '{ext}'. Allowed formats: {', '.join(ALLOWED_EXTENSIONS)}"
            )

        safe_filename = cls.sanitize_filename(raw_filename)
        unique_id = uuid.uuid4().hex[:12]
        dest_filename = f"{unique_id}_{safe_filename}"
        destination_path = os.path.join(settings.UPLOAD_DIR, dest_filename)

        # Path traversal guard
        abs_dest = os.path.abspath(destination_path)
        abs_upload_dir = os.path.abspath(settings.UPLOAD_DIR)
        if os.path.commonpath([abs_upload_dir, abs_dest]) != abs_upload_dir:
            raise ValidationException("Illegal path traversal detected in file upload")

        total_bytes = 0
        max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        first_chunk = True

        with open(destination_path, "wb") as buffer:
            while chunk := upload_file.file.read(1024 * 1024):  # 1MB stream chunks
                if first_chunk:
                    cls.validate_content_signature(chunk[:256], ext)
                    first_chunk = False

                total_bytes += len(chunk)
                if total_bytes > max_bytes:
                    buffer.close()
                    if os.path.exists(destination_path):
                        os.remove(destination_path)
                    raise ValidationException(
                        f"File size exceeds maximum allowed limit of {settings.MAX_UPLOAD_SIZE_MB}MB"
                    )
                buffer.write(chunk)

        file_type = "csv"
        if ext in [".xlsx", ".xls"]:
            file_type = "excel"
        elif ext == ".json":
            file_type = "json"

        return destination_path, file_type, total_bytes

    @classmethod
    def load_dataframe(cls, file_path: str, file_type: str = "csv") -> pd.DataFrame:
        """Read file into Pandas DataFrame with path confinement and error protection."""
        if not os.path.exists(file_path):
            raise FileProcessingException(f"Dataset file not found at: {file_path}")

        # Path confinement check
        abs_path = os.path.abspath(file_path)
        allowed_dirs = [
            os.path.abspath(settings.UPLOAD_DIR),
            os.path.abspath(settings.REMEDIATED_DIR),
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "sample_data"))
        ]
        is_confined = any(os.path.commonpath([d, abs_path]) == d for d in allowed_dirs)
        if not is_confined:
            raise FileProcessingException(f"Access denied: Attempted to load file outside authorized storage zones")

        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        effective_type = "json" if ext == ".json" else ("excel" if ext in [".xlsx", ".xls"] else ("csv" if ext == ".csv" else file_type))

        try:
            if effective_type == "csv":
                df = pd.read_csv(file_path)
            elif effective_type == "excel":
                df = pd.read_excel(file_path)
            elif effective_type == "json":
                df = pd.read_json(file_path)
            else:
                df = pd.read_csv(file_path)
            return df
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {str(e)}")
            raise FileProcessingException(f"Failed to parse dataset: {str(e)}")

    @classmethod
    def ingest_uploaded_dataset(
        cls,
        db: Session,
        upload_file: UploadFile,
        dataset_name: str,
        description: str,
        owner: User
    ) -> Dataset:
        """Complete ingestion pipeline: validate, save, parse schema, and create records."""
        file_path, file_type, file_size = cls.validate_and_save_upload(upload_file)
        sha256_hash = cls.calculate_file_hash(file_path)
        
        # Load and extract basic dimensions
        df = cls.load_dataframe(file_path, file_type)
        row_count, col_count = df.shape

        # Create Dataset entity
        dataset = Dataset(
            name=dataset_name or upload_file.filename,
            description=description,
            file_type=file_type,
            file_path=file_path,
            original_filename=upload_file.filename,
            file_size_bytes=file_size,
            row_count=row_count,
            column_count=col_count,
            sha256_hash=sha256_hash,
            owner_id=owner.id,
            is_active=True
        )
        db.add(dataset)
        db.flush()

        # Create Version 1 (Immutable Baseline)
        version = DatasetVersion(
            dataset_id=dataset.id,
            version_num=1,
            file_path=file_path,
            row_count=row_count,
            column_count=col_count,
            change_summary="Initial dataset ingestion and baseline establishment",
            is_remediated=False
        )
        db.add(version)
        db.flush()

        # Infer schema and register initial columns
        for col_name in df.columns:
            dtype_str = str(df[col_name].dtype)
            nullable = bool(df[col_name].isnull().any())
            unique_cnt = int(df[col_name].nunique())
            sample_vals = df[col_name].dropna().head(5).tolist()

            schema_entry = DatasetSchema(
                dataset_id=dataset.id,
                version_id=version.id,
                column_name=str(col_name),
                data_type=dtype_str,
                is_nullable=nullable,
                unique_count=unique_cnt,
                sample_values=sample_vals
            )
            db.add(schema_entry)

        db.commit()
        db.refresh(dataset)
        logger.info(f"Dataset '{dataset.name}' (ID: {dataset.id}) ingested successfully. Rows: {row_count}, Cols: {col_count}")
        return dataset
