import math
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session
from app.models.dataset import Dataset, DatasetVersion
from app.models.profiling import ProfilingResult
from app.services.ingestion import IngestionService
from app.core.logging import logger

class ProfilingService:
    @staticmethod
    def infer_column_type(series: pd.Series) -> str:
        """Categorize column into standard semantic types."""
        if pd.api.types.is_bool_dtype(series):
            return "boolean"
        elif pd.api.types.is_datetime64_any_dtype(series):
            return "datetime"
        elif pd.api.types.is_numeric_dtype(series):
            return "numeric"
        else:
            # Check if strings are actually convertible to datetimes or numbers
            non_null = series.dropna().astype(str)
            if len(non_null) > 0 and non_null.nunique() / len(non_null) < 0.15:
                return "categorical"
            return "text"

    @classmethod
    def profile_dataframe(cls, df: pd.DataFrame) -> Dict[str, Any]:
        """Compute exhaustive deterministic statistical profiling of dataset."""
        total_rows, total_columns = df.shape
        total_cells = total_rows * total_columns if total_rows * total_columns > 0 else 1

        missing_cells_count = int(df.isna().sum().sum())
        duplicate_rows_count = int(df.duplicated().sum())

        column_metrics: Dict[str, Any] = {}
        total_outlier_count = 0
        numeric_cells_count = 0

        for col in df.columns:
            series = df[col]
            inferred_type = cls.infer_column_type(series)
            null_count = int(series.isna().sum())
            null_percentage = round((null_count / total_rows * 100), 2) if total_rows > 0 else 0.0
            unique_count = int(series.nunique(dropna=True))
            unique_percentage = round((unique_count / total_rows * 100), 2) if total_rows > 0 else 0.0

            col_metric: Dict[str, Any] = {
                "name": str(col),
                "data_type": str(series.dtype),
                "inferred_type": inferred_type,
                "total_count": total_rows,
                "null_count": null_count,
                "null_percentage": null_percentage,
                "unique_count": unique_count,
                "unique_percentage": unique_percentage,
                "min_value": None,
                "max_value": None,
                "mean_value": None,
                "std_value": None,
                "median_value": None,
                "q25": None,
                "q75": None,
                "outliers_iqr_count": 0,
                "top_frequent_values": [],
                "histogram": None,
            }

            # Numerical statistics
            if inferred_type == "numeric":
                clean_numeric = pd.to_numeric(series, errors="coerce").dropna()
                num_count = len(clean_numeric)
                numeric_cells_count += num_count
                
                if num_count > 0:
                    q25 = float(clean_numeric.quantile(0.25))
                    q75 = float(clean_numeric.quantile(0.75))
                    iqr = q75 - q25
                    lower_bound = q25 - 1.5 * iqr
                    upper_bound = q75 + 1.5 * iqr
                    outliers = clean_numeric[(clean_numeric < lower_bound) | (clean_numeric > upper_bound)]
                    outlier_count = int(len(outliers))
                    total_outlier_count += outlier_count

                    col_metric.update({
                        "min_value": float(clean_numeric.min()),
                        "max_value": float(clean_numeric.max()),
                        "mean_value": round(float(clean_numeric.mean()), 4),
                        "std_value": round(float(clean_numeric.std()), 4) if num_count > 1 else 0.0,
                        "median_value": round(float(clean_numeric.median()), 4),
                        "q25": round(q25, 4),
                        "q75": round(q75, 4),
                        "outliers_iqr_count": outlier_count
                    })

                    # Calculate histogram with 10 bins
                    counts, bin_edges = np.histogram(clean_numeric, bins=min(10, max(2, num_count)))
                    col_metric["histogram"] = {
                        "counts": counts.tolist(),
                        "bin_edges": [round(float(b), 4) for b in bin_edges]
                    }

            # Frequency distribution for categorical/text
            top_vals = series.value_counts(dropna=False).head(5)
            col_metric["top_frequent_values"] = [
                {"value": str(k) if pd.notna(k) else "<NULL>", "count": int(v)}
                for k, v in top_vals.items()
            ]

            column_metrics[str(col)] = col_metric

        # Transparent Data Quality Scoring calculation
        null_ratio = missing_cells_count / total_cells
        dup_ratio = duplicate_rows_count / total_rows if total_rows > 0 else 0
        outlier_ratio = total_outlier_count / max(1, numeric_cells_count)

        completeness_score = max(0.0, round((1.0 - null_ratio) * 100, 2))
        uniqueness_score = max(0.0, round((1.0 - dup_ratio) * 100, 2))
        validity_score = max(0.0, round((1.0 - outlier_ratio) * 100, 2))
        consistency_score = 100.0  # Base consistency

        # Penalties:
        # 40% weight on completeness, 30% on uniqueness, 20% on validity (outliers), 10% on consistency
        null_penalty = round(null_ratio * 40, 2)
        dup_penalty = round(dup_ratio * 30, 2)
        outlier_penalty = round(outlier_ratio * 20, 2)
        consistency_penalty = 0.0

        overall_score = max(0.0, min(100.0, round(100.0 - (null_penalty + dup_penalty + outlier_penalty + consistency_penalty), 2)))

        quality_breakdown = {
            "overall_score": overall_score,
            "completeness_score": completeness_score,
            "uniqueness_score": uniqueness_score,
            "validity_score": validity_score,
            "consistency_score": consistency_score,
            "penalties": {
                "missingness_penalty": null_penalty,
                "duplicate_penalty": dup_penalty,
                "outlier_penalty": outlier_penalty,
                "consistency_penalty": consistency_penalty,
            }
        }

        return {
            "overall_score": overall_score,
            "total_rows": total_rows,
            "total_columns": total_columns,
            "missing_cells_count": missing_cells_count,
            "duplicate_rows_count": duplicate_rows_count,
            "column_metrics": column_metrics,
            "quality_breakdown": quality_breakdown
        }

    @classmethod
    def run_profiling(cls, db: Session, dataset_id: int, version_id: Optional[int] = None) -> ProfilingResult:
        """Run full profiling on a dataset or version and persist results in database."""
        dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not dataset:
            raise ValueError(f"Dataset with ID {dataset_id} not found")

        file_path = dataset.file_path
        if version_id:
            ver = db.query(DatasetVersion).filter(DatasetVersion.id == version_id, DatasetVersion.dataset_id == dataset_id).first()
            if ver:
                file_path = ver.file_path

        df = IngestionService.load_dataframe(file_path, dataset.file_type)
        profile_data = cls.profile_dataframe(df)

        profiling_record = ProfilingResult(
            dataset_id=dataset.id,
            version_id=version_id,
            overall_score=profile_data["overall_score"],
            total_rows=profile_data["total_rows"],
            total_columns=profile_data["total_columns"],
            missing_cells_count=profile_data["missing_cells_count"],
            duplicate_rows_count=profile_data["duplicate_rows_count"],
            column_metrics=profile_data["column_metrics"],
            quality_breakdown=profile_data["quality_breakdown"]
        )
        db.add(profiling_record)
        db.commit()
        db.refresh(profiling_record)
        logger.info(f"Profiling completed for dataset {dataset_id}. Quality score: {profiling_record.overall_score}/100")
        return profiling_record

