import os
import uuid
import datetime
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from app.config import settings
from app.models.dataset import Dataset, DatasetVersion, DatasetSchema
from app.models.remediation import RemediationSuggestion
from app.services.ingestion import IngestionService
from app.services.profiling_service import ProfilingService
from app.api.deps import record_audit
from app.core.exceptions import ValidationException
from app.core.logging import logger

class RemediationEngine:
    @classmethod
    def apply_transformation(
        cls,
        df: pd.DataFrame,
        action: str,
        column_name: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Tuple[pd.DataFrame, int]:
        """Apply transformation cleanly to a copy of DataFrame without altering original."""
        clean_df = df.copy()
        affected_count = 0
        params = parameters or {}

        if action == "deduplicate":
            initial_len = len(clean_df)
            clean_df = clean_df.drop_duplicates(keep=params.get("keep", "first"))
            affected_count = initial_len - len(clean_df)

        elif action in ["impute_median", "impute_mean", "impute_mode", "impute_constant"] and column_name in clean_df.columns:
            series = clean_df[column_name]
            null_mask = series.isna()
            affected_count = int(null_mask.sum())
            if affected_count > 0:
                if action == "impute_median":
                    fill_val = float(pd.to_numeric(series, errors="coerce").dropna().median())
                elif action == "impute_mean":
                    fill_val = float(pd.to_numeric(series, errors="coerce").dropna().mean())
                elif action == "impute_mode":
                    mode_vals = series.mode(dropna=True)
                    fill_val = mode_vals.iloc[0] if len(mode_vals) > 0 else "UNKNOWN"
                else:  # constant
                    fill_val = params.get("value", "UNKNOWN")
                clean_df[column_name] = clean_df[column_name].fillna(fill_val)

        elif action == "drop_nulls" and column_name in clean_df.columns:
            initial_len = len(clean_df)
            clean_df = clean_df.dropna(subset=[column_name])
            affected_count = initial_len - len(clean_df)

        elif action == "clip_iqr" and column_name in clean_df.columns:
            series = pd.to_numeric(clean_df[column_name], errors="coerce")
            q25 = series.quantile(0.25)
            q75 = series.quantile(0.75)
            iqr = q75 - q25
            factor = params.get("factor", 1.5)
            lower = q25 - factor * iqr
            upper = q75 + factor * iqr
            
            clipped = series.clip(lower=lower, upper=upper)
            affected_count = int((series != clipped).sum())
            clean_df[column_name] = clipped

        return clean_df, affected_count

    @classmethod
    def preview_remediation(
        cls,
        db: Session,
        remediation_id: int,
        preview_limit: int = 5
    ) -> Dict[str, Any]:
        """Generate side-by-side before and after transformation diff for preview."""
        rem = db.query(RemediationSuggestion).filter(RemediationSuggestion.id == remediation_id).first()
        if not rem:
            raise ValidationException(f"Remediation suggestion {remediation_id} not found")

        dataset = db.query(Dataset).filter(Dataset.id == rem.dataset_id).first()
        file_path = dataset.file_path
        if rem.version_id:
            ver = db.query(DatasetVersion).filter(DatasetVersion.id == rem.version_id).first()
            if ver:
                file_path = ver.file_path

        df = IngestionService.load_dataframe(file_path, dataset.file_type)
        transformed_df, affected_count = cls.apply_transformation(
            df, rem.proposed_action, rem.column_name, rem.parameters
        )

        # Find rows that changed for preview
        if rem.proposed_action == "deduplicate":
            before_preview = df[df.duplicated(keep=False)].head(preview_limit).fillna("").to_dict(orient="records")
            after_preview = transformed_df.head(preview_limit).fillna("").to_dict(orient="records")
        elif rem.column_name and rem.column_name in df.columns:
            # Rows where before and after differ
            changed_mask = df[rem.column_name].isna() if "impute" in rem.proposed_action else (df[rem.column_name] != transformed_df[rem.column_name])
            changed_indices = df[changed_mask].index[:preview_limit]
            before_preview = df.loc[changed_indices].fillna("").to_dict(orient="records")
            after_preview = transformed_df.loc[changed_indices].fillna("").to_dict(orient="records")
        else:
            before_preview = df.head(preview_limit).fillna("").to_dict(orient="records")
            after_preview = transformed_df.head(preview_limit).fillna("").to_dict(orient="records")

        # Estimated quality score improvement
        current_prof = ProfilingService.profile_dataframe(df)
        remed_prof = ProfilingService.profile_dataframe(transformed_df)
        score_diff = round(remed_prof["overall_score"] - current_prof["overall_score"], 2)

        return {
            "remediation_id": rem.id,
            "proposed_action": rem.proposed_action,
            "column_name": rem.column_name,
            "affected_rows_count": affected_count,
            "before_preview": before_preview,
            "after_preview": after_preview,
            "expected_quality_score_improvement": max(0.0, score_diff)
        }

    @classmethod
    def execute_approved_remediation(
        cls,
        db: Session,
        remediation_id: int,
        reviewer_name: str
    ) -> DatasetVersion:
        """Execute approved transformation on a newly cloned file copy and persist as a new version."""
        rem = db.query(RemediationSuggestion).filter(RemediationSuggestion.id == remediation_id).first()
        if not rem:
            raise ValidationException(f"Remediation {remediation_id} not found")

        if rem.status != "APPROVED":
            raise ValidationException(f"Remediation must be APPROVED before execution. Current status: '{rem.status}'")

        dataset = db.query(Dataset).filter(Dataset.id == rem.dataset_id).first()
        base_version = db.query(DatasetVersion).filter(
            DatasetVersion.id == rem.version_id
        ).first() if rem.version_id else dataset.versions[0]

        # Load baseline DataFrame
        source_df = IngestionService.load_dataframe(base_version.file_path, dataset.file_type)
        
        # Apply transformation
        clean_df, affected_count = cls.apply_transformation(
            source_df, rem.proposed_action, rem.column_name, rem.parameters
        )

        # Write to dedicated REMEDIATED directory matching source format
        new_ver_num = len(dataset.versions) + 1
        if dataset.file_type == "json":
            safe_filename = f"remediated_ds{dataset.id}_v{new_ver_num}_{uuid.uuid4().hex[:8]}.json"
            remediated_path = os.path.join(settings.REMEDIATED_DIR, safe_filename)
            clean_df.to_json(remediated_path, orient="records", indent=2)
        elif dataset.file_type == "excel":
            safe_filename = f"remediated_ds{dataset.id}_v{new_ver_num}_{uuid.uuid4().hex[:8]}.xlsx"
            remediated_path = os.path.join(settings.REMEDIATED_DIR, safe_filename)
            clean_df.to_excel(remediated_path, index=False)
        else:
            safe_filename = f"remediated_ds{dataset.id}_v{new_ver_num}_{uuid.uuid4().hex[:8]}.csv"
            remediated_path = os.path.join(settings.REMEDIATED_DIR, safe_filename)
            clean_df.to_csv(remediated_path, index=False)

        # Create new DatasetVersion
        new_version = DatasetVersion(
            dataset_id=dataset.id,
            version_num=new_ver_num,
            file_path=remediated_path,
            row_count=len(clean_df),
            column_count=len(clean_df.columns),
            change_summary=f"Remediation executed: {rem.proposed_action} on {rem.column_name or 'dataset'} ({affected_count} rows affected)",
            is_remediated=True
        )
        db.add(new_version)
        db.flush()

        # Update Remediation record
        rem.status = "EXECUTED"
        rem.reviewed_by = reviewer_name
        rem.reviewed_at = datetime.datetime.utcnow()
        rem.execution_result = {
            "new_version_id": new_version.id,
            "new_version_num": new_ver_num,
            "rows_affected": affected_count,
            "remediated_file_path": remediated_path
        }

        # Run profiling on the newly generated remediated version
        ProfilingService.run_profiling(db, dataset.id, new_version.id)

        # Audit log
        record_audit(
            db=db,
            action="EXECUTE_REMEDIATION",
            entity_type="remediation",
            entity_id=rem.id,
            details={
                "dataset_id": dataset.id,
                "new_version_id": new_version.id,
                "action_applied": rem.proposed_action,
                "column": rem.column_name,
                "rows_affected": affected_count
            }
        )

        db.commit()
        db.refresh(new_version)
        logger.info(f"Remediation {rem.id} executed successfully. Created new version {new_ver_num} for dataset {dataset.id}.")
        return new_version
