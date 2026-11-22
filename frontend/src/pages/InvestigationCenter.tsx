import React, { useEffect, useState } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { Layout } from '../components/Layout';
import { StatusBadge } from '../components/StatusBadge';
import { api } from '../services/api';
import { Dataset, Investigation, AgentTrace } from '../types';
import {
  Sparkles,
  Bot,
  Activity,
  Cpu,
  Layers,
  Search,
  CheckCircle2,
  AlertTriangle,
  Play,
  Clock,
  ExternalLink,
  ChevronRight,
  ShieldCheck,
  FileText,
  Bookmark
} from 'lucide-react';

export const InvestigationCenter: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const dsParam = searchParams.get('dataset_id');

  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [selectedDatasetId, setSelectedDatasetId] = useState<number | null>(
    dsParam ? parseInt(dsParam) : null
  );

  const [investigations, setInvestigations] = useState<Investigation[]>([]);
  const [activeInvestigation, setActiveInvestigation] = useState<Investigation | null>(null);
  const [selectedTrace, setSelectedTrace] = useState<AgentTrace | null>(null);

  const [running, setRunning] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);

  // Load datasets
  useEffect(() => {
    const loadDatasets = async () => {
      try {
        const list = await api.getDatasets();
        setDatasets(list);
        if (!selectedDatasetId && list.length > 0) {
          setSelectedDatasetId(list[0].id);
        }
      } catch (err) {
        console.error('Failed to load datasets:', err);
      }
    };
    loadDatasets();
  }, []);

  // Load investigations for selected dataset
  useEffect(() => {
    if (!selectedDatasetId) return;

    const fetchInvestigations = async () => {
      try {
        setLoading(true);
        const list = await api.getDatasetInvestigations(selectedDatasetId);
        setInvestigations(list);
        if (list.length > 0) {
          setActiveInvestigation(list[0]);
          if (list[0].agent_traces && list[0].agent_traces.length > 0) {
            setSelectedTrace(list[0].agent_traces[0]);
          }
        } else {
          setActiveInvestigation(null);
          setSelectedTrace(null);
        }
      } catch (err) {
        console.error('Error fetching investigations:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchInvestigations();
  }, [selectedDatasetId]);

  const handleStartInvestigation = async () => {
    if (!selectedDatasetId) return;

    try {
      setRunning(true);
      const res = await api.startInvestigation(selectedDatasetId, {
        focus_areas: ['quality', 'anomalies', 'schema', 'drift'],
      });
      setActiveInvestigation(res);
      if (res.agent_traces && res.agent_traces.length > 0) {
        setSelectedTrace(res.agent_traces[0]);
      }
      // Refresh list
      const list = await api.getDatasetInvestigations(selectedDatasetId);
      setInvestigations(list);
    } catch (err) {
      console.error('Investigation workflow execution failed:', err);
    } finally {
      setRunning(false);
    }
  };

  const getAgentIcon = (name: string) => {
    if (name.includes('Quality')) return <Activity className="w-4 h-4 text-emerald-400" />;
    if (name.includes('Anomaly')) return <Cpu className="w-4 h-4 text-amber-400" />;
    if (name.includes('Schema')) return <Layers className="w-4 h-4 text-indigo-400" />;
    if (name.includes('Root Cause')) return <Search className="w-4 h-4 text-purple-400" />;
    if (name.includes('Remediation')) return <ShieldCheck className="w-4 h-4 text-sky-400" />;
    return <FileText className="w-4 h-4 text-blue-400" />;
  };

  return (
    <Layout
      title="Autonomous AI Investigation Command Center"
      subtitle="LangGraph Stateful Multi-Agent Investigation Workflow & RAG Domain Knowledge Precedents"
    >
      {/* Top Controls Bar */}
      <div className="glass-card rounded-2xl p-6 border border-gray-800 space-y-4">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div>
            <h2 className="text-base font-semibold text-white flex items-center gap-2">
              <Bot className="w-5 h-5 text-sky-400" />
              LangGraph Multi-Agent Orchestrator
            </h2>
            <p className="text-xs text-gray-400 font-mono">
              Sequentially executes 6 specialized agents with state sharing, RAG indexing, and causal synthesis
            </p>
          </div>

          <div className="flex items-center gap-3">
            <select
              value={selectedDatasetId || ''}
              onChange={(e) => {
                const id = parseInt(e.target.value);
                setSelectedDatasetId(id);
                setSearchParams({ dataset_id: String(id) });
              }}
              className="px-3.5 py-2 bg-gray-900 border border-gray-800 rounded-lg text-xs font-mono text-white focus:outline-none focus:border-sky-500"
            >
              {datasets.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.name} ({d.row_count} rows)
                </option>
              ))}
            </select>

            <button
              onClick={handleStartInvestigation}
              disabled={running || !selectedDatasetId}
              className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-sky-600 to-indigo-600 hover:from-sky-500 hover:to-indigo-500 text-white rounded-lg text-xs font-mono font-bold uppercase transition-all shadow-lg shadow-sky-600/25 disabled:opacity-50"
            >
              {running ? (
                <>
                  <div className="w-3.5 h-3.5 border-2 border-white/20 border-t-white rounded-full animate-spin" />
                  <span>Agents Investigating...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>Deploy Multi-Agent Workflow</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="py-24 text-center text-gray-500">
          <div className="inline-block w-8 h-8 border-2 border-sky-500 border-t-transparent rounded-full animate-spin mb-3" />
          <p className="font-mono text-xs">Loading agent execution records...</p>
        </div>
      ) : !activeInvestigation ? (
        <div className="glass-card rounded-2xl p-12 text-center border border-gray-800 space-y-4">
          <Bot className="w-12 h-12 text-sky-400 mx-auto" />
          <div>
            <h3 className="text-base font-semibold text-white">No Investigations Run for this Dataset</h3>
            <p className="text-xs text-gray-400 mt-1 max-w-md mx-auto">
              Deploy our autonomous LangGraph agents to continuously inspect data quality degradation, detect
              unsupervised Isolation Forest anomalies, compare schemas, and retrieve historical incident playbooks.
            </p>
          </div>
          <button
            onClick={handleStartInvestigation}
            className="px-5 py-2.5 bg-sky-600 hover:bg-sky-500 text-white rounded-lg text-xs font-mono font-semibold"
          >
            Deploy Investigation Agents
          </button>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Executive Overview Banner */}
          <div className="glass-card rounded-2xl p-6 border border-gray-800 space-y-4">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-gray-800/80 pb-4">
              <div>
                <span className="text-[10px] font-mono uppercase tracking-wider text-sky-400 font-semibold">
                  Autonomous Investigation Dossier #{activeInvestigation.id}
                </span>
                <h3 className="text-lg font-bold text-white font-sans mt-0.5">{activeInvestigation.title}</h3>
                <p className="text-xs text-gray-400 font-mono mt-0.5">
                  Executed {new Date(activeInvestigation.created_at).toLocaleString()} &bull; State Graph status:{' '}
                  <StatusBadge status={activeInvestigation.status} />
                </p>
              </div>

              <div className="flex items-center gap-4">
                <div className="text-right font-mono">
                  <span className="text-xs text-gray-400 block">Agent Confidence</span>
                  <span className="text-xl font-bold text-emerald-400">{activeInvestigation.confidence_score}%</span>
                </div>
                <div className="flex gap-2">
                  <a
                    href={api.getExportPdfUrl(activeInvestigation.id)}
                    target="_blank"
                    rel="noreferrer"
                    className="px-3 py-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 text-xs font-mono text-gray-200 border border-gray-700 transition-colors"
                  >
                    Export PDF
                  </a>
                  <a
                    href={api.getExportCsvUrl(activeInvestigation.id)}
                    target="_blank"
                    rel="noreferrer"
                    className="px-3 py-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 text-xs font-mono text-gray-200 border border-gray-700 transition-colors"
                  >
                    Export CSV
                  </a>
                </div>
              </div>
            </div>

            {/* Root Cause & Summary Insights */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
              <div className="p-4 rounded-xl bg-gray-900/60 border border-gray-800">
                <span className="text-sky-400 font-semibold uppercase text-[10px] block mb-1">
                  Executive Investigation Summary
                </span>
                <p className="text-gray-300 leading-relaxed font-sans text-xs">
                  {activeInvestigation.summary || 'Investigation completed without anomalous warnings.'}
                </p>
              </div>

              <div className="p-4 rounded-xl bg-gray-900/60 border border-gray-800">
                <span className="text-amber-400 font-semibold uppercase text-[10px] block mb-1">
                  Root Cause Hypothesis (Deduction)
                </span>
                <p className="text-gray-300 leading-relaxed font-sans text-xs">
                  {activeInvestigation.root_cause_hypothesis || 'All metrics within standard tolerance thresholds.'}
                </p>
              </div>
            </div>
          </div>

          {/* LangGraph Agent Pipeline Visualization */}
          <div className="glass-card rounded-2xl p-6 border border-gray-800">
            <h3 className="text-xs font-mono uppercase tracking-wider text-gray-400 font-semibold mb-4">
              LangGraph Specialized Agent Execution Pipeline (6 Nodes)
            </h3>

            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
              {activeInvestigation.agent_traces?.map((trace, idx) => {
                const isSelected = selectedTrace?.agent_name === trace.agent_name;
                return (
                  <button
                    key={trace.agent_name}
                    onClick={() => setSelectedTrace(trace)}
                    className={`p-3.5 rounded-xl border text-left transition-all relative overflow-hidden ${
                      isSelected
                        ? 'bg-sky-500/15 border-sky-400 shadow-lg shadow-sky-500/10'
                        : 'bg-gray-900/50 border-gray-800 hover:border-gray-700'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="p-1.5 rounded-lg bg-gray-800">{getAgentIcon(trace.agent_name)}</div>
                      <span className="text-[10px] font-mono text-gray-500">Node {idx + 1}</span>
                    </div>
                    <div className="font-semibold text-xs text-white truncate font-sans">{trace.agent_name}</div>
                    <div className="flex items-center justify-between mt-2 text-[10px] font-mono text-gray-400">
                      <span className="text-emerald-400 font-bold">{trace.status}</span>
                      <span>{trace.execution_time_ms}ms</span>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Selected Agent Trace Inspector */}
          {selectedTrace && (
            <div className="glass-card rounded-2xl p-6 border border-gray-800 space-y-4">
              <div className="flex items-center justify-between border-b border-gray-800 pb-3">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-xl bg-gray-800">{getAgentIcon(selectedTrace.agent_name)}</div>
                  <div>
                    <h3 className="text-sm font-bold text-white">{selectedTrace.agent_name}</h3>
                    <p className="text-xs text-gray-400 font-mono">{selectedTrace.role_description}</p>
                  </div>
                </div>

                <div className="flex items-center gap-3 font-mono text-xs">
                  <span className="text-gray-400">Latency: {selectedTrace.execution_time_ms}ms</span>
                  <StatusBadge status={selectedTrace.status} />
                </div>
              </div>

              {/* Agent Summary Insight */}
              <div className="p-4 rounded-xl bg-sky-950/20 border border-sky-800/30 text-xs">
                <span className="font-mono text-sky-400 font-semibold block uppercase text-[10px] mb-1">
                  Agent Key Insight
                </span>
                <p className="text-gray-200 font-sans">{selectedTrace.summary_insight}</p>
              </div>

              {/* RAG Knowledge Precedents Matched */}
              {selectedTrace.rag_sources && selectedTrace.rag_sources.length > 0 && (
                <div className="space-y-2">
                  <span className="text-xs font-mono uppercase tracking-wider text-purple-400 font-semibold flex items-center gap-1.5">
                    <Bookmark className="w-3.5 h-3.5" />
                    RAG Knowledge Precedents Retrieved & Cited
                  </span>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {selectedTrace.rag_sources.map((src, i) => (
                      <div key={i} className="p-3.5 rounded-xl bg-gray-900/60 border border-gray-800 text-xs font-mono">
                        <div className="flex items-center justify-between text-purple-300 font-bold mb-1">
                          <span>{src.title}</span>
                          <span className="text-[10px] text-gray-500">Relevance: {Math.round(src.relevance_score * 100)}%</span>
                        </div>
                        <p className="text-gray-400 font-sans text-xs mb-2">{src.content}</p>
                        <div className="text-[10px] text-gray-500 italic">{src.citation}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Structured JSON Findings */}
              <div>
                <span className="text-xs font-mono uppercase tracking-wider text-gray-400 font-semibold block mb-2">
                  Structured Node Findings (Telemetry Snapshot)
                </span>
                <pre className="p-4 rounded-xl bg-gray-950 border border-gray-800/80 text-gray-300 font-mono text-xs overflow-x-auto max-h-64">
                  {JSON.stringify(selectedTrace.findings, null, 2)}
                </pre>
              </div>
            </div>
          )}

          {/* Remediation Action Link */}
          <div className="glass-card rounded-2xl p-6 border border-emerald-500/20 bg-gradient-to-r from-emerald-950/20 to-sky-950/20 flex flex-col sm:flex-row items-center justify-between gap-4">
            <div>
              <h4 className="text-sm font-semibold text-white flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                Human-in-the-Loop Remediation Suggestions Ready
              </h4>
              <p className="text-xs text-gray-400 font-sans mt-0.5">
                The investigation workflow synthesized non-destructive data correction proposals awaiting review.
              </p>
            </div>
            <Link
              to={`/remediation?dataset_id=${selectedDatasetId}`}
              className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-semibold flex items-center gap-2 transition-colors shrink-0"
            >
              <span>Review Remediation Center</span>
              <ChevronRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      )}
    </Layout>
  );
};

