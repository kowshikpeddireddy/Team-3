import React, { useState, useEffect } from 'react';
import './Overview.css';
import { getOverview, getDistribution, getTrends, getTeamPerformance } from '../api/client';
import {
  PieChart, Pie, Cell,
  LineChart, Line,
  BarChart, Bar,
  XAxis, YAxis, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import { TrendingUp, TrendingDown, Clock } from 'lucide-react';
import { motion } from 'framer-motion';

const fade = { initial: { opacity: 0, y: 10 }, animate: { opacity: 1, y: 0 }, transition: { duration: 0.3, ease: 'easeOut' } };

function Overview() {
  const [metrics, setMetrics] = useState(null);
  const [distribution, setDistribution] = useState([]);
  const [trends, setTrends] = useState([]);
  const [teamPerformance, setTeamPerformance] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const [m, d, t, tp] = await Promise.all([
          getOverview(),
          getDistribution(),
          getTrends(),
          getTeamPerformance()
        ]);
        setMetrics(m.data);
        setDistribution(d.data);
        setTrends(t.data);
        setTeamPerformance(tp.data);
      } catch (e) {
        console.error('Overview fetch error:', e);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  if (loading) return <div className="loading">Loading dashboard...</div>;

  return (
    <div className="overview-page holo-bg">
      <h1 className="page-title">Overview</h1>

      <div className="metrics-grid">
        {[
          { title: 'Open Tasks', value: metrics.open_tasks, change: metrics.open_change, color: 'blue' },
          { title: 'In Progress', value: metrics.in_progress, change: metrics.progress_change, color: 'green' },
          { title: 'Closed Today', value: metrics.completed_today, change: metrics.today_change, color: 'green', subtitle: '3:00 - 4:00 PM' },
          { title: 'Completion Rate', value: `${metrics.completion_rate}%`, change: metrics.rate_change, color: 'green' },
        ].map((m, i) => (
          <motion.div key={m.title} className={`metric-card ${m.color}`} {...fade} transition={{ ...fade.transition, delay: i * 0.04 }}>
            <div className="metric-header"><span className="metric-title">{m.title}</span></div>
            <div className="metric-value">{m.value}</div>
            {m.subtitle && <div className="metric-subtitle"><Clock size={14} /> {m.subtitle}</div>}
            <div className={`metric-change ${m.change > 0 ? 'positive' : m.change < 0 ? 'negative' : ''}`}>
              {m.change > 0 ? <TrendingUp size={14} /> : m.change < 0 ? <TrendingDown size={14} /> : null}
              <span>{Math.abs(m.change)}% vs last week</span>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="charts-row">
        <motion.div className="chart-card holo-sheen" {...fade}>
          <h3 className="chart-title">Task Distribution ({metrics.total_tasks})</h3>
          <div className="pie-chart-container">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie data={distribution} cx="50%" cy="50%" innerRadius={60} outerRadius={100} paddingAngle={2} dataKey="value">
                  {distribution.map((entry, index) => <Cell key={`cell-${index}`} fill={entry.color} />)}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            <div className="pie-legend">
              {distribution.map((item, index) => (
                <div key={index} className="pie-legend-item">
                  <div className="legend-color" style={{ background: item.color }}></div>
                  <span>{item.name}: {item.value}</span>
                </div>
              ))}
            </div>
          </div>
        </motion.div>

        <motion.div className="chart-card holo-sheen" {...fade} transition={{ ...fade.transition, delay: 0.05 }}>
          <h3 className="chart-title">7-Day Trend Analysis</h3>
          <div className="chart-3d-wrap">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={trends}>
                <XAxis dataKey="date" stroke="#6b7280" />
                <YAxis stroke="#6b7280" />
                <Tooltip contentStyle={{ background: '#1a1a2e', border: '1px solid #2a2a3e' }} />
                <Legend />
                <Line type="monotone" dataKey="completed" stroke="#10b981" strokeWidth={2} name="Tasks Completed" />
                <Line type="monotone" dataKey="created" stroke="#60a5fa" strokeWidth={2} name="Tasks Created" />
                <Line type="monotone" dataKey="in_progress" stroke="#a78bfa" strokeWidth={2} name="Tasks In Progress" />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <div className="trend-stats">
            <div className="stat"><span className="stat-label">Avg. Daily Completion</span><span className="stat-value">2.4</span></div>
            <div className="stat"><span className="stat-label">Avg. Daily Creation</span><span className="stat-value">4.1</span></div>
            <div className="stat"><span className="stat-label">Avg. In Progress</span><span className="stat-value">7.6</span></div>
          </div>
        </motion.div>
      </div>

      <motion.div className="chart-card full-width holo-sheen" {...fade}>
        <h3 className="chart-title">Team Performance</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={teamPerformance}>
            <XAxis dataKey="name" stroke="#6b7280" />
            <YAxis stroke="#6b7280" />
            <Tooltip contentStyle={{ background: '#1a1a2e', border: '1px solid #2a2a3e' }} />
            <Legend />
            <Bar dataKey="completed" fill="#10b981" name="Completed" />
            <Bar dataKey="in_progress" fill="#60a5fa" name="In Progress" />
            <Bar dataKey="open" fill="#a78bfa" name="Open" />
          </BarChart>
        </ResponsiveContainer>
      </motion.div>
    </div>
  );
}

export default Overview;