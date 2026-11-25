import { apiClient } from './apiClient';

export const healthCheck = async () => {
  const response = await apiClient.get('/api/v1/health');
  return response.data;
};

export const predictImage = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await apiClient.post('/api/v1/predict', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};
