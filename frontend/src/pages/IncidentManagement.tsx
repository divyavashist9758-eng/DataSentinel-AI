import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Layout } from '../components/Layout';
import { StatusBadge } from '../components/StatusBadge';
import { Modal } from '../components/Modal';
import { api } from '../services/api';
import { Incident, Dataset } from '../types';
import {
  AlertTriangle,
  Plus,
  Filter,
  Clock,
  User,
  CheckCircle2,
  AlertCircle,
  FileText,
  Search,
  MessageSquare
} from 'lucide-react';

export const IncidentManagement: React.FC = () => {
  const [searchParams] = useSearchParams();
  const dsParam = searchParams.get('dataset_id');

  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  // Filters
  const [severityFilter, setSeverityFilter] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('');

  // Modals & Active
  const [isCreateOpen, setIsCreateOpen] = useState<boolean>(false);
  const [selectedIncident, setSelectedIncident] = useState<Incident | null>(null);

  // Create form state
  const [newTitle, setNewTitle] = useState('');
  const [newDesc, setNewDesc] = useState('');
  const [newSeverity, setNewSeverity] = useState('HIGH');
  const [newDatasetId, setNewDatasetId] = useState<number | null>(null);
  const [newAssignee, setNewAssignee] = useState('admin');
  const [creating, setCreating] = useState(false);

  // Update notes
  const [resolutionNotes, setResolutionNotes] = useState('');
  const [updating, setUpdating] = useState(false);

  const fetchIncidents = async () => {
    try {
      setLoading(true);
      const data = await api.getIncidents({
        severity: severityFilter || undefined,
        status: statusFilter || undefined,
        dataset_id: dsParam ? parseInt(dsParam) : undefined,
      });
      setIncidents(data);
      if (selectedIncident) {
        const refreshed = data.find((i) => i.id === selectedIncident.id);
        if (refreshed) setSelectedIncident(refreshed);
      }
    } catch (err) {
      console.error('Failed to fetch incidents:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const loadDatasets = async () => {
      try {
        const list = await api.getDatasets();
        setDatasets(list);
        if (list.length > 0 && !newDatasetId) {
          setNewDatasetId(list[0].id);
        }
      } catch (err) {
        console.error('Error fetching datasets:', err);
      }
    };
    loadDatasets();
  }, []);

  useEffect(() => {
    fetchIncidents();
  }, [severityFilter, statusFilter, dsParam]);

  const handleCreateIncident = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newDatasetId || !newTitle) return;

    try {
      setCreating(true);
      const created = await api.createIncident({
        dataset_id: newDatasetId,
        title: newTitle,
        description: newDesc,
        severity: newSeverity,
        assigned_to: newAssignee,
      });
      setIsCreateOpen(false);
      setNewTitle('');
      setNewDesc('');
      fetchIncidents();
      setSelectedIncident(created);
    } catch (err) {
      console.error('Failed to create incident:', err);
    } finally {
      setCreating(false);
    }
  };

  const handleStatusChange = async (newStatus: string) => {
    if (!selectedIncident) return;
    try {
      setUpdating(true);
      const updated = await api.updateIncident(selectedIncident.id, {
        status: newStatus,
        resolution_notes: resolutionNotes || undefined,
      });
      setSelectedIncident(updated);
      fetchIncidents();
      setResolutionNotes('');
    } catch (err) {
      console.error('Failed to update incident:', err);
    } finally {
      setUpdating(false);
    }
  };

  return (
    <Layout title="Incident Response & SLA Management" subtitle="Track Critical Data Pipeline Failures, Quality Degradations, and Root Causes">
      {/* Action & Filter Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pb-2">
        <div className="flex flex-wrap items-center gap-3 w-full sm:w-auto font-mono text-xs">
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="px-3 py-2 bg-gray-900 border border-gray-800 rounded-lg text-white focus:outline-none focus:border-sky-500"
          >
            <option value="">All Severities</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 bg-gray-900 border border-gray-800 rounded-lg text-white focus:outline-none focus:border-sky-500"
          >
            <option value="">All Statuses</option>
            <option value="OPEN">Open</option>
            <option value="INVESTIGATING">Investigating</option>
            <option value="REMEDIATED">Remediated</option>
            <option value="RESOLVED">Resolved</option>
          </select>
        </div>

        <button
          onClick={() => setIsCreateOpen(true)}
          className="w-full sm:w-auto flex items-center justify-center gap-2 px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white rounded-lg text-xs font-semibold transition-colors shadow-lg shadow-rose-600/20"
        >
          <Plus className="w-4 h-4" />
          <span>Log New Incident</span>
        </button>
      </div>

      {/* Main Grid: Incidents List & Incident Inspector */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Incident List */}
        <div className="glass-card rounded-2xl border border-gray-800 overflow-hidden lg:col-span-1">
          <div className="p-4 border-b border-gray-800 bg-gray-900/50 flex items-center justify-between">
            <h3 className="text-xs font-mono uppercase tracking-wider text-white font-semibold">
              Pipeline Incidents ({incidents.length})
            </h3>
          </div>

          <div className="divide-y divide-gray-800/60 max-h-[600px] overflow-y-auto">
            {loading ? (
              <div className="py-12 text-center text-gray-500 font-mono text-xs">Loading incidents...</div>
            ) : incidents.length === 0 ? (
              <div className="py-12 text-center text-gray-500 font-mono text-xs">No incidents matching filters.</div>
            ) : (
              incidents.map((inc) => {
                const isSelected = selectedIncident?.id === inc.id;
                return (
                  <div
                    key={inc.id}
                    onClick={() => setSelectedIncident(inc)}
                    className={`p-4 cursor-pointer transition-colors ${
                      isSelected ? 'bg-sky-500/10 border-l-2 border-sky-400' : 'hover:bg-gray-800/30'
                    }`}
                  >
                    <div className="flex items-center justify-between gap-2 mb-1.5">
                      <StatusBadge status={inc.severity} type="severity" />
                      <StatusBadge status={inc.status} />
                    </div>
                    <div className="font-semibold text-xs text-white font-sans">{inc.title}</div>
                    <div className="flex items-center justify-between mt-2 text-[10px] font-mono text-gray-500">
                      <span>{inc.dataset_name || `Dataset #${inc.dataset_id}`}</span>
                      <span>{new Date(inc.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Selected Incident Detail View */}
        <div className="glass-card rounded-2xl p-6 border border-gray-800 lg:col-span-2 space-y-6">
          {selectedIncident ? (
            <>
              {/* Header */}
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-gray-800 pb-4">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <StatusBadge status={selectedIncident.severity} type="severity" />
                    <StatusBadge status={selectedIncident.status} />
                    <span className="text-[10px] font-mono text-gray-500">Incident #{selectedIncident.id}</span>
                  </div>
                  <h3 className="text-lg font-bold text-white font-sans">{selectedIncident.title}</h3>
                  <p className="text-xs text-gray-400 font-mono mt-0.5">
                    Target Dataset: <span className="text-sky-300 font-semibold">{selectedIncident.dataset_name || `#${selectedIncident.dataset_id}`}</span> &bull; Assigned to: <span className="text-gray-300">{selectedIncident.assigned_to || 'Unassigned'}</span>
                  </p>
                </div>

                {/* State Transition Actions */}
                <div className="flex flex-wrap items-center gap-2">
                  {selectedIncident.status === 'OPEN' && (
                    <button
                      onClick={() => handleStatusChange('INVESTIGATING')}
                      disabled={updating}
                      className="px-3 py-1.5 rounded-lg bg-sky-600 hover:bg-sky-500 text-white font-mono text-xs font-semibold"
                    >
                      Investigate
                    </button>
                  )}
                  {selectedIncident.status === 'INVESTIGATING' && (
                    <button
                      onClick={() => handleStatusChange('REMEDIATED')}
                      disabled={updating}
                      className="px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-mono text-xs font-semibold"
                    >
                      Mark Remediated
                    </button>
                  )}
                  {selectedIncident.status !== 'RESOLVED' && (
                    <button
                      onClick={() => handleStatusChange('RESOLVED')}
                      disabled={updating}
                      className="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-mono text-xs font-semibold"
                    >
                      Resolve Incident
                    </button>
                  )}
                </div>
              </div>

              {/* Description & Root Cause */}
              <div className="space-y-3 font-mono text-xs">
                <div>
                  <span className="text-gray-400 font-semibold uppercase text-[10px] block mb-1">Description</span>
                  <p className="text-gray-200 font-sans text-xs bg-gray-900/60 p-3 rounded-xl border border-gray-800">
                    {selectedIncident.description}
                  </p>
                </div>

                {selectedIncident.root_cause && (
                  <div>
                    <span className="text-amber-400 font-semibold uppercase text-[10px] block mb-1">
                      Identified Root Cause
                    </span>
                    <p className="text-gray-200 font-sans text-xs bg-amber-950/20 p-3 rounded-xl border border-amber-800/30">
                      {selectedIncident.root_cause}
                    </p>
                  </div>
                )}
              </div>

              {/* Chronological Timeline Viewer */}
              <div>
                <h4 className="text-xs font-mono uppercase tracking-wider text-sky-400 font-semibold mb-3 flex items-center gap-2">
                  <Clock className="w-4 h-4" />
                  Chronological Incident Timeline & Audit Trail
                </h4>

                <div className="space-y-3 relative before:absolute before:inset-0 before:left-3 before:w-0.5 before:bg-gray-800">
                  {selectedIncident.timeline?.map((event, idx) => (
                    <div key={idx} className="relative flex items-start gap-4 pl-8 font-mono text-xs">
                      <div className="absolute left-1.5 top-1.5 w-3.5 h-3.5 rounded-full bg-sky-500 border-4 border-[#0b0f19]" />
                      <div className="flex-1 p-3 rounded-xl bg-gray-900/60 border border-gray-800">
                        <div className="flex items-center justify-between gap-2 text-[10px] text-gray-500 mb-1">
                          <span className="text-sky-400 font-semibold">{event.event}</span>
                          <span>{new Date(event.timestamp).toLocaleString()}</span>
                        </div>
                        <div className="text-gray-300 font-sans text-xs">{event.details || event.event}</div>
                        <div className="text-[10px] text-gray-500 mt-1">Actor: {event.actor}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </>
          ) : (
            <div className="py-24 text-center text-gray-500 font-mono text-xs">
              Select an incident from the left panel to inspect details and history.
            </div>
          )}
        </div>
      </div>

      {/* Create Incident Modal */}
      <Modal isOpen={isCreateOpen} onClose={() => setIsCreateOpen(false)} title="Log Pipeline Data Incident">
        <form onSubmit={handleCreateIncident} className="space-y-4 font-mono text-xs">
          <div>
            <label className="block text-gray-400 uppercase mb-1 font-semibold">Affected Dataset</label>
            <select
              value={newDatasetId || ''}
              onChange={(e) => setNewDatasetId(parseInt(e.target.value))}
              className="w-full px-3.5 py-2.5 bg-gray-900 border border-gray-800 rounded-lg text-white"
            >
              {datasets.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.name} ({d.row_count} rows)
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-gray-400 uppercase mb-1 font-semibold">Incident Title</label>
            <input
              type="text"
              required
              value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
              placeholder="e.g. 100x Scale Currency Error on Foreign Accounts"
              className="w-full px-3.5 py-2.5 bg-gray-900 border border-gray-800 rounded-lg text-white"
            />
          </div>

          <div>
            <label className="block text-gray-400 uppercase mb-1 font-semibold">Severity</label>
            <select
              value={newSeverity}
              onChange={(e) => setNewSeverity(e.target.value)}
              className="w-full px-3.5 py-2.5 bg-gray-900 border border-gray-800 rounded-lg text-white font-bold"
            >
              <option value="CRITICAL">CRITICAL (Data Pipeline Down / Severe Contamination)</option>
              <option value="HIGH">HIGH (Major Distribution Drift or Missing Keys)</option>
              <option value="MEDIUM">MEDIUM (Moderate Outlier Rates)</option>
              <option value="LOW">LOW (Informational / Schema Additions)</option>
            </select>
          </div>

          <div>
            <label className="block text-gray-400 uppercase mb-1 font-semibold">Description</label>
            <textarea
              rows={3}
              required
              value={newDesc}
              onChange={(e) => setNewDesc(e.target.value)}
              placeholder="Describe anomaly symptoms, impacted partitions, and upstream services..."
              className="w-full px-3.5 py-2.5 bg-gray-900 border border-gray-800 rounded-lg text-white font-sans text-xs"
            />
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={() => setIsCreateOpen(false)}
              className="px-4 py-2 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-300 font-semibold"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={creating}
              className="px-4 py-2 rounded-lg bg-rose-600 hover:bg-rose-500 text-white font-semibold flex items-center gap-2"
            >
              {creating ? 'Logging Incident...' : 'Create Incident'}
            </button>
          </div>
        </form>
      </Modal>
    </Layout>
  );
};

