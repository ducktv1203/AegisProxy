import React from 'react';
import { 
  ShieldCheck, 
  ShieldAlert, 
  Activity, 
  Zap,
  ArrowUpRight
} from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import './Dashboard.css';

const data = [
  { name: '00:00', requests: 400, blocked: 24 },
  { name: '04:00', requests: 300, blocked: 10 },
  { name: '08:00', requests: 200, blocked: 5 },
  { name: '12:00', requests: 278, blocked: 38 },
  { name: '16:00', requests: 189, blocked: 40 },
  { name: '20:00', requests: 239, blocked: 25 },
  { name: '23:59', requests: 349, blocked: 15 },
];

const StatCard: React.FC<{
  title: string;
  value: string;
  change: string;
  trend: 'up' | 'down' | 'neutral';
  icon: React.ElementType;
}> = ({ title, value, change, trend, icon: Icon }) => (
  <div className="glass-panel stat-card">
    <div className="stat-header">
      <div className="stat-icon-wrapper">
        <Icon size={20} />
      </div>
      <span className="stat-change" data-trend={trend}>
        {change}
        <ArrowUpRight size={14} />
      </span>
    </div>
    <div className="stat-content">
      <h3>{value}</h3>
      <p>{title}</p>
    </div>
  </div>
);

export const Dashboard: React.FC = () => {
  return (
    <div className="dashboard">
      <header className="page-header">
        <div>
          <h2>Mission Control</h2>
          <p className="text-secondary">Real-time security monitoring</p>
        </div>
        <div className="header-actions">
          <button className="btn-primary">
            <Activity size={16} />
            Live View
          </button>
        </div>
      </header>

      <div className="stats-grid">
        <StatCard
          title="Total Requests"
          value="124.5k"
          change="+12.5%"
          trend="up"
          icon={Zap}
        />
        <StatCard
          title="Threats Blocked"
          value="1,204"
          change="+2.4%"
          trend="down"
          icon={ShieldAlert}
        />
        <StatCard
          title="PII Redacted"
          value="843"
          change="+5.1%"
          trend="up"
          icon={ShieldCheck}
        />
        <StatCard
          title="Avg Latency"
          value="142ms"
          change="-12ms"
          trend="up"
          icon={Activity}
        />
      </div>

      <div className="charts-section glass-panel">
        <div className="chart-header">
          <h3>Traffic Overview</h3>
          <div className="chart-legend">
            <span className="legend-item"><span className="dot requests"></span>Requests</span>
            <span className="legend-item"><span className="dot blocked"></span>Blocked</span>
          </div>
        </div>
        <div className="chart-container">
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={data}>
              <defs>
                <linearGradient id="colorRequests" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="colorBlocked" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#27272a" vertical={false} />
              <XAxis dataKey="name" stroke="#52525b" fontSize={12} tickLine={false} axisLine={false} />
              <YAxis stroke="#52525b" fontSize={12} tickLine={false} axisLine={false} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#111', border: '1px solid #27272a', borderRadius: '8px' }}
                itemStyle={{ color: '#fff' }}
              />
              <Area type="monotone" dataKey="requests" stroke="#3b82f6" fillOpacity={1} fill="url(#colorRequests)" strokeWidth={2} />
              <Area type="monotone" dataKey="blocked" stroke="#ef4444" fillOpacity={1} fill="url(#colorBlocked)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
