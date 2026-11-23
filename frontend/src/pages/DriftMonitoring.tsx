import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Layout } from '../components/Layout';
import { StatCard } from '../components/StatCard';
import { StatusBadge } from '../components/StatusBadge';
import { api } from '../services/api';
import { Dataset, DriftResult, FeatureDriftMetric } from '../types';
import {
  GitCompare,
  AlertTriangle,
  CheckCircle2,
  Play,
  Layers,
  ArrowRight,
  Sparkles,
  Database,
  BarChart2,
  Info
} from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from 'recharts';

export const DriftMonitoring: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const dsParam = searchParams.get('dataset_id');

  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [selectedDatasetId, setSelectedDatasetId] = useState<number | null>(
    dsParam ? parseInt(dsParam) : null
  );
  const [selectedDatasetDetail, setSelectedDatasetDetail] = useState<any | null>(null);

  const [baselineVersionId, setBaselineVersionId] = useState<number | null>(null);
  const [currentVersionId, setCurrentVersionId] = useState<number | null>(null);

  const [driftResult, setDriftResult] = useState<DriftResult | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [analyzing, setAnalyzing] = useState<boolean>(false);
  const [selectedFeature, setSelectedFeature] = useState<FeatureDriftMetric | null>(null);

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

  // Load dataset detail and versions
  useEffect(() => {
    if (!selectedDatasetId) return;

    const fetchDetail = async () => {
      try {
        setLoading(true);
        const detail = await api.getDataset(selectedDatasetId);
        setSelectedDatasetDetail(detail);

        if (detail.versions && detail.versions.length >= 2) {
          setBaselineVersionId(detail.versions[detail.versions.length - 1].id);
          setCurrentVersionId(detail.versions[0].id);
        } else if (detail.versions && detail.versions.length === 1) {
          setBaselineVersionId(detail.versions[0].id);
          setCurrentVersionId(detail.versions[0].id);
        }

        // Try to fetch latest drift
        try {
          const latestDrift = await api.getLatestDrift(selectedDatasetId);
          setDriftResult(latestDrift);
          if (latestDrift.feature_metrics) {
            setSelectedFeature(Object.values(latestDrift.feature_metrics)[0]);
          }
        } catch (e) {
          setDriftResult(null);
        }
      } catch (err) {
        console.error('Error loading dataset detail for drift:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchDetail();
  }, [selectedDatasetId]);

  const handleRunDrift = async () => {
    if (!selectedDatasetId || !baselineVersionId || !currentVersionId) return;

    try {
      setAnalyzing(true);
      const res = await api.runDriftAnalysis(selectedDatasetId, {
        baseline_version_id: baselineVersionId,
        current_version_id: currentVersionId,
        p_value_threshold: 0.05,
        psi_threshold: 0.25,
      });
      setDriftResult(res);
      if (res.feature_metrics) {
        setSelectedFeature(Object.values(res.feature_metrics)[0]);
      }
    } catch (err: any) {
      console.error('Drift analysis failed:', err);
      alert(err.response?.data?.detail || 'Drift analysis failed.');
    } finally {
      setAnalyzing(false);
    }
  };

  const getDistributionComparisonData = (metric: FeatureDriftMetric) => {
    if (!metric.baseline_distribution?.bins) return [];
    const bins = metric.baseline_distribution.bins;
    const baseP = metric.baseline_distribution.proportions || metric.baseline_distribution.baseline_proportions;
    const currP = metric.current_distribution?.proportions || metric.baseline_distribution.current_proportions;

    if (!baseP || !currP) return [];

    return baseP.map((bp: number, i: number) => ({
      bin: bins[i] != null ? `${bins[i]} - ${bins[i + 1] || ''}` : `Bin ${i + 1}`,
      Baseline: Math.round(bp * 1000) / 10,
      Current: Math.round((currP[i] || 0) * 1000) / 10,
    }));
  };

  return (
    <Layout title="Statistical Data & Schema Drift Monitor" subtitle="Two-Sample Kolmogorov-Smirnov Test, Population Stability Index (PSI) & Schema Mutations">
      {/* Top Configuration Bar */}
      <div className="glass-card rounded-2xl p-6 border border-gray-800 space-y-4">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div>
            <h2 className="text-base font-semibold text-white flex items-center gap-2">
              <GitCompare className="w-5 h-5 text-sky-400" />
              Distribution Drift Comparison Configuration
            </h2>
            <p className="text-xs text-gray-400 font-mono">Measure continuous KS distance, binwise PSI, and structural schema diff</p>
          </div>

          <button
            onClick={handleRunDrift}
            disabled={analyzing || !selectedDatasetId || !baselineVersionId || !currentVersionId}
            className="flex items-center gap-2 px-4 py-2 bg-sky-600 hover:bg-sky-500 text-white rounded-lg text-xs font-mono font-bold uppercase transition-colors shadow-lg shadow-sky-600/20 disabled:opacity-50"
          >
            {analyzing ? (
              <div className="w-3.5 h-3.5 border-2 border-white/20 border-t-white rounded-full animate-spin" />
            ) : (
              <Play className="w-3.5 h-3.5 fill-current" />
            )}
            <span>Execute Drift Analysis</span>
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2 font-mono text-xs border-t border-gray-800/80">
          <div>
            <label className="text-gray-400 block mb-1.5 uppercase font-semibold">Dataset</label>
            <select
              value={selectedDatasetId || ''}
              onChange={(e) => {
                const id = parseInt(e.target.value);
                setSelectedDatasetId(id);
                setSearchParams({ dataset_id: String(id) });
              }}
              className="w-full px-3 py-2 bg-gray-900 border border-gray-800 rounded-lg text-xs text-white focus:outline-none focus:border-sky-500"
            >
              {datasets.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.name} ({d.row_count} rows)
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-gray-400 block mb-1.5 uppercase font-semibold">Baseline Version (Reference)</label>
            <select
              value={baselineVersionId || ''}
              onChange={(e) => setBaselineVersionId(parseInt(e.target.value))}
              className="w-full px-3 py-2 bg-gray-900 border border-gray-800 rounded-lg text-xs text-white focus:outline-none focus:border-sky-500"
            >
              {selectedDatasetDetail?.versions?.map((v: any) => (
                <option key={v.id} value={v.id}>
                  Version {v.version_num} ({v.row_count} rows &bull; {new Date(v.created_at).toLocaleDateString()})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-gray-400 block mb-1.5 uppercase font-semibold">Current Version (Target)</label>
            <select
              value={currentVersionId || ''}
              onChange={(e) => setCurrentVersionId(parseInt(e.target.value))}
              className="w-full px-3 py-2 bg-gray-900 border border-gray-800 rounded-lg text-xs text-white focus:outline-none focus:border-sky-500"
            >
              {selectedDatasetDetail?.versions?.map((v: any) => (
                <option key={v.id} value={v.id}>
                  Version {v.version_num} ({v.row_count} rows &bull; {new Date(v.created_at).toLocaleDateString()})
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="py-24 text-center text-gray-500">
          <div className="inline-block w-8 h-8 border-2 border-sky-500 border-t-transparent rounded-full animate-spin mb-3" />
          <p className="font-mono text-xs">Comparing distribution vectors across historical versions...</p>
        </div>
      ) : !driftResult ? (
        <div className="glass-card rounded-2xl p-12 text-center border border-gray-800">
          <Info className="w-8 h-8 text-sky-400 mx-auto mb-2" />
          <p className="text-white font-semibold">No drift analysis recorded between selected versions</p>
          <p className="text-xs text-gray-400 mt-1">Select versions and execute drift analysis above.</p>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Summary Stat Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
            <StatCard
              title="Overall Drift Status"
              value={driftResult.overall_drift_detected ? 'DRIFT DETECTED' : 'STABLE'}
              icon={driftResult.overall_drift_detected ? AlertTriangle : CheckCircle2}
              colorScheme={driftResult.overall_drift_detected ? 'rose' : 'emerald'}
              description={`Drift Score: ${driftResult.drift_score}%`}
            />
            <StatCard
              title="Drifted Features"
              value={`${driftResult.drifted_features_count} / ${driftResult.total_features_count}`}
              icon={Layers}
              colorScheme={driftResult.drifted_features_count > 0 ? 'amber' : 'emerald'}
              description="Exceeding KS p < 0.05 or PSI > 0.25"
            />
            <StatCard
              title="Added Schema Columns"
              value={driftResult.schema_diff?.added_columns.length || 0}
              icon={Database}
              colorScheme="blue"
              description="New features added to current version"
            />
            <StatCard
              title="Type Conversions"
              value={driftResult.schema_diff?.type_changes.length || 0}
              icon={GitCompare}
              colorScheme="purple"
              description="Breaking datatype mutations"
            />
          </div>

          {/* Schema Drift Structural Mutation Panel */}
          {driftResult.schema_diff && (
            <div className="glass-card rounded-2xl p-6 border border-gray-800 space-y-4">
              <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                <Layers className="w-4 h-4 text-indigo-400" />
                Structural Schema Mutations
              </h3>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 font-mono text-xs">
                <div className="p-3.5 rounded-xl bg-gray-900/60 border border-gray-800">
                  <span className="text-gray-500 block uppercase text-[10px]">Added Columns</span>
                  <div className="mt-1 flex flex-wrap gap-1">
                    {driftResult.schema_diff.added_columns.length > 0 ? (
                      driftResult.schema_diff.added_columns.map((c) => (
                        <span key={c} className="px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                          +{c}
                        </span>
                      ))
                    ) : (
                      <span className="text-gray-500">None</span>
                    )}
                  </div>
                </div>

                <div className="p-3.5 rounded-xl bg-gray-900/60 border border-gray-800">
                  <span className="text-gray-500 block uppercase text-[10px]">Removed Columns</span>
                  <div className="mt-1 flex flex-wrap gap-1">
                    {driftResult.schema_diff.removed_columns.length > 0 ? (
                      driftResult.schema_diff.removed_columns.map((c) => (
                        <span key={c} className="px-1.5 py-0.5 rounded bg-rose-500/10 text-rose-400 border border-rose-500/20">
                          -{c}
                        </span>
                      ))
                    ) : (
                      <span className="text-gray-500">None</span>
                    )}
                  </div>
                </div>

                <div className="p-3.5 rounded-xl bg-gray-900/60 border border-gray-800">
                  <span className="text-gray-500 block uppercase text-[10px]">Unexpected Categories</span>
                  <div className="mt-1 flex flex-wrap gap-1">
                    {driftResult.schema_diff.unexpected_categories.length > 0 ? (
                      driftResult.schema_diff.unexpected_categories.map((uc, i) => (
                        <span key={i} className="px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-300 border border-amber-500/20">
                          {uc.column}: {uc.new_categories.join(', ')}
                        </span>
                      ))
                    ) : (
                      <span className="text-gray-500">None</span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Feature Drift Table & Distribution Comparison */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Feature Metrics Table */}
            <div className="glass-card rounded-2xl border border-gray-800 overflow-hidden lg:col-span-2">
              <div className="p-4 border-b border-gray-800 bg-gray-900/40">
                <h3 className="text-xs font-mono uppercase tracking-wider text-gray-300 font-semibold">
                  Feature-Level Statistical Drift Metrics
                </h3>
              </div>

              <div className="overflow-x-auto max-h-[450px]">
                <table className="w-full text-left text-xs font-mono">
                  <thead className="bg-gray-900 sticky top-0 border-b border-gray-800 text-gray-400">
                    <tr>
                      <th className="py-2.5 px-3">Feature Name</th>
                      <th className="py-2.5 px-3">Type</th>
                      <th className="py-2.5 px-3">KS Statistic</th>
                      <th className="py-2.5 px-3">p-value</th>
                      <th className="py-2.5 px-3">PSI Score</th>
                      <th className="py-2.5 px-3">Drift Level</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-800/60">
                    {Object.values(driftResult.feature_metrics || {}).map((metric) => {
                      const isSelected = selectedFeature?.column_name === metric.column_name;
                      return (
                        <tr
                          key={metric.column_name}
                          onClick={() => setSelectedFeature(metric)}
                          className={`cursor-pointer transition-colors ${
                            isSelected ? 'bg-sky-500/10 border-l-2 border-sky-400' : 'hover:bg-gray-800/30'
                          }`}
                        >
                          <td className="py-2.5 px-3 font-semibold text-white">{metric.column_name}</td>
                          <td className="py-2.5 px-3 uppercase text-gray-400">{metric.feature_type}</td>
                          <td className="py-2.5 px-3 text-gray-300">{metric.ks_statistic ?? '-'}</td>
                          <td className="py-2.5 px-3">
                            <span className={metric.p_value != null && metric.p_value < 0.05 ? 'text-rose-400 font-bold' : 'text-gray-400'}>
                              {metric.p_value != null ? metric.p_value.toFixed(4) : '-'}
                            </span>
                          </td>
                          <td className="py-2.5 px-3">
                            <span className={metric.psi_score != null && metric.psi_score >= 0.25 ? 'text-rose-400 font-bold' : 'text-gray-300'}>
                              {metric.psi_score != null ? metric.psi_score.toFixed(3) : '-'}
                            </span>
                          </td>
                          <td className="py-2.5 px-3">
                            <StatusBadge status={metric.drift_level} type="severity" />
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Distribution Bin Comparison Visualizer */}
            <div className="glass-card rounded-2xl p-5 border border-gray-800 flex flex-col justify-between">
              <div>
                <h3 className="text-xs font-mono uppercase tracking-wider text-sky-400 font-semibold mb-1 flex items-center gap-1.5">
                  <BarChart2 className="w-4 h-4" />
                  Baseline vs Current Distribution
                </h3>
                <p className="text-[11px] text-gray-400 font-mono mb-4">
                  Feature: <span className="text-white font-bold">{selectedFeature?.column_name}</span> &bull; PSI: {selectedFeature?.psi_score ?? 'N/A'}
                </p>

                {selectedFeature && selectedFeature.baseline_distribution ? (
                  <div className="h-64 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={getDistributionComparisonData(selectedFeature)}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                        <XAxis dataKey="bin" stroke="#6b7280" fontSize={9} fontStyle="mono" tick={false} />
                        <YAxis stroke="#6b7280" fontSize={10} fontStyle="mono" unit="%" />
                        <Tooltip contentStyle={{ backgroundColor: '#111827', borderColor: '#374151', fontSize: '11px' }} />
                        <Legend wrapperStyle={{ fontSize: '11px', fontFamily: 'monospace' }} />
                        <Bar dataKey="Baseline" fill="#0ea5e9" radius={[4, 4, 0, 0]} />
                        <Bar dataKey="Current" fill="#f43f5e" radius={[4, 4, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                ) : (
                  <p className="text-xs text-gray-500 font-mono text-center pt-16">
                    Select a continuous numerical feature to inspect distribution quantile bins.
                  </p>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </Layout>
  );
};

