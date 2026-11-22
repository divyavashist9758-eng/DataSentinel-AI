import React from 'react';
import { LucideIcon } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string | number;
  change?: string;
  isPositive?: boolean;
  icon: LucideIcon;
  description?: string;
  colorScheme?: 'blue' | 'emerald' | 'amber' | 'rose' | 'purple';
}

const colorMap = {
  blue: {
    bg: 'bg-sky-500/10',
    border: 'border-sky-500/20',
    text: 'text-sky-400',
    glow: 'hover:border-sky-500/40',
  },
  emerald: {
    bg: 'bg-emerald-500/10',
    border: 'border-emerald-500/20',
    text: 'text-emerald-400',
    glow: 'hover:border-emerald-500/40',
  },
  amber: {
    bg: 'bg-amber-500/10',
    border: 'border-amber-500/20',
    text: 'text-amber-400',
    glow: 'hover:border-amber-500/40',
  },
  rose: {
    bg: 'bg-rose-500/10',
    border: 'border-rose-500/20',
    text: 'text-rose-400',
    glow: 'hover:border-rose-500/40',
  },
  purple: {
    bg: 'bg-purple-500/10',
    border: 'border-purple-500/20',
    text: 'text-purple-400',
    glow: 'hover:border-purple-500/40',
  },
};

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  change,
  isPositive,
  icon: Icon,
  description,
  colorScheme = 'blue',
}) => {
  const styles = colorMap[colorScheme];

  return (
    <div
      className={`glass-card rounded-xl p-5 border ${styles.border} ${styles.glow} transition-all duration-300 relative overflow-hidden`}
    >
      <div className="flex items-center justify-between">
        <span className="text-xs font-mono tracking-wider text-gray-400 uppercase">{title}</span>
        <div className={`p-2 rounded-lg ${styles.bg} ${styles.text}`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>

      <div className="mt-3 flex items-baseline gap-2">
        <span className="text-2xl font-bold tracking-tight text-white font-mono">{value}</span>
        {change && (
          <span
            className={`text-xs font-medium ${
              isPositive ? 'text-emerald-400' : 'text-rose-400'
            }`}
          >
            {isPositive ? '+' : ''}{change}
          </span>
        )}
      </div>

      {description && <p className="mt-1 text-xs text-gray-400 font-sans">{description}</p>}
    </div>
  );
};

