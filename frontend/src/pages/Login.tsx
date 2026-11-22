import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';
import { ShieldCheck, ArrowRight, Lock, User as UserIcon } from 'lucide-react';

export const Login: React.FC = () => {
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('admin123');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const data = await api.login({ username_or_email: username, password });
      login(data.access_token, data.user);
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Authentication failed. Please check credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0b0f19] flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Brand Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-tr from-sky-500 to-indigo-600 shadow-xl shadow-sky-500/20 mb-4">
            <ShieldCheck className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white">DataSentinel AI</h1>
          <p className="text-xs text-gray-400 font-mono mt-1">Autonomous Observability & Data Intelligence</p>
        </div>

        {/* Login Card */}
        <div className="glass-card rounded-2xl p-8 border border-gray-800 shadow-2xl">
          <h2 className="text-lg font-semibold text-white mb-2">Sign In</h2>
          <p className="text-xs text-gray-400 mb-6">Enter platform credentials to access telemetry</p>

          {error && (
            <div className="mb-4 p-3 rounded-lg bg-rose-500/10 border border-rose-500/20 text-xs text-rose-400">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-mono text-gray-300 uppercase mb-1.5">Username or Email</label>
              <div className="relative">
                <input
                  type="text"
                  required
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-gray-900/80 border border-gray-800 rounded-lg text-sm text-white placeholder-gray-500 focus:outline-none focus:border-sky-500 font-mono"
                  placeholder="admin"
                />
                <UserIcon className="w-4 h-4 text-gray-500 absolute right-3.5 top-3" />
              </div>
            </div>

            <div>
              <label className="block text-xs font-mono text-gray-300 uppercase mb-1.5">Password</label>
              <div className="relative">
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-gray-900/80 border border-gray-800 rounded-lg text-sm text-white placeholder-gray-500 focus:outline-none focus:border-sky-500 font-mono"
                  placeholder="••••••••"
                />
                <Lock className="w-4 h-4 text-gray-500 absolute right-3.5 top-3" />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full mt-2 py-2.5 bg-sky-600 hover:bg-sky-500 text-white rounded-lg text-sm font-semibold flex items-center justify-center gap-2 transition-colors disabled:opacity-50"
            >
              {loading ? (
                <div className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin" />
              ) : (
                <>
                  <span>Sign In</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          <div className="mt-6 pt-6 border-t border-gray-800/80 text-center text-xs text-gray-400">
            Don't have an account?{' '}
            <Link to="/register" className="text-sky-400 hover:underline font-medium">
              Register here
            </Link>
          </div>
        </div>

        {/* Demo Credentials Hint */}
        <div className="mt-4 p-3 rounded-xl bg-gray-900/60 border border-gray-800 text-center text-xs text-gray-400 font-mono">
          Demo Admin: <span className="text-sky-300">admin</span> / <span className="text-sky-300">admin123</span>
        </div>
      </div>
    </div>
  );
};

