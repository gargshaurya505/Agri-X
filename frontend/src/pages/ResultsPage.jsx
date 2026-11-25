import React, { useState } from 'react';
import { useLocation, Link, useNavigate } from 'react-router-dom';
import { 
  ScanSearch, 
  ArrowLeft, 
  ShieldAlert, 
  CheckCircle2, 
  AlertTriangle, 
  Layers, 
  FileText, 
  Info,
  Eye,
  RefreshCw,
  Download
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  Cell 
} from 'recharts';
import { TOMATO_DISEASES } from '../data/diseases';
import { explainImage } from '../services/explanationService';

export const ResultsPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { prediction, previewUrl, file } = location.state || {};

  const [explaining, setExplaining] = useState(false);
  const [explanationData, setExplanationData] = useState(null);
  const [explanationError, setExplanationError] = useState(null);

  if (!prediction) {
    return (
      <div className="max-w-md mx-auto text-center py-16 space-y-4">
        <AlertTriangle className="w-12 h-12 text-amber-500 mx-auto" />
        <h2 className="text-xl font-bold text-slate-900">No Active Analysis Found</h2>
        <p className="text-sm text-slate-600">
          Please upload a leaf photograph from the detection page to view neural diagnostic predictions.
        </p>
        <Link
          to="/detect"
          className="inline-flex items-center space-x-2 px-4 py-2.5 bg-forest-700 text-white rounded-xl font-semibold text-sm hover:bg-forest-800"
        >
          <ScanSearch className="w-4 h-4" />
          <span>Go to Leaf Scanner</span>
        </Link>
      </div>
    );
  }

  const diseaseInfo = TOMATO_DISEASES.find(
    (d) => d.name.toLowerCase() === (prediction.display_name || prediction.predicted_class || '').toLowerCase()
  ) || {
    name: prediction.display_name || prediction.predicted_class,
    category: 'Diagnosed Category',
    severity: 'Moderate',
    description: 'Pathological symptoms detected based on trained neural representations.',
    symptoms: ['Foliar lesion or chlorosis signature identified by convolutional network.'],
    prevention: ['Isolate affected specimens and monitor canopy spread.'],
    management: ['Consult local extension guidelines for confirmed crop treatments.']
  };

  const isHealthy = diseaseInfo.name.toLowerCase().includes('healthy');

  const formattedConfidence = prediction.confidence > 1.0 
    ? (prediction.confidence).toFixed(1) 
    : (prediction.confidence * 100).toFixed(1);

  const chartData = (prediction.top_predictions || []).map((p) => {
    const rawVal = p.probability;
    const normProb = rawVal > 1.0 ? rawVal / 100.0 : rawVal;
    return {
      name: p.class_name,
      probability: normProb,
      percentage: (normProb * 100).toFixed(1)
    };
  }).reverse();

  const handleRunExplainability = async () => {
    if (!file) {
      setExplanationError('Original file handle is unavailable in current session.');
      return;
    }
    setExplaining(true);
    setExplanationError(null);

    try {
      const exp = await explainImage(file);
      setExplanationData(exp);
    } catch (err) {
      setExplanationError(err.message || 'Failed to generate Grad-CAM attribution.');
    } finally {
      setExplaining(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      
      <div className="flex items-center justify-between">
        <button
          onClick={() => navigate('/detect')}
          className="inline-flex items-center space-x-2 text-sm font-semibold text-slate-600 hover:text-slate-900"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Analyze Another Leaf</span>
        </button>

        <span className="text-xs font-mono px-3 py-1 bg-sand-200/60 rounded-full text-slate-600">
          Model: {prediction.model_name || 'ResNet18'}
        </span>
      </div>

      
      <div className={`p-6 sm:p-8 rounded-3xl border shadow-sm ${
        isHealthy 
          ? 'bg-emerald-50/70 border-emerald-200 text-emerald-950' 
          : 'bg-white border-sand-200'
      }`}>
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider bg-sand-100 text-slate-700">
              <span>{diseaseInfo.category}</span>
              <span>•</span>
              <span className={isHealthy ? 'text-emerald-700' : 'text-amber-700'}>
                Severity: {diseaseInfo.severity}
              </span>
            </div>

            <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-slate-900">
              {prediction.display_name || prediction.predicted_class}
            </h1>

            {diseaseInfo.scientific_name && (
              <p className="text-sm font-serif italic text-slate-500">
                {diseaseInfo.scientific_name}
              </p>
            )}
          </div>

          <div className="text-right bg-sand-50 p-4 rounded-2xl border border-sand-200 min-w-[180px]">
            <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Model Confidence
            </div>
            <div className="text-4xl font-extrabold text-forest-700 mt-1">
              {formattedConfidence}%
            </div>
            <div className="text-[11px] text-slate-400 mt-0.5">
              Softmax Probability Score
            </div>
          </div>
        </div>
      </div>

      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        <div className="bg-white p-6 rounded-3xl border border-sand-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-slate-900">Analyzed Leaf Photograph</h3>
            <span className="text-xs text-slate-500">Uploaded Specimen</span>
          </div>

          <div className="h-72 bg-slate-900 rounded-2xl overflow-hidden flex items-center justify-center">
            {previewUrl ? (
              <img
                src={previewUrl}
                alt="Analyzed Tomato Leaf"
                className="w-full h-full object-contain"
              />
            ) : (
              <span className="text-xs text-slate-400">Preview not stored</span>
            )}
          </div>

          <p className="text-xs text-slate-500 text-center italic">
            Evaluated by local PyTorch ResNet18 runtime.
          </p>
        </div>

        
        <div className="bg-white p-6 rounded-3xl border border-sand-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-slate-900">Prediction Probabilities</h3>
            <span className="text-xs text-slate-500">Top Classes</span>
          </div>

          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                layout="vertical"
                data={chartData}
                margin={{ top: 10, right: 45, left: 10, bottom: 5 }}
              >
                <XAxis 
                  type="number" 
                  domain={[0, 1]} 
                  tickFormatter={(v) => `${Math.round(v * 100)}%`} 
                  tick={{ fontSize: 11 }} 
                />
                <YAxis dataKey="name" type="category" width={110} tick={{ fontSize: 11 }} />
                <Tooltip
                  formatter={(val) => [`${(val * 100).toFixed(1)}%`, 'Score']}
                  contentStyle={{ backgroundColor: '#fff', borderRadius: '8px', border: '1px solid #e2e8f0', fontSize: '12px' }}
                />
                <Bar dataKey="probability" radius={[0, 4, 4, 0]}>
                  {chartData.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={index === chartData.length - 1 ? '#16a34a' : '#94a3b8'}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          <p className="text-xs text-slate-400 text-center">
            Probabilities reflect model activations, not guaranteed biological certainty.
          </p>
        </div>
      </div>

      
      <div className="bg-white p-6 sm:p-8 rounded-3xl border border-sand-200 shadow-sm space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center space-x-1.5 text-xs font-semibold uppercase tracking-wider text-forest-700">
              <Eye className="w-4 h-4" />
              <span>Interpretability & Attribution</span>
            </div>
            <h3 className="text-2xl font-bold text-slate-900 mt-1">
              Inspect Grad-CAM Visual Heatmap
            </h3>
            <p className="text-sm text-slate-600 mt-0.5">
              Visualize exactly which spatial pixels influenced the ResNet18 classification decision.
            </p>
          </div>

          {!explanationData && (
            <button
              onClick={handleRunExplainability}
              disabled={explaining}
              className="inline-flex items-center space-x-2 px-5 py-3 rounded-xl font-semibold bg-forest-700 hover:bg-forest-800 text-white text-sm shadow-sm transition-all disabled:opacity-75"
            >
              {explaining ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Computing Heatmap...</span>
                </>
              ) : (
                <>
                  <Eye className="w-4 h-4" />
                  <span>Generate Grad-CAM Overlay</span>
                </>
              )}
            </button>
          )}
        </div>

        {explanationError && (
          <div className="p-4 rounded-xl bg-amber-50 border border-amber-200 text-amber-900 text-xs">
            {explanationError}
          </div>
        )}

        
        {explanationData && (
          <div className="space-y-6 pt-4 border-t border-sand-200">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="space-y-2 text-center">
                <span className="text-xs font-semibold text-slate-700">1. Original Photo</span>
                <div className="h-56 bg-slate-900 rounded-xl overflow-hidden flex items-center justify-center">
                  <img src={previewUrl} alt="Original" className="w-full h-full object-contain" />
                </div>
              </div>

              <div className="space-y-2 text-center">
                <span className="text-xs font-semibold text-slate-700">2. Activation Heatmap</span>
                <div className="h-56 bg-slate-900 rounded-xl overflow-hidden flex items-center justify-center">
                  {explanationData.heatmap ? (
                    <img src={explanationData.heatmap} alt="Heatmap" className="w-full h-full object-contain" />
                  ) : (
                    <span className="text-xs text-slate-400">Raw activation map</span>
                  )}
                </div>
              </div>

              <div className="space-y-2 text-center">
                <span className="text-xs font-semibold text-slate-700">3. Diagnostic Overlay</span>
                <div className="h-56 bg-slate-900 rounded-xl overflow-hidden flex items-center justify-center border-2 border-forest-500">
                  {explanationData.overlay ? (
                    <img src={explanationData.overlay} alt="Overlay" className="w-full h-full object-contain" />
                  ) : (
                    <span className="text-xs text-slate-400">Blended visual overlay</span>
                  )}
                </div>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-sand-100 text-xs text-slate-600 space-y-1">
              <p className="font-semibold text-slate-800">Interpretation Guidelines:</p>
              <p>
                Warm regions (red / yellow) denote highest gradient attribution towards the "{explanationData.target_class || prediction.display_name}" decision. Cool areas (blue) contributed minimally.
              </p>
            </div>
          </div>
        )}
      </div>

      
      <div className="bg-white p-6 sm:p-8 rounded-3xl border border-sand-200 shadow-sm space-y-6">
        <h3 className="text-xl font-bold text-slate-900">
          Agronomic Management & Actionable Advisory
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 text-sm">
          <div className="space-y-3">
            <h4 className="font-bold text-slate-900 flex items-center space-x-2">
              <span className="w-2 h-2 rounded-full bg-amber-500" />
              <span>Visible Pathology Symptoms</span>
            </h4>
            <ul className="space-y-2 text-slate-600 list-disc list-inside">
              {diseaseInfo.symptoms.map((s, i) => (
                <li key={i}>{s}</li>
              ))}
            </ul>
          </div>

          <div className="space-y-3">
            <h4 className="font-bold text-slate-900 flex items-center space-x-2">
              <span className="w-2 h-2 rounded-full bg-forest-600" />
              <span>Preventative Field Protocols</span>
            </h4>
            <ul className="space-y-2 text-slate-600 list-disc list-inside">
              {diseaseInfo.prevention.map((p, i) => (
                <li key={i}>{p}</li>
              ))}
            </ul>
          </div>
        </div>

        <div className="pt-4 border-t border-sand-200 flex flex-wrap gap-4 items-center justify-between">
          <Link
            to={`/library/${diseaseInfo.slug || 'bacterial_spot'}`}
            className="text-xs font-semibold text-forest-700 hover:text-forest-800"
          >
            Read Comprehensive Clinical Profile in Disease Library →
          </Link>

          <Link
            to="/detect"
            className="px-5 py-2.5 rounded-xl font-semibold bg-forest-700 hover:bg-forest-800 text-white text-xs shadow-sm"
          >
            Scan Another Leaf
          </Link>
        </div>
      </div>
    </div>
  );
};
