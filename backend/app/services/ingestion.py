import os
import hashlib
import uuid
import datetime
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
    def validate_and_save_upload(cls, upload_file: UploadFile) -> Tuple[str, str, int]:
        """Validate file extension and size, then save securely to disk."""
        filename = upload_file.filename or "uploaded_dataset"
        _, ext = os.path.splitext(filename)
        ext = ext.lower()

        if ext not in ALLOWED_EXTENSIONS:
            raise ValidationException(
                f"Unsupported file format '{ext}'. Allowed formats: {', '.join(ALLOWED_EXTENSIONS)}"
            )

        unique_id = uuid.uuid4().hex[:12]
        safe_name = f"{unique_id}_{filename.replace(' ', '_')}"
        destination_path = os.path.join(settings.UPLOAD_DIR, safe_name)

        total_bytes = 0
        max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024

        with open(destination_path, "wb") as buffer:
            while chunk := upload_file.file.read(1024 * 1024):  # 1MB chunks
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
        """Read file into Pandas DataFrame with error protection."""
        if not os.path.exists(file_path):
            raise FileProcessingException(f"Dataset file not found at: {file_path}")

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

        # Create Version 1 entity
        version_1 = DatasetVersion(
            dataset_id=dataset.id,
            version_num=1,
            file_path=file_path,
            row_count=row_count,
            column_count=col_count,
            change_summary="Initial dataset upload",
            is_remediated=False
        )
        db.add(version_1)
        db.flush()

        # Extract column schema metadata
        for col in df.columns:
            series = df[col]
            data_type = str(series.dtype)
            is_nullable = bool(series.isna().any())
            unique_count = int(series.nunique(dropna=True))
            
            # Extract clean serializable sample values
            samples = series.dropna().head(5).tolist()
            clean_samples = [str(x) if not isinstance(x, (int, float, bool, str)) else x for x in samples]

            schema_record = DatasetSchema(
                dataset_id=dataset.id,
                version_id=version_1.id,
                column_name=str(col),
                data_type=data_type,
                is_nullable=is_nullable,
                unique_count=unique_count,
                sample_values=clean_samples
            )
            db.add(schema_record)

        db.commit()
        db.refresh(dataset)
        logger.info(f"Dataset '{dataset.name}' (ID: {dataset.id}) ingested successfully. Rows: {row_count}, Cols: {col_count}")
        return dataset
