import React from 'react';
import { Link } from 'react-router-dom';
import { Sprout, ShieldCheck, Cpu, Eye, ExternalLink } from 'lucide-react';

export const Footer = () => {
  return (
    <footer className="bg-slate-900 text-slate-300 border-t border-slate-800 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          
          <div className="space-y-4 md:col-span-1">
            <div className="flex items-center space-x-2.5">
              <div className="w-9 h-9 rounded-lg bg-forest-600 flex items-center justify-center text-white">
                <Sprout className="w-5 h-5 text-emerald-300" />
              </div>
              <span className="text-xl font-bold tracking-tight text-white">
                AGRI<span className="text-emerald-400">-X</span>
              </span>
            </div>
            <p className="text-sm text-slate-400 leading-relaxed">
              Explainable AI-based crop disease diagnosis and agricultural intelligence system engineered for precision farming.
            </p>
            <div className="flex items-center space-x-2 text-xs text-slate-400">
              <Cpu className="w-4 h-4 text-emerald-400" />
              <span>ResNet18 + Grad-CAM Core</span>
            </div>
          </div>

          
          <div>
            <h4 className="text-sm font-semibold text-white uppercase tracking-wider mb-4">Core Modules</h4>
            <ul className="space-y-2.5 text-sm">
              <li>
                <Link to="/detect" className="hover:text-emerald-400 transition-colors">
                  Diagnostic Leaf Scanner
                </Link>
              </li>
              <li>
                <Link to="/library" className="hover:text-emerald-400 transition-colors">
                  Tomato Disease Library
                </Link>
              </li>
              <li>
                <Link to="/dashboard" className="hover:text-emerald-400 transition-colors">
                  Analytics Dashboard
                </Link>
              </li>
              <li>
                <Link to="/history" className="hover:text-emerald-400 transition-colors">
                  Local Prediction Log
                </Link>
              </li>
            </ul>
          </div>

          
          <div>
            <h4 className="text-sm font-semibold text-white uppercase tracking-wider mb-4">XAI Research</h4>
            <ul className="space-y-2.5 text-sm">
              <li className="flex items-center space-x-1.5">
                <Eye className="w-4 h-4 text-emerald-400" />
                <span>Grad-CAM Attribution</span>
              </li>
              <li className="flex items-center space-x-1.5">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                <span>Leakage-Free Splitting</span>
              </li>
              <li className="flex items-center space-x-1.5">
                <span>PlantDoc Benchmark</span>
              </li>
              <li>
                <Link to="/about" className="hover:text-emerald-400 transition-colors">
                  Technical Architecture
                </Link>
              </li>
            </ul>
          </div>

          
          <div>
            <h4 className="text-sm font-semibold text-white uppercase tracking-wider mb-4">Local Deployment</h4>
            <div className="p-4 rounded-xl bg-slate-800/80 border border-slate-700/60 text-xs space-y-2">
              <div className="flex justify-between">
                <span className="text-slate-400">Inference Engine:</span>
                <span className="font-mono text-emerald-400">PyTorch Local</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Model:</span>
                <span className="font-mono text-slate-200">ResNet18 (10 Cls)</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Privacy:</span>
                <span className="font-mono text-emerald-400">Zero Cloud Upload</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Storage:</span>
                <span className="font-mono text-slate-200">Browser Local</span>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-8 pt-8 border-t border-slate-800 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-400">
          <p>© 2026 AGRI-X Project. College Major Project Architecture.</p>
          <p className="mt-2 sm:mt-0">Built with React, Vite, Tailwind CSS & PyTorch.</p>
        </div>
      </div>
    </footer>
  );
};
