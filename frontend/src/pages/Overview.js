import React, { useState, useEffect } from 'react';
import './Overview.css';
import { getOverview, getDistribution, getTrends, getTeamPerformance } from '../api/client';
import { PieChart, Pie, Cell, LineChart, Line, BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TrendingUp, TrendingDown, Clock } from 'lucide-react';

function Overview({ timeFilter }) {
  const [metrics, setMetrics] = useState(null);
  const [distribution, setDistribution] = useState([]);
  const [trends, setTrends] = useState([]);
  const [teamPerformance, setTeamPerformance] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
    // Auto-refresh every 10 seconds
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, [timeFilter]); // Re-fetch when filter changes

  const fetchData = async () => {
    try {
      const [metricsRes, distRes, trendsRes, teamRes] = await Promise.all([
        getOverview(timeFilter),
        getDistribution(timeFilter),
        getTrends(timeFilter),
        getTeamPerformance(timeFilter)
      ]);
      
      setMetrics(metricsRes.data);
      setDistribution(distRes.data);
      setTrends(trendsRes.data);
      setTeamPerformance(teamRes.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching overview data:', error);
      setLoading(false);
    }
  };

  const getFilterLabel = () => {
    switch(timeFilter) {
      case 'today': return 'Today';
      case 'week': return 'This Week';
      case 'month': return 'This Month';
      case 'all': return 'All Time';
      default: return 'Today';
    }
  };

  const getTrendTitle = () => {
    switch(timeFilter) {
      case 'today': return '7-Day Trend Analysis';
      case 'week': return 'Weekly Trend Analysis';
      case 'month': return '30-Day Trend Analysis';
      case 'all': return 'Trend Analysis';
      default: return 'Trend Analysis';
    }
  };

  const getClosedLabel = () => {
    switch(timeFilter) {
      case 'today': return 'Closed Today';
      case 'week': return 'Closed This Week';
      case 'month': return 'Closed This Month';
      case 'all': return 'Total Closed';
      default: return 'Closed Today';
    }
  };

  if (loading && !metrics) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading dashboard data...</p>
      </div>
    );
  }

  return (
    <div className="overview-page">
      <div className="page-header">
        <h1 className="page-title">Overview</h1>
        <div className="filter-badge">
          <span className="filter-icon">📊</span>
          <span className="filter-text">Showing: {getFilterLabel()}</span>
          {loading && <div className="filter-loading-dot"></div>}
        </div>
      </div>
      
      {loading && metrics ? (
        <div className="overlay-loading">
          <div className="loading-spinner-small"></div>
        </div>
      ) : null}
      
      {/* Metric Cards */}
      <div className="metrics-grid">
        <MetricCard
          title="Open Tasks"
          value={metrics?.open_tasks || 0}
          change={metrics?.open_change || 0}
          color="blue"
          loading={loading}
        />
        <MetricCard
          title="In Progress"
          value={metrics?.in_progress || 0}
          change={metrics?.progress_change || 0}
          color="green"
          loading={loading}
        />
        <MetricCard
          title={getClosedLabel()}
          value={metrics?.completed_today || 0}
          change={metrics?.today_change || 0}
          color="green"
          subtitle={timeFilter === 'today' ? '3:00 - 4:00 PM' : null}
          loading={loading}
        />
        <MetricCard
          title="Completion Rate"
          value={`${metrics?.completion_rate || 0}%`}
          change={metrics?.rate_change || 0}
          color="green"
          loading={loading}
        />
      </div>

      {/* Charts Row */}
      <div className="charts-row">
        {/* Task Distribution */}
        <div className="chart-card">
          <h3 className="chart-title">
            Task Distribution ({metrics?.total_tasks || 0})
            {loading && <span className="loading-text"> • Updating...</span>}
          </h3>
          <div className="pie-chart-container">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={distribution}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={2}
                  dataKey="value"
                >
                  {distribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
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
        </div>

        {/* Trend Analysis */}
        <div className="chart-card">
          <h3 className="chart-title">
            {getTrendTitle()}
            {loading && <span className="loading-text"> • Updating...</span>}
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={trends}>
              <XAxis dataKey="date" stroke="#6b7280" />
              <YAxis stroke="#6b7280" />
              <Tooltip 
                contentStyle={{ background: '#1a1a2e', border: '1px solid #2a2a3e' }}
              />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="completed" 
                stroke="#10b981" 
                strokeWidth={2}
                name="Tasks Completed"
              />
              <Line 
                type="monotone" 
                dataKey="created" 
                stroke="#60a5fa" 
                strokeWidth={2}
                name="Tasks Created"
              />
              <Line 
                type="monotone" 
                dataKey="in_progress" 
                stroke="#a78bfa" 
                strokeWidth={2}
                name="Tasks In Progress"
              />
            </LineChart>
          </ResponsiveContainer>
          <div className="trend-stats">
            <div className="stat">
              <span className="stat-label">Avg. Daily Completion</span>
              <span className="stat-value">2.4 tasks</span>
            </div>
            <div className="stat">
              <span className="stat-label">Avg. Daily Creation</span>
              <span className="stat-value">4.1 tasks</span>
            </div>
            <div className="stat">
              <span className="stat-label">Avg. In Progress</span>
              <span className="stat-value">7.6 tasks</span>
            </div>
          </div>
        </div>
      </div>

      {/* Team Performance */}
      <div className="chart-card full-width">
        <h3 className="chart-title">
          Team Performance
          {loading && <span className="loading-text"> • Updating...</span>}
        </h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={teamPerformance}>
            <XAxis dataKey="name" stroke="#6b7280" />
            <YAxis stroke="#6b7280" />
            <Tooltip 
              contentStyle={{ background: '#1a1a2e', border: '1px solid #2a2a3e' }}
            />
            <Legend />
            <Bar dataKey="completed" fill="#10b981" name="Completed" />
            <Bar dataKey="in_progress" fill="#60a5fa" name="In Progress" />
            <Bar dataKey="open" fill="#a78bfa" name="Open" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

function MetricCard({ title, value, change, color, subtitle, loading }) {
  const isPositive = change > 0;
  const isNegative = change < 0;
  
  return (
    <div className={`metric-card ${color} ${loading ? 'loading' : ''}`}>
      <div className="metric-header">
        <span className="metric-title">{title}</span>
      </div>
      <div className="metric-value">{value}</div>
      {subtitle && <div className="metric-subtitle"><Clock size={14} /> {subtitle}</div>}
      <div className={`metric-change ${isPositive ? 'positive' : isNegative ? 'negative' : ''}`}>
        {isPositive ? <TrendingUp size={14} /> : isNegative ? <TrendingDown size={14} /> : null}
        <span>{Math.abs(change)}% vs last period</span>
      </div>
    </div>
  );
}

export default Overview;


