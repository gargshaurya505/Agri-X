import React from 'react';
import { 
  Sprout, 
  Cpu, 
  Eye, 
  ShieldCheck, 
  Layers, 
  Microscope,
  CheckCircle2,
  Code
} from 'lucide-react';

export const AboutPage = () => {
  return (
    <div className="max-w-4xl mx-auto space-y-12 py-4">
      
      <div className="space-y-3">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-forest-50 border border-forest-100 text-forest-700 text-xs font-semibold uppercase">
          <Microscope className="w-3.5 h-3.5" />
          <span>College Major Project Specification</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-slate-900">
          About AGRI-X
        </h1>
        <p className="text-base text-slate-600 leading-relaxed">
          <strong>AGRI-X</strong> (Explainable AI-Based Crop Disease Detection and Agricultural Intelligence System) is an applied computer vision and machine learning engineering project designed to provide accurate disease diagnosis coupled with interpretable visual explanations for precision farming.
        </p>
      </div>

      
      <div className="bg-white p-8 rounded-3xl border border-sand-200 shadow-sm space-y-4">
        <h2 className="text-xl font-bold text-slate-900">Problem Statement & Motivation</h2>
        <p className="text-sm text-slate-600 leading-relaxed">
          Foliar crop diseases account for catastrophic yield loss across global tomato cultivation. While modern deep convolutional neural networks achieve superior classification metrics on laboratory benchmark datasets, they behave as opaque "black-box" systems. In field deployment, models frequently make correct classifications for entirely incorrect reasons (e.g., attending to background soil, grower fingers, or specular illumination).
        </p>
        <p className="text-sm text-slate-600 leading-relaxed">
          AGRI-X addresses this fundamental challenge by enforcing strict <strong>zero-leakage group-aware data splitting</strong> and integrating <strong>Grad-CAM</strong> visual attributions to make neural network decisions transparent and auditable for agricultural domain specialists.
        </p>
      </div>

      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-2xl border border-sand-200 shadow-sm space-y-3">
          <div className="w-10 h-10 rounded-xl bg-forest-50 text-forest-700 flex items-center justify-center">
            <Cpu className="w-5 h-5" />
          </div>
          <h3 className="text-base font-bold text-slate-900">ResNet18 Deep Neural Network</h3>
          <p className="text-xs text-slate-600 leading-relaxed">
            Pretrained on ImageNet and fine-tuned using a 2-stage transfer learning schedule on 18,146 cleaned PlantVillage tomato images across 10 disease categories. Validated on an untouched held-out test split.
          </p>
        </div>

        <div className="bg-white p-6 rounded-2xl border border-sand-200 shadow-sm space-y-3">
          <div className="w-10 h-10 rounded-xl bg-forest-50 text-forest-700 flex items-center justify-center">
            <Eye className="w-5 h-5" />
          </div>
          <h3 className="text-base font-bold text-slate-900">Grad-CAM Visual Attribution</h3>
          <p className="text-xs text-slate-600 leading-relaxed">
            Hooks the final convolutional layer (<code className="bg-sand-100 px-1 py-0.5 rounded text-slate-700 font-mono text-[11px]">layer4[-1]</code>) to compute spatial gradients of the predicted class score, generating normalized heatmaps overlaid on the input leaf photo.
          </p>
        </div>
      </div>

      
      <div className="bg-white p-8 rounded-3xl border border-sand-200 shadow-sm space-y-4">
        <h2 className="text-xl font-bold text-slate-900">End-to-End Technology Stack</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-sand-200 text-slate-400 uppercase tracking-wider">
                <th className="py-2.5 font-semibold">Tier</th>
                <th className="py-2.5 font-semibold">Technologies</th>
                <th className="py-2.5 font-semibold">Purpose</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-sand-100 text-slate-700">
              <tr>
                <td className="py-3 font-semibold text-slate-900">Frontend Web UI</td>
                <td>React, Vite, Tailwind CSS, Recharts, Lucide</td>
                <td>Interactive local AI dashboard and diagnostic scanner</td>
              </tr>
              <tr>
                <td className="py-3 font-semibold text-slate-900">Local Backend API</td>
                <td>FastAPI, Uvicorn, Pydantic</td>
                <td>Lightweight local HTTP communication layer to PyTorch</td>
              </tr>
              <tr>
                <td className="py-3 font-semibold text-slate-900">Machine Learning</td>
                <td>Python 3.12, PyTorch, Torchvision, Scikit-learn</td>
                <td>ResNet18 transfer learning, training loops & metrics</td>
              </tr>
              <tr>
                <td className="py-3 font-semibold text-slate-900">Explainability (XAI)</td>
                <td>PyTorch Forward/Backward Hooks, Grad-CAM, Matplotlib</td>
                <td>Gradient-weighted spatial lesion attribution heatmaps</td>
              </tr>
              <tr>
                <td className="py-3 font-semibold text-slate-900">Primary Dataset</td>
                <td>PlantVillage (10 Tomato Subsets)</td>
                <td>18,146 cleaned, de-duplicated foliar images</td>
              </tr>
              <tr>
                <td className="py-3 font-semibold text-slate-900">External Benchmark</td>
                <td>PlantDoc In-The-Wild Dataset</td>
                <td>Real-world cross-domain generalization stress testing</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      
      <div className="bg-white p-8 rounded-3xl border border-sand-200 shadow-sm space-y-4">
        <h2 className="text-xl font-bold text-slate-900">Project Development Status</h2>
        <div className="space-y-3 text-xs">
          <div className="flex items-center space-x-2 text-forest-700 font-semibold">
            <CheckCircle2 className="w-4 h-4 text-forest-600" />
            <span>Phase 1: Project Foundation & Multi-Device Utility (Complete)</span>
          </div>
          <div className="flex items-center space-x-2 text-forest-700 font-semibold">
            <CheckCircle2 className="w-4 h-4 text-forest-600" />
            <span>Phase 2: Dataset Preparation & ResNet18 Model Training (Complete - 98.4% Test Acc)</span>
          </div>
          <div className="flex items-center space-x-2 text-forest-700 font-semibold">
            <CheckCircle2 className="w-4 h-4 text-forest-600" />
            <span>Phase 3: Grad-CAM Explainable AI & Robustness Analysis (Complete)</span>
          </div>
          <div className="flex items-center space-x-2 text-forest-700 font-semibold">
            <CheckCircle2 className="w-4 h-4 text-forest-600" />
            <span>Phase 4: Complete React Frontend Application (Current)</span>
          </div>
          <div className="flex items-center space-x-2 text-slate-400">
            <span className="w-4 h-4 rounded-full border border-slate-300 flex items-center justify-center text-[9px]">5</span>
            <span>Phase 5: Local Python FastAPI Inference Integration (Upcoming)</span>
          </div>
          <div className="flex items-center space-x-2 text-slate-400">
            <span className="w-4 h-4 rounded-full border border-slate-300 flex items-center justify-center text-[9px]">6</span>
            <span>Phase 6: Project Report, Presentation & Viva Preparation (Upcoming)</span>
          </div>
        </div>
      </div>
    </div>
  );
};
