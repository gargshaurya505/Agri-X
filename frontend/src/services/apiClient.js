import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 45000,
  headers: {
    'Accept': 'application/json',
  },
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    let message = 'Local AI service is unreachable.';
    if (error.code === 'ECONNREFUSED' || error.message.includes('Network Error')) {
      message = 'Local AI service is not running. Please start the AGRI-X Python service on localhost:8000.';
    } else if (error.response?.data?.detail) {
      message = error.response.data.detail;
    }
    return Promise.reject(new Error(message));
  }
);
