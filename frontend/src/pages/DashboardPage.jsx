import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  ScanSearch, 
  History, 
  Activity, 
  CheckCircle2, 
  AlertTriangle, 
  Calendar,
  Layers,
  ArrowRight,
  TrendingUp,
  PieChart as PieChartIcon
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  Cell,
  PieChart,
  Pie
} from 'recharts';
import { getHistory } from '../services/historyService';

const CHART_COLORS = ['#16a34a', '#2563eb', '#d97706', '#dc2626', '#9333ea', '#0891b2', '#ea580c', '#4f46e5'];

export const DashboardPage = () => {
  const [history, setHistory] = useState([]);
  const [stats, setStats] = useState({
    total: 0,
    healthyCount: 0,
    diseaseCount: 0,
    topDisease: 'None',
    lastAnalysisDate: 'No analyses yet'
  });

  useEffect(() => {
    const records = getHistory();
    setHistory(records);

    if (records.length > 0) {
      let healthy = 0;
      const diseaseCounts = {};

      records.forEach((r) => {
        const clsName = r.display_name || r.predicted_class || 'Unknown';
        if (clsName.toLowerCase().includes('healthy')) {
          healthy += 1;
        } else {
          diseaseCounts[clsName] = (diseaseCounts[clsName] || 0) + 1;
        }
      });

      let maxCnt = 0;
      let topDis = 'None';
      Object.entries(diseaseCounts).forEach(([name, count]) => {
        if (count > maxCnt) {
          maxCnt = count;
          topDis = name;
        }
      });

      const lastDate = new Date(records[0].timestamp).toLocaleDateString(undefined, {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });

      setStats({
        total: records.length,
        healthyCount: healthy,
        diseaseCount: records.length - healthy,
        topDisease: topDis,
        lastAnalysisDate: lastDate
      });
    }
  }, []);

  const classDistributionData = React.useMemo(() => {
    const counts = {};
    history.forEach((r) => {
      const name = r.display_name || r.predicted_class || 'Unknown';
      counts[name] = (counts[name] || 0) + 1;
    });
    return Object.entries(counts).map(([name, count]) => ({
      name,
      count
    }));
  }, [history]);

  return (
    <div className="space-y-8">
      
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-slate-900">
            Agricultural Intelligence Dashboard
          </h1>
          <p className="text-slate-600 text-sm mt-1">
            Aggregated diagnostics compiled from your browser-stored analysis history.
          </p>
        </div>

        <Link
          to="/detect"
          className="inline-flex items-center space-x-2 px-4 py-2.5 rounded-xl font-semibold bg-forest-700 hover:bg-forest-800 text-white shadow-sm transition-all text-sm w-fit"
        >
          <ScanSearch className="w-4 h-4" />
          <span>Analyze New Image</span>
        </Link>
      </div>

      
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="bg-white p-5 rounded-2xl border border-sand-200 shadow-sm space-y-3">
          <div className="flex items-center justify-between text-slate-500 text-xs font-medium uppercase tracking-wider">
            <span>Total Analyses</span>
            <Activity className="w-4 h-4 text-forest-600" />
          </div>
          <div className="text-3xl font-bold text-slate-900">{stats.total}</div>
          <p className="text-xs text-slate-500">Recorded in local browser log</p>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-sand-200 shadow-sm space-y-3">
          <div className="flex items-center justify-between text-slate-500 text-xs font-medium uppercase tracking-wider">
            <span>Most Frequent Disease</span>
            <AlertTriangle className="w-4 h-4 text-amber-500" />
          </div>
          <div className="text-xl font-bold text-slate-900 truncate" title={stats.topDisease}>
            {stats.topDisease}
          </div>
          <p className="text-xs text-slate-500">Most identified pathology</p>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-sand-200 shadow-sm space-y-3">
          <div className="flex items-center justify-between text-slate-500 text-xs font-medium uppercase tracking-wider">
            <span>Healthy Foliage</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="text-3xl font-bold text-slate-900">{stats.healthyCount}</div>
          <p className="text-xs text-slate-500">
            {stats.total > 0 ? `${((stats.healthyCount / stats.total) * 100).toFixed(0)}% of scans` : '0%'}
          </p>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-sand-200 shadow-sm space-y-3">
          <div className="flex items-center justify-between text-slate-500 text-xs font-medium uppercase tracking-wider">
            <span>Latest Activity</span>
            <Calendar className="w-4 h-4 text-blue-500" />
          </div>
          <div className="text-base font-bold text-slate-900 truncate">
            {stats.lastAnalysisDate}
          </div>
          <p className="text-xs text-slate-500">Last diagnostic session</p>
        </div>
      </div>

      
      {history.length === 0 ? (
        <div className="bg-white rounded-2xl border border-dashed border-sand-300 p-12 text-center space-y-4">
          <div className="w-14 h-14 bg-forest-50 text-forest-700 rounded-2xl flex items-center justify-center mx-auto">
            <ScanSearch className="w-7 h-7" />
          </div>
          <div className="max-w-md mx-auto space-y-1">
            <h3 className="text-lg font-bold text-slate-900">No Analysis History Yet</h3>
            <p className="text-sm text-slate-600">
              Your dashboard statistics and distribution metrics populate automatically as you perform leaf disease diagnoses.
            </p>
          </div>
          <Link
            to="/detect"
            className="inline-flex items-center space-x-2 px-5 py-2.5 rounded-xl font-semibold bg-forest-700 hover:bg-forest-800 text-white text-sm shadow-sm transition-all"
          >
            <span>Scan First Tomato Leaf</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          
          <div className="bg-white p-6 rounded-2xl border border-sand-200 shadow-sm space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-base font-bold text-slate-900">Disease Frequency Breakdown</h3>
              <span className="text-xs text-slate-500 font-medium">Actual User Scans</span>
            </div>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={classDistributionData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                  <XAxis dataKey="name" angle={-25} textAnchor="end" interval={0} tick={{ fontSize: 10 }} />
                  <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#fff', borderRadius: '8px', border: '1px solid #e2e8f0', fontSize: '12px' }} 
                  />
                  <Bar dataKey="count" fill="#16a34a" radius={[4, 4, 0, 0]}>
                    {classDistributionData.map((_, index) => (
                      <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          
          <div className="bg-white p-6 rounded-2xl border border-sand-200 shadow-sm space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-base font-bold text-slate-900">Recent Diagnostic Scans</h3>
              <Link to="/history" className="text-xs font-semibold text-forest-700 hover:text-forest-800">
                View All ({history.length})
              </Link>
            </div>
            <div className="divide-y divide-sand-100 max-h-64 overflow-y-auto custom-scrollbar">
              {history.slice(0, 5).map((rec) => (
                <div key={rec.prediction_id} className="py-3 flex items-center justify-between">
                  <div className="space-y-0.5">
                    <div className="text-sm font-semibold text-slate-800">
                      {rec.display_name || rec.predicted_class}
                    </div>
                    <div className="text-xs text-slate-400">
                      {new Date(rec.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} • Conf: {(rec.confidence * 100).toFixed(1)}%
                    </div>
                  </div>
                  <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-forest-50 text-forest-700 border border-forest-100">
                    {(rec.confidence * 100).toFixed(0)}%
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
