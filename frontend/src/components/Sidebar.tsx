import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Database,
  UploadCloud,
  Activity,
  Cpu,
  GitCompare,
  Sparkles,
  AlertTriangle,
  CheckCircle2,
  FileText,
  Settings,
  ShieldCheck
} from 'lucide-react';

const navItems = [
  { path: '/', label: 'Overview Dashboard', icon: LayoutDashboard },
  { path: '/datasets', label: 'Dataset Hub', icon: Database },
  { path: '/upload', label: 'Ingest Dataset', icon: UploadCloud },
  { path: '/profiling', label: 'Quality Profiling', icon: Activity },
  { path: '/anomalies', label: 'Anomaly Explorer', icon: Cpu },
  { path: '/drift', label: 'Drift Monitoring', icon: GitCompare },
  { path: '/investigations', label: 'AI Investigation', icon: Sparkles, badge: 'Agentic' },
  { path: '/incidents', label: 'Incidents & SLAs', icon: AlertTriangle },
  { path: '/remediation', label: 'Remediation Approvals', icon: CheckCircle2, badge: 'HITL' },
  { path: '/reports', label: 'Reports & Audit', icon: FileText },
  { path: '/settings', label: 'Platform Settings', icon: Settings },
];

export const Sidebar: React.FC = () => {
  return (
    <aside className="w-64 bg-[#0d1322] border-r border-gray-800 flex flex-col h-screen fixed left-0 top-0 z-30 select-none">
      {/* Platform Branding */}
      <div className="p-5 flex items-center gap-3 border-b border-gray-800/80">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-sky-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-sky-500/20">
          <ShieldCheck className="w-6 h-6 text-white" />
        </div>
        <div>
          <div className="font-bold text-base tracking-wide text-white flex items-center gap-1.5">
            DataSentinel <span className="text-sky-400 font-mono text-xs px-1.5 py-0.5 rounded bg-sky-950/80 border border-sky-800/50">AI</span>
          </div>
          <p className="text-xs text-gray-400 font-mono">Autonomous Observability</p>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        <div className="text-[10px] font-mono tracking-wider text-gray-400 uppercase px-3 mb-2 font-semibold">
          Platform Navigation
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center justify-between px-3.5 py-2.5 rounded-lg text-xs font-medium transition-all ${
                  isActive
                    ? 'bg-sky-500/10 text-sky-400 border border-sky-500/30 font-semibold'
                    : 'text-gray-300 hover:text-white hover:bg-gray-800/50'
                }`
              }
            >
              <div className="flex items-center gap-3">
                <Icon className="w-4 h-4 shrink-0" />
                <span>{item.label}</span>
              </div>
              {item.badge && (
                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-sky-500/20 text-sky-300 border border-sky-500/30">
                  {item.badge}
                </span>
              )}
            </NavLink>
          );
        })}
      </nav>

      {/* Footer Info */}
      <div className="p-4 border-t border-gray-800 text-[11px] text-gray-400 flex items-center justify-between">
        <span className="flex items-center gap-1.5 font-mono">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          Engine Online
        </span>
        <span className="font-mono text-gray-400">v1.0.0</span>
      </div>
    </aside>
  );
};

