import React, { useState, useEffect } from 'react';
import { Layout } from '../components/Layout';
import { StatusBadge } from '../components/StatusBadge';
import { Modal } from '../components/Modal';
import { api } from '../services/api';
import { Dataset, RemediationSuggestion } from '../types';
import {
  CheckCircle2,
  XCircle,
  Play,
  Eye,
  ShieldCheck,
  AlertTriangle,
  Sparkles,
  ArrowRight,
  Database,
  Filter,
  RefreshCw,
  Info,
  Check,
  Clock
} from 'lucide-react';

export const RemediationCenter: React.FC = () => {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [selectedDatasetId, setSelectedDatasetId] = useState<number | null>(null);
  const [remediations, setRemediations] = useState<RemediationSuggestion[]>([]);
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [loading, setLoading] = useState<boolean>(true);
  const [actionLoading, setActionLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  // Preview Modal State
  const [previewModalOpen, setPreviewModalOpen] = useState<boolean>(false);
  const [previewData, setPreviewData] = useState<any | null>(null);
  const [activeRemediation, setActiveRemediation] = useState<RemediationSuggestion | null>(null);

  // Action / Approval Modal State
  const [reviewModalOpen, setReviewModalOpen] = useState<boolean>(false);
  const [reviewAction, setReviewAction] = useState<'APPROVE' | 'REJECT'>('APPROVE');
  const [reviewNotes, setReviewNotes] = useState<string>('');

  useEffect(() => {
    fetchDatasets();
  }, []);

  useEffect(() => {
    if (selectedDatasetId) {
      fetchRemediations(selectedDatasetId, statusFilter === 'ALL' ? undefined : statusFilter);
    }
  }, [selectedDatasetId, statusFilter]);

  const fetchDatasets = async () => {
    try {
      setLoading(true);
      const data = await api.getDatasets();
      setDatasets(data);
      if (data.length > 0) {
        setSelectedDatasetId(data[0].id);
      }
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to load datasets.');
    } finally {
      setLoading(false);
    }
  };

  const fetchRemediations = async (datasetId: number, filter?: string) => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getRemediations(datasetId, filter);
      setRemediations(data);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to load remediation suggestions.');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenPreview = async (remediation: RemediationSuggestion) => {
    setActiveRemediation(remediation);
    setActionLoading(true);
    try {
      const preview = await api.previewRemediation(remediation.id, 5);
      setPreviewData(preview);
      setPreviewModalOpen(true);
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Failed to generate transformation preview.');
    } finally {
      setActionLoading(false);
    }
  };

  const handleOpenReview = (remediation: RemediationSuggestion, action: 'APPROVE' | 'REJECT') => {
    setActiveRemediation(remediation);
    setReviewAction(action);
    setReviewNotes('');
    setReviewModalOpen(true);
  };

  const handleConfirmReview = async () => {
    if (!activeRemediation) return;
    setActionLoading(true);
    try {
      await api.reviewRemediation(activeRemediation.id, reviewAction, reviewNotes);
      setSuccessMsg(`Plan successfully ${reviewAction.toLowerCase()}d.`);
      setReviewModalOpen(false);
      if (selectedDatasetId) {
        fetchRemediations(selectedDatasetId, statusFilter === 'ALL' ? undefined : statusFilter);
      }
      setTimeout(() => setSuccessMsg(null), 4000);
    } catch (err: any) {
      alert(err?.response?.data?.detail || `Failed to ${reviewAction.toLowerCase()} remediation.`);
    } finally {
      setActionLoading(false);
    }
  };

  const handleExecuteRemediation = async (remediation: RemediationSuggestion) => {
    const confirmExec = window.confirm(
      `Execute remediation "${remediation.proposed_action}"?\n\nA non-destructive copy of dataset will be created and remediated. The original dataset will remain untouched.`
    );
    if (!confirmExec) return;

    setActionLoading(true);
    try {
      const res = await api.executeRemediation(remediation.id);
      setSuccessMsg(`Successfully executed remediation! Non-destructive dataset copy created.`);
      if (selectedDatasetId) {
        fetchRemediations(selectedDatasetId, statusFilter === 'ALL' ? undefined : statusFilter);
      }
      setTimeout(() => setSuccessMsg(null), 5000);
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Failed to execute remediation on dataset.');
    } finally {
      setActionLoading(false);
    }
  };

  const filteredRemediations = statusFilter === 'ALL'
    ? remediations
    : remediations.filter(r => r.status === statusFilter);

  const getRiskBadge = (risk: string) => {
    switch (risk?.toUpperCase()) {
      case 'LOW':
        return <span className="px-2 py-0.5 rounded text-xs font-semibold bg-emerald-950/60 border border-emerald-800 text-emerald-400">LOW RISK</span>;
      case 'MEDIUM':
        return <span className="px-2 py-0.5 rounded text-xs font-semibold bg-amber-950/60 border border-amber-800 text-amber-400">MEDIUM RISK</span>;
      case 'HIGH':
        return <span className="px-2 py-0.5 rounded text-xs font-semibold bg-rose-950/60 border border-rose-800 text-rose-400">HIGH RISK</span>;
      default:
        return <span className="px-2 py-0.5 rounded text-xs font-semibold bg-gray-800 text-gray-300">{risk}</span>;
    }
  };

  return (
    <Layout
      title="Autonomous Remediation & HITL Station"
      subtitle="Review, preview, and approve AI-recommended data transformations with non-destructive copy execution."
    >
      {/* Banner / Instructions */}
      <div className="bg-gradient-to-r from-sky-950/40 via-indigo-950/30 to-purple-950/20 border border-sky-800/40 rounded-xl p-5 shadow-lg">
        <div className="flex items-start gap-4">
          <div className="p-3 bg-sky-900/40 border border-sky-700/50 rounded-lg text-sky-400 mt-1">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div className="flex-1">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              Human-in-the-Loop Safe Execution Architecture
              <span className="text-xs px-2 py-0.5 rounded bg-emerald-900/60 border border-emerald-700 text-emerald-300 font-mono">
                Zero Data Loss Guarantee
              </span>
            </h3>
            <p className="text-xs text-gray-300 mt-1 leading-relaxed">
              Every AI-proposed remediation adheres to enterprise immutability safeguards. Raw datasets are NEVER modified in place.
              When an approved remediation executes, DataSentinel AI clones the dataset into a versioned copy, executes the audited transformation,
              and recalculates the post-remediation data quality score automatically.
            </p>
          </div>
        </div>
      </div>

      {successMsg && (
        <div className="p-4 bg-emerald-950/70 border border-emerald-800 text-emerald-300 rounded-lg flex items-center gap-3 text-sm animate-fade-in">
          <CheckCircle2 className="w-5 h-5 text-emerald-400 flex-shrink-0" />
          <span>{successMsg}</span>
        </div>
      )}

      {error && (
        <div className="p-4 bg-rose-950/70 border border-rose-800 text-rose-300 rounded-lg flex items-center gap-3 text-sm">
          <AlertTriangle className="w-5 h-5 text-rose-400 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Dataset Selector & Status Filters */}
      <div className="flex flex-col md:flex-row gap-4 justify-between items-center bg-[#131b2e] border border-gray-800 p-4 rounded-xl">
        <div className="flex items-center gap-3 w-full md:w-auto">
          <Database className="w-4 h-4 text-sky-400" />
          <span className="text-xs font-semibold uppercase tracking-wider text-gray-400">Dataset:</span>
          <select
            value={selectedDatasetId || ''}
            onChange={(e) => setSelectedDatasetId(Number(e.target.value))}
            className="bg-[#0b0f19] border border-gray-700 text-gray-200 text-xs rounded-lg px-3 py-2 focus:ring-1 focus:ring-sky-500 focus:outline-none"
          >
            {datasets.map((d) => (
              <option key={d.id} value={d.id}>
                {d.name} ({d.file_type.toUpperCase()} • {d.row_count} rows)
              </option>
            ))}
          </select>
          <button
            onClick={() => selectedDatasetId && fetchRemediations(selectedDatasetId, statusFilter === 'ALL' ? undefined : statusFilter)}
            disabled={loading}
            className="p-2 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-lg text-xs flex items-center gap-1 transition"
            title="Refresh Remediations"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>

        {/* Filter Pills */}
        <div className="flex items-center gap-2 overflow-x-auto w-full md:w-auto pb-1 md:pb-0">
          <Filter className="w-3.5 h-3.5 text-gray-400" />
          {['ALL', 'PENDING', 'APPROVED', 'EXECUTED', 'REJECTED'].map((filter) => (
            <button
              key={filter}
              onClick={() => setStatusFilter(filter)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                statusFilter === filter
                  ? 'bg-sky-600 text-white shadow-md shadow-sky-600/30'
                  : 'bg-gray-800/80 text-gray-400 hover:text-gray-200 hover:bg-gray-800'
              }`}
            >
              {filter}
            </button>
          ))}
        </div>
      </div>

      {/* Remediation Cards List */}
      <div className="space-y-4">
        {loading ? (
          <div className="p-12 text-center bg-[#131b2e] border border-gray-800 rounded-xl">
            <RefreshCw className="w-8 h-8 text-sky-400 animate-spin mx-auto mb-3" />
            <p className="text-sm text-gray-400 font-mono">Fetching AI remediation plans...</p>
          </div>
        ) : filteredRemediations.length === 0 ? (
          <div className="p-12 text-center bg-[#131b2e] border border-gray-800 rounded-xl space-y-3">
            <CheckCircle2 className="w-10 h-10 text-emerald-400 mx-auto" />
            <h4 className="text-sm font-semibold text-gray-200">No Remediations Found</h4>
            <p className="text-xs text-gray-400 max-w-md mx-auto">
              There are currently no {statusFilter !== 'ALL' ? statusFilter.toLowerCase() : ''} remediation plans for this dataset.
              Run an AI Investigation to identify quality defects and generate autonomous remediation proposals.
            </p>
          </div>
        ) : (
          filteredRemediations.map((rem) => (
            <div
              key={rem.id}
              className="bg-[#131b2e] border border-gray-800/90 rounded-xl p-6 hover:border-gray-700/80 transition-all shadow-md space-y-4"
            >
              {/* Card Header */}
              <div className="flex flex-wrap items-center justify-between gap-3 border-b border-gray-800 pb-3">
                <div className="flex items-center gap-3">
                  <span className="px-2.5 py-1 rounded bg-sky-950/80 border border-sky-800 text-sky-400 text-xs font-mono font-semibold">
                    {rem.problem_type}
                  </span>
                  {rem.column_name && (
                    <span className="text-xs font-mono text-gray-300 bg-gray-800/60 px-2 py-0.5 rounded border border-gray-700">
                      Column: <span className="text-white font-bold">{rem.column_name}</span>
                    </span>
                  )}
                  {getRiskBadge(rem.risk_level)}
                </div>

                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-1.5 text-xs text-gray-400 font-mono">
                    <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                    <span>Confidence: {(rem.confidence * 100).toFixed(0)}%</span>
                  </div>
                  <StatusBadge status={rem.status} />
                </div>
              </div>

              {/* Card Body */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2 space-y-3">
                  <div>
                    <div className="text-xs font-mono text-gray-400 uppercase tracking-wider mb-1">Proposed Transformation Action</div>
                    <div className="text-base font-semibold text-white flex items-center gap-2">
                      <span className="font-mono text-sky-400">{rem.proposed_action}</span>
                    </div>
                  </div>

                  {rem.hypothesis && (
                    <div className="text-xs text-gray-300 leading-relaxed bg-[#0b0f19]/60 p-3 rounded-lg border border-gray-800">
                      <span className="font-semibold text-gray-400 font-mono uppercase block mb-1">Diagnostic Hypothesis:</span>
                      {rem.hypothesis}
                    </div>
                  )}

                  {rem.supporting_evidence && (
                    <div className="text-xs text-gray-400 leading-relaxed">
                      <span className="font-semibold text-gray-400 font-mono uppercase block mb-1">Evidence:</span>
                      {rem.supporting_evidence}
                    </div>
                  )}
                </div>

                {/* Right Metric Summary */}
                <div className="bg-[#0b0f19] border border-gray-800/80 rounded-xl p-4 flex flex-col justify-between space-y-3">
                  <div>
                    <div className="text-xs font-mono text-gray-400 uppercase tracking-wider mb-1">Expected Quality Impact</div>
                    <div className="text-sm font-semibold text-emerald-400 flex items-center gap-1.5">
                      <CheckCircle2 className="w-4 h-4" />
                      {rem.expected_impact}
                    </div>
                  </div>

                  {rem.parameters && Object.keys(rem.parameters).length > 0 && (
                    <div>
                      <div className="text-xs font-mono text-gray-400 uppercase tracking-wider mb-1">Strategy Parameters</div>
                      <pre className="text-[11px] font-mono text-gray-300 bg-gray-900/80 p-2 rounded border border-gray-800 overflow-x-auto">
                        {JSON.stringify(rem.parameters, null, 2)}
                      </pre>
                    </div>
                  )}

                  <div className="pt-2 border-t border-gray-800 flex items-center justify-between text-[11px] text-gray-400 font-mono">
                    <span>Created: {new Date(rem.created_at).toLocaleDateString()}</span>
                    {rem.reviewed_by && <span>Reviewer: {rem.reviewed_by}</span>}
                  </div>
                </div>
              </div>

              {/* Action Toolbar */}
              <div className="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-gray-800">
                <button
                  onClick={() => handleOpenPreview(rem)}
                  disabled={actionLoading}
                  className="px-3.5 py-1.5 bg-gray-800 hover:bg-gray-700 text-sky-400 border border-sky-800/40 rounded-lg text-xs font-medium flex items-center gap-2 transition"
                >
                  <Eye className="w-3.5 h-3.5" />
                  Preview Transformation Diff
                </button>

                <div className="flex items-center gap-2">
                  {rem.status === 'PENDING' && (
                    <>
                      <button
                        onClick={() => handleOpenReview(rem, 'REJECT')}
                        disabled={actionLoading}
                        className="px-3.5 py-1.5 bg-rose-950/60 hover:bg-rose-900/60 text-rose-300 border border-rose-800/60 rounded-lg text-xs font-medium flex items-center gap-1.5 transition"
                      >
                        <XCircle className="w-3.5 h-3.5" />
                        Reject
                      </button>
                      <button
                        onClick={() => handleOpenReview(rem, 'APPROVE')}
                        disabled={actionLoading}
                        className="px-4 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5 shadow-md shadow-emerald-700/30 transition"
                      >
                        <Check className="w-3.5 h-3.5" />
                        Approve Plan
                      </button>
                    </>
                  )}

                  {rem.status === 'APPROVED' && (
                    <button
                      onClick={() => handleExecuteRemediation(rem)}
                      disabled={actionLoading}
                      className="px-4 py-1.5 bg-gradient-to-r from-sky-600 to-indigo-600 hover:from-sky-500 hover:to-indigo-500 text-white rounded-lg text-xs font-semibold flex items-center gap-2 shadow-lg shadow-sky-600/30 transition"
                    >
                      <Play className="w-3.5 h-3.5 fill-current" />
                      Execute on Cloned Copy
                    </button>
                  )}

                  {rem.status === 'EXECUTED' && (
                    <div className="flex items-center gap-2 text-xs font-mono text-emerald-400 bg-emerald-950/40 px-3 py-1.5 rounded-lg border border-emerald-800/60">
                      <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                      <span>Executed Non-Destructively • Version Cloned</span>
                    </div>
                  )}

                  {rem.status === 'REJECTED' && (
                    <div className="flex items-center gap-2 text-xs font-mono text-rose-400 bg-rose-950/40 px-3 py-1.5 rounded-lg border border-rose-800/60">
                      <XCircle className="w-4 h-4 text-rose-400" />
                      <span>Plan Disapproved by Reviewer</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Preview Transformation Diff Modal */}
      <Modal
        isOpen={previewModalOpen}
        onClose={() => setPreviewModalOpen(false)}
        title="Safe Transformation Diff Preview"
        maxWidth="max-w-4xl"
      >
        {previewData && (
          <div className="space-y-5">
            <div className="bg-[#0b0f19] border border-gray-800 rounded-xl p-4 flex flex-wrap items-center justify-between gap-4">
              <div>
                <span className="text-xs font-mono text-gray-400 uppercase block">Action</span>
                <span className="text-sm font-bold text-sky-400 font-mono">
                  {previewData.action || activeRemediation?.proposed_action}
                </span>
              </div>
              <div>
                <span className="text-xs font-mono text-gray-400 uppercase block">Affected Records</span>
                <span className="text-sm font-bold text-amber-400 font-mono">
                  {previewData.rows_affected} records
                </span>
              </div>
              <div>
                <span className="text-xs font-mono text-gray-400 uppercase block">Est. Quality Improvement</span>
                <span className="text-sm font-bold text-emerald-400 font-mono flex items-center gap-1">
                  +{previewData.estimated_quality_gain || 5.0} points
                </span>
              </div>
            </div>

            {/* Side-by-Side Before and After Records */}
            {previewData.preview_diff ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Before Diff */}
                <div className="bg-[#0b0f19] border border-rose-900/40 rounded-xl p-4 space-y-3">
                  <div className="text-xs font-bold text-rose-400 flex items-center gap-2 border-b border-rose-900/40 pb-2">
                    <span className="w-2.5 h-2.5 rounded-full bg-rose-500"></span>
                    BEFORE (Original Data Records)
                  </div>
                  <div className="max-h-72 overflow-y-auto space-y-2">
                    {previewData.preview_diff.before && previewData.preview_diff.before.map((row: any, idx: number) => (
                      <div key={idx} className="bg-gray-900/70 p-2.5 rounded border border-gray-800 text-[11px] font-mono text-gray-300">
                        <div className="text-gray-400 font-bold mb-1">Row #{idx + 1}</div>
                        <div className="grid grid-cols-2 gap-x-2 gap-y-1">
                          {Object.entries(row).slice(0, 6).map(([k, v]) => (
                            <div key={k} className="truncate">
                              <span className="text-gray-400">{k}:</span>{' '}
                              <span className={v === null || v === '' ? 'text-rose-400 font-bold bg-rose-950/60 px-1 rounded' : 'text-gray-200'}>
                                {v === null ? 'NULL' : String(v)}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* After Diff */}
                <div className="bg-[#0b0f19] border border-emerald-900/40 rounded-xl p-4 space-y-3">
                  <div className="text-xs font-bold text-emerald-400 flex items-center gap-2 border-b border-emerald-900/40 pb-2">
                    <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
                    AFTER (Remediated Transformation Preview)
                  </div>
                  <div className="max-h-72 overflow-y-auto space-y-2">
                    {previewData.preview_diff.after && previewData.preview_diff.after.map((row: any, idx: number) => (
                      <div key={idx} className="bg-gray-900/70 p-2.5 rounded border border-gray-800 text-[11px] font-mono text-gray-300">
                        <div className="text-emerald-400 font-bold mb-1">Row #{idx + 1} (Transformed)</div>
                        <div className="grid grid-cols-2 gap-x-2 gap-y-1">
                          {Object.entries(row).slice(0, 6).map(([k, v]) => (
                            <div key={k} className="truncate">
                              <span className="text-gray-400">{k}:</span>{' '}
                              <span className="text-emerald-300 font-semibold bg-emerald-950/40 px-1 rounded">
                                {v === null ? 'NULL' : String(v)}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-xs text-gray-400 font-mono text-center py-6">
                Transformation preview generated without record diffs.
              </div>
            )}

            <div className="flex justify-end gap-3 pt-3 border-t border-gray-800">
              <button
                onClick={() => setPreviewModalOpen(false)}
                className="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-lg text-xs font-medium transition"
              >
                Close Preview
              </button>
            </div>
          </div>
        )}
      </Modal>

      {/* Review & Approval Modal */}
      <Modal
        isOpen={reviewModalOpen}
        onClose={() => setReviewModalOpen(false)}
        title={reviewAction === 'APPROVE' ? 'Approve Remediation Plan' : 'Reject Remediation Plan'}
        maxWidth="max-w-lg"
      >
        <div className="space-y-4">
          <p className="text-xs text-gray-300 leading-relaxed">
            {reviewAction === 'APPROVE'
              ? 'By approving this plan, you authorize DataSentinel AI to execute the proposed transformation upon human confirmation. A non-destructive clone of the dataset will be created.'
              : 'Please provide reason notes explaining why this proposed transformation is being declined for the audit log.'}
          </p>

          <div>
            <label className="text-xs font-mono text-gray-400 block mb-1">Reviewer Audit Notes (Optional)</label>
            <textarea
              value={reviewNotes}
              onChange={(e) => setReviewNotes(e.target.value)}
              placeholder="e.g. Approved strategy for Q4 baseline normalization. Verified column nullability thresholds."
              rows={3}
              className="w-full bg-[#0b0f19] border border-gray-700 text-gray-200 text-xs rounded-lg p-3 focus:ring-1 focus:ring-sky-500 focus:outline-none"
            />
          </div>

          <div className="flex justify-end gap-3 pt-3 border-t border-gray-800">
            <button
              onClick={() => setReviewModalOpen(false)}
              className="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-lg text-xs font-medium transition"
            >
              Cancel
            </button>
            <button
              onClick={handleConfirmReview}
              disabled={actionLoading}
              className={`px-5 py-2 rounded-lg text-xs font-semibold text-white transition flex items-center gap-2 ${
                reviewAction === 'APPROVE'
                  ? 'bg-emerald-600 hover:bg-emerald-500'
                  : 'bg-rose-600 hover:bg-rose-500'
              }`}
            >
              {actionLoading ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : null}
              Confirm {reviewAction === 'APPROVE' ? 'Approval' : 'Rejection'}
            </button>
          </div>
        </div>
      </Modal>
    </Layout>
  );
};
export default RemediationCenter;
