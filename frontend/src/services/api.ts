import axios from 'axios';
import {
  User,
  Dataset,
  ProfilingResult,
  AnomalyResult,
  DriftResult,
  Investigation,
  RemediationSuggestion,
  Incident,
  DashboardMetrics
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to inject JWT bearer token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('datasentinel_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for authentication errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('datasentinel_token');
      localStorage.removeItem('datasentinel_user');
      if (window.location.pathname !== '/login' && window.location.pathname !== '/register') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export const api = {
  // Auth
  login: async (credentials: { username_or_email: string; password: string }) => {
    const res = await apiClient.post<{ access_token: string; user: User }>('/auth/login', credentials);
    return res.data;
  },
  register: async (userData: any) => {
    const res = await apiClient.post<User>('/auth/register', userData);
    return res.data;
  },
  getMe: async () => {
    const res = await apiClient.get<User>('/auth/me');
    return res.data;
  },

  // Datasets
  getDatasets: async () => {
    const res = await apiClient.get<Dataset[]>('/datasets/');
    return res.data;
  },
  getDataset: async (id: number) => {
    const res = await apiClient.get<any>(`/datasets/${id}`);
    return res.data;
  },
  uploadDataset: async (formData: FormData) => {
    const res = await apiClient.post<Dataset>('/datasets/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },
  deleteDataset: async (id: number) => {
    await apiClient.delete(`/datasets/${id}`);
  },

  // Profiling
  runProfiling: async (datasetId: number, versionId?: number) => {
    const url = versionId ? `/profiling/${datasetId}/run?version_id=${versionId}` : `/profiling/${datasetId}/run`;
    const res = await apiClient.post<ProfilingResult>(url);
    return res.data;
  },
  getLatestProfiling: async (datasetId: number) => {
    const res = await apiClient.get<ProfilingResult>(`/profiling/${datasetId}/latest`);
    return res.data;
  },
  getProfilingHistory: async (datasetId: number) => {
    const res = await apiClient.get<ProfilingResult[]>(`/profiling/${datasetId}/history`);
    return res.data;
  },

  // Machine Learning Anomaly Detection
  runAnomalies: async (datasetId: number, params: { detector_type: string; contamination_rate: number; selected_columns?: string[] }) => {
    const res = await apiClient.post<AnomalyResult>(`/ml/${datasetId}/anomalies`, params);
    return res.data;
  },
  getLatestAnomalies: async (datasetId: number) => {
    const res = await apiClient.get<AnomalyResult>(`/ml/${datasetId}/anomalies/latest`);
    return res.data;
  },

  // Drift
  runDriftAnalysis: async (datasetId: number, params: { baseline_version_id: number; current_version_id: number; p_value_threshold?: number; psi_threshold?: number }) => {
    const res = await apiClient.post<DriftResult>(`/drift/${datasetId}/analyze`, params);
    return res.data;
  },
  getLatestDrift: async (datasetId: number) => {
    const res = await apiClient.get<DriftResult>(`/drift/${datasetId}/latest`);
    return res.data;
  },

  // Investigations (LangGraph)
  startInvestigation: async (datasetId: number, params: { incident_id?: number; version_id?: number; focus_areas?: string[] }) => {
    const res = await apiClient.post<Investigation>(`/investigations/${datasetId}/start`, params);
    return res.data;
  },
  getInvestigation: async (id: number) => {
    const res = await apiClient.get<Investigation>(`/investigations/${id}`);
    return res.data;
  },
  getDatasetInvestigations: async (datasetId: number) => {
    const res = await apiClient.get<Investigation[]>(`/investigations/dataset/${datasetId}`);
    return res.data;
  },

  // Remediation
  getRemediations: async (datasetId: number, statusFilter?: string) => {
    const url = statusFilter ? `/remediation/${datasetId}/list?status_filter=${statusFilter}` : `/remediation/${datasetId}/list`;
    const res = await apiClient.get<RemediationSuggestion[]>(url);
    return res.data;
  },
  previewRemediation: async (remediationId: number, limit = 5) => {
    const res = await apiClient.post<any>(`/remediation/${remediationId}/preview?preview_limit=${limit}`);
    return res.data;
  },
  reviewRemediation: async (remediationId: number, action: 'APPROVE' | 'REJECT', notes?: string) => {
    const res = await apiClient.post<RemediationSuggestion>(`/remediation/${remediationId}/action`, {
      action,
      reviewer_notes: notes,
    });
    return res.data;
  },
  executeRemediation: async (remediationId: number) => {
    const res = await apiClient.post<RemediationSuggestion>(`/remediation/${remediationId}/execute`);
    return res.data;
  },

  // Incidents
  getIncidents: async (filters?: { status?: string; severity?: string; dataset_id?: number }) => {
    let url = '/incidents/?';
    if (filters?.status) url += `status_filter=${filters.status}&`;
    if (filters?.severity) url += `severity_filter=${filters.severity}&`;
    if (filters?.dataset_id) url += `dataset_id=${filters.dataset_id}&`;
    const res = await apiClient.get<Incident[]>(url);
    return res.data;
  },
  getIncident: async (id: number) => {
    const res = await apiClient.get<Incident>(`/incidents/${id}`);
    return res.data;
  },
  createIncident: async (data: any) => {
    const res = await apiClient.post<Incident>('/incidents/', data);
    return res.data;
  },
  updateIncident: async (id: number, data: any) => {
    const res = await apiClient.patch<Incident>(`/incidents/${id}`, data);
    return res.data;
  },

  // Reports & Analytics
  getDashboardMetrics: async () => {
    const res = await apiClient.get<DashboardMetrics>('/reports/dashboard/metrics');
    return res.data;
  },
  downloadInvestigationPdf: async (investigationId: number) => {
    const res = await apiClient.get(`/reports/export/investigation/${investigationId}/pdf`, {
      responseType: 'blob',
    });
    return res.data as Blob;
  },
  downloadInvestigationCsv: async (investigationId: number) => {
    const res = await apiClient.get(`/reports/export/investigation/${investigationId}/csv`, {
      responseType: 'blob',
    });
    return res.data as Blob;
  },
  getExportPdfUrl: (investigationId: number) => `${API_BASE_URL}/reports/export/investigation/${investigationId}/pdf`,
  getExportCsvUrl: (investigationId: number) => `${API_BASE_URL}/reports/export/investigation/${investigationId}/csv`,

  // RAG
  searchKnowledge: async (query: string, category?: string) => {
    let url = `/rag/search?query=${encodeURIComponent(query)}`;
    if (category) url += `&category=${category}`;
    const res = await apiClient.get<any[]>(url);
    return res.data;
  },
  getAllKnowledge: async () => {
    const res = await apiClient.get<any[]>('/rag/all');
    return res.data;
  },
};

