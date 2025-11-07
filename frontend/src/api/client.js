import axios from 'axios';

const API_BASE_URL = 'http://localhost:5001/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Overview endpoints
export const getOverview = (filter = 'today') => apiClient.get(`/overview?filter=${filter}`);
export const getDistribution = (filter = 'today') => apiClient.get(`/distribution?filter=${filter}`);
export const getTrends = (filter = 'today') => apiClient.get(`/trends?filter=${filter}`);
export const getTeamPerformance = (filter = 'today') => apiClient.get(`/team-performance?filter=${filter}`);

// Tasks endpoints
export const getTasks = (filters = {}) => {
  const params = new URLSearchParams(filters).toString();
  return apiClient.get(`/tasks${params ? '?' + params : ''}`);
};
export const getTaskStatusCounts = () => apiClient.get('/tasks/status-counts');
export const uploadTasksCSV = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return apiClient.post('/tasks/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};
export const getTask = (taskId) => apiClient.get(`/tasks/${taskId}`);
export const getProjects = () => apiClient.get('/projects');
export const getProjectStats = () => apiClient.get('/projects/stats');

// Users endpoints
export const getUsers = (search = '') => {
  return apiClient.get(`/users${search ? '?search=' + search : ''}`);
};
export const getUser = (userId) => apiClient.get(`/users/${userId}`);

// AI Insights endpoints (with filter support)
export const getAISummary = (filter = 'today') => apiClient.get(`/ai/summary?filter=${filter}`);
export const getClosurePerformance = (filter = 'today') => apiClient.get(`/ai/closure-performance?filter=${filter}`);
export const getDueCompliance = (filter = 'today') => apiClient.get(`/ai/due-compliance?filter=${filter}`);
export const getPredictions = (filter = 'today') => apiClient.get(`/ai/predictions?filter=${filter}`);
export const getTeamBenchmarking = (filter = 'today') => apiClient.get(`/ai/team-benchmarking?filter=${filter}`);
export const getProductivityTrends = (filter = 'today') => apiClient.get(`/ai/productivity-trends?filter=${filter}`);
export const getSentiment = (filter = 'today') => apiClient.get(`/ai/sentiment?filter=${filter}`);

// Natural Language Query endpoint
export const sendChatQuery = (question) => apiClient.post('/query', { question });

// Settings endpoints
export const getSettings = () => apiClient.get('/settings');
export const saveSettings = (settings) => apiClient.post('/settings', settings);

export default apiClient;

