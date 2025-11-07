import React from 'react';
import './Navbar.css';
import { Activity, User } from 'lucide-react';

function Navbar({ timeFilter, setTimeFilter, activePage, setActivePage }) {
  const navItems = [
    { id: 'overview', label: 'Overview' },
    { id: 'tasks', label: 'Tasks' },
    { id: 'ai-insights', label: 'AI Insights' },
    { id: 'queries', label: 'Query' },
    { id: 'settings', label: 'Settings' },
  ];

  return (
    <nav className="navbar">
      <div className="navbar-left">
        <div className="logo-container">
          <Activity size={24} className="logo-icon" />
          <span className="logo-text">PULSEVO</span>
        </div>
        
        <div className="nav-tabs">
          {navItems.map((item) => (
            <button
              key={item.id}
              className={`nav-tab ${activePage === item.id ? 'active' : ''}`}
              onClick={() => setActivePage(item.id)}
            >
              {item.label}
            </button>
          ))}
        </div>
      </div>

      <div className="navbar-right">
        <select 
          className="time-selector"
          value={timeFilter}
          onChange={(e) => setTimeFilter(e.target.value)}
        >
          <option value="today">Today</option>
          <option value="week">This Week</option>
          <option value="month">This Month</option>
          <option value="all">All Time</option>
        </select>
        <button className="profile-button">
          <User size={20} />
        </button>
      </div>
    </nav>
  );
}

export default Navbar;

