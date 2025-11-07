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
import { motion } from 'framer-motion';

const fadeUp = {
  initial: { opacity: 0, y: 12 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.35, ease: 'easeOut' }
};

function AIInsights() {
  const [summary, setSummary] = useState(null);
  const [closure, setClosure] = useState(null);
  const [compliance, setCompliance] = useState(null);
  const [predictions, setPredictions] = useState(null);
  const [teams, setTeams] = useState([]);
  const [trends, setTrends] = useState([]);
  const [sentiment, setSentiment] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const [
          summaryRes,
          closureRes,
          complianceRes,
          predictionsRes,
          teamsRes,
          trendsRes,
          sentimentRes
        ] = await Promise.all([
          getAISummary(),
          getClosurePerformance(),
          getDueCompliance(),
          getPredictions(),
          getTeamBenchmarking(),
          getProductivityTrends(),
          getSentiment()
        ]);

        setSummary(summaryRes.data);
        setClosure(closureRes.data);
        setCompliance(complianceRes.data);
        setPredictions(predictionsRes.data);
        setTeams(teamsRes.data);
        setTrends(trendsRes.data);
        setSentiment(sentimentRes.data);
      } catch (e) {
        console.error('Error fetching AI insights:', e);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  if (loading) return <div className="loading">Loading AI insights...</div>;

  // --- ADDED GUARD ---
  // This check prevents the crash. If loading is false but any of these
  // are still null (due to an API error), we show an error message.
  if (!summary || !closure || !compliance || !predictions || !sentiment) {
    return (
      <div className="loading">
        Error loading AI insights. Please check the console or try again.
      </div>
    );
  }
  // --- END GUARD ---

  return (
    <div className="ai-insights-page holo-bg">
      <h1 className="page-title">AI Insights</h1>

      {/* Summary */}
      <motion.div className="ai-summary-card holo-sheen" {...fadeUp}>
        <div className="summary-icon">
          <Sparkles size={24} color="#10b981" />
        </div>
        <div className="summary-content">
          <h3>AI-Powered Summary</h3>
          {/* This is now safe */}
          <p>{summary.summary}</p>
        </div>
      </motion.div>

      {/* Metric boxes */}
      <div className="metrics-row">
        {[
          {
            icon: <TrendingUp size={20} color="#10b981" />,
            title: 'Task Closure Performance',
            body: (
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
            ),
          },
          {
            icon: <AlertTriangle size={20} color="#f59e0b" />,
            title: 'Blocked Tasks',
            body: (
              <div className="metric-values">
                <div className="metric-item">
                  <span className="label">Blocked</span>
                  <span className="value danger">{closure.blocked_tasks}</span>
                </div>
                <div className="metric-item">
                  <span className="label">% of Total</span>
                  <span className="value">{closure.blocked_percentage}%</span>
                </div>
              </div>
            ),
          },
          {
            icon: <CheckCircle size={20} color="#3b82f6" />,
            title: 'Due Date Compliance',
            body: (
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
            ),
          },
          {
            icon: <Users size={20} color="#8b5cf6" />,
            title: 'In Progress',
            body: (
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
            ),
          },
        ].map((m, i) => (
          <motion.div
            key={i}
            className="metric-box holo-border"
            {...fadeUp}
            transition={{ ...fadeUp.transition, delay: 0.05 * i }}
          >
            <div className="metric-icon">{m.icon}</div>
            <div>
              <h4>{m.title}</h4>
              {m.body}
            </div>
          </motion.div>
        ))}
      </div>

      {/* Predictions */}
      <motion.div className="predictions-card holo-sheen" {...fadeUp} transition={{ duration: 0.4 }}>
        <h3>Predictive Performance Analysis</h3>
        <p className="subtitle">Based on historical data patterns and current velocity</p>

        <div className="prediction-grid">
          <div className="prediction-item">
            <span className="pred-label">Sprint Completion</span>
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: `${predictions.sprint_completion}%` }} />
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
      </motion.div>

      {/* Benchmarking */}
      <motion.div className="benchmarking-card holo-border" {...fadeUp}>
        <div className="bench-header">
          <Users size={24} color="#10b981" />
          <div>
            <h3>Team Benchmarking</h3>
            <p>AI-powered comparison across teams</p>
          </div>
        </div>

        <div className="trends-chart">
          <h4>4-Week Productivity Trends</h4>
          <div className="chart-3d-wrap">
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={trends}>
                <XAxis dataKey="week" stroke="#6b7280" />
                <YAxis stroke="#6b7280" />
                <Tooltip contentStyle={{ background: '#1a1a2e', border: '1px solid #2a2a3e' }} />
                <Legend />
                <Line type="monotone" dataKey="your_team" stroke="#60a5fa" strokeWidth={2} name="Your Team" />
                <Line type="monotone" dataKey="alpha_team" stroke="#a78bfa" strokeWidth={2} name="Alpha Team" />
                <Line type="monotone" dataKey="beta_team" stroke="#10b981" strokeWidth={2} name="Beta Team" />
                <Line type="monotone" dataKey="gamma_team" stroke="#fbbf24" strokeWidth={2} name="Gamma Team" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="team-cards-grid">
          {teams.map((team, i) => (
            <motion.div
              key={team.name}
              className={`team-card ${team.rank === 1 ? 'top-rank' : ''}`}
              {...fadeUp}
              transition={{ ...fadeUp.transition, delay: 0.04 * i }}
            >
              {team.badge && <span className="badge">{team.badge}</span>}
              <h4>{team.name}</h4>
              <div className="team-stats">
                <div className="stat"><span className="stat-label">Total Tasks</span><span className="stat-value">{team.total_tasks}</span></div>
                <div className="stat"><span className="stat-label">Velocity</span><span className="stat-value">{team.velocity}/wk</span></div>
                <div className="stat"><span className="stat-label">Efficiency</span><span className="stat-value">{team.efficiency}%</span></div>
                <div className="stat"><span className="stat-label">Rank</span><span className="stat-value rank">#{team.rank}</span></div>
              </div>
            </motion.div>
          ))}
        </div>

        <div className="bench-insights">
          <Sparkles size={20} color="#10b981" />
          <div>
            <h4>Benchmarking Insights</h4>
            <p>Your team ranks #2 with 8 tasks behind Alpha. Velocity up 22% over 4 weeks; increasing efficiency should secure #1.</p>
          </div>
        </div>
      </motion.div>

      {/* Sentiment */}
      <motion.div className="sentiment-card holo-sheen" {...fadeUp}>
        <h3>Team Communication Sentiment</h3>
        <p className="subtitle">Analyzed from commit messages and task comments</p>

        <div className="sentiment-bars">
          {['positive', 'neutral', 'negative'].map((k) => (
            <div key={k} className="sentiment-bar">
              <span className="bar-label">{k[0].toUpperCase() + k.slice(1)}</span>
              <div className="bar">
                <div className={`bar-fill ${k}`} style={{ width: `${sentiment[k]}%` }} />
              </div>
              <span className="bar-value">{sentiment[k]}%</span>
            </div>
          ))}
        </div>

        <div className="sentiment-insight">
          <Sparkles size={18} color="#10b981" />
          <p>{sentiment.insight}</p>
        </div>
      </motion.div>
    </div>
  );
}

export default AIInsights;