import React from 'react';
import './Navbar.css';
import { Activity, User } from 'lucide-react';

function Navbar() {
  return (
    <nav className="navbar">
      <div className="navbar-left">
        <Activity size={24} className="logo-icon" />
        <span className="logo-text">PULSEVO</span>
      </div>
      <div className="navbar-right">
        <select className="time-selector">
          <option>Today</option>
          <option>This Week</option>
          <option>This Month</option>
        </select>
        <button className="profile-button">
          <User size={20} />
        </button>
      </div>
    </nav>
  );
}

export default Navbar;

