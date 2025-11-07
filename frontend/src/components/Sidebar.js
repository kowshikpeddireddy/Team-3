import React from 'react';
import './Sidebar.css';
import { LayoutDashboard, CheckSquare, Sparkles, MessageCircle, Settings } from 'lucide-react';

function Sidebar({ activePage, setActivePage }) {
  const menuItems = [
    { id: 'overview', icon: LayoutDashboard, label: 'Overview' },
    { id: 'tasks', icon: CheckSquare, label: 'Tasks' },
    { id: 'ai-insights', icon: Sparkles, label: 'AI Insights' },
    { id: 'queries', icon: MessageCircle, label: 'Query' },
    { id: 'settings', icon: Settings, label: 'Settings' },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-menu">
        {menuItems.map((item) => (
          <button
            key={item.id}
            className={`sidebar-item ${activePage === item.id ? 'active' : ''}`}
            onClick={() => setActivePage(item.id)}
          >
            <item.icon size={20} />
            <span>{item.label}</span>
          </button>
        ))}
      </div>
    </aside>
  );
}

export default Sidebar;

