import React from 'react';
import './Navbar.css';
import { Activity, User } from 'lucide-react';

function Navbar({ timeFilter, setTimeFilter }) {
  return (
    <nav className="navbar">
      <div className="navbar-left">
        <Activity size={24} className="logo-icon" />
        <span className="logo-text">PULSEVO</span>
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

