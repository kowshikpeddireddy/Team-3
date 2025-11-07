import React, { useState, useEffect } from 'react';
import './Tasks.css';
import { getTasks, getUsers, getProjectStats } from '../api/client';
import { Search, Upload, TrendingUp, TrendingDown } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

function Tasks() {
  const [tasks, setTasks] = useState([]);
  const [users, setUsers] = useState([]);
  const [projectStats, setProjectStats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('All Tasks');
  const [showUpload, setShowUpload] = useState(false);

  useEffect(() => {
    fetchData();
  }, [statusFilter]);

  const fetchData = async () => {
    try {
      const filters = statusFilter !== 'All Tasks' ? { status: statusFilter } : {};
      const [tasksRes, usersRes, statsRes] = await Promise.all([
        getTasks(filters),
        getUsers(),
        getProjectStats()
      ]);
      
      setTasks(tasksRes.data);
      setUsers(usersRes.data);
      setProjectStats(statsRes.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching tasks:', error);
      setLoading(false);
    }
  };

  const filteredUsers = users.filter(user =>
    user.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Prepare project charts data
  const projectTasksData = projectStats.map((p, i) => ({
    name: p.project,
    value: p.total,
    color: ['#ec4899', '#60a5fa', '#fbbf24'][i]
  }));

  const projectIssuesData = projectStats.map((p, i) => ({
    name: p.project,
    value: p.open,
    color: ['#ec4899', '#60a5fa', '#fbbf24'][i]
  }));

  if (loading) {
    return <div className="loading">Loading tasks...</div>;
  }

  return (
    <div className="tasks-page">
      <div className="tasks-header">
        <h1 className="page-title">Tasks</h1>
        <button className="upload-button" onClick={() => setShowUpload(!showUpload)}>
          <Upload size={18} />
          Upload
        </button>
      </div>

      {showUpload && (
        <div className="upload-modal">
          <div className="upload-content">
            <h3>Upload Files</h3>
            <div className="upload-area">
              <Upload size={48} color="#60a5fa" />
              <p>Drag and drop files here, or click to browse</p>
              <p className="upload-hint">PDF, DOCX, JPG, PNG up to 10MB each</p>
              <button className="browse-button">Browse Files</button>
            </div>
            <button className="close-upload" onClick={() => setShowUpload(false)}>Close</button>
          </div>
        </div>
      )}

      <div className="tasks-content">
        {/* Left Section - Task Management */}
        <div className="tasks-left">
          <div className="task-management-card">
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
                <option>All Tasks</option>
                <option>Open</option>
                <option>In Progress</option>
                <option>Completed</option>
                <option>Blocked</option>
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
                {filteredUsers.map((user) => (
                  <div key={user.user_id} className="table-row">
                    <div className="td name">
                      <div className="user-avatar" style={{
                        background: getAvatarColor(user.initials)
                      }}>
                        {user.initials}
                      </div>
                      <span>{user.name}</span>
                    </div>
                    <div className="td">{user.assigned}</div>
                    <div className="td">
                      <span className="badge badge-success">{user.completed}</span>
                    </div>
                    <div className="td">
                      <span className="badge badge-info">{user.in_progress}</span>
                    </div>
                    <div className="td trend">
                      {user.trend > 50 ? (
                        <span className="trend-up">
                          <TrendingUp size={14} /> {user.completion_percentage}%
                        </span>
                      ) : user.trend === 0 ? (
                        <span className="trend-neutral">— {user.completion_percentage}%</span>
                      ) : (
                        <span className="trend-down">
                          <TrendingDown size={14} /> {user.completion_percentage}%
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="pagination">
              <button className="page-btn">Previous</button>
              <button className="page-btn active">1</button>
              <button className="page-btn">2</button>
              <button className="page-btn">Next</button>
            </div>
          </div>
        </div>

        {/* Right Section - Charts */}
        <div className="tasks-right">
          {/* Tasks by Project */}
          <div className="project-chart-card">
            <h3 className="chart-title">Tasks by Project</h3>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={projectTasksData}
                  cx="50%"
                  cy="50%"
                  innerRadius={40}
                  outerRadius={80}
                  dataKey="value"
                >
                  {projectTasksData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            <div className="chart-legend">
              {projectTasksData.map((item, i) => (
                <div key={i} className="legend-item">
                  <div className="legend-dot" style={{ background: item.color }}></div>
                  <span>{item.name}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Open Issues by Project */}
          <div className="project-chart-card">
            <h3 className="chart-title">Open Issues by Project</h3>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={projectIssuesData}
                  cx="50%"
                  cy="50%"
                  innerRadius={40}
                  outerRadius={80}
                  dataKey="value"
                >
                  {projectIssuesData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            <div className="chart-legend">
              {projectIssuesData.map((item, i) => (
                <div key={i} className="legend-item">
                  <div className="legend-dot" style={{ background: item.color }}></div>
                  <span>{item.name}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function getAvatarColor(initials) {
  const colors = [
    'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
    'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
  ];
  const hash = initials.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
  return colors[hash % colors.length];
}

export default Tasks;

