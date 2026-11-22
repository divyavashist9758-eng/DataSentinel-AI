import datetime
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sqlalchemy.orm import Session
from app.models.dataset import Dataset, DatasetVersion
from app.models.anomaly import AnomalyResult
from app.services.ingestion import IngestionService
from app.core.logging import logger

def make_json_serializable(val: Any) -> Any:
    """Ensure all numpy and pandas datatypes are serializable to JSON."""
    if val is None or pd.isna(val):
        return None
    if isinstance(val, (pd.Timestamp, datetime.date, datetime.datetime)):
        return val.isoformat()
    if isinstance(val, (np.integer, int)):
        return int(val)
    if isinstance(val, (np.floating, float)):
        return float(val)
    if isinstance(val, (np.bool_, bool)):
        return bool(val)
    if isinstance(val, (dict, list)):
        return val
    return str(val)

class MLEngine:
    @classmethod
    def detect_anomalies_isolation_forest(
        cls,
        df: pd.DataFrame,
        contamination: float = 0.05,
        selected_columns: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Real Isolation Forest unsupervised multi-dimensional anomaly detection."""
        # Filter numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if selected_columns:
            numeric_cols = [c for c in selected_columns if c in numeric_cols]

        if not numeric_cols or len(df) < 5:
            return {
                "anomalous_rows_count": 0,
                "total_evaluated_rows": len(df),
                "anomaly_indices": [],
                "feature_importance": {},
                "anomaly_samples": []
            }

        # Impute numeric NaN with column median for modeling
        X = df[numeric_cols].copy()
        for col in numeric_cols:
            median_val = X[col].median()
            if pd.isna(median_val):
                median_val = 0.0
            X[col] = X[col].fillna(median_val)

        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # Train Isolation Forest
        model = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100,
            n_jobs=-1
        )
        preds = model.fit_predict(X_scaled)  # -1 for anomaly, 1 for inlier
        scores = model.decision_function(X_scaled)  # Lower is more abnormal

        anomaly_mask = preds == -1
        anomaly_indices = np.where(anomaly_mask)[0].tolist()
        anomalous_rows_count = len(anomaly_indices)

        # Compute feature importance based on absolute deviation from median of anomalous vs normal points
        feature_importance: Dict[str, float] = {}
        if anomalous_rows_count > 0:
            normal_mask = preds == 1
            if np.any(normal_mask):
                normal_means = X_scaled[normal_mask].mean(axis=0)
                anomaly_means = X_scaled[anomaly_mask].mean(axis=0)
                diffs = np.abs(anomaly_means - normal_means)
                total_diff = np.sum(diffs)
                if total_diff > 0:
                    for i, col in enumerate(numeric_cols):
                        feature_importance[col] = round(float(diffs[i] / total_diff), 4)

        # Format top anomaly samples for explanation
        anomaly_samples: List[Dict[str, Any]] = []
        # Sort indices by most severe anomaly score (lowest decision_function)
        if anomaly_indices:
            sorted_indices = sorted(anomaly_indices, key=lambda idx: scores[idx])
            for idx in sorted_indices[:20]:  # Top 20 most anomalous rows
                row_dict = {str(k): make_json_serializable(v) for k, v in df.iloc[idx].to_dict().items()}
                
                # Identify which specific features deviated most for this specific row
                row_deviations = []
                for col in numeric_cols:
                    col_std = df[col].std()
                    col_mean = df[col].mean()
                    if col_std and col_std > 0:
                        val = df.iloc[idx][col]
                        if pd.notna(val):
                            z = abs((val - col_mean) / col_std)
                            if z > 2.0:
                                row_deviations.append(f"{col} (z-score: {round(float(z), 2)})")

                anomaly_samples.append({
                    "row_index": int(idx),
                    "anomaly_score": round(float(-scores[idx]), 4),  # Invert so higher = more abnormal
                    "values": row_dict,
                    "flagged_reasons": row_deviations if row_deviations else ["Multivariate pattern anomaly"]
                })

        return {
            "anomalous_rows_count": anomalous_rows_count,
            "total_evaluated_rows": len(df),
            "anomaly_indices": anomaly_indices,
            "feature_importance": feature_importance,
            "anomaly_samples": anomaly_samples
        }

    @classmethod
    def detect_statistical_outliers(
        cls,
        df: pd.DataFrame,
        method: str = "iqr"  # iqr or z_score
    ) -> Dict[str, Any]:
        """Detect univariate statistical outliers using IQR or Z-score method."""
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        outlier_rows = set()
        feature_outliers: Dict[str, Any] = {}

        for col in numeric_cols:
            series = df[col].dropna()
            if len(series) < 4:
                continue

            if method == "z_score":
                mean = series.mean()
                std = series.std()
                if std > 0:
                    z_scores = np.abs((series - mean) / std)
                    flagged = series[z_scores > 3.0]
                    indices = flagged.index.tolist()
                    outlier_rows.update(indices)
                    feature_outliers[col] = {
                        "count": len(indices),
                        "indices": [int(i) for i in indices[:50]],
                        "min_outlier": float(flagged.min()) if len(flagged) else None,
                        "max_outlier": float(flagged.max()) if len(flagged) else None,
                    }
            else:  # iqr
                q25 = series.quantile(0.25)
                q75 = series.quantile(0.75)
                iqr = q75 - q25
                lower = q25 - 1.5 * iqr
                upper = q75 + 1.5 * iqr
                flagged = series[(series < lower) | (series > upper)]
                indices = flagged.index.tolist()
                outlier_rows.update(indices)
                feature_outliers[col] = {
                    "count": len(indices),
                    "lower_fence": round(float(lower), 4),
                    "upper_fence": round(float(upper), 4),
                    "indices": [int(i) for i in indices[:50]],
                    "min_outlier": float(flagged.min()) if len(flagged) else None,
                    "max_outlier": float(flagged.max()) if len(flagged) else None,
                }

        return {
            "total_outliers_count": len(outlier_rows),
            "outlier_indices": [int(i) for i in sorted(list(outlier_rows))],
            "feature_outliers": feature_outliers
        }

    @classmethod
    def run_anomaly_analysis(
        cls,
        db: Session,
        dataset_id: int,
        version_id: Optional[int] = None,
        detector_type: str = "isolation_forest",
        contamination: float = 0.05,
        selected_columns: Optional[List[str]] = None
    ) -> AnomalyResult:
        """Run ML anomaly detection and persist findings in the database."""
        dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not dataset:
            raise ValueError(f"Dataset {dataset_id} not found")

        file_path = dataset.file_path
        if version_id:
            ver = db.query(DatasetVersion).filter(DatasetVersion.id == version_id, DatasetVersion.dataset_id == dataset_id).first()
            if ver:
                file_path = ver.file_path

        df = IngestionService.load_dataframe(file_path, dataset.file_type)

        if detector_type == "isolation_forest":
            ml_res = cls.detect_anomalies_isolation_forest(df, contamination, selected_columns)
        else:
            # Statistical method
            stat_res = cls.detect_statistical_outliers(df, method=detector_type)
            # Format into common schema
            ml_res = {
                "anomalous_rows_count": stat_res["total_outliers_count"],
                "total_evaluated_rows": len(df),
                "anomaly_indices": stat_res["outlier_indices"],
                "feature_importance": {k: v["count"] for k, v in stat_res["feature_outliers"].items()},
                "anomaly_samples": [
                    {
                        "row_index": idx,
                        "anomaly_score": 1.0,
                        "values": {str(k): make_json_serializable(v) for k, v in df.iloc[idx].to_dict().items()},
                        "flagged_reasons": ["Statistical IQR/Z-score outlier"]
                    }
                    for idx in stat_res["outlier_indices"][:20]
                ]
            }

        anomaly_record = AnomalyResult(
            dataset_id=dataset.id,
            version_id=version_id,
            detector_type=detector_type,
            contamination_rate=contamination,
            anomalous_rows_count=ml_res["anomalous_rows_count"],
            total_evaluated_rows=ml_res["total_evaluated_rows"],
            anomaly_indices=ml_res["anomaly_indices"],
            feature_importance=ml_res["feature_importance"],
            anomaly_samples=ml_res["anomaly_samples"]
        )
        db.add(anomaly_record)
        db.commit()
        db.refresh(anomaly_record)
        logger.info(f"Anomaly analysis completed for dataset {dataset_id}. Found {anomaly_record.anomalous_rows_count} anomalies.")
        return anomaly_record
