export interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  role: 'admin' | 'analyst' | 'viewer';
  is_active: boolean;
  created_at: string;
}

export interface Dataset {
  id: number;
  name: string;
  description?: string;
  file_type: 'csv' | 'excel' | 'json' | 'database';
  original_filename: string;
  file_size_bytes: number;
  row_count: number;
  column_count: number;
  sha256_hash: string;
  owner_id: number;
  is_active: boolean;
  created_at: string;
  latest_quality_score?: number;
  versions_count?: number;
}

export interface DatasetVersion {
  id: number;
  dataset_id: number;
  version_num: number;
  row_count: number;
  column_count: number;
  change_summary?: string;
  is_remediated: boolean;
  created_at: string;
}

export interface ColumnMetric {
  name: string;
  data_type: string;
  inferred_type: string;
  total_count: number;
  null_count: number;
  null_percentage: number;
  unique_count: number;
  unique_percentage: number;
  min_value?: number;
  max_value?: number;
  mean_value?: number;
  std_value?: number;
  median_value?: number;
  q25?: number;
  q75?: number;
  outliers_iqr_count?: number;
  top_frequent_values?: Array<{ value: string; count: number }>;
  histogram?: {
    counts: number[];
    bin_edges: number[];
  };
}

export interface QualityBreakdown {
  overall_score: number;
  completeness_score: number;
  uniqueness_score: number;
  validity_score: number;
  consistency_score: number;
  penalties: {
    missingness_penalty: number;
    duplicate_penalty: number;
    outlier_penalty: number;
    consistency_penalty: number;
  };
}

export interface ProfilingResult {
  id: number;
  dataset_id: number;
  version_id?: number;
  overall_score: number;
  total_rows: number;
  total_columns: number;
  missing_cells_count: number;
  duplicate_rows_count: number;
  column_metrics: Record<string, ColumnMetric>;
  quality_breakdown: QualityBreakdown;
  created_at: string;
}

export interface AnomalySample {
  row_index: number;
  anomaly_score: number;
  values: Record<string, any>;
  flagged_reasons: string[];
}

export interface AnomalyResult {
  id: number;
  dataset_id: number;
  version_id?: number;
  detector_type: string;
  contamination_rate: number;
  anomalous_rows_count: number;
  total_evaluated_rows: number;
  anomaly_indices: number[];
  feature_importance: Record<string, number>;
  anomaly_samples: AnomalySample[];
  created_at: string;
}

export interface FeatureDriftMetric {
  column_name: string;
  feature_type: string;
  is_drifted: boolean;
  ks_statistic?: number;
  p_value?: number;
  psi_score?: number;
  drift_level: 'NONE' | 'MODERATE' | 'CRITICAL';
  baseline_distribution?: any;
  current_distribution?: any;
}

export interface SchemaDiff {
  added_columns: string[];
  removed_columns: string[];
  type_changes: Array<{ column: string; baseline_type: string; current_type: string }>;
  nullability_changes: Array<{ column: string; baseline_nullable: boolean; current_nullable: boolean; new_null_count: number }>;
  unexpected_categories: Array<{ column: string; new_categories: string[] }>;
}

export interface DriftResult {
  id: number;
  dataset_id: number;
  baseline_version_id: number;
  current_version_id: number;
  overall_drift_detected: boolean;
  drift_score: number;
  drifted_features_count: number;
  total_features_count: number;
  feature_metrics: Record<string, FeatureDriftMetric>;
  schema_diff?: SchemaDiff;
  created_at: string;
}

export interface AgentTrace {
  agent_name: string;
  role_description: string;
  status: 'SUCCESS' | 'WARNING' | 'FAILED';
  execution_time_ms: number;
  findings: Record<string, any>;
  summary_insight: string;
  rag_sources?: Array<{
    id: string;
    title: string;
    content: string;
    citation: string;
    relevance_score: number;
  }>;
}

export interface Investigation {
  id: number;
  dataset_id: number;
  version_id?: number;
  incident_id?: number;
  title: string;
  status: string;
  summary?: string;
  root_cause_hypothesis?: string;
  confidence_score: number;
  agent_traces: AgentTrace[];
  created_at: string;
  updated_at: string;
}

export interface RemediationSuggestion {
  id: number;
  dataset_id: number;
  version_id?: number;
  incident_id?: number;
  investigation_id?: number;
  problem_type: string;
  column_name?: string;
  proposed_action: string;
  parameters?: Record<string, any>;
  hypothesis?: string;
  expected_impact: string;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH';
  confidence: number;
  supporting_evidence?: string;
  status: 'PENDING' | 'APPROVED' | 'REJECTED' | 'EXECUTED';
  reviewed_by?: string;
  reviewed_at?: string;
  created_at: string;
}

export interface Incident {
  id: number;
  dataset_id: number;
  dataset_name?: string;
  version_id?: number;
  title: string;
  description: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  status: 'OPEN' | 'INVESTIGATING' | 'REMEDIATED' | 'RESOLVED';
  root_cause?: string;
  assigned_to?: string;
  resolution_notes?: string;
  timeline?: Array<{
    timestamp: string;
    event: string;
    actor: string;
    details?: string;
  }>;
  created_at: string;
  updated_at: string;
}

export interface DashboardMetrics {
  overall_health_score: number;
  total_datasets: number;
  total_anomalies_detected: number;
  total_drift_events: number;
  pending_remediations: number;
  incident_severity_distribution: Record<string, number>;
  incident_status_distribution: Record<string, number>;
  quality_score_trends: Array<{ timestamp: string; score: number; dataset: string }>;
  recent_audit_trail: Array<{
    id: number;
    action: string;
    entity_type: string;
    entity_id: string;
    timestamp: string;
  }>;
}

