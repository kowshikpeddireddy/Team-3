import axios from 'axios';

const API_BASE_URL = 'http://localhost:5001/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Overview endpoints
export const getOverview = () => apiClient.get('/overview');
export const getDistribution = () => apiClient.get('/distribution');
export const getTrends = () => apiClient.get('/trends');
export const getTeamPerformance = () => apiClient.get('/team-performance');

// Tasks endpoints
export const getTasks = (filters = {}) => {
  const params = new URLSearchParams(filters).toString();
  return apiClient.get(`/tasks${params ? '?' + params : ''}`);
};
export const getTask = (taskId) => apiClient.get(`/tasks/${taskId}`);
export const getProjects = () => apiClient.get('/projects');
export const getProjectStats = () => apiClient.get('/projects/stats');

// Users endpoints
export const getUsers = (search = '') => {
  return apiClient.get(`/users${search ? '?search=' + search : ''}`);
};
export const getUser = (userId) => apiClient.get(`/users/${userId}`);

// AI Insights endpoints
export const getAISummary = () => apiClient.get('/ai/summary');
export const getClosurePerformance = () => apiClient.get('/ai/closure-performance');
export const getDueCompliance = () => apiClient.get('/ai/due-compliance');
export const getPredictions = () => apiClient.get('/ai/predictions');
export const getTeamBenchmarking = () => apiClient.get('/ai/team-benchmarking');
export const getProductivityTrends = () => apiClient.get('/ai/productivity-trends');
export const getSentiment = () => apiClient.get('/ai/sentiment');

// Chat endpoint
export const sendChatQuery = (query) => apiClient.post('/chat', { query });

// Settings endpoints
export const getSettings = () => apiClient.get('/settings');
export const saveSettings = (settings) => apiClient.post('/settings', settings);

export default apiClient;

