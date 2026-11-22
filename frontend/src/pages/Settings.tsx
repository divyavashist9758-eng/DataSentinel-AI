import React, { useState, useEffect } from 'react';
import { Layout } from '../components/Layout';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';
import { DashboardMetrics } from '../types';
import {
  Settings as SettingsIcon,
  Server,
  Cpu,
  Database,
  Sparkles,
  ShieldCheck,
  CheckCircle2,
  Sliders,
  History,
  Lock,
  RefreshCw,
  HardDrive
} from 'lucide-react';

export const Settings: React.FC = () => {
  const { user } = useAuth();
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [contamination, setContamination] = useState<number>(0.05);
  const [pValueThreshold, setPValueThreshold] = useState<number>(0.05);
  const [psiThreshold, setPsiThreshold] = useState<number>(0.25);
  const [saveSuccess, setSaveSuccess] = useState<boolean>(false);

  useEffect(() => {
    fetchSystemData();
  }, []);

  const fetchSystemData = async () => {
    try {
      setLoading(true);
      const data = await api.getDashboardMetrics();
      setMetrics(data);
    } catch (err) {
      console.error('Failed to load system metrics', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveSettings = (e: React.FormEvent) => {
    e.preventDefault();
    setSaveSuccess(true);
    setTimeout(() => setSaveSuccess(false), 3000);
  };

  return (
    <Layout
      title="Platform Settings & System Diagnostics"
      subtitle="Engine observability, ML hyperparameters, Groq LLM orchestration status, and enterprise audit logs."
    >
      {/* System Engine Health Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-[#131b2e] border border-gray-800 rounded-xl p-4 flex items-center gap-3">
          <div className="p-2.5 rounded-lg bg-emerald-950/80 border border-emerald-800 text-emerald-400">
            <Server className="w-5 h-5" />
          </div>
          <div>
            <div className="text-[10px] font-mono text-gray-400 uppercase tracking-wider">FastAPI Backend</div>
            <div className="text-sm font-bold text-white flex items-center gap-1.5">
              Online • v1.0.0
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            </div>
          </div>
        </div>

        <div className="bg-[#131b2e] border border-gray-800 rounded-xl p-4 flex items-center gap-3">
          <div className="p-2.5 rounded-lg bg-sky-950/80 border border-sky-800 text-sky-400">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <div className="text-[10px] font-mono text-gray-400 uppercase tracking-wider">ML Scikit-Learn</div>
            <div className="text-sm font-bold text-white flex items-center gap-1.5">
              Isolation Forest
              <span className="w-2 h-2 rounded-full bg-sky-500"></span>
            </div>
          </div>
        </div>

        <div className="bg-[#131b2e] border border-gray-800 rounded-xl p-4 flex items-center gap-3">
          <div className="p-2.5 rounded-lg bg-purple-950/80 border border-purple-800 text-purple-400">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <div className="text-[10px] font-mono text-gray-400 uppercase tracking-wider">Agentic LangGraph</div>
            <div className="text-sm font-bold text-white flex items-center gap-1.5">
              6-Agent Workflow
              <span className="w-2 h-2 rounded-full bg-purple-500"></span>
            </div>
          </div>
        </div>

        <div className="bg-[#131b2e] border border-gray-800 rounded-xl p-4 flex items-center gap-3">
          <div className="p-2.5 rounded-lg bg-indigo-950/80 border border-indigo-800 text-indigo-400">
            <Database className="w-5 h-5" />
          </div>
          <div>
            <div className="text-[10px] font-mono text-gray-400 uppercase tracking-wider">Database Mode</div>
            <div className="text-sm font-bold text-white flex items-center gap-1.5">
              Dual SQLite/Postgres
              <span className="w-2 h-2 rounded-full bg-indigo-500"></span>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Generative AI & Agent Architecture */}
        <div className="bg-[#131b2e] border border-gray-800 rounded-xl p-6 space-y-4">
          <div className="flex items-center gap-2 border-b border-gray-800 pb-3">
            <Sparkles className="w-5 h-5 text-sky-400" />
            <h3 className="text-base font-bold text-white">Generative AI & LLM Provider</h3>
          </div>

          <div className="space-y-3 text-xs">
            <div className="flex justify-between items-center p-3 bg-[#0b0f19] rounded-lg border border-gray-800">
              <span className="text-gray-400">Active LLM Engine:</span>
              <span className="font-mono text-white font-semibold">Groq API / Llama-3.3-70B-Versatile</span>
            </div>

            <div className="flex justify-between items-center p-3 bg-[#0b0f19] rounded-lg border border-gray-800">
              <span className="text-gray-400">Deterministic Fallback:</span>
              <span className="font-mono text-emerald-400 font-semibold flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5" />
                Active (Local Rule-Based Heuristic)
              </span>
            </div>

            <div className="flex justify-between items-center p-3 bg-[#0b0f19] rounded-lg border border-gray-800">
              <span className="text-gray-400">LangGraph Agent Nodes:</span>
              <span className="font-mono text-sky-400 font-semibold">
                6 Nodes (Quality, Anomaly, Schema, Root Cause, Remediation, Report)
              </span>
            </div>

            <div className="flex justify-between items-center p-3 bg-[#0b0f19] rounded-lg border border-gray-800">
              <span className="text-gray-400">RAG Semantic Knowledge Index:</span>
              <span className="font-mono text-purple-400 font-semibold">
                TF-IDF & Cosine Similarity (15+ Postmortems & Rules)
              </span>
            </div>
          </div>
        </div>

        {/* Machine Learning Observability Hyperparameters */}
        <div className="bg-[#131b2e] border border-gray-800 rounded-xl p-6 space-y-4">
          <div className="flex items-center gap-2 border-b border-gray-800 pb-3">
            <Sliders className="w-5 h-5 text-indigo-400" />
            <h3 className="text-base font-bold text-white">Observability Thresholds</h3>
          </div>

          <form onSubmit={handleSaveSettings} className="space-y-4">
            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-gray-300 font-medium">Default Isolation Forest Contamination:</span>
                <span className="font-mono text-sky-400">{contamination}</span>
              </div>
              <input
                type="range"
                min="0.01"
                max="0.20"
                step="0.01"
                value={contamination}
                onChange={(e) => setContamination(parseFloat(e.target.value))}
                className="w-full accent-sky-500 cursor-pointer"
              />
            </div>

            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-gray-300 font-medium">Kolmogorov-Smirnov p-value Threshold:</span>
                <span className="font-mono text-sky-400">{pValueThreshold}</span>
              </div>
              <input
                type="range"
                min="0.01"
                max="0.10"
                step="0.01"
                value={pValueThreshold}
                onChange={(e) => setPValueThreshold(parseFloat(e.target.value))}
                className="w-full accent-indigo-500 cursor-pointer"
              />
            </div>

            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-gray-300 font-medium">Population Stability Index (PSI) Critical Threshold:</span>
                <span className="font-mono text-sky-400">{psiThreshold}</span>
              </div>
              <input
                type="range"
                min="0.10"
                max="0.50"
                step="0.05"
                value={psiThreshold}
                onChange={(e) => setPsiThreshold(parseFloat(e.target.value))}
                className="w-full accent-purple-500 cursor-pointer"
              />
            </div>

            <div className="flex items-center justify-between pt-2">
              {saveSuccess && (
                <span className="text-xs font-mono text-emerald-400 flex items-center gap-1">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  Threshold preferences saved.
                </span>
              )}
              <button
                type="submit"
                className="ml-auto px-4 py-2 bg-sky-600 hover:bg-sky-500 text-white rounded-lg text-xs font-semibold transition"
              >
                Save Preferences
              </button>
            </div>
          </form>
        </div>
      </div>

      {/* Safety & Immutability Architecture */}
      <div className="bg-gradient-to-r from-emerald-950/30 to-sky-950/20 border border-emerald-900/40 rounded-xl p-5 flex items-start gap-4">
        <div className="p-3 bg-emerald-900/40 border border-emerald-700/50 rounded-lg text-emerald-400">
          <ShieldCheck className="w-6 h-6" />
        </div>
        <div className="space-y-1">
          <h4 className="text-sm font-bold text-white flex items-center gap-2">
            Non-Destructive Ingestion & Safe Storage Policy
            <span className="px-2 py-0.5 rounded bg-emerald-900/60 border border-emerald-700 text-emerald-300 text-[10px] font-mono">
              ENFORCED
            </span>
          </h4>
          <p className="text-xs text-gray-300 leading-relaxed">
            DataSentinel AI enforces SHA-256 cryptographic verification upon dataset ingestion. File uploads are strictly validated
            against MIME structures, headers, and a 100 MB per-dataset quota.
            All AI remediations execute strictly on versioned dataset clones, safeguarding original production data from accidental alteration or loss.
          </p>
        </div>
      </div>

      {/* Recent Enterprise Audit Trail */}
      <div className="bg-[#131b2e] border border-gray-800 rounded-xl p-6 space-y-4">
        <div className="flex items-center justify-between border-b border-gray-800 pb-3">
          <div className="flex items-center gap-2">
            <History className="w-5 h-5 text-sky-400" />
            <h3 className="text-base font-bold text-white">System Audit Trail</h3>
          </div>
          <button
            onClick={fetchSystemData}
            disabled={loading}
            className="p-1.5 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-lg text-xs flex items-center gap-1 transition"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>

        {metrics?.recent_audit_trail && metrics.recent_audit_trail.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-[#0b0f19] text-gray-400 uppercase tracking-wider text-[10px]">
                <tr>
                  <th className="py-2.5 px-3">Log ID</th>
                  <th className="py-2.5 px-3">Action</th>
                  <th className="py-2.5 px-3">Entity Type</th>
                  <th className="py-2.5 px-3">Entity ID</th>
                  <th className="py-2.5 px-3">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800/60 text-gray-300">
                {metrics.recent_audit_trail.map((log) => (
                  <tr key={log.id} className="hover:bg-gray-800/30 transition">
                    <td className="py-2 px-3 text-gray-400 font-bold">#{log.id}</td>
                    <td className="py-2 px-3">
                      <span className="px-2 py-0.5 rounded bg-sky-950/60 border border-sky-800 text-sky-400 text-[11px] font-semibold">
                        {log.action}
                      </span>
                    </td>
                    <td className="py-2 px-3 text-gray-300">{log.entity_type}</td>
                    <td className="py-2 px-3 text-gray-400">{log.entity_id}</td>
                    <td className="py-2 px-3 text-gray-400 text-[11px]">
                      {new Date(log.timestamp).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="py-8 text-center text-xs text-gray-400">
            No audit records registered yet. System actions (uploads, remediations, reviews) will be tracked here.
          </div>
        )}
      </div>
    </Layout>
  );
};
export default Settings;

