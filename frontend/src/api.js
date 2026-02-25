import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
});

export const checkHealth = () => api.get('/health');

export const getSymbols = () => api.get('/symbols');

export const analyzeSymbol = (symbol) => api.get(`/analyze/${symbol.toUpperCase()}`);

export const startScan = (type) => api.post('/scan/start', { type });

export const getScanStatus = (jobId) => api.get(`/scan/status/${jobId}`);

export const getScanResults = (jobId) => api.get(`/scan/results/${jobId}`);

export const getLatestResults = (scanType) => api.get(`/scan/latest/${scanType}`);

export default api;
