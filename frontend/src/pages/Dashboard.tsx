import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Layout } from '../components/Layout';
import { StatCard } from '../components/StatCard';
import { ScoreMeter } from '../components/ScoreMeter';
import { StatusBadge } from '../components/StatusBadge';
import { api } from '../services/api';
import { DashboardMetrics } from '../types';
import {
  Database,
  AlertTriangle,
  Cpu,
  GitCompare,
  CheckCircle2,
  Sparkles,
  ArrowRight,
  TrendingUp,
  Clock,
  RefreshCw
} from 'lucide-react';
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell
} from 'recharts';

export const Dashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>('');

  const fetchMetrics = async () => {
    try {
      setLoading(true);
      const data = await api.getDashboardMetrics();
      setMetrics(data);
    } catch (err: any) {
      setError('Unable to load telemetry metrics. Please ensure backend is running.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
  }, []);

  const severityColors: Record<string, string> = {
    CRITICAL: '#f43f5e',
    HIGH: '#f59e0b',
    MEDIUM: '#0ea5e9',
    LOW: '#10b981',
  };

  const severityChartData = metrics
    ? Object.entries(metrics.incident_severity_distribution).map(([name, count]) => ({
        name,
        count,
        color: severityColors[name] || '#94a3b8',
      }))
    : [];

  return (
    <Layout title="Autonomous Observability Command Center" subtitle="Live Data Pipeline Telemetry & Machine Learning Health">
      {/* Header Controls */}
      <div className="flex items-center justify-between pb-2">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight">System Status Overview</h2>
          <p className="text-xs text-gray-400 font-mono">Continuous Data Quality, Distribution Drift & Autonomous Agents</p>
        </div>
        <button
          onClick={fetchMetrics}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 text-xs font-mono text-gray-300 transition-colors border border-gray-700"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          Refresh Metrics
        </button>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs font-mono flex items-center justify-between">
          <span>{error}</span>
          <button onClick={fetchMetrics} className="underline hover:text-white">Retry</button>
        </div>
      )}

      {/* Top Banner: Health Gauge & Core KPIs */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Overall Health Score Card */}
        <div className="glass-card rounded-2xl p-6 border border-gray-800 flex flex-col items-center justify-center text-center relative overflow-hidden">
          <div className="absolute top-3 left-4 text-[10px] font-mono text-gray-400 tracking-wider uppercase">
            Platform Quality Score
          </div>
          <div className="mt-4">
            <ScoreMeter score={metrics?.overall_health_score || 0} size="lg" />
          </div>
          <p className="mt-3 text-xs text-gray-400 text-center max-w-xs">
            Weighted across completeness, uniqueness, validity, and consistency SLA baselines.
          </p>
        </div>

        {/* Core Stat Cards */}
        <div className="lg:col-span-3 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <StatCard
            title="Monitored Datasets"
            value={metrics?.total_datasets || 0}
            icon={Database}
            colorScheme="blue"
            description="Active versioned storage items"
          />
          <StatCard
            title="Anomalies Flagged"
            value={metrics?.total_anomalies_detected || 0}
            icon={Cpu}
            colorScheme="amber"
            description="Detected by Isolation Forest & IQR"
          />
          <StatCard
            title="Drift Events"
            value={metrics?.total_drift_events || 0}
            icon={GitCompare}
            colorScheme="purple"
            description="KS-test & PSI distribution shifts"
          />
          <StatCard
            title="Active Incidents"
            value={
              metrics
                ? Object.values(metrics.incident_status_distribution).reduce((a, b) => a + b, 0) -
                  (metrics.incident_status_distribution.RESOLVED || 0)
                : 0
            }
            icon={AlertTriangle}
            colorScheme="rose"
            description="Open data pipeline SLA alerts"
          />
          <StatCard
            title="Pending Remediations"
            value={metrics?.pending_remediations || 0}
            icon={CheckCircle2}
            colorScheme="emerald"
            description="Awaiting Human-in-the-Loop review"
          />
          <div className="glass-card rounded-xl p-5 border border-sky-500/20 bg-gradient-to-br from-sky-950/30 to-indigo-950/20 flex flex-col justify-between">
            <div>
              <span className="text-[10px] font-mono text-sky-400 uppercase tracking-wider font-semibold">Autonomous AI</span>
              <h3 className="text-sm font-semibold text-white mt-1">Multi-Agent Investigation</h3>
              <p className="text-xs text-gray-400 mt-1">Deploy 6 LangGraph agents to isolate pipeline failure roots.</p>
            </div>
            <Link
              to="/investigations"
              className="mt-3 text-xs font-semibold text-sky-400 flex items-center gap-1.5 hover:underline"
            >
              <span>Launch Agent Workflow</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>
      </div>

      {/* Visual Analytics Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Trend Chart */}
        <div className="glass-card rounded-2xl p-6 border border-gray-800 lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-sky-400" />
                Data Quality Score Trajectory
              </h3>
              <p className="text-xs text-gray-400 font-mono">Historical quality evaluation trends across pipelines</p>
            </div>
          </div>
          <div className="h-64 w-full">
            {metrics?.quality_score_trends && metrics.quality_score_trends.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={metrics.quality_score_trends}>
                  <defs>
                    <linearGradient id="scoreGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.4} />
                      <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0.0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                  <XAxis dataKey="timestamp" stroke="#6b7280" fontSize={11} fontStyle="mono" />
                  <YAxis domain={[50, 100]} stroke="#6b7280" fontSize={11} fontStyle="mono" />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#111827', borderColor: '#374151', borderRadius: '8px', fontSize: '12px' }}
                  />
                  <Area type="monotone" dataKey="score" stroke="#0ea5e9" strokeWidth={2} fillOpacity={1} fill="url(#scoreGrad)" />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-gray-500 font-mono">
                No historical trends recorded yet. Ingest a dataset to begin tracking.
              </div>
            )}
          </div>
        </div>

        {/* Severity Distribution */}
        <div className="glass-card rounded-2xl p-6 border border-gray-800">
          <h3 className="text-sm font-semibold text-white flex items-center gap-2 mb-1">
            <AlertTriangle className="w-4 h-4 text-amber-400" />
            Incidents by Severity
          </h3>
          <p className="text-xs text-gray-400 font-mono mb-4">Open & investigated pipeline alerts</p>
          <div className="h-64 w-full">
            {severityChartData.some((d) => d.count > 0) ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={severityChartData} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                  <XAxis type="number" stroke="#6b7280" fontSize={11} fontStyle="mono" />
                  <YAxis dataKey="name" type="category" stroke="#6b7280" fontSize={11} fontStyle="mono" width={65} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#111827', borderColor: '#374151', borderRadius: '8px', fontSize: '12px' }}
                  />
                  <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                    {severityChartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex flex-col items-center justify-center text-center text-xs text-gray-500 font-mono">
                <CheckCircle2 className="w-8 h-8 text-emerald-500 mb-2" />
                <span>Zero active incident alerts.</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Recent Audit Trail Table */}
      <div className="glass-card rounded-2xl p-6 border border-gray-800">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-semibold text-white flex items-center gap-2">
              <Clock className="w-4 h-4 text-sky-400" />
              Real-Time Security & Remediation Audit Trail
            </h3>
            <p className="text-xs text-gray-400 font-mono">Immutable audit history of all platform operations</p>
          </div>
          <Link to="/reports" className="text-xs text-sky-400 hover:underline font-mono">
            Full Audit Logs &rarr;
          </Link>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead>
              <tr className="border-b border-gray-800 text-gray-400">
                <th className="py-2.5 px-3">Timestamp</th>
                <th className="py-2.5 px-3">Action</th>
                <th className="py-2.5 px-3">Target Entity</th>
                <th className="py-2.5 px-3">Entity ID</th>
                <th className="py-2.5 px-3">Audit Verification</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800/60">
              {metrics?.recent_audit_trail && metrics.recent_audit_trail.length > 0 ? (
                metrics.recent_audit_trail.map((log) => (
                  <tr key={log.id} className="hover:bg-gray-800/30 transition-colors">
                    <td className="py-2.5 px-3 text-gray-400">{log.timestamp}</td>
                    <td className="py-2.5 px-3">
                      <span className="px-2 py-0.5 rounded bg-gray-800 text-sky-300 border border-gray-700">
                        {log.action}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 capitalize text-gray-300">{log.entity_type}</td>
                    <td className="py-2.5 px-3 text-gray-400">#{log.entity_id}</td>
                    <td className="py-2.5 px-3">
                      <span className="text-emerald-400 font-semibold flex items-center gap-1">
                        <CheckCircle2 className="w-3.5 h-3.5" /> Verified
                      </span>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={5} className="py-6 text-center text-gray-500">
                    No recent audit events logged.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </Layout>
  );
};

