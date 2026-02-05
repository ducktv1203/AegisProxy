import React, { useEffect, useState } from 'react';
import { 
  ShieldCheck, 
  ShieldAlert, 
  Activity, 
  Zap,
  ArrowUpRight
} from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { fetchDashboardStats, type DashboardStats, type ChartDataPoint } from '../services/api';
import './Dashboard.css';

const StatCard: React.FC<{
  title: string;
  value: string | number;
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
  const [stats, setStats] = useState<DashboardStats>({
    total_requests: 0,
    blocked_requests: 0,
    pii_detected: 0,
    injection_detected: 0,
    start_time: new Date().toISOString()
  });
  const [chartData, setChartData] = useState<ChartDataPoint[]>([]);

  useEffect(() => {
    const loadData = async () => {
        const data = await fetchDashboardStats();
        setStats(data.summary);
        setChartData(data.chart_data);
    };

    loadData();
    // Poll every 5 seconds
    const interval = setInterval(loadData, 5000);
    return () => clearInterval(interval);
  }, []);

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
            Live View {stats.total_requests > 0 && <span className="badge">LIVE</span>}
          </button>
        </div>
      </header>

      <div className="stats-grid">
        <StatCard
          title="Total Requests"
          value={stats.total_requests}
          change="~"
          trend="neutral"
          icon={Zap}
        />
        <StatCard
          title="Threats Blocked"
          value={stats.blocked_requests}
          change={`${stats.total_requests > 0 ? ((stats.blocked_requests / stats.total_requests) * 100).toFixed(1) : 0}%`}
          trend={stats.blocked_requests > 0 ? "down" : "neutral"}
          icon={ShieldAlert}
        />
        <StatCard
          title="PII Detected"
          value={stats.pii_detected}
          change="~"
          trend="up"
          icon={ShieldCheck}
        />
        <StatCard
          title="Injection Attempts"
          value={stats.injection_detected}
          change="~"
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
            <AreaChart data={chartData.length > 0 ? chartData : [{time: 'Now', requests: 0, blocked: 0}]}>
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
              <XAxis dataKey="time" stroke="#52525b" fontSize={12} tickLine={false} axisLine={false} />
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
