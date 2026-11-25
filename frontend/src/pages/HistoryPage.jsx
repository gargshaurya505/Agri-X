import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  History, 
  Trash2, 
  Search, 
  Filter, 
  Calendar, 
  ScanSearch, 
  AlertTriangle,
  ArrowRight
} from 'lucide-react';
import { getHistory, deleteHistoryItem, clearAllHistory } from '../services/historyService';

export const HistoryPage = () => {
  const [history, setHistory] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [confirmClear, setConfirmClear] = useState(false);

  useEffect(() => {
    setHistory(getHistory());
  }, []);

  const handleDelete = (id) => {
    const updated = deleteHistoryItem(id);
    setHistory(updated);
  };

  const handleClearAll = () => {
    clearAllHistory();
    setHistory([]);
    setConfirmClear(false);
  };

  const filteredHistory = history.filter((item) => {
    const term = searchQuery.toLowerCase();
    const name = (item.display_name || item.predicted_class || '').toLowerCase();
    return name.includes(term);
  });

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-slate-900">
            Local Diagnostic Scan History
          </h1>
          <p className="text-slate-600 text-sm mt-1">
            Browse and manage all previous disease diagnoses stored securely inside your browser.
          </p>
        </div>

        {history.length > 0 && (
          <div>
            {!confirmClear ? (
              <button
                onClick={() => setConfirmClear(true)}
                className="inline-flex items-center space-x-1.5 px-3 py-2 rounded-xl text-xs font-semibold text-rose-600 hover:bg-rose-50 border border-rose-200 transition-colors"
              >
                <Trash2 className="w-4 h-4" />
                <span>Clear All Logs</span>
              </button>
            ) : (
              <div className="flex items-center space-x-2">
                <button
                  onClick={handleClearAll}
                  className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-rose-600 text-white hover:bg-rose-700"
                >
                  Confirm Delete
                </button>
                <button
                  onClick={() => setConfirmClear(false)}
                  className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-sand-200 text-slate-700 hover:bg-sand-300"
                >
                  Cancel
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      
      {history.length > 0 && (
        <div className="bg-white p-4 rounded-2xl border border-sand-200 shadow-sm flex items-center space-x-3">
          <Search className="w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search prediction history by disease name..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full text-sm bg-transparent focus:outline-none"
          />
        </div>
      )}

      
      {history.length === 0 ? (
        <div className="bg-white rounded-3xl border border-sand-200 p-12 text-center space-y-4 shadow-sm">
          <div className="w-14 h-14 bg-forest-50 text-forest-700 rounded-2xl flex items-center justify-center mx-auto">
            <History className="w-7 h-7" />
          </div>
          <div className="max-w-sm mx-auto space-y-1">
            <h3 className="text-lg font-bold text-slate-900">No Prior Analyses Recorded</h3>
            <p className="text-xs text-slate-500">
              Diagnoses are automatically saved in local browser storage when you analyze leaves using the AI scanner.
            </p>
          </div>
          <Link
            to="/detect"
            className="inline-flex items-center space-x-2 px-5 py-2.5 rounded-xl font-semibold bg-forest-700 hover:bg-forest-800 text-white text-xs shadow-sm"
          >
            <ScanSearch className="w-4 h-4" />
            <span>Scan First Tomato Leaf</span>
          </Link>
        </div>
      ) : (
        <div className="bg-white rounded-2xl border border-sand-200 shadow-sm divide-y divide-sand-100 overflow-hidden">
          {filteredHistory.map((item) => (
            <div
              key={item.prediction_id}
              className="p-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 hover:bg-sand-50/70 transition-colors"
            >
              <div className="space-y-1">
                <div className="flex items-center space-x-2">
                  <span className="text-base font-bold text-slate-900">
                    {item.display_name || item.predicted_class}
                  </span>
                  <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-forest-50 text-forest-700 border border-forest-100">
                    {(item.confidence * 100).toFixed(1)}% Conf
                  </span>
                </div>
                <div className="flex items-center space-x-4 text-xs text-slate-400">
                  <span className="flex items-center space-x-1">
                    <Calendar className="w-3.5 h-3.5" />
                    <span>{new Date(item.timestamp).toLocaleString()}</span>
                  </span>
                  <span>•</span>
                  <span>Model: {item.model_name || 'ResNet18'}</span>
                </div>
              </div>

              <div className="flex items-center space-x-2 w-full sm:w-auto justify-end">
                <button
                  onClick={() => handleDelete(item.prediction_id)}
                  className="p-2 text-slate-400 hover:text-rose-600 rounded-lg hover:bg-sand-100 transition-colors"
                  title="Delete record"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
