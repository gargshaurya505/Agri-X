import { apiClient } from './apiClient';

export const explainImage = async (file, targetClass = null) => {
  const formData = new FormData();
  formData.append('file', file);
  if (targetClass !== null && targetClass !== undefined) {
    formData.append('target_class', targetClass);
  }

  const response = await apiClient.post('/api/v1/explain', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};
