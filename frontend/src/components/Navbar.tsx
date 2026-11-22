import React from 'react';
import { useAuth } from '../context/AuthContext';
import { LogOut, User as UserIcon, ShieldAlert, Cpu } from 'lucide-react';

interface NavbarProps {
  title?: string;
  subtitle?: string;
}

export const Navbar: React.FC<NavbarProps> = ({ title, subtitle }) => {
  const { user, logout } = useAuth();

  return (
    <header className="h-16 bg-[#0d1322]/80 backdrop-blur-md border-b border-gray-800/80 fixed top-0 right-0 left-64 z-20 px-6 flex items-center justify-between">
      {/* Title / Context */}
      <div>
        <h1 className="text-sm font-semibold text-white tracking-wide flex items-center gap-2">
          {title || 'Autonomous Data Observability Platform'}
        </h1>
        {subtitle && <p className="text-xs text-gray-400 font-mono">{subtitle}</p>}
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-4">
        {/* System Health Status */}
        <div className="hidden md:flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-950/40 border border-emerald-800/40 text-[11px] font-mono text-emerald-400">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span>
          <span>LANGGRAPH & ML ACTIVE</span>
        </div>

        {/* User Profile & Logout */}
        {user ? (
          <div className="flex items-center gap-3 pl-3 border-l border-gray-800">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-full bg-sky-500/20 border border-sky-500/30 flex items-center justify-center text-sky-400 font-semibold text-xs">
                {user.username.slice(0, 2).toUpperCase()}
              </div>
              <div className="hidden sm:block text-left">
                <div className="text-xs font-medium text-white">{user.full_name || user.username}</div>
                <div className="text-[10px] text-gray-400 font-mono capitalize">{user.role}</div>
              </div>
            </div>

            <button
              onClick={logout}
              title="Sign Out"
              className="p-1.5 rounded-lg text-gray-400 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        ) : (
          <a
            href="/login"
            className="text-xs bg-sky-600 hover:bg-sky-500 text-white font-medium px-3.5 py-1.5 rounded-lg transition-colors"
          >
            Sign In
          </a>
        )}
      </div>
    </header>
  );
};

