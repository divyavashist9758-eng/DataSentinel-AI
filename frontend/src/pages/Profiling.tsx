import React, { useEffect, useState } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { Layout } from '../components/Layout';
import { ScoreMeter } from '../components/ScoreMeter';
import { api } from '../services/api';
import { Dataset, ProfilingResult, ColumnMetric } from '../types';
import {
  Activity,
  Layers,
  Sparkles,
  RefreshCw,
  AlertTriangle,
  BarChart2,
  ChevronRight,
  Database,
  Hash,
  Filter
} from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

export const Profiling: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const datasetIdParam = searchParams.get('dataset_id');

  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [selectedDatasetId, setSelectedDatasetId] = useState<number | null>(
    datasetIdParam ? parseInt(datasetIdParam) : null
  );
  const [profiling, setProfiling] = useState<ProfilingResult | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [reprofiling, setReprofiling] = useState<boolean>(false);
  const [selectedColumn, setSelectedColumn] = useState<ColumnMetric | null>(null);

  // Load datasets list
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

  // Fetch profiling for selected dataset
  useEffect(() => {
    if (!selectedDatasetId) return;

    const fetchProfiling = async () => {
      try {
        setLoading(true);
        const data = await api.getLatestProfiling(selectedDatasetId);
        setProfiling(data);
        if (data.column_metrics && Object.keys(data.column_metrics).length > 0) {
          setSelectedColumn(Object.values(data.column_metrics)[0]);
        }
      } catch (err) {
        console.error('Failed to load profiling:', err);
        setProfiling(null);
        setSelectedColumn(null);
      } finally {
        setLoading(false);
      }
    };

    fetchProfiling();
  }, [selectedDatasetId]);

  const handleRunProfiling = async () => {
    if (!selectedDatasetId) return;
    try {
      setReprofiling(true);
      const res = await api.runProfiling(selectedDatasetId);
      setProfiling(res);
      if (res.column_metrics && Object.keys(res.column_metrics).length > 0) {
        setSelectedColumn(Object.values(res.column_metrics)[0]);
      }
    } catch (err) {
      console.error('Reprofiling failed:', err);
    } finally {
      setReprofiling(false);
    }
  };

  const getHistogramData = (col: ColumnMetric) => {
    if (!col.histogram) return [];
    return col.histogram.counts.map((count, i) => ({
      bin: `${col.histogram!.bin_edges[i]} - ${col.histogram!.bin_edges[i + 1]}`,
      count,
    }));
  };

  return (
    <Layout title="Autonomous Data Profiling & Quality Engine" subtitle="Deterministic Statistical Telemetry, Completeness, Cardinality & Transparent Scoring">
      {/* Top Selector Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pb-2">
        <div className="flex items-center gap-3 w-full sm:w-auto">
          <label className="text-xs font-mono text-gray-400 uppercase font-semibold">Dataset:</label>
          <select
            value={selectedDatasetId || ''}
            onChange={(e) => {
              const newId = parseInt(e.target.value);
              setSelectedDatasetId(newId);
              setSearchParams({ dataset_id: String(newId) });
            }}
            className="px-3.5 py-2 bg-gray-900 border border-gray-800 rounded-lg text-xs font-mono text-white focus:outline-none focus:border-sky-500"
          >
            {datasets.map((d) => (
              <option key={d.id} value={d.id}>
                {d.name} ({d.row_count} rows &bull; {d.file_type.toUpperCase()})
              </option>
            ))}
          </select>
        </div>

        <div className="flex items-center gap-3 w-full sm:w-auto justify-end">
          <button
            onClick={handleRunProfiling}
            disabled={reprofiling || !selectedDatasetId}
            className="flex items-center gap-2 px-3.5 py-2 rounded-lg bg-gray-800 hover:bg-gray-700 text-xs font-mono text-gray-200 border border-gray-700 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${reprofiling ? 'animate-spin' : ''}`} />
            <span>Re-compute Profile</span>
          </button>
          {selectedDatasetId && (
            <Link
              to={`/investigations?dataset_id=${selectedDatasetId}`}
              className="flex items-center gap-2 px-3.5 py-2 rounded-lg bg-sky-600 hover:bg-sky-500 text-xs font-semibold text-white transition-colors shadow-lg shadow-sky-600/20"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>Launch AI Investigation</span>
            </Link>
          )}
        </div>
      </div>

      {loading ? (
        <div className="py-24 text-center text-gray-500">
          <div className="inline-block w-8 h-8 border-2 border-sky-500 border-t-transparent rounded-full animate-spin mb-3" />
          <p className="font-mono text-xs">Computing statistical distribution metrics...</p>
        </div>
      ) : !profiling ? (
        <div className="glass-card rounded-2xl p-12 text-center border border-gray-800">
          <AlertTriangle className="w-10 h-10 text-amber-500 mx-auto mb-3" />
          <p className="text-base font-semibold text-white">No profiling record found</p>
          <p className="text-xs text-gray-400 mt-1 mb-4">Click below to compute initial statistical profile.</p>
          <button
            onClick={handleRunProfiling}
            className="px-4 py-2 bg-sky-600 hover:bg-sky-500 text-white rounded-lg text-xs font-mono font-semibold"
          >
            Run Initial Profile
          </button>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Quality Score Breakdown Banner */}
          <div className="glass-card rounded-2xl p-6 border border-gray-800 grid grid-cols-1 md:grid-cols-4 gap-6 items-center">
            <div className="flex flex-col items-center justify-center border-b md:border-b-0 md:border-r border-gray-800 pb-4 md:pb-0 md:pr-6">
              <ScoreMeter score={profiling.overall_score} size="lg" label="Overall Quality Score" />
            </div>

            <div className="md:col-span-3 grid grid-cols-2 sm:grid-cols-4 gap-4 font-mono text-xs">
              <div className="p-3.5 rounded-xl bg-gray-900/60 border border-gray-800">
                <span className="text-gray-400 block text-[10px] uppercase">Completeness</span>
                <span className="text-xl font-bold text-emerald-400">
                  {profiling.quality_breakdown.completeness_score}%
                </span>
                <span className="text-[10px] text-gray-400 block mt-0.5">
                  -{profiling.quality_breakdown.penalties.missingness_penalty} penalty
                </span>
              </div>

              <div className="p-3.5 rounded-xl bg-gray-900/60 border border-gray-800">
                <span className="text-gray-400 block text-[10px] uppercase">Uniqueness</span>
                <span className="text-xl font-bold text-sky-400">
                  {profiling.quality_breakdown.uniqueness_score}%
                </span>
                <span className="text-[10px] text-gray-400 block mt-0.5">
                  -{profiling.quality_breakdown.penalties.duplicate_penalty} penalty
                </span>
              </div>

              <div className="p-3.5 rounded-xl bg-gray-900/60 border border-gray-800">
                <span className="text-gray-400 block text-[10px] uppercase">Validity (Outliers)</span>
                <span className="text-xl font-bold text-amber-400">
                  {profiling.quality_breakdown.validity_score}%
                </span>
                <span className="text-[10px] text-gray-400 block mt-0.5">
                  -{profiling.quality_breakdown.penalties.outlier_penalty} penalty
                </span>
              </div>

              <div className="p-3.5 rounded-xl bg-gray-900/60 border border-gray-800">
                <span className="text-gray-400 block text-[10px] uppercase">Consistency</span>
                <span className="text-xl font-bold text-indigo-400">
                  {profiling.quality_breakdown.consistency_score}%
                </span>
                <span className="text-[10px] text-gray-400 block mt-0.5">Structure valid</span>
              </div>
            </div>
          </div>

          {/* Quick Metrics Bar */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 font-mono text-xs">
            <div className="glass-card rounded-xl p-4 border border-gray-800">
              <span className="text-gray-500 block">Total Evaluated Rows</span>
              <span className="text-lg font-bold text-white">{profiling.total_rows.toLocaleString()}</span>
            </div>
            <div className="glass-card rounded-xl p-4 border border-gray-800">
              <span className="text-gray-500 block">Total Features / Columns</span>
              <span className="text-lg font-bold text-white">{profiling.total_columns}</span>
            </div>
            <div className="glass-card rounded-xl p-4 border border-gray-800">
              <span className="text-gray-500 block">Missing Cells Count</span>
              <span className={`text-lg font-bold ${profiling.missing_cells_count > 0 ? 'text-amber-400' : 'text-emerald-400'}`}>
                {profiling.missing_cells_count.toLocaleString()}
              </span>
            </div>
            <div className="glass-card rounded-xl p-4 border border-gray-800">
              <span className="text-gray-500 block">Duplicate Rows</span>
              <span className={`text-lg font-bold ${profiling.duplicate_rows_count > 0 ? 'text-rose-400' : 'text-emerald-400'}`}>
                {profiling.duplicate_rows_count.toLocaleString()}
              </span>
            </div>
          </div>

          {/* Column Breakdown & Distribution Visualizer */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Column Metrics Table */}
            <div className="glass-card rounded-2xl border border-gray-800 overflow-hidden lg:col-span-2">
              <div className="p-4 border-b border-gray-800 bg-gray-900/40 flex items-center justify-between">
                <h3 className="text-xs font-mono uppercase tracking-wider text-gray-300 font-semibold">
                  Feature-Level Statistical Profiling
                </h3>
                <span className="text-[11px] font-mono text-gray-500">Click a row to inspect distribution</span>
              </div>

              <div className="overflow-x-auto max-h-[500px]">
                <table className="w-full text-left text-xs font-mono">
                  <thead className="bg-gray-900/80 sticky top-0 border-b border-gray-800 text-gray-400">
                    <tr>
                      <th className="py-2.5 px-3">Feature Name</th>
                      <th className="py-2.5 px-3">Inferred Type</th>
                      <th className="py-2.5 px-3">Null %</th>
                      <th className="py-2.5 px-3">Unique %</th>
                      <th className="py-2.5 px-3">Mean / Mode</th>
                      <th className="py-2.5 px-3">IQR Outliers</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-800/60">
                    {Object.values(profiling.column_metrics).map((col) => {
                      const isSelected = selectedColumn?.name === col.name;
                      return (
                        <tr
                          key={col.name}
                          onClick={() => setSelectedColumn(col)}
                          className={`cursor-pointer transition-colors ${
                            isSelected ? 'bg-sky-500/10 border-l-2 border-sky-400' : 'hover:bg-gray-800/30'
                          }`}
                        >
                          <td className="py-2.5 px-3 font-semibold text-white">{col.name}</td>
                          <td className="py-2.5 px-3">
                            <span className="px-1.5 py-0.5 rounded text-[10px] bg-gray-800 text-gray-300 border border-gray-700">
                              {col.inferred_type}
                            </span>
                          </td>
                          <td className="py-2.5 px-3">
                            <span className={col.null_percentage > 5 ? 'text-amber-400 font-bold' : 'text-gray-300'}>
                              {col.null_percentage}%
                            </span>
                          </td>
                          <td className="py-2.5 px-3 text-gray-300">{col.unique_percentage}%</td>
                          <td className="py-2.5 px-3 text-gray-400">
                            {col.mean_value != null ? col.mean_value.toFixed(2) : '-'}
                          </td>
                          <td className="py-2.5 px-3">
                            {col.outliers_iqr_count && col.outliers_iqr_count > 0 ? (
                              <span className="text-rose-400 font-semibold">{col.outliers_iqr_count}</span>
                            ) : (
                              <span className="text-gray-600">0</span>
                            )}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Selected Column Distribution Visualizer */}
            <div className="glass-card rounded-2xl p-5 border border-gray-800 flex flex-col justify-between">
              <div>
                <h3 className="text-xs font-mono uppercase tracking-wider text-sky-400 font-semibold mb-1 flex items-center gap-1.5">
                  <BarChart2 className="w-4 h-4" />
                  Distribution Inspector: {selectedColumn?.name || 'Select a feature'}
                </h3>
                <p className="text-[11px] text-gray-400 font-mono mb-4">
                  {selectedColumn?.inferred_type.toUpperCase()} &bull; {selectedColumn?.unique_count} distinct values
                </p>

                {selectedColumn ? (
                  <div className="space-y-4">
                    {/* Numerical Quantiles if numeric */}
                    {selectedColumn.inferred_type === 'numeric' && (
                      <div className="grid grid-cols-2 gap-2 text-xs font-mono bg-gray-900/60 p-3 rounded-xl border border-gray-800">
                        <div>
                          <span className="text-gray-500 block text-[10px]">Min:</span>
                          <span className="text-white font-bold">{selectedColumn.min_value}</span>
                        </div>
                        <div>
                          <span className="text-gray-500 block text-[10px]">Max:</span>
                          <span className="text-white font-bold">{selectedColumn.max_value}</span>
                        </div>
                        <div>
                          <span className="text-gray-500 block text-[10px]">Median (Q2):</span>
                          <span className="text-sky-400 font-bold">{selectedColumn.median_value}</span>
                        </div>
                        <div>
                          <span className="text-gray-500 block text-[10px]">Std Deviation:</span>
                          <span className="text-gray-300 font-bold">{selectedColumn.std_value}</span>
                        </div>
                      </div>
                    )}

                    {/* Chart (Histogram or Top Frequencies) */}
                    <div className="h-56 w-full pt-2">
                      {selectedColumn.histogram ? (
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart data={getHistogramData(selectedColumn)}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                            <XAxis dataKey="bin" stroke="#6b7280" fontSize={9} fontStyle="mono" tick={false} />
                            <YAxis stroke="#6b7280" fontSize={10} fontStyle="mono" />
                            <Tooltip contentStyle={{ backgroundColor: '#111827', borderColor: '#374151', fontSize: '11px' }} />
                            <Bar dataKey="count" fill="#0ea5e9" radius={[4, 4, 0, 0]} />
                          </BarChart>
                        </ResponsiveContainer>
                      ) : selectedColumn.top_frequent_values && selectedColumn.top_frequent_values.length > 0 ? (
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart data={selectedColumn.top_frequent_values} layout="vertical">
                            <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                            <XAxis type="number" stroke="#6b7280" fontSize={10} fontStyle="mono" />
                            <YAxis dataKey="value" type="category" stroke="#6b7280" fontSize={10} fontStyle="mono" width={60} />
                            <Tooltip contentStyle={{ backgroundColor: '#111827', borderColor: '#374151', fontSize: '11px' }} />
                            <Bar dataKey="count" fill="#818cf8" radius={[0, 4, 4, 0]} />
                          </BarChart>
                        </ResponsiveContainer>
                      ) : (
                        <p className="text-center text-gray-500 text-xs font-mono pt-12">No frequency data</p>
                      )}
                    </div>
                  </div>
                ) : (
                  <p className="text-xs text-gray-500 font-mono">Select a feature column to visualize distribution.</p>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </Layout>
  );
};

