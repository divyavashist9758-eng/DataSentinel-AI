import React, { useState, useEffect } from 'react';
import { Layout } from '../components/Layout';
import { StatusBadge } from '../components/StatusBadge';
import { api } from '../services/api';
import { Dataset, Investigation } from '../types';
import {
  FileText,
  Download,
  BookOpen,
  Search,
  Sparkles,
  Bot,
  Database,
  ExternalLink,
  ShieldCheck,
  CheckCircle2,
  RefreshCw,
  AlertCircle
} from 'lucide-react';

export const Reports: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'REPORTS' | 'KNOWLEDGE'>('REPORTS');
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [selectedDatasetId, setSelectedDatasetId] = useState<number | null>(null);
  const [investigations, setInvestigations] = useState<Investigation[]>([]);
  const [selectedInvestigation, setSelectedInvestigation] = useState<Investigation | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // RAG Knowledge Base State
  const [knowledgeList, setKnowledgeList] = useState<any[]>([]);
  const [knowledgeQuery, setKnowledgeQuery] = useState<string>('');
  const [ragLoading, setRagLoading] = useState<boolean>(false);

  useEffect(() => {
    fetchInitialData();
  }, []);

  useEffect(() => {
    if (selectedDatasetId) {
      fetchInvestigations(selectedDatasetId);
    }
  }, [selectedDatasetId]);

  const fetchInitialData = async () => {
    try {
      setLoading(true);
      const ds = await api.getDatasets();
      setDatasets(ds);
      if (ds.length > 0) {
        setSelectedDatasetId(ds[0].id);
      }
      // Preload RAG items
      fetchKnowledge();
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to initialize reports page.');
    } finally {
      setLoading(false);
    }
  };

  const fetchInvestigations = async (datasetId: number) => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getDatasetInvestigations(datasetId);
      setInvestigations(data);
      if (data.length > 0) {
        setSelectedInvestigation(data[0]);
      } else {
        setSelectedInvestigation(null);
      }
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to fetch investigations.');
    } finally {
      setLoading(false);
    }
  };

  const fetchKnowledge = async (query?: string) => {
    try {
      setRagLoading(true);
      if (query && query.trim().length > 0) {
        const results = await api.searchKnowledge(query);
        setKnowledgeList(results);
      } else {
        const all = await api.getAllKnowledge();
        setKnowledgeList(all);
      }
    } catch (err) {
      console.error('Failed to load knowledge base', err);
    } finally {
      setRagLoading(false);
    }
  };

  const [exportLoading, setExportLoading] = useState<boolean>(false);

  const handleExportPdf = async (invId: number) => {
    try {
      setExportLoading(true);
      const blob = await api.downloadInvestigationPdf(invId);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `investigation_report_${invId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      alert('Failed to download PDF dossier: ' + (err?.response?.data?.detail || err.message));
    } finally {
      setExportLoading(false);
    }
  };

  const handleExportCsv = async (invId: number) => {
    try {
      setExportLoading(true);
      const blob = await api.downloadInvestigationCsv(invId);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `investigation_traces_${invId}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      alert('Failed to download CSV summary: ' + (err?.response?.data?.detail || err.message));
    } finally {
      setExportLoading(false);
    }
  };

  return (
    <Layout
      title="Reports & RAG Knowledge Repository"
      subtitle="Export formal PDF investigation dossiers, analytical CSV summaries, and explore retrieval-augmented playbooks."
    >
      {/* Top Navigation Tabs */}
      <div className="flex border-b border-gray-800 gap-4 mb-2">
        <button
          onClick={() => setActiveTab('REPORTS')}
          className={`flex items-center gap-2 pb-3 px-2 text-xs font-semibold uppercase tracking-wider transition ${
            activeTab === 'REPORTS'
              ? 'border-b-2 border-sky-500 text-sky-400'
              : 'text-gray-400 hover:text-gray-200'
          }`}
        >
          <FileText className="w-4 h-4" />
          Investigation Reports & Export Center
        </button>
        <button
          onClick={() => setActiveTab('KNOWLEDGE')}
          className={`flex items-center gap-2 pb-3 px-2 text-xs font-semibold uppercase tracking-wider transition ${
            activeTab === 'KNOWLEDGE'
              ? 'border-b-2 border-sky-500 text-sky-400'
              : 'text-gray-400 hover:text-gray-200'
          }`}
        >
          <BookOpen className="w-4 h-4" />
          RAG Knowledge Base & Playbooks
        </button>
      </div>

      {activeTab === 'REPORTS' ? (
        <div className="space-y-6">
          {/* Dataset Selector Bar */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 bg-[#131b2e] border border-gray-800 p-4 rounded-xl">
            <div className="flex items-center gap-3">
              <Database className="w-4 h-4 text-sky-400" />
              <span className="text-xs font-semibold uppercase tracking-wider text-gray-400">Target Dataset:</span>
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
            </div>

            {selectedInvestigation && (
              <div className="flex items-center gap-3">
                <button
                  onClick={() => handleExportPdf(selectedInvestigation.id)}
                  className="px-4 py-2 bg-gradient-to-r from-sky-600 to-indigo-600 hover:from-sky-500 hover:to-indigo-500 text-white rounded-lg text-xs font-semibold flex items-center gap-2 shadow-lg shadow-sky-600/20 transition"
                >
                  <Download className="w-4 h-4" />
                  Export PDF Dossier
                </button>
                <button
                  onClick={() => handleExportCsv(selectedInvestigation.id)}
                  className="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-gray-200 border border-gray-700 rounded-lg text-xs font-semibold flex items-center gap-2 transition"
                >
                  <FileText className="w-4 h-4 text-emerald-400" />
                  Export CSV Summary
                </button>
              </div>
            )}
          </div>

          {/* Investigation Master-Detail View */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left Column: Investigation List */}
            <div className="bg-[#131b2e] border border-gray-800 rounded-xl p-4 space-y-3">
              <div className="text-xs font-mono text-gray-400 uppercase tracking-wider mb-2">
                Available Investigations ({investigations.length})
              </div>

              {loading ? (
                <div className="py-8 text-center text-xs text-gray-400">Loading investigations...</div>
              ) : investigations.length === 0 ? (
                <div className="py-8 text-center text-xs text-gray-400 space-y-2">
                  <AlertCircle className="w-6 h-6 text-gray-400 mx-auto" />
                  <p>No investigations on record.</p>
                  <p className="text-[11px] text-gray-400">Trigger one from AI Investigation Center.</p>
                </div>
              ) : (
                <div className="space-y-2 max-h-[600px] overflow-y-auto">
                  {investigations.map((inv) => (
                    <div
                      key={inv.id}
                      onClick={() => setSelectedInvestigation(inv)}
                      className={`p-3 rounded-lg border cursor-pointer transition ${
                        selectedInvestigation?.id === inv.id
                          ? 'bg-sky-950/50 border-sky-700 shadow-md'
                          : 'bg-[#0b0f19] border-gray-800 hover:border-gray-700'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs font-bold text-white font-mono">#{inv.id} {inv.title}</span>
                        <StatusBadge status={inv.status} />
                      </div>
                      <div className="text-[11px] text-gray-400 line-clamp-2 mb-2">
                        {inv.summary || 'Investigation completed across 6 agent nodes.'}
                      </div>
                      <div className="flex items-center justify-between text-[10px] font-mono text-gray-400">
                        <span>Confidence: {(inv.confidence_score * 100).toFixed(0)}%</span>
                        <span>{new Date(inv.created_at).toLocaleDateString()}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Right Column: Selected Investigation Full Dossier */}
            <div className="lg:col-span-2 space-y-6">
              {selectedInvestigation ? (
                <>
                  {/* Executive Summary Card */}
                  <div className="bg-[#131b2e] border border-gray-800 rounded-xl p-6 space-y-4">
                    <div className="flex flex-wrap items-center justify-between gap-3 border-b border-gray-800 pb-3">
                      <div>
                        <div className="text-xs font-mono text-sky-400 mb-0.5">
                          Investigation #{selectedInvestigation.id} Report
                        </div>
                        <h2 className="text-lg font-bold text-white">{selectedInvestigation.title}</h2>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-mono text-gray-400">Confidence:</span>
                        <span className="px-2.5 py-1 rounded bg-sky-950/80 border border-sky-800 text-sky-400 text-xs font-mono font-bold">
                          {(selectedInvestigation.confidence_score * 100).toFixed(0)}%
                        </span>
                      </div>
                    </div>

                    {selectedInvestigation.summary && (
                      <div>
                        <div className="text-xs font-mono text-gray-400 uppercase tracking-wider mb-1">
                          Executive Synthesis
                        </div>
                        <p className="text-xs text-gray-200 leading-relaxed bg-[#0b0f19] p-3.5 rounded-lg border border-gray-800">
                          {selectedInvestigation.summary}
                        </p>
                      </div>
                    )}

                    {selectedInvestigation.root_cause_hypothesis && (
                      <div>
                        <div className="text-xs font-mono text-amber-400 uppercase tracking-wider mb-1 flex items-center gap-1.5">
                          <Sparkles className="w-3.5 h-3.5" />
                          Root Cause Diagnostic Hypothesis
                        </div>
                        <p className="text-xs text-amber-200/90 leading-relaxed bg-amber-950/20 p-3.5 rounded-lg border border-amber-900/40">
                          {selectedInvestigation.root_cause_hypothesis}
                        </p>
                      </div>
                    )}
                  </div>

                  {/* 6 Specialized Agent Execution Traces */}
                  <div className="bg-[#131b2e] border border-gray-800 rounded-xl p-6 space-y-4">
                    <div className="text-xs font-mono text-gray-400 uppercase tracking-wider mb-2 flex items-center gap-2">
                      <Bot className="w-4 h-4 text-sky-400" />
                      Multi-Agent Investigation Workflow Trace
                    </div>

                    <div className="space-y-3">
                      {selectedInvestigation.agent_traces && selectedInvestigation.agent_traces.map((trace, idx) => (
                        <div
                          key={idx}
                          className="bg-[#0b0f19] border border-gray-800/80 rounded-xl p-4 space-y-2 hover:border-gray-700 transition"
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                              <span className="w-5 h-5 rounded-full bg-sky-950 border border-sky-800 flex items-center justify-center text-[10px] font-mono font-bold text-sky-400">
                                {idx + 1}
                              </span>
                              <span className="text-xs font-bold text-white uppercase font-mono tracking-wide">
                                {trace.agent_name.replace(/_/g, ' ')}
                              </span>
                              <span className="text-[11px] text-gray-400 font-mono">
                                ({trace.role_description})
                              </span>
                            </div>
                            <div className="flex items-center gap-2 font-mono text-[10px] text-gray-400">
                              <span>{trace.execution_time_ms}ms</span>
                              <StatusBadge status={trace.status} />
                            </div>
                          </div>

                          <p className="text-xs text-gray-300 leading-relaxed pl-7">
                            {trace.summary_insight}
                          </p>

                          {/* Cited RAG Knowledge Sources */}
                          {trace.rag_sources && trace.rag_sources.length > 0 && (
                            <div className="pl-7 pt-2 border-t border-gray-800/60 mt-2 space-y-1">
                              <span className="text-[10px] font-mono uppercase tracking-wider text-indigo-400 block mb-1">
                                Cited Knowledge Playbooks:
                              </span>
                              {trace.rag_sources.map((src, sIdx) => (
                                <div
                                  key={sIdx}
                                  className="text-[11px] font-mono text-gray-400 bg-gray-900/60 p-2 rounded border border-gray-800 flex items-center justify-between"
                                >
                                  <div>
                                    <span className="text-sky-300 font-semibold">{src.title}</span> ({src.citation})
                                  </div>
                                  <span className="text-[10px] text-gray-400">Score: {src.relevance_score}</span>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                </>
              ) : (
                <div className="p-12 text-center bg-[#131b2e] border border-gray-800 rounded-xl space-y-2">
                  <FileText className="w-8 h-8 text-gray-400 mx-auto" />
                  <p className="text-sm font-semibold text-gray-300">No Investigation Selected</p>
                  <p className="text-xs text-gray-400">Select an investigation from the left panel to inspect the full dossier and export reports.</p>
                </div>
              )}
            </div>
          </div>
        </div>
      ) : (
        /* RAG Knowledge Base Browser */
        <div className="space-y-6">
          <div className="bg-[#131b2e] border border-gray-800 p-4 rounded-xl flex flex-col md:flex-row gap-4 justify-between items-center">
            <div className="relative w-full md:w-96">
              <Search className="w-4 h-4 text-gray-400 absolute left-3.5 top-3" />
              <input
                type="text"
                placeholder="Search rules, root causes, playbooks..."
                value={knowledgeQuery}
                onChange={(e) => setKnowledgeQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && fetchKnowledge(knowledgeQuery)}
                className="w-full bg-[#0b0f19] border border-gray-700 text-gray-200 text-xs rounded-lg pl-10 pr-4 py-2.5 focus:ring-1 focus:ring-sky-500 focus:outline-none"
              />
            </div>
            <div className="flex items-center gap-3 w-full md:w-auto">
              <button
                onClick={() => fetchKnowledge(knowledgeQuery)}
                className="px-4 py-2 bg-sky-600 hover:bg-sky-500 text-white rounded-lg text-xs font-semibold flex items-center gap-2 transition"
              >
                Search Knowledge
              </button>
              <button
                onClick={() => {
                  setKnowledgeQuery('');
                  fetchKnowledge();
                }}
                className="p-2 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-lg text-xs transition"
                title="Reset search"
              >
                <RefreshCw className="w-4 h-4" />
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {ragLoading ? (
              <div className="col-span-full py-12 text-center text-xs text-gray-400">Searching knowledge base...</div>
            ) : knowledgeList.length === 0 ? (
              <div className="col-span-full py-12 text-center text-xs text-gray-400">No knowledge entries found.</div>
            ) : (
              knowledgeList.map((item, idx) => (
                <div
                  key={idx}
                  className="bg-[#131b2e] border border-gray-800 rounded-xl p-5 hover:border-gray-700 transition flex flex-col justify-between space-y-3"
                >
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="px-2 py-0.5 rounded bg-indigo-950/80 border border-indigo-800 text-indigo-400 text-[10px] font-mono font-bold">
                        {item.category}
                      </span>
                      <span className="text-[10px] font-mono text-gray-400">{item.citation}</span>
                    </div>
                    <h4 className="text-sm font-bold text-white">{item.title}</h4>
                    <p className="text-xs text-gray-300 leading-relaxed">{item.content}</p>
                  </div>

                  {item.remediation_strategy && (
                    <div className="pt-2 border-t border-gray-800">
                      <span className="text-[10px] font-mono uppercase text-emerald-400 block mb-0.5">
                        Recommended Playbook:
                      </span>
                      <p className="text-xs font-mono text-gray-300 bg-[#0b0f19] p-2 rounded border border-gray-800">
                        {item.remediation_strategy}
                      </p>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </Layout>
  );
};
export default Reports;

