import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Layout } from '../components/Layout';
import { Modal } from '../components/Modal';
import { api } from '../services/api';
import { Dataset } from '../types';
import {
  Database,
  Search,
  UploadCloud,
  Eye,
  Trash2,
  Activity,
  Cpu,
  Sparkles,
  Layers,
  FileSpreadsheet,
  FileCode,
  FileText,
  Clock,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';

export const Datasets: React.FC = () => {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedDataset, setSelectedDataset] = useState<any | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState<number | null>(null);

  const fetchDatasets = async () => {
    try {
      setLoading(true);
      const data = await api.getDatasets();
      setDatasets(data);
    } catch (err) {
      console.error('Error fetching datasets:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDatasets();
  }, []);

  const handleInspect = async (id: number) => {
    try {
      setPreviewLoading(true);
      const detail = await api.getDataset(id);
      setSelectedDataset(detail);
    } catch (err) {
      console.error('Error loading dataset detail:', err);
    } finally {
      setPreviewLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await api.deleteDataset(id);
      setDeleteConfirm(null);
      fetchDatasets();
    } catch (err) {
      console.error('Error deleting dataset:', err);
    }
  };

  const filtered = datasets.filter(
    (d) =>
      d.name.toLowerCase().includes(search.toLowerCase()) ||
      d.original_filename.toLowerCase().includes(search.toLowerCase())
  );

  const getFormatIcon = (type: string) => {
    if (type === 'excel') return <FileSpreadsheet className="w-4 h-4 text-emerald-400" />;
    if (type === 'json') return <FileCode className="w-4 h-4 text-amber-400" />;
    return <FileText className="w-4 h-4 text-sky-400" />;
  };

  return (
    <Layout title="Dataset Inventory & Version Registry" subtitle="Manage Storage Ingestion, Historical Versions, and Schema Contracts">
      {/* Top Action Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pb-2">
        <div className="relative w-full sm:w-80">
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search datasets or files..."
            className="w-full pl-9 pr-3.5 py-2 bg-gray-900 border border-gray-800 rounded-lg text-xs text-white placeholder-gray-500 focus:outline-none focus:border-sky-500 font-mono"
          />
          <Search className="w-4 h-4 text-gray-500 absolute left-3 top-2.5" />
        </div>

        <Link
          to="/upload"
          className="w-full sm:w-auto flex items-center justify-center gap-2 px-4 py-2 bg-sky-600 hover:bg-sky-500 text-white rounded-lg text-xs font-semibold transition-colors shadow-lg shadow-sky-600/20"
        >
          <UploadCloud className="w-4 h-4" />
          <span>Ingest New Dataset</span>
        </Link>
      </div>

      {/* Datasets Table */}
      <div className="glass-card rounded-2xl border border-gray-800 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead>
              <tr className="border-b border-gray-800 bg-gray-900/50 text-gray-400">
                <th className="py-3 px-4">Dataset Name & File</th>
                <th className="py-3 px-4">Type</th>
                <th className="py-3 px-4">Dimensions</th>
                <th className="py-3 px-4">File Size</th>
                <th className="py-3 px-4">Quality Score</th>
                <th className="py-3 px-4">Versions</th>
                <th className="py-3 px-4">Ingested</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800/60">
              {loading ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-gray-500">
                    <div className="inline-block w-6 h-6 border-2 border-sky-500 border-t-transparent rounded-full animate-spin mb-2" />
                    <p>Loading dataset inventory...</p>
                  </td>
                </tr>
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-gray-500">
                    <Database className="w-10 h-10 text-gray-700 mx-auto mb-3" />
                    <p className="text-sm font-semibold text-gray-400">No datasets found</p>
                    <p className="text-xs text-gray-600 mt-1">Upload a CSV, Excel or JSON file to begin.</p>
                  </td>
                </tr>
              ) : (
                filtered.map((d) => (
                  <tr key={d.id} className="hover:bg-gray-800/30 transition-colors">
                    <td className="py-3.5 px-4">
                      <div className="font-semibold text-white font-sans text-sm">{d.name}</div>
                      <div className="text-[11px] text-gray-500 font-mono">{d.original_filename}</div>
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="flex items-center gap-1.5 uppercase font-semibold text-gray-300">
                        {getFormatIcon(d.file_type)}
                        {d.file_type}
                      </span>
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="text-sky-400 font-bold">{d.row_count.toLocaleString()}</span> rows ×{' '}
                      <span className="text-gray-300">{d.column_count}</span> cols
                    </td>
                    <td className="py-3.5 px-4 text-gray-400">
                      {(d.file_size_bytes / 1024).toFixed(1)} KB
                    </td>
                    <td className="py-3.5 px-4">
                      {d.latest_quality_score != null ? (
                        <span
                          className={`px-2 py-0.5 rounded font-bold ${
                            d.latest_quality_score >= 85
                              ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                              : d.latest_quality_score >= 70
                              ? 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
                              : 'bg-rose-500/10 text-rose-400 border border-rose-500/30'
                          }`}
                        >
                          {d.latest_quality_score}/100
                        </span>
                      ) : (
                        <span className="text-gray-500">Unscored</span>
                      )}
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="flex items-center gap-1 text-gray-300">
                        <Layers className="w-3.5 h-3.5 text-indigo-400" />
                        v{d.versions_count || 1}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-gray-400 text-[11px]">
                      {new Date(d.created_at).toLocaleDateString()}
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <div className="flex items-center justify-end gap-1.5">
                        <button
                          onClick={() => handleInspect(d.id)}
                          title="Inspect Data & Schema"
                          className="p-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-300 hover:text-white transition-colors"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                        <Link
                          to={`/profiling?dataset_id=${d.id}`}
                          title="Quality Profile"
                          className="p-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 text-emerald-400 hover:text-emerald-300 transition-colors"
                        >
                          <Activity className="w-4 h-4" />
                        </Link>
                        <Link
                          to={`/anomalies?dataset_id=${d.id}`}
                          title="ML Anomaly Explorer"
                          className="p-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 text-amber-400 hover:text-amber-300 transition-colors"
                        >
                          <Cpu className="w-4 h-4" />
                        </Link>
                        <Link
                          to={`/investigations?dataset_id=${d.id}`}
                          title="Launch AI Agent Investigation"
                          className="p-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 text-sky-400 hover:text-sky-300 transition-colors"
                        >
                          <Sparkles className="w-4 h-4" />
                        </Link>
                        <button
                          onClick={() => setDeleteConfirm(d.id)}
                          title="Delete Dataset"
                          className="p-1.5 rounded-lg bg-gray-800 hover:bg-rose-500/20 text-gray-500 hover:text-rose-400 transition-colors"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Dataset Inspection Modal */}
      <Modal
        isOpen={!!selectedDataset}
        onClose={() => setSelectedDataset(null)}
        title={`Dataset Inspection: ${selectedDataset?.name || ''}`}
        maxWidth="max-w-4xl"
      >
        {selectedDataset && (
          <div className="space-y-6">
            {/* Metadata Summary */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 font-mono text-xs">
              <div className="p-3 rounded-lg bg-gray-900 border border-gray-800">
                <span className="text-gray-500 block">Total Rows</span>
                <span className="text-base font-bold text-white">{selectedDataset.row_count.toLocaleString()}</span>
              </div>
              <div className="p-3 rounded-lg bg-gray-900 border border-gray-800">
                <span className="text-gray-500 block">Total Columns</span>
                <span className="text-base font-bold text-white">{selectedDataset.column_count}</span>
              </div>
              <div className="p-3 rounded-lg bg-gray-900 border border-gray-800">
                <span className="text-gray-500 block">Quality Score</span>
                <span className="text-base font-bold text-emerald-400">
                  {selectedDataset.latest_quality_score ?? 'N/A'}/100
                </span>
              </div>
              <div className="p-3 rounded-lg bg-gray-900 border border-gray-800">
                <span className="text-gray-500 block">SHA-256 Hash</span>
                <span className="text-[10px] text-gray-300 truncate block">{selectedDataset.sha256_hash.slice(0, 16)}...</span>
              </div>
            </div>

            {/* Versions History */}
            <div>
              <h4 className="text-xs font-mono text-gray-400 uppercase tracking-wider mb-2 font-semibold">
                Version History ({selectedDataset.versions?.length || 0})
              </h4>
              <div className="space-y-1.5 font-mono text-xs">
                {selectedDataset.versions?.map((v: any) => (
                  <div key={v.id} className="p-2.5 rounded-lg bg-gray-900/60 border border-gray-800 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="px-1.5 py-0.5 rounded bg-sky-950 text-sky-400 border border-sky-800 font-bold">
                        v{v.version_num}
                      </span>
                      <span className="text-gray-300">{v.change_summary || 'Initial version'}</span>
                      {v.is_remediated && (
                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                          Remediated Copy
                        </span>
                      )}
                    </div>
                    <span className="text-gray-500 text-[11px]">{new Date(v.created_at).toLocaleString()}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Sample Records Preview */}
            <div>
              <h4 className="text-xs font-mono text-gray-400 uppercase tracking-wider mb-2 font-semibold">
                Sample Record Preview (First 10 Rows)
              </h4>
              {selectedDataset.sample_rows && selectedDataset.sample_rows.length > 0 ? (
                <div className="overflow-x-auto border border-gray-800 rounded-lg">
                  <table className="w-full text-left text-[11px] font-mono">
                    <thead className="bg-gray-900 border-b border-gray-800 text-gray-400">
                      <tr>
                        {Object.keys(selectedDataset.sample_rows[0]).map((col) => (
                          <th key={col} className="p-2 border-r border-gray-800 last:border-none">
                            {col}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-800/60">
                      {selectedDataset.sample_rows.map((row: any, i: number) => (
                        <tr key={i} className="hover:bg-gray-800/40">
                          {Object.values(row).map((val: any, j: number) => (
                            <td key={j} className="p-2 border-r border-gray-800/60 last:border-none text-gray-300 truncate max-w-xs">
                              {val === null || val === '' ? <span className="text-rose-400 italic">null</span> : String(val)}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p className="text-xs text-gray-500 font-mono">No sample records preview available.</p>
              )}
            </div>
          </div>
        )}
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={deleteConfirm !== null}
        onClose={() => setDeleteConfirm(null)}
        title="Confirm Dataset Deletion"
        maxWidth="max-w-md"
      >
        <div className="space-y-4">
          <p className="text-xs text-gray-300">
            Are you sure you want to deactivate and remove this dataset? This will hide the dataset from the active inventory.
          </p>
          <div className="flex justify-end gap-3 pt-2">
            <button
              onClick={() => setDeleteConfirm(null)}
              className="px-3.5 py-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 text-xs font-medium text-gray-300"
            >
              Cancel
            </button>
            <button
              onClick={() => deleteConfirm && handleDelete(deleteConfirm)}
              className="px-3.5 py-1.5 rounded-lg bg-rose-600 hover:bg-rose-500 text-xs font-medium text-white"
            >
              Confirm Delete
            </button>
          </div>
        </div>
      </Modal>
    </Layout>
  );
};

