import React, { useState, useEffect } from 'react';
import './AIInsights.css';
import {
  getAISummary,
  getClosurePerformance,
  getDueCompliance,
  getPredictions,
  getTeamBenchmarking,
  getProductivityTrends,
  getSentiment
} from '../api/client';
import { Sparkles, TrendingUp, AlertTriangle, CheckCircle, Users } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts';

function AIInsights({ timeFilter = 'today' }) {
  const [summary, setSummary] = useState(null);
  const [closure, setClosure] = useState(null);
  const [compliance, setCompliance] = useState(null);
  const [predictions, setPredictions] = useState(null);
  const [teams, setTeams] = useState([]);
  const [trends, setTrends] = useState([]);
  const [sentiment, setSentiment] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, [timeFilter]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [summaryRes, closureRes, complianceRes, predictionsRes, teamsRes, trendsRes, sentimentRes] = await Promise.all([
        getAISummary(timeFilter),
        getClosurePerformance(timeFilter),
        getDueCompliance(timeFilter),
        getPredictions(timeFilter),
        getTeamBenchmarking(timeFilter),
        getProductivityTrends(timeFilter),
        getSentiment(timeFilter)
      ]);
      
      setSummary(summaryRes.data);
      setClosure(closureRes.data);
      setCompliance(complianceRes.data);
      setPredictions(predictionsRes.data);
      setTeams(teamsRes.data);
      setTrends(trendsRes.data);
      setSentiment(sentimentRes.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching AI insights:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="ai-insights-page">
        <h1 className="page-title">AI Insights</h1>
        <div className="loading-spinner">Loading AI insights...</div>
      </div>
    );
  }

  const getFilterLabel = () => {
    switch(timeFilter) {
      case 'today': return 'Today';
      case 'week': return 'This Week';
      case 'month': return 'This Month';
      case 'all': return 'All Time';
      default: return 'Today';
    }
  };

  const generateBenchmarkingInsight = (teams) => {
    if (teams.length === 0) return '';
    
    // Find "Your Team"
    const yourTeam = teams.find(t => t.name === 'Your Team');
    const topTeam = teams.find(t => t.rank === 1);
    
    if (!yourTeam) return '';
    
    if (yourTeam.rank === 1) {
      return `Congratulations! Your team ranks #1 with ${yourTeam.velocity} tasks/week velocity and ${yourTeam.efficiency}% efficiency. Keep up the excellent work!`;
    } else {
      const tasksDifference = topTeam.velocity - yourTeam.velocity;
      const efficiencyDiff = topTeam.efficiency - yourTeam.efficiency;
      
      return `Your team ranks #${yourTeam.rank} with ${tasksDifference} tasks/week behind ${topTeam.name}. ` +
             `Your velocity is ${yourTeam.velocity}/week with ${yourTeam.efficiency}% efficiency. ` +
             `Focus on ${efficiencyDiff > 5 ? 'efficiency improvements' : 'increasing velocity'} to reach #1 position.`;
    }
  };

  return (
    <div className="ai-insights-page">
      <div className="page-header">
        <h1 className="page-title">AI Insights</h1>
        <div className="filter-badge">Showing: {getFilterLabel()}</div>
      </div>

      {/* AI Summary */}
      <div className="ai-summary-card">
        <div className="summary-icon">
          <Sparkles size={24} color="#10b981" />
        </div>
        <div className="summary-content">
          <h3>AI-Powered Summary</h3>
          <p>{summary.summary}</p>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="metrics-row">
        <div className="metric-box">
          <div className="metric-icon">
            <TrendingUp size={20} color="#10b981" />
          </div>
          <div>
            <h4>Task Closure Performance</h4>
            <div className="metric-values">
              <div className="metric-item">
                <span className="label">Current Avg</span>
                <span className="value">{closure.current_avg}h</span>
              </div>
              <div className="metric-item">
                <span className="label">Previous Avg</span>
                <span className="value">{closure.previous_avg}h</span>
              </div>
            </div>
          </div>
        </div>

        <div className="metric-box">
          <div className="metric-icon">
            <AlertTriangle size={20} color="#f59e0b" />
          </div>
          <div>
            <h4>Blocked Tasks Alert</h4>
            <div className="metric-values">
              <div className="metric-item">
                <span className="label">Blocked Tasks</span>
                <span className="value danger">{closure.blocked_tasks}</span>
              </div>
              <div className="metric-item">
                <span className="label">% of Total</span>
                <span className="value">{closure.blocked_percentage}%</span>
              </div>
            </div>
          </div>
        </div>

        <div className="metric-box">
          <div className="metric-icon">
            <CheckCircle size={20} color="#3b82f6" />
          </div>
          <div>
            <h4>Due Date Compliance</h4>
            <div className="metric-values">
              <div className="metric-item">
                <span className="label">Overdue</span>
                <span className="value danger">{compliance.overdue}</span>
              </div>
              <div className="metric-item">
                <span className="label">On Time</span>
                <span className="value success">{compliance.on_time}</span>
              </div>
            </div>
          </div>
        </div>

        <div className="metric-box">
          <div className="metric-icon">
            <Users size={20} color="#8b5cf6" />
          </div>
          <div>
            <h4>In Progress Status</h4>
            <div className="metric-values">
              <div className="metric-item">
                <span className="label">Active Tasks</span>
                <span className="value">{compliance.active_tasks}</span>
              </div>
              <div className="metric-item">
                <span className="label">Avg Active Time</span>
                <span className="value">{compliance.avg_active_time}h</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Predictions */}
      <div className="predictions-card">
        <h3>Predictive Performance Analysis</h3>
        <p className="subtitle">Based on historical data patterns and current velocity</p>
        
        <div className="prediction-grid">
          <div className="prediction-item">
            <span className="pred-label">Projected Sprint Completion</span>
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: `${predictions.sprint_completion}%` }}></div>
            </div>
            <span className="pred-value">{predictions.sprint_completion}%</span>
          </div>
          
          <div className="prediction-item">
            <span className="pred-label">Next Week Workload</span>
            <span className="pred-value-large">{predictions.next_week_workload}</span>
            <span className="pred-detail">~{predictions.expected_tasks} tasks expected</span>
          </div>
          
          <div className="prediction-item">
            <span className="pred-label">Risk Level</span>
            <span className="pred-value-large success">{predictions.risk_level}</span>
            <span className="pred-detail">{predictions.risk_description}</span>
          </div>
        </div>
      </div>

      {/* Team Benchmarking */}
      <div className="benchmarking-card">
        <div className="bench-header">
          <Users size={24} color="#10b981" />
          <div>
            <h3>Team Benchmarking</h3>
            <p>AI-powered comparison across teams</p>
          </div>
        </div>

        {/* Trends Chart */}
        <div className="trends-chart">
          <h4>4-Week Productivity Trends</h4>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={trends}>
              <XAxis dataKey="week" stroke="#6b7280" />
              <YAxis stroke="#6b7280" />
              <Tooltip
                contentStyle={{ background: '#1a1a2e', border: '1px solid #2a2a3e' }}
              />
              <Legend />
              <Line type="monotone" dataKey="your_team" stroke="#60a5fa" strokeWidth={2} name="Your Team" />
              <Line type="monotone" dataKey="alpha_team" stroke="#a78bfa" strokeWidth={2} name="Alpha Team" />
              <Line type="monotone" dataKey="beta_team" stroke="#10b981" strokeWidth={2} name="Beta Team" />
              <Line type="monotone" dataKey="gamma_team" stroke="#fbbf24" strokeWidth={2} name="Gamma Team" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Team Cards */}
        <div className="team-cards-grid">
          {teams.map((team) => (
            <div key={team.name} className={`team-card ${team.rank === 1 ? 'top-rank' : ''}`}>
              {team.badge && <span className="badge">{team.badge}</span>}
              <h4>{team.name}</h4>
              <div className="team-stats">
                <div className="stat">
                  <span className="stat-label">Total Tasks</span>
                  <span className="stat-value">{team.total_tasks}</span>
                </div>
                <div className="stat">
                  <span className="stat-label">Velocity</span>
                  <span className="stat-value">{team.velocity}/wk</span>
                </div>
                <div className="stat">
                  <span className="stat-label">Efficiency</span>
                  <span className="stat-value">{team.efficiency}%</span>
                </div>
                <div className="stat">
                  <span className="stat-label">Rank</span>
                  <span className="stat-value rank">#{team.rank}</span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Insights */}
        {teams.length > 0 && (
          <div className="bench-insights">
            <Sparkles size={20} color="#10b981" />
            <div>
              <h4>Benchmarking Insights</h4>
              <p>{generateBenchmarkingInsight(teams)}</p>
            </div>
          </div>
        )}
      </div>

      {/* Sentiment Analysis */}
      <div className="sentiment-card">
        <h3>Team Communication Sentiment</h3>
        <p className="subtitle">Analyzed from commit messages and task comments</p>
        
        <div className="sentiment-bars">
          <div className="sentiment-bar">
            <span className="bar-label">Positive</span>
            <div className="bar">
              <div className="bar-fill positive" style={{ width: `${sentiment.positive}%` }}></div>
            </div>
            <span className="bar-value">{sentiment.positive}%</span>
          </div>
          
          <div className="sentiment-bar">
            <span className="bar-label">Neutral</span>
            <div className="bar">
              <div className="bar-fill neutral" style={{ width: `${sentiment.neutral}%` }}></div>
            </div>
            <span className="bar-value">{sentiment.neutral}%</span>
          </div>
          
          <div className="sentiment-bar">
            <span className="bar-label">Negative</span>
            <div className="bar">
              <div className="bar-fill negative" style={{ width: `${sentiment.negative}%` }}></div>
            </div>
            <span className="bar-value">{sentiment.negative}%</span>
          </div>
        </div>

        <div className="sentiment-insight">
          <Sparkles size={18} color="#10b981" />
          <p>{sentiment.insight}</p>
        </div>
      </div>
    </div>
  );
}

export default AIInsights;

