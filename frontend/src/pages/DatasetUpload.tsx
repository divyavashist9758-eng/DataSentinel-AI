import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Layout } from '../components/Layout';
import { api } from '../services/api';
import { extractErrorMessage } from '../utils/error';
import {
  UploadCloud,
  FileSpreadsheet,
  FileCode,
  FileText,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  Database,
  Sparkles
} from 'lucide-react';

export const DatasetUpload: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [datasetName, setDatasetName] = useState('');
  const [description, setDescription] = useState('');
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState<any | null>(null);

  const navigate = useNavigate();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0];
      setFile(selected);
      if (!datasetName) {
        setDatasetName(selected.name.replace(/\.[^/.]+$/, ''));
      }
      setError('');
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const selected = e.dataTransfer.files[0];
      setFile(selected);
      if (!datasetName) {
        setDatasetName(selected.name.replace(/\.[^/.]+$/, ''));
      }
      setError('');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a dataset file to upload.');
      return;
    }

    setUploading(true);
    setError('');

    const formData = new FormData();
    formData.append('file', file);
    formData.append('name', datasetName || file.name);
    formData.append('description', description);

    try {
      const res = await api.uploadDataset(formData);
      setSuccess(res);
      setTimeout(() => {
        navigate(`/profiling?dataset_id=${res.id}`);
      }, 1500);
    } catch (err: any) {
      setError(extractErrorMessage(err, 'Failed to ingest dataset. Ensure format is valid CSV, Excel, or JSON.'));
    } finally {
      setUploading(false);
    }
  };

  return (
    <Layout title="Dataset Ingestion & Validation Gateway" subtitle="Secure Raw Storage, MIME Validation, Cryptographic Integrity Hashing">
      <div className="max-w-3xl mx-auto space-y-6">
        <div className="glass-card rounded-2xl p-8 border border-gray-800 shadow-2xl">
          <h2 className="text-lg font-semibold text-white mb-1">Ingest Dataset</h2>
          <p className="text-xs text-gray-400 mb-6">
            Supported formats: CSV, Excel (.xlsx, .xls), JSON. Uploads are strictly immutable and never modified in-place.
          </p>

          {error && (
            <div className="mb-6 p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-xs text-rose-400 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {success && (
            <div className="mb-6 p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-xs text-emerald-400 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 shrink-0" />
                <span>Dataset '{success.name}' ingested successfully! Initial Quality Score: {success.latest_quality_score}/100</span>
              </div>
              <span className="font-mono text-[10px]">Redirecting to Profiler...</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Drag and Drop Zone */}
            <div
              onDragOver={(e) => e.preventDefault()}
              onDrop={handleDrop}
              className={`border-2 border-dashed rounded-xl p-8 text-center transition-all cursor-pointer ${
                file
                  ? 'border-sky-500/50 bg-sky-500/5'
                  : 'border-gray-700 hover:border-gray-600 bg-gray-900/40'
              }`}
            >
              <input
                type="file"
                id="file-upload"
                onChange={handleFileChange}
                accept=".csv,.xlsx,.xls,.json"
                className="hidden"
              />
              <label htmlFor="file-upload" className="cursor-pointer block">
                <div className="w-12 h-12 rounded-xl bg-sky-500/10 border border-sky-500/20 text-sky-400 flex items-center justify-center mx-auto mb-3">
                  <UploadCloud className="w-6 h-6" />
                </div>
                {file ? (
                  <div>
                    <p className="text-sm font-semibold text-white font-mono">{file.name}</p>
                    <p className="text-xs text-gray-400 mt-1 font-mono">
                      {(file.size / 1024).toFixed(1)} KB &bull; Ready for validation
                    </p>
                  </div>
                ) : (
                  <div>
                    <p className="text-sm font-medium text-gray-200">
                      Drag & drop your dataset here, or <span className="text-sky-400 underline">browse</span>
                    </p>
                    <p className="text-xs text-gray-500 mt-1 font-mono">CSV, Excel (.xlsx, .xls), or JSON up to 100MB</p>
                  </div>
                )}
              </label>
            </div>

            {/* Form Fields */}
            <div className="grid grid-cols-1 gap-4 font-mono text-xs">
              <div>
                <label className="block text-gray-400 uppercase mb-1.5 font-semibold">Dataset Identifier / Name</label>
                <input
                  type="text"
                  required
                  value={datasetName}
                  onChange={(e) => setDatasetName(e.target.value)}
                  placeholder="e.g. Q4 Financial Transactions"
                  className="w-full px-3.5 py-2.5 bg-gray-900 border border-gray-800 rounded-lg text-sm text-white placeholder-gray-600 focus:outline-none focus:border-sky-500"
                />
              </div>

              <div>
                <label className="block text-gray-400 uppercase mb-1.5 font-semibold">Description & Context</label>
                <textarea
                  rows={3}
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Describe pipeline source, business entity, upstream schema context..."
                  className="w-full px-3.5 py-2.5 bg-gray-900 border border-gray-800 rounded-lg text-sm text-white placeholder-gray-600 focus:outline-none focus:border-sky-500 font-sans"
                />
              </div>
            </div>

            {/* Ingest Button */}
            <button
              type="submit"
              disabled={uploading || !file}
              className="w-full py-3 bg-sky-600 hover:bg-sky-500 text-white rounded-lg text-xs font-mono font-bold tracking-wider uppercase flex items-center justify-center gap-2 transition-all shadow-lg shadow-sky-600/20 disabled:opacity-50"
            >
              {uploading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin" />
                  <span>Validating & Profiling Telemetry...</span>
                </>
              ) : (
                <>
                  <span>Ingest & Run Automated Profiler</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>
        </div>

        {/* Informational Architecture Card */}
        <div className="glass-card rounded-2xl p-6 border border-gray-800 space-y-3 text-xs text-gray-400">
          <div className="flex items-center gap-2 text-white font-semibold">
            <Sparkles className="w-4 h-4 text-sky-400" />
            <span>Autonomous Ingestion Pipeline Guarantees</span>
          </div>
          <ul className="list-disc list-inside space-y-1 font-mono text-[11px] text-gray-400">
            <li>Zero in-place mutation: Raw datasets are saved with SHA-256 cryptographic digests.</li>
            <li>Automatic type inference: Numerics, categorical strings, booleans, and datetime formats.</li>
            <li>Instant 100-point Data Quality Score calculation upon receipt.</li>
            <li>Prepared for LangGraph multi-agent investigation and historical drift benchmarking.</li>
          </ul>
        </div>
      </div>
    </Layout>
  );
};

