import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { api } from '../services/api';
import { ShieldCheck, ArrowRight, Lock, User as UserIcon, Mail } from 'lucide-react';

export const Register: React.FC = () => {
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [fullName, setFullName] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('analyst');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await api.register({
        email,
        username,
        full_name: fullName,
        password,
        role,
      });
      setSuccess(true);
      setTimeout(() => navigate('/login'), 1500);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0b0f19] flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-tr from-sky-500 to-indigo-600 shadow-xl shadow-sky-500/20 mb-4">
            <ShieldCheck className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white">DataSentinel AI</h1>
          <p className="text-xs text-gray-400 font-mono mt-1">Create Account & Provision Access</p>
        </div>

        <div className="glass-card rounded-2xl p-8 border border-gray-800 shadow-2xl">
          <h2 className="text-lg font-semibold text-white mb-2">Register</h2>
          <p className="text-xs text-gray-400 mb-6">Create a new user role for data observability</p>

          {error && (
            <div className="mb-4 p-3 rounded-lg bg-rose-500/10 border border-rose-500/20 text-xs text-rose-400">
              {error}
            </div>
          )}

          {success && (
            <div className="mb-4 p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-xs text-emerald-400">
              Registration successful! Redirecting to sign in...
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-mono text-gray-300 uppercase mb-1">Email Address</label>
              <div className="relative">
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-gray-900/80 border border-gray-800 rounded-lg text-sm text-white placeholder-gray-500 focus:outline-none focus:border-sky-500 font-mono"
                  placeholder="analyst@organization.com"
                />
                <Mail className="w-4 h-4 text-gray-500 absolute right-3.5 top-3" />
              </div>
            </div>

            <div>
              <label className="block text-xs font-mono text-gray-300 uppercase mb-1">Username</label>
              <div className="relative">
                <input
                  type="text"
                  required
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-gray-900/80 border border-gray-800 rounded-lg text-sm text-white placeholder-gray-500 focus:outline-none focus:border-sky-500 font-mono"
                  placeholder="jdoe"
                />
                <UserIcon className="w-4 h-4 text-gray-500 absolute right-3.5 top-3" />
              </div>
            </div>

            <div>
              <label className="block text-xs font-mono text-gray-300 uppercase mb-1">Full Name</label>
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="w-full px-3.5 py-2.5 bg-gray-900/80 border border-gray-800 rounded-lg text-sm text-white placeholder-gray-500 focus:outline-none focus:border-sky-500"
                placeholder="Jane Doe"
              />
            </div>

            <div>
              <label className="block text-xs font-mono text-gray-300 uppercase mb-1">Password</label>
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

            <div>
              <label className="block text-xs font-mono text-gray-300 uppercase mb-1">Role</label>
              <select
                value={role}
                onChange={(e) => setRole(e.target.value)}
                className="w-full px-3.5 py-2.5 bg-gray-900/80 border border-gray-800 rounded-lg text-sm text-white focus:outline-none focus:border-sky-500 font-mono"
              >
                <option value="analyst">Data Analyst</option>
                <option value="admin">Platform Admin</option>
                <option value="viewer">Viewer (Read-only)</option>
              </select>
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
                  <span>Create Account</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          <div className="mt-6 pt-6 border-t border-gray-800/80 text-center text-xs text-gray-400">
            Already registered?{' '}
            <Link to="/login" className="text-sky-400 hover:underline font-medium">
              Sign in
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

