import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Layout } from '../components/Layout';
import { StatCard } from '../components/StatCard';
import { api } from '../services/api';
import { Dataset, AnomalyResult } from '../types';
import {
  Cpu,
  AlertTriangle,
  Play,
  Sliders,
  CheckCircle2,
  TrendingDown,
  Layers,
  Sparkles,
  Info
} from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell } from 'recharts';

export const AnomalyExplorer: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const dsParam = searchParams.get('dataset_id');

  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [selectedDatasetId, setSelectedDatasetId] = useState<number | null>(
    dsParam ? parseInt(dsParam) : null
  );
  const [anomalyData, setAnomalyData] = useState<AnomalyResult | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [running, setRunning] = useState<boolean>(false);

  // Detector parameters
  const [detectorType, setDetectorType] = useState<string>('isolation_forest');
  const [contamination, setContamination] = useState<number>(0.05);

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

  useEffect(() => {
    if (!selectedDatasetId) return;

    const fetchAnomalies = async () => {
      try {
        setLoading(true);
        const data = await api.getLatestAnomalies(selectedDatasetId);
        setAnomalyData(data);
        if (data.detector_type) setDetectorType(data.detector_type);
        if (data.contamination_rate) setContamination(data.contamination_rate);
      } catch (err) {
        console.error('Failed to fetch anomalies:', err);
        setAnomalyData(null);
      } finally {
        setLoading(false);
      }
    };

    fetchAnomalies();
  }, [selectedDatasetId]);

  const handleRunDetection = async () => {
    if (!selectedDatasetId) return;
    try {
      setRunning(true);
      const res = await api.runAnomalies(selectedDatasetId, {
        detector_type: detectorType,
        contamination_rate: contamination,
      });
      setAnomalyData(res);
    } catch (err) {
      console.error('Anomaly detection run failed:', err);
    } finally {
      setRunning(false);
    }
  };

  const featureChartData = anomalyData
    ? Object.entries(anomalyData.feature_importance || {}).map(([name, score]) => ({
        feature: name,
        contribution: Math.round(score * 1000) / 10,
      }))
    : [];

  return (
    <Layout title="Machine Learning Anomaly Explorer" subtitle="Multivariate Isolation Forest & Statistical Outlier Engine">
      {/* Top Controls & Parameters */}
      <div className="glass-card rounded-2xl p-6 border border-gray-800 space-y-4">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div>
            <h2 className="text-base font-semibold text-white flex items-center gap-2">
              <Cpu className="w-5 h-5 text-sky-400" />
              Model Configuration & Parameters
            </h2>
            <p className="text-xs text-gray-400 font-mono">Unsupervised multivariate tree-based isolation and statistical fences</p>
          </div>

          <button
            onClick={handleRunDetection}
            disabled={running || !selectedDatasetId}
            className="flex items-center gap-2 px-4 py-2 bg-sky-600 hover:bg-sky-500 text-white rounded-lg text-xs font-mono font-bold uppercase transition-colors shadow-lg shadow-sky-600/20 disabled:opacity-50"
          >
            {running ? (
              <div className="w-3.5 h-3.5 border-2 border-white/20 border-t-white rounded-full animate-spin" />
            ) : (
              <Play className="w-3.5 h-3.5 fill-current" />
            )}
            <span>Execute Detection</span>
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2 font-mono text-xs border-t border-gray-800/80">
          <div>
            <label className="text-gray-400 block mb-1.5 uppercase font-semibold">Target Dataset</label>
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
            <label className="text-gray-400 block mb-1.5 uppercase font-semibold">Detection Algorithm</label>
            <select
              value={detectorType}
              onChange={(e) => setDetectorType(e.target.value)}
              className="w-full px-3 py-2 bg-gray-900 border border-gray-800 rounded-lg text-xs text-white focus:outline-none focus:border-sky-500"
            >
              <option value="isolation_forest">Isolation Forest (Multivariate ML)</option>
              <option value="iqr">Statistical IQR Outlier Fences</option>
              <option value="z_score">Z-Score Distribution Testing (|z| &gt; 3.0)</option>
            </select>
          </div>

          <div>
            <div className="flex justify-between text-gray-400 uppercase font-semibold mb-1.5">
              <span>Contamination Rate</span>
              <span className="text-sky-400 font-bold">{Math.round(contamination * 100)}%</span>
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
        </div>
      </div>

      {loading ? (
        <div className="py-24 text-center text-gray-500">
          <div className="inline-block w-8 h-8 border-2 border-sky-500 border-t-transparent rounded-full animate-spin mb-3" />
          <p className="font-mono text-xs">Evaluating multidimensional feature space...</p>
        </div>
      ) : !anomalyData ? (
        <div className="glass-card rounded-2xl p-12 text-center border border-gray-800">
          <Info className="w-8 h-8 text-sky-400 mx-auto mb-2" />
          <p className="text-white font-semibold">No anomaly detection runs recorded yet</p>
          <p className="text-xs text-gray-500 mt-1">Configure parameters above and click 'Execute Detection'.</p>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Key Detection Stat Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
            <StatCard
              title="Flagged Anomalies"
              value={anomalyData.anomalous_rows_count}
              icon={AlertTriangle}
              colorScheme={anomalyData.anomalous_rows_count > 0 ? 'rose' : 'emerald'}
              description={`Contamination: ${(anomalyData.contamination_rate * 100).toFixed(0)}%`}
            />
            <StatCard
              title="Total Evaluated Rows"
              value={anomalyData.total_evaluated_rows.toLocaleString()}
              icon={Layers}
              colorScheme="blue"
              description="Complete multidimensional feature pass"
            />
            <StatCard
              title="Detection Algorithm"
              value={anomalyData.detector_type === 'isolation_forest' ? 'Isolation Forest' : 'IQR Outliers'}
              icon={Cpu}
              colorScheme="purple"
              description="Scikit-Learn ensemble model"
            />
            <StatCard
              title="Status"
              value={anomalyData.anomalous_rows_count > 0 ? 'ANOMALIES FOUND' : 'CLEAN'}
              icon={CheckCircle2}
              colorScheme={anomalyData.anomalous_rows_count > 0 ? 'amber' : 'emerald'}
              description="Traceable in AI Investigation"
            />
          </div>

          {/* Feature Importance Contribution Chart */}
          <div className="glass-card rounded-2xl p-6 border border-gray-800">
            <div className="mb-4">
              <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-sky-400" />
                Feature Importance & Anomaly Drivers
              </h3>
              <p className="text-xs text-gray-400 font-mono">
                Percentage contribution of individual columns driving the anomaly decision function
              </p>
            </div>

            <div className="h-56 w-full">
              {featureChartData.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={featureChartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                    <XAxis dataKey="feature" stroke="#6b7280" fontSize={11} fontStyle="mono" />
                    <YAxis stroke="#6b7280" fontSize={11} fontStyle="mono" unit="%" />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#111827', borderColor: '#374151', borderRadius: '8px', fontSize: '12px' }}
                    />
                    <Bar dataKey="contribution" fill="#38bdf8" radius={[4, 4, 0, 0]}>
                      {featureChartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={index === 0 ? '#f43f5e' : '#38bdf8'} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-full flex items-center justify-center text-xs text-gray-500 font-mono">
                  No feature variance deviations detected.
                </div>
              )}
            </div>
          </div>

          {/* Anomaly Sample Records Table */}
          <div className="glass-card rounded-2xl border border-gray-800 overflow-hidden">
            <div className="p-4 border-b border-gray-800 bg-gray-900/50 flex items-center justify-between">
              <div>
                <h3 className="text-xs font-mono uppercase tracking-wider text-white font-semibold">
                  Detected Anomalous Records ({anomalyData.anomaly_samples?.length || 0} Inspected)
                </h3>
                <p className="text-[11px] text-gray-400 font-mono">Sorted by severity of anomaly score</p>
              </div>
            </div>

            <div className="overflow-x-auto max-h-[450px]">
              <table className="w-full text-left text-xs font-mono">
                <thead className="bg-gray-900 border-b border-gray-800 text-gray-400 sticky top-0">
                  <tr>
                    <th className="py-2.5 px-3">Row Index</th>
                    <th className="py-2.5 px-3">Anomaly Score</th>
                    <th className="py-2.5 px-3">Flagged Indicators</th>
                    <th className="py-2.5 px-3">Record Values</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-800/60">
                  {anomalyData.anomaly_samples && anomalyData.anomaly_samples.length > 0 ? (
                    anomalyData.anomaly_samples.map((sample) => (
                      <tr key={sample.row_index} className="hover:bg-gray-800/30 transition-colors">
                        <td className="py-3 px-3 font-bold text-sky-400">#{sample.row_index}</td>
                        <td className="py-3 px-3">
                          <span className="px-2 py-0.5 rounded bg-rose-500/10 text-rose-400 border border-rose-500/30 font-bold">
                            {sample.anomaly_score.toFixed(3)}
                          </span>
                        </td>
                        <td className="py-3 px-3">
                          <div className="flex flex-wrap gap-1">
                            {sample.flagged_reasons.map((r, i) => (
                              <span key={i} className="px-1.5 py-0.5 rounded text-[10px] bg-amber-500/10 text-amber-300 border border-amber-500/20">
                                {r}
                              </span>
                            ))}
                          </div>
                        </td>
                        <td className="py-3 px-3 text-gray-300">
                          <div className="max-w-md truncate font-sans text-xs">
                            {Object.entries(sample.values)
                              .map(([k, v]) => `${k}: ${v}`)
                              .join(' | ')}
                          </div>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={4} className="py-8 text-center text-gray-500">
                        Zero anomalous row vectors identified by model.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </Layout>
  );
};

