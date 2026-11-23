from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd
from scipy import stats
from sqlalchemy.orm import Session
from app.models.dataset import Dataset, DatasetVersion, DatasetSchema
from app.models.drift import DriftResult
from app.services.ingestion import IngestionService
from app.core.logging import logger

class DriftEngine:
    @staticmethod
    def calculate_psi(baseline: np.ndarray, current: np.ndarray, num_bins: int = 10) -> Tuple[float, Dict[str, Any]]:
        """Calculate Population Stability Index (PSI) between two numeric distributions."""
        baseline = baseline[~np.isnan(baseline)]
        current = current[~np.isnan(current)]

        if len(baseline) == 0 or len(current) == 0:
            return 0.0, {}

        # Define bins using quantiles of baseline
        quantiles = np.linspace(0, 100, num_bins + 1)
        bins = np.percentile(baseline, quantiles)
        bins = np.unique(bins)  # Handle duplicate quantile edges

        if len(bins) < 2:
            return 0.0, {}

        # Add small margins to outer bins
        bins[0] -= 1e-5
        bins[-1] += 1e-5

        # Bin counts
        b_counts, _ = np.histogram(baseline, bins=bins)
        c_counts, _ = np.histogram(current, bins=bins)

        # Convert to proportions with Laplace smoothing
        b_prop = (b_counts + 1e-4) / (len(baseline) + 1e-4 * len(b_counts))
        c_prop = (c_counts + 1e-4) / (len(current) + 1e-4 * len(c_counts))

        # PSI formula: sum((c_i - b_i) * ln(c_i / b_i))
        psi_values = (c_prop - b_prop) * np.log(c_prop / b_prop)
        total_psi = float(np.sum(psi_values))

        distribution_data = {
            "bins": [round(float(b), 4) for b in bins],
            "baseline_proportions": [round(float(p), 4) for p in b_prop],
            "current_proportions": [round(float(p), 4) for p in c_prop],
        }

        return max(0.0, total_psi), distribution_data

    @classmethod
    def compare_schemas(
        cls,
        base_df: pd.DataFrame,
        curr_df: pd.DataFrame
    ) -> Dict[str, Any]:
        """Detect schema differences between baseline and current datasets."""
        base_cols = set(base_df.columns)
        curr_cols = set(curr_df.columns)

        added = sorted(list(curr_cols - base_cols))
        removed = sorted(list(base_cols - curr_cols))
        common = sorted(list(base_cols & curr_cols))

        type_changes = []
        nullability_changes = []
        unexpected_categories = []

        for col in common:
            base_type = str(base_df[col].dtype)
            curr_type = str(curr_df[col].dtype)
            if base_type != curr_type:
                type_changes.append({
                    "column": col,
                    "baseline_type": base_type,
                    "current_type": curr_type
                })

            base_has_nulls = bool(base_df[col].isna().any())
            curr_has_nulls = bool(curr_df[col].isna().any())
            if not base_has_nulls and curr_has_nulls:
                nullability_changes.append({
                    "column": col,
                    "baseline_nullable": False,
                    "current_nullable": True,
                    "new_null_count": int(curr_df[col].isna().sum())
                })

            # Check categorical additions
            if not pd.api.types.is_numeric_dtype(base_df[col]) and not pd.api.types.is_numeric_dtype(curr_df[col]):
                base_cats = set(base_df[col].dropna().astype(str).unique())
                curr_cats = set(curr_df[col].dropna().astype(str).unique())
                new_cats = curr_cats - base_cats
                if new_cats and len(new_cats) <= 20:
                    unexpected_categories.append({
                        "column": col,
                        "new_categories": sorted(list(new_cats))
                    })

        return {
            "added_columns": added,
            "removed_columns": removed,
            "type_changes": type_changes,
            "nullability_changes": nullability_changes,
            "unexpected_categories": unexpected_categories
        }

    @classmethod
    def analyze_drift(
        cls,
        base_df: pd.DataFrame,
        curr_df: pd.DataFrame,
        p_val_threshold: float = 0.05,
        psi_threshold: float = 0.25
    ) -> Dict[str, Any]:
        """Exhaustive data and schema drift analysis between two DataFrames."""
        schema_diff = cls.compare_schemas(base_df, curr_df)
        common_cols = [c for c in base_df.columns if c in curr_df.columns]

        feature_metrics: Dict[str, Any] = {}
        drifted_count = 0
        total_features = len(common_cols)

        for col in common_cols:
            base_series = base_df[col]
            curr_series = curr_df[col]

            if pd.api.types.is_numeric_dtype(base_series) and pd.api.types.is_numeric_dtype(curr_series):
                b_arr = base_series.dropna().to_numpy()
                c_arr = curr_series.dropna().to_numpy()

                if len(b_arr) > 4 and len(c_arr) > 4:
                    # Two-sample KS test
                    ks_res = stats.ks_2samp(b_arr, c_arr)
                    ks_stat = float(ks_res.statistic)
                    p_val = float(ks_res.pvalue)

                    # PSI
                    psi_score, dist_data = cls.calculate_psi(b_arr, c_arr)

                    is_drifted = bool(p_val < p_val_threshold or psi_score >= psi_threshold)
                    drift_level = "NONE"
                    if psi_score >= psi_threshold or p_val < 0.01:
                        drift_level = "CRITICAL"
                    elif is_drifted:
                        drift_level = "MODERATE"

                    if is_drifted:
                        drifted_count += 1

                    baseline_dist = {
                        "bins": dist_data.get("bins", []),
                        "proportions": dist_data.get("baseline_proportions", []),
                        "baseline_proportions": dist_data.get("baseline_proportions", []),
                        "current_proportions": dist_data.get("current_proportions", [])
                    }
                    current_dist = {
                        "bins": dist_data.get("bins", []),
                        "proportions": dist_data.get("current_proportions", []),
                        "baseline_proportions": dist_data.get("baseline_proportions", []),
                        "current_proportions": dist_data.get("current_proportions", [])
                    }

                    feature_metrics[col] = {
                        "column_name": col,
                        "feature_type": "numeric",
                        "is_drifted": is_drifted,
                        "ks_statistic": round(ks_stat, 4),
                        "p_value": round(p_val, 6),
                        "psi_score": round(psi_score, 4),
                        "drift_level": drift_level,
                        "baseline_distribution": baseline_dist,
                        "current_distribution": current_dist
                    }
                else:
                    feature_metrics[col] = {
                        "column_name": col,
                        "feature_type": "numeric",
                        "is_drifted": False,
                        "drift_level": "NONE"
                    }
            else:
                # Categorical drift based on frequency changes
                b_counts = base_series.value_counts(normalize=True)
                c_counts = curr_series.value_counts(normalize=True)
                all_cats = list(set(b_counts.index) | set(c_counts.index))

                max_diff = 0.0
                for cat in all_cats:
                    diff = abs(c_counts.get(cat, 0.0) - b_counts.get(cat, 0.0))
                    if diff > max_diff:
                        max_diff = diff

                is_drifted = max_diff > 0.20
                if is_drifted:
                    drifted_count += 1

                feature_metrics[col] = {
                    "column_name": col,
                    "feature_type": "categorical",
                    "is_drifted": is_drifted,
                    "psi_score": round(float(max_diff), 4),
                    "drift_level": "MODERATE" if is_drifted else "NONE"
                }

        overall_drift_detected = (drifted_count > 0) or len(schema_diff["added_columns"]) > 0 or len(schema_diff["removed_columns"]) > 0
        drift_score = round((drifted_count / max(1, total_features)) * 100, 2)

        return {
            "overall_drift_detected": overall_drift_detected,
            "drift_score": drift_score,
            "drifted_features_count": drifted_count,
            "total_features_count": total_features,
            "feature_metrics": feature_metrics,
            "schema_diff": schema_diff
        }

    @classmethod
    def run_drift_analysis(
        cls,
        db: Session,
        dataset_id: int,
        baseline_version_id: int,
        current_version_id: int,
        p_val_threshold: float = 0.05,
        psi_threshold: float = 0.25
    ) -> DriftResult:
        """Run drift analysis between two versions and persist."""
        dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not dataset:
            raise ValueError(f"Dataset {dataset_id} not found")

        v_base = db.query(DatasetVersion).filter(DatasetVersion.id == baseline_version_id).first()
        v_curr = db.query(DatasetVersion).filter(DatasetVersion.id == current_version_id).first()

        if not v_base or not v_curr:
            raise ValueError("Baseline or current dataset version not found")

        base_dataset = v_base.dataset if hasattr(v_base, "dataset") and v_base.dataset else dataset
        curr_dataset = v_curr.dataset if hasattr(v_curr, "dataset") and v_curr.dataset else dataset

        base_file_type = base_dataset.file_type if base_dataset else dataset.file_type
        curr_file_type = curr_dataset.file_type if curr_dataset else dataset.file_type

        base_df = IngestionService.load_dataframe(v_base.file_path, base_file_type)
        curr_df = IngestionService.load_dataframe(v_curr.file_path, curr_file_type)

        analysis = cls.analyze_drift(base_df, curr_df, p_val_threshold, psi_threshold)

        drift_record = DriftResult(
            dataset_id=dataset.id,
            baseline_version_id=v_base.id,
            current_version_id=v_curr.id,
            overall_drift_detected=analysis["overall_drift_detected"],
            drift_score=analysis["drift_score"],
            drifted_features_count=analysis["drifted_features_count"],
            total_features_count=analysis["total_features_count"],
            feature_metrics=analysis["feature_metrics"],
            schema_diff=analysis["schema_diff"]
        )
        db.add(drift_record)
        db.commit()
        db.refresh(drift_record)
        logger.info(f"Drift analysis completed for dataset {dataset_id} (v{v_base.version_num} vs v{v_curr.version_num}). Drift detected: {drift_record.overall_drift_detected}")
        return drift_record
