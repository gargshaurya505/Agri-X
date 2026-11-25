import React from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, 
  ShieldAlert, 
  CheckCircle2, 
  BookOpen, 
  ScanSearch, 
  AlertTriangle,
  HeartPulse
} from 'lucide-react';
import { TOMATO_DISEASES } from '../data/diseases';

export const DiseaseDetailsPage = () => {
  const { slug } = useParams();
  const navigate = useNavigate();

  const disease = TOMATO_DISEASES.find((d) => d.slug === slug);

  if (!disease) {
    return (
      <div className="max-w-md mx-auto text-center py-16 space-y-4">
        <AlertTriangle className="w-12 h-12 text-amber-500 mx-auto" />
        <h2 className="text-xl font-bold text-slate-900">Disease Profile Not Found</h2>
        <Link
          to="/library"
          className="inline-flex items-center space-x-2 px-4 py-2 bg-forest-700 text-white rounded-xl text-sm font-semibold"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Library</span>
        </Link>
      </div>
    );
  }

  const isHealthy = disease.slug === 'healthy';

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      
      <button
        onClick={() => navigate('/library')}
        className="inline-flex items-center space-x-2 text-sm font-semibold text-slate-600 hover:text-slate-900"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Back to Disease Library</span>
      </button>

      
      <div className="bg-white p-8 rounded-3xl border border-sand-200 shadow-sm space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="space-y-1">
            <span className="text-xs uppercase font-bold tracking-wider px-3 py-1 rounded-full bg-forest-50 text-forest-700 border border-forest-100">
              {disease.category}
            </span>
            <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-900 mt-2">
              {disease.name}
            </h1>
            <p className="text-sm font-serif italic text-slate-500">
              {disease.scientific_name}
            </p>
          </div>

          <div className="text-right">
            <span className="text-xs text-slate-400 block uppercase font-medium">Severity Level</span>
            <span className={`text-lg font-bold ${
              disease.severity === 'Critical / Extreme' 
                ? 'text-rose-600' 
                : isHealthy 
                ? 'text-emerald-600' 
                : 'text-amber-600'
            }`}>
              {disease.severity}
            </span>
          </div>
        </div>

        <p className="text-base text-slate-700 leading-relaxed pt-2 border-t border-sand-100">
          {disease.description}
        </p>
      </div>

      
      <div className="bg-white p-8 rounded-3xl border border-sand-200 shadow-sm space-y-4">
        <h2 className="text-xl font-bold text-slate-900 flex items-center space-x-2">
          <HeartPulse className="w-5 h-5 text-rose-500" />
          <span>Identifiable Foliar Symptoms</span>
        </h2>
        <ul className="space-y-2.5 text-sm text-slate-700">
          {disease.symptoms.map((s, idx) => (
            <li key={idx} className="flex items-start space-x-2.5">
              <span className="w-1.5 h-1.5 rounded-full bg-rose-500 mt-2 flex-shrink-0" />
              <span>{s}</span>
            </li>
          ))}
        </ul>
      </div>

      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-2xl border border-sand-200 shadow-sm space-y-3">
          <h3 className="text-base font-bold text-slate-900 flex items-center space-x-2">
            <CheckCircle2 className="w-5 h-5 text-forest-600" />
            <span>Preventative Measures</span>
          </h3>
          <ul className="space-y-2 text-xs text-slate-600 list-disc list-inside">
            {disease.prevention.map((p, idx) => (
              <li key={idx}>{p}</li>
            ))}
          </ul>
        </div>

        <div className="bg-white p-6 rounded-2xl border border-sand-200 shadow-sm space-y-3">
          <h3 className="text-base font-bold text-slate-900 flex items-center space-x-2">
            <ShieldAlert className="w-5 h-5 text-amber-600" />
            <span>Curative & Field Action</span>
          </h3>
          <ul className="space-y-2 text-xs text-slate-600 list-disc list-inside">
            {disease.management.map((m, idx) => (
              <li key={idx}>{m}</li>
            ))}
          </ul>
        </div>
      </div>

      
      <div className="p-6 rounded-2xl bg-forest-900 text-white flex flex-col sm:flex-row items-center justify-between gap-4">
        <div>
          <h4 className="text-base font-bold">Have a leaf suspected of {disease.name}?</h4>
          <p className="text-xs text-slate-300">Run immediate local neural network inference with visual Grad-CAM attribution.</p>
        </div>
        <Link
          to="/detect"
          className="px-5 py-2.5 rounded-xl font-semibold bg-emerald-500 text-forest-950 hover:bg-emerald-400 text-xs shadow-md whitespace-nowrap"
        >
          Scan Leaf Now
        </Link>
      </div>
    </div>
  );
};
