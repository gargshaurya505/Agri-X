const HISTORY_KEY = 'agrix_prediction_history';

export const getHistory = () => {
  try {
    const raw = localStorage.getItem(HISTORY_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch (e) {
    console.error('Failed to parse history from localStorage', e);
    return [];
  }
};

export const savePredictionToHistory = (predictionRecord) => {
  try {
    const existing = getHistory();
    const updated = [predictionRecord, ...existing];
    const trimmed = updated.slice(0, 50);
    localStorage.setItem(HISTORY_KEY, JSON.stringify(trimmed));
    return trimmed;
  } catch (e) {
    console.error('Failed to save record to localStorage', e);
    return getHistory();
  }
};

export const deleteHistoryItem = (predictionId) => {
  try {
    const existing = getHistory();
    const updated = existing.filter((item) => item.prediction_id !== predictionId);
    localStorage.setItem(HISTORY_KEY, JSON.stringify(updated));
    return updated;
  } catch (e) {
    console.error('Failed to delete history item', e);
    return getHistory();
  }
};

export const clearAllHistory = () => {
  try {
    localStorage.removeItem(HISTORY_KEY);
    return [];
  } catch (e) {
    console.error('Failed to clear history', e);
    return [];
  }
};
