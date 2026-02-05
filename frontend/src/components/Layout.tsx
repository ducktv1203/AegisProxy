import { LucideIcon } from 'lucide-react';
import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { Shield, Activity, Settings, FileText, Lock } from 'lucide-react';
import './Layout.css';

interface SidebarItemProps {
  icon: LucideIcon;
  label: string;
  to: string;
}

const SidebarItem: React.FC<SidebarItemProps> = ({ icon: Icon, label, to }) => {
  const location = useLocation();
  const isActive = location.pathname === to;

  return (
    <NavLink to={to} className={`sidebar-item ${isActive ? 'active' : ''}`}>
      <Icon size={20} />
      <span>{label}</span>
      {isActive && <div className="active-indicator" />}
    </NavLink>
  );
};

export const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="logo-container">
          <Shield className="logo-icon" size={32} />
          <div className="logo-text">
            <h1>Aegis</h1>
            <span className="badge">PROXY</span>
          </div>
        </div>

        <nav className="nav-menu">
          <SidebarItem icon={Activity} label="Dashboard" to="/" />
          <SidebarItem icon={FileText} label="Live Logs" to="/logs" />
          <SidebarItem icon={Lock} label="Security Rules" to="/rules" />
          <SidebarItem icon={Settings} label="Configuration" to="/config" />
        </nav>

        <div className="status-container">
          <div className="status-item">
            <div className="status-dot online" />
            <span>System Operational</span>
          </div>
        </div>
      </aside>
      <main className="main-content">
        {children}
      </main>
    </div>
  );
};
