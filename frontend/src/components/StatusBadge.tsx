import React from 'react';

interface StatusBadgeProps {
  status: string;
  type?: 'status' | 'severity' | 'risk';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, type = 'status' }) => {
  const norm = (status || '').toUpperCase();

  let styles = 'bg-gray-800 text-gray-300 border-gray-700';

  if (type === 'severity') {
    if (norm === 'CRITICAL') styles = 'bg-rose-500/10 text-rose-400 border-rose-500/30';
    else if (norm === 'HIGH') styles = 'bg-amber-500/10 text-amber-400 border-amber-500/30';
    else if (norm === 'MEDIUM') styles = 'bg-sky-500/10 text-sky-400 border-sky-500/30';
    else if (norm === 'LOW') styles = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
  } else if (type === 'risk') {
    if (norm === 'HIGH') styles = 'bg-rose-500/10 text-rose-400 border-rose-500/30';
    else if (norm === 'MEDIUM') styles = 'bg-amber-500/10 text-amber-400 border-amber-500/30';
    else styles = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
  } else {
    // General status
    if (norm === 'OPEN' || norm === 'PENDING') styles = 'bg-amber-500/10 text-amber-400 border-amber-500/30';
    else if (norm === 'INVESTIGATING' || norm === 'RUNNING') styles = 'bg-sky-500/10 text-sky-400 border-sky-500/30';
    else if (norm === 'APPROVED' || norm === 'RESOLVED' || norm === 'COMPLETED' || norm === 'HEALTHY')
      styles = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
    else if (norm === 'REJECTED' || norm === 'FAILED' || norm === 'CRITICAL')
      styles = 'bg-rose-500/10 text-rose-400 border-rose-500/30';
    else if (norm === 'EXECUTED')
      styles = 'bg-indigo-500/10 text-indigo-400 border-indigo-500/30';
  }

  return (
    <span className={`inline-flex items-center text-[10px] font-mono px-2 py-0.5 rounded-full border ${styles} uppercase tracking-wider font-semibold`}>
      {status}
    </span>
  );
};

