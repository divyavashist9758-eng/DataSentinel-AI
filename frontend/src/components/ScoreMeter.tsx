import React from 'react';

interface ScoreMeterProps {
  score: number;
  size?: 'sm' | 'md' | 'lg';
  label?: string;
}

export const ScoreMeter: React.FC<ScoreMeterProps> = ({
  score,
  size = 'md',
  label = 'Quality Score',
}) => {
  const clampedScore = Math.max(0, Math.min(100, Math.round(score * 10) / 10));

  let color = 'text-emerald-400 stroke-emerald-500';
  let bgColor = 'text-emerald-950/40';
  let badgeColor = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
  let statusText = 'EXCELLENT';

  if (clampedScore < 70) {
    color = 'text-rose-400 stroke-rose-500';
    bgColor = 'text-rose-950/40';
    badgeColor = 'bg-rose-500/10 text-rose-400 border-rose-500/20';
    statusText = 'CRITICAL';
  } else if (clampedScore < 85) {
    color = 'text-amber-400 stroke-amber-500';
    bgColor = 'text-amber-950/40';
    badgeColor = 'bg-amber-500/10 text-amber-400 border-amber-500/20';
    statusText = 'DEGRADED';
  }

  const radius = size === 'sm' ? 28 : size === 'lg' ? 56 : 42;
  const strokeWidth = size === 'sm' ? 5 : size === 'lg' ? 9 : 7;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (clampedScore / 100) * circumference;
  const dimension = (radius + strokeWidth) * 2;

  return (
    <div className="flex flex-col items-center justify-center">
      <div className="relative inline-flex items-center justify-center">
        <svg width={dimension} height={dimension} className="transform -rotate-90">
          <circle
            cx={dimension / 2}
            cy={dimension / 2}
            r={radius}
            stroke="currentColor"
            strokeWidth={strokeWidth}
            className="text-gray-800"
            fill="transparent"
          />
          <circle
            cx={dimension / 2}
            cy={dimension / 2}
            r={radius}
            stroke="currentColor"
            strokeWidth={strokeWidth}
            fill="transparent"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            className={`${color} transition-all duration-1000 ease-out`}
          />
        </svg>
        <div className="absolute flex flex-col items-center justify-center">
          <span
            className={`font-mono font-bold tracking-tight ${
              size === 'sm' ? 'text-sm' : size === 'lg' ? 'text-3xl' : 'text-xl'
            } text-white`}
          >
            {clampedScore}
          </span>
          {size !== 'sm' && <span className="text-[10px] text-gray-400 font-mono">/ 100</span>}
        </div>
      </div>

      {label && <span className="mt-2 text-xs font-mono text-gray-400 uppercase tracking-wider">{label}</span>}
      <span className={`mt-1 text-[10px] font-mono px-2 py-0.5 rounded-full border ${badgeColor}`}>
        {statusText}
      </span>
    </div>
  );
};

