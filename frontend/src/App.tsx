import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { Dashboard } from './pages/Dashboard';
import { Datasets } from './pages/Datasets';
import { DatasetUpload } from './pages/DatasetUpload';
import { Profiling } from './pages/Profiling';
import { AnomalyExplorer } from './pages/AnomalyExplorer';
import { DriftMonitoring } from './pages/DriftMonitoring';
import { InvestigationCenter } from './pages/InvestigationCenter';
import { IncidentManagement } from './pages/IncidentManagement';
import { RemediationCenter } from './pages/RemediationCenter';
import { Reports } from './pages/Reports';
import { Settings } from './pages/Settings';

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { token, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#0b0f19] flex items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-2 border-sky-500 border-t-transparent rounded-full animate-spin"></div>
          <span className="text-xs font-mono text-gray-400">Authenticating DataSentinel session...</span>
        </div>
      </div>
    );
  }

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public Authentication Routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Protected Observability Platform Routes */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/datasets"
            element={
              <ProtectedRoute>
                <Datasets />
              </ProtectedRoute>
            }
          />
          <Route
            path="/upload"
            element={
              <ProtectedRoute>
                <DatasetUpload />
              </ProtectedRoute>
            }
          />
          <Route
            path="/profiling"
            element={
              <ProtectedRoute>
                <Profiling />
              </ProtectedRoute>
            }
          />
          <Route
            path="/anomalies"
            element={
              <ProtectedRoute>
                <AnomalyExplorer />
              </ProtectedRoute>
            }
          />
          <Route
            path="/drift"
            element={
              <ProtectedRoute>
                <DriftMonitoring />
              </ProtectedRoute>
            }
          />
          <Route
            path="/investigations"
            element={
              <ProtectedRoute>
                <InvestigationCenter />
              </ProtectedRoute>
            }
          />
          <Route
            path="/incidents"
            element={
              <ProtectedRoute>
                <IncidentManagement />
              </ProtectedRoute>
            }
          />
          <Route
            path="/remediation"
            element={
              <ProtectedRoute>
                <RemediationCenter />
              </ProtectedRoute>
            }
          />
          <Route
            path="/reports"
            element={
              <ProtectedRoute>
                <Reports />
              </ProtectedRoute>
            }
          />
          <Route
            path="/settings"
            element={
              <ProtectedRoute>
                <Settings />
              </ProtectedRoute>
            }
          />

          {/* Catch-all Fallback */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
};
export default App;

