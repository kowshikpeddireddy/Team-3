import React, { useState, useEffect, useRef } from 'react';
import './Tasks.css';
import { getTasks, getUsers, getProjectStats, getTaskStatusCounts, uploadTasksCSV } from '../api/client';
import { Search, Upload, TrendingUp, TrendingDown, CheckCircle, Clock, AlertCircle, XCircle } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

function Tasks() {
  const [users, setUsers] = useState([]);
  const [projectStats, setProjectStats] = useState([]);
  const [statusCounts, setStatusCounts] = useState({
    all: 0,
    open: 0,
    in_progress: 0,
    completed: 0,
    blocked: 0
  });
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('All Tasks');
  const [currentPage, setCurrentPage] = useState(1);
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState(null);
  const fileInputRef = useRef(null);
  const usersPerPage = 10;

  useEffect(() => {
    fetchData();
  }, [statusFilter]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const filters = statusFilter !== 'All Tasks' ? { status: statusFilter } : {};
      const [tasksRes, usersRes, statsRes, countsRes] = await Promise.all([
        getTasks({ ...filters, page: 1, per_page: 2000 }), // Get all filtered tasks to calculate stats
        getUsers(),
        getProjectStats(),
        getTaskStatusCounts()
      ]);
      
      // Merge users with their task stats (from FILTERED tasks)
      const fetchedUsers = usersRes.data;
      const usersStats = tasksRes.data.users_stats || {};
      
      // Only include users who have tasks in the filtered set
      const mergedUsers = fetchedUsers
        .map(user => {
          const stats = usersStats[user.user_id] || {
            assigned: 0,
            completed: 0,
            in_progress: 0,
            open: 0
          };
          
          const assigned = stats.assigned;
          const completed = stats.completed;
          const inProgress = stats.in_progress;
          const open = stats.open;
          const completionPercentage = assigned > 0 ? Math.round((completed / assigned) * 100) : 0;
          
          return {
            ...user,
            assigned,
            completed,
            in_progress: inProgress,
            open,
            completion_percentage: completionPercentage,
            trend: completionPercentage
          };
        })
        .filter(user => user.assigned > 0); // Only show users with tasks in the filtered set
      
      setUsers(mergedUsers);
      setProjectStats(statsRes.data);
      setStatusCounts(countsRes.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching tasks:', error);
      setLoading(false);
    }
  };

  // Filter users by search term
  const filteredUsers = users.filter(user =>
    user.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Apply pagination
  const totalPages = Math.ceil(filteredUsers.length / usersPerPage);
  const startIndex = (currentPage - 1) * usersPerPage;
  const endIndex = startIndex + usersPerPage;
  const paginatedUsers = filteredUsers.slice(startIndex, endIndex);

  // Handle page change
  const handlePageChange = (page) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page);
    }
  };

  // Handle file upload
  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Validate file type
    if (!file.name.endsWith('.csv')) {
      setUploadMessage({
        type: 'error',
        text: 'Please upload a CSV file'
      });
      return;
    }

    setUploading(true);
    setUploadMessage(null);

    try {
      const response = await uploadTasksCSV(file);
      
      setUploadMessage({
        type: 'success',
        text: `Successfully uploaded! ${response.data.tasks_added} tasks added, ${response.data.tasks_skipped} skipped.`
      });

      // Refresh data after upload
      await fetchData();

      // Clear file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }

      // Clear message after 5 seconds
      setTimeout(() => {
        setUploadMessage(null);
      }, 5000);

    } catch (error) {
      console.error('Upload error:', error);
      const errorMsg = error.response?.data?.error || 'Upload failed. Please try again.';
      setUploadMessage({
        type: 'error',
        text: errorMsg
      });

      // Clear error message after 5 seconds
      setTimeout(() => {
        setUploadMessage(null);
      }, 5000);
    } finally {
      setUploading(false);
    }
  };

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
        <div className="header-left">
          <h1 className="page-title">Tasks</h1>
          {uploadMessage && (
            <div className={`upload-message ${uploadMessage.type}`}>
              {uploadMessage.text}
            </div>
          )}
        </div>
        <div className="header-right">
          <input
            type="file"
            ref={fileInputRef}
            accept=".csv"
            onChange={handleFileUpload}
            style={{ display: 'none' }}
          />
          <button 
            className="upload-button"
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
          >
            <Upload size={18} />
            {uploading ? 'Uploading...' : 'Upload CSV'}
          </button>
        </div>
      </div>

      {/* Status Stats Bar */}
      <div className="status-stats-bar">
        <div 
          className={`status-stat-card ${statusFilter === 'All Tasks' ? 'active' : ''}`}
          onClick={() => {
            setStatusFilter('All Tasks');
            setCurrentPage(1);
          }}
        >
          <div className="stat-icon all">
            <Clock size={20} />
          </div>
          <div className="stat-content">
            <div className="stat-label">All Tasks</div>
            <div className="stat-value">{statusCounts.all}</div>
          </div>
        </div>

        <div 
          className={`status-stat-card ${statusFilter === 'Open' ? 'active' : ''}`}
          onClick={() => {
            setStatusFilter('Open');
            setCurrentPage(1);
          }}
        >
          <div className="stat-icon open">
            <AlertCircle size={20} />
          </div>
          <div className="stat-content">
            <div className="stat-label">Open</div>
            <div className="stat-value">{statusCounts.open}</div>
          </div>
        </div>

        <div 
          className={`status-stat-card ${statusFilter === 'In Progress' ? 'active' : ''}`}
          onClick={() => {
            setStatusFilter('In Progress');
            setCurrentPage(1);
          }}
        >
          <div className="stat-icon in-progress">
            <Clock size={20} />
          </div>
          <div className="stat-content">
            <div className="stat-label">In Progress</div>
            <div className="stat-value">{statusCounts.in_progress}</div>
          </div>
        </div>

        <div 
          className={`status-stat-card ${statusFilter === 'Completed' ? 'active' : ''}`}
          onClick={() => {
            setStatusFilter('Completed');
            setCurrentPage(1);
          }}
        >
          <div className="stat-icon completed">
            <CheckCircle size={20} />
          </div>
          <div className="stat-content">
            <div className="stat-label">Completed</div>
            <div className="stat-value">{statusCounts.completed}</div>
          </div>
        </div>

        <div 
          className={`status-stat-card ${statusFilter === 'Blocked' ? 'active' : ''}`}
          onClick={() => {
            setStatusFilter('Blocked');
            setCurrentPage(1);
          }}
        >
          <div className="stat-icon blocked">
            <XCircle size={20} />
          </div>
          <div className="stat-content">
            <div className="stat-label">Blocked</div>
            <div className="stat-value">{statusCounts.blocked}</div>
          </div>
        </div>
      </div>

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
                  onChange={(e) => {
                    setSearchTerm(e.target.value);
                    setCurrentPage(1); // Reset to page 1 when searching
                  }}
                />
              </div>
              
              <select 
                className="status-filter"
                value={statusFilter}
                onChange={(e) => {
                  setStatusFilter(e.target.value);
                  setCurrentPage(1); // Reset to page 1 when filtering
                }}
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
                {paginatedUsers.map((user) => (
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
                      {user.completion_percentage >= 50 ? (
                        <span className="trend-up">
                          <TrendingUp size={14} /> {user.completion_percentage}%
                        </span>
                      ) : user.completion_percentage === 0 ? (
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

            {filteredUsers.length > 0 && (
              <>
                <div className="pagination">
                  <button 
                    className="page-btn"
                    onClick={() => handlePageChange(currentPage - 1)}
                    disabled={currentPage === 1}
                  >
                    Previous
                  </button>
                  
                  {/* Show page numbers */}
                  {[...Array(totalPages)].map((_, index) => {
                    const pageNum = index + 1;
                    // Show first page, last page, current page, and pages around current
                    if (
                      pageNum === 1 ||
                      pageNum === totalPages ||
                      (pageNum >= currentPage - 1 && pageNum <= currentPage + 1)
                    ) {
                      return (
                        <button
                          key={pageNum}
                          className={`page-btn ${currentPage === pageNum ? 'active' : ''}`}
                          onClick={() => handlePageChange(pageNum)}
                        >
                          {pageNum}
                        </button>
                      );
                    } else if (pageNum === currentPage - 2 || pageNum === currentPage + 2) {
                      return <span key={pageNum} className="page-ellipsis">...</span>;
                    }
                    return null;
                  })}
                  
                  <button 
                    className="page-btn"
                    onClick={() => handlePageChange(currentPage + 1)}
                    disabled={currentPage === totalPages || totalPages === 0}
                  >
                    Next
                  </button>
                </div>
                
                <div className="pagination-info">
                  Showing {startIndex + 1}-{Math.min(endIndex, filteredUsers.length)} of {filteredUsers.length} users
                  {statusFilter !== 'All Tasks' && (
                    <span className="filter-indicator"> (filtered by {statusFilter})</span>
                  )}
                </div>
              </>
            )}
            
            {filteredUsers.length === 0 && !loading && (
              <div className="no-results">
                <p>No users found</p>
                {statusFilter !== 'All Tasks' && (
                  <p className="hint">Try changing the filter or search term</p>
                )}
              </div>
            )}
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
