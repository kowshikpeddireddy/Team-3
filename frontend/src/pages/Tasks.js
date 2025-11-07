import React, { useState, useEffect } from 'react';
import './Tasks.css';
import { getTasks, getUsers, getProjectStats } from '../api/client';
import { Search, Upload, TrendingUp, TrendingDown } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { motion } from 'framer-motion';

function Tasks() {
  const [tasks, setTasks] = useState([]);
  const [users, setUsers] = useState([]);
  const [projectStats, setProjectStats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('All Tasks');
  const [showUpload, setShowUpload] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    let isCancelled = false;

    (async () => {
      setLoading(true);
      setError(null);
      try {
        const filters = statusFilter !== 'All Tasks' ? { status: statusFilter } : {};
        const [tasksRes, usersRes, statsRes] = await Promise.all([
          getTasks(filters),
          getUsers(),
          getProjectStats(),
        ]);

        if (isCancelled) return;

        setTasks(Array.isArray(tasksRes?.data) ? tasksRes.data : []);
        setUsers(Array.isArray(usersRes?.data) ? usersRes.data : []);
        setProjectStats(Array.isArray(statsRes?.data) ? statsRes.data : []);
      } catch (err) {
        if (!isCancelled) setError('Failed to load data');
        // eslint-disable-next-line no-console
        console.error('Error fetching tasks:', err);
      } finally {
        if (!isCancelled) setLoading(false);
      }
    })();

    return () => { isCancelled = true; };
  }, [statusFilter]);

  const filteredUsers = users
    .filter((u) => (u?.name || '').toLowerCase().includes(searchTerm.toLowerCase()));

  const palette = ['#ec4899', '#60a5fa', '#fbbf24', '#34d399', '#a78bfa', '#f87171', '#22d3ee'];

  const projectTasksData = projectStats.map((p, i) => ({
    name: p?.project ?? `Project ${i + 1}`,
    value: Number.isFinite(+p?.total) ? +p.total : 0,
    color: palette[i % palette.length],
  }));

  const projectIssuesData = projectStats.map((p, i) => ({
    name: p?.project ?? `Project ${i + 1}`,
    value: Number.isFinite(+p?.open) ? +p.open : 0,
    color: palette[i % palette.length],
  }));

  const handleTilt = (e) => {
    const el = e.currentTarget;
    const r = el.getBoundingClientRect();
    const x = (e.clientX - r.left) / r.width;
    const y = (e.clientY - r.top) / r.height;
    el.style.transform = `perspective(1000px) rotateX(${(0.5 - y) * 8}deg) rotateY(${(x - 0.5) * 8}deg)`;
  };
  const resetTilt = (e) => { e.currentTarget.style.transform = ''; };

  if (loading) return <div className="loading">Loading tasks...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="tasks-page holo-bg">
      <div className="tasks-header">
        <h1 className="page-title">Tasks</h1>
        <motion.button
          className="upload-button"
          onClick={() => setShowUpload((v) => !v)}
          whileTap={{ scale: 0.96 }}
          whileHover={{ scale: 1.02 }}
        >
          <Upload size={18} />
          Upload
        </motion.button>
      </div>

      {showUpload && (
        <div className="upload-modal">
          <motion.div
            className="upload-content holo-border"
            initial={{ opacity: 0, scale: 0.96, y: 10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            transition={{ duration: 0.25 }}
          >
            <h3>Upload Files</h3>
            <div className="upload-area" role="button" tabIndex={0}>
              <Upload size={48} color="#60a5fa" />
              <p>Drag and drop files here, or click to browse</p>
              <p className="upload-hint">PDF, DOCX, JPG, PNG up to 10MB each</p>
              <button className="browse-button">Browse Files</button>
            </div>
            <button className="close-upload" onClick={() => setShowUpload(false)}>Close</button>
          </motion.div>
        </div>
      )}

      <div className="tasks-content">
        {/* Left Section - Task Management */}
        <motion.div
          className="tasks-left"
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45 }}
        >
          <div className="task-management-card holo-border tilt" onMouseMove={handleTilt} onMouseLeave={resetTilt}>
            <h2 className="card-title">Task Management</h2>

            <div className="task-filters">
              <div className="search-box">
                <Search size={18} />
                <input
                  type="text"
                  placeholder="Search Name..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>

              <select
                className="status-filter"
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
              >
                <option value="All Tasks">All Tasks</option>
                <option value="Open">Open</option>
                <option value="In Progress">In Progress</option>
                <option value="Completed">Completed</option>
                <option value="Blocked">Blocked</option>
              </select>
            </div>

            <div className="users-table">
              <div className="table-header">
                <div className="th name">Name</div>
                <div className="th">Assigned</div>
                <div className="th">Completed</div>
                <div className="th">Ongoing</div>
                <div className="th">Trend</div>
              </div>

              <div className="table-body">
                {filteredUsers.map((user) => {
                  const initials = getInitials(user?.name) || (user?.initials ?? '');
                  const assigned = toInt(user?.assigned);
                  const completed = toInt(user?.completed);
                  const inProgress = toInt(user?.in_progress);
                  const completionPct =
                    Number.isFinite(user?.completion_percentage)
                      ? user.completion_percentage
                      : calcCompletionPct(completed, assigned);

                  return (
                    <motion.div
                      key={user?.user_id ?? user?.id ?? user?.name}
                      className="table-row"
                      initial={{ opacity: 0, y: 10 }}
                      whileInView={{ opacity: 1, y: 0 }}
                      viewport={{ once: true, amount: 0.2 }}
                      transition={{ duration: 0.25 }}
                    >
                      <div className="td name">
                        <div
                          className="user-avatar"
                          style={{ background: getAvatarColor(initials) }}
                          aria-label={`Avatar for ${user?.name}`}
                        >
                          {initials}
                        </div>
                        <span>{user?.name ?? 'Unknown'}</span>
                      </div>
                      <div className="td">{assigned}</div>
                      <div className="td">
                        <span className="badge badge-success">{completed}</span>
                      </div>
                      <div className="td">
                        <span className="badge badge-info">{inProgress}</span>
                      </div>
                      <div className="td trend">
                        {toInt(user?.trend) > 50 ? (
                          <span className="trend-up">
                            <TrendingUp size={14} /> {completionPct}%
                          </span>
                        ) : toInt(user?.trend) === 0 ? (
                          <span className="trend-neutral">— {completionPct}%</span>
                        ) : (
                          <span className="trend-down">
                            <TrendingDown size={14} /> {completionPct}%
                          </span>
                        )}
                      </div>
                    </motion.div>
                  );
                })}
              </div>
            </div>

            <div className="pagination">
              <button className="page-btn">Previous</button>
              <button className="page-btn active">1</button>
              <button className="page-btn">2</button>
              <button className="page-btn">Next</button>
            </div>
          </div>
        </motion.div>

        {/* Right Section - Charts */}
        <div className="tasks-right">
          {/* Tasks by Project */}
          <motion.div
            className="project-chart-card tilt holo-sheen"
            onMouseMove={handleTilt}
            onMouseLeave={resetTilt}
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.2 }}
            transition={{ duration: 0.45 }}
          >
            <h3 className="chart-title">Tasks by Project</h3>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie data={projectTasksData} cx="50%" cy="50%" innerRadius={40} outerRadius={80} dataKey="value" nameKey="name">
                  {projectTasksData.map((entry, index) => (
                    <Cell key={`tasks-cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            <div className="chart-legend">
              {projectTasksData.map((item, i) => (
                <div key={`tasks-legend-${i}`} className="legend-item">
                  <div className="legend-dot" style={{ background: item.color }} />
                  <span>{item.name}</span>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Open Issues by Project */}
          <motion.div
            className="project-chart-card tilt holo-sheen"
            onMouseMove={handleTilt}
            onMouseLeave={resetTilt}
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.2 }}
            transition={{ duration: 0.45, delay: 0.05 }}
          >
            <h3 className="chart-title">Open Issues by Project</h3>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie data={projectIssuesData} cx="50%" cy="50%" innerRadius={40} outerRadius={80} dataKey="value" nameKey="name">
                  {projectIssuesData.map((entry, index) => (
                    <Cell key={`issues-cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            <div className="chart-legend">
              {projectIssuesData.map((item, i) => (
                <div key={`issues-legend-${i}`} className="legend-item">
                  <div className="legend-dot" style={{ background: item.color }} />
                  <span>{item.name}</span>
                </div>
              ))}
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}

// --- Helpers ---
function getInitials(name) {
  if (!name || typeof name !== 'string') return '';
  const parts = name.trim().split(/\s+/).slice(0, 2);
  return parts.map((p) => p[0]?.toUpperCase() ?? '').join('');
}

function toInt(v) {
  const n = parseInt(v, 10);
  return Number.isFinite(n) ? n : 0;
}

function calcCompletionPct(completed, assigned) {
  if (!assigned) return 0;
  const pct = Math.round((completed / assigned) * 100);
  return Number.isFinite(pct) ? pct : 0;
}

function getAvatarColor(initials) {
  const colors = [
    'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
    'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
  ];
  const safe = initials || 'AA';
  const hash = safe.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
  return colors[hash % colors.length];
}

export default Tasks;