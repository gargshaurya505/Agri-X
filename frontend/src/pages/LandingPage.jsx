import React from 'react';
import { Link } from 'react-router-dom';
import { 
  ScanSearch, 
  BookOpen, 
  Eye, 
  ShieldCheck, 
  Cpu, 
  ArrowRight, 
  CheckCircle2, 
  Microscope, 
  Sparkles,
  Layers,
  Activity
} from 'lucide-react';
import { TOMATO_DISEASES } from '../data/diseases';

export const LandingPage = () => {
  return (
    <div className="space-y-24 py-6">
      
      <section className="relative overflow-hidden rounded-3xl bg-gradient-to-b from-forest-900 via-forest-900 to-forest-950 text-white p-8 sm:p-14 lg:p-20 shadow-2xl">
        <div className="relative z-10 max-w-3xl space-y-6">
          <div className="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-xs font-semibold tracking-wide uppercase">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Explainable AI Agricultural Intelligence</span>
          </div>

          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight leading-tight">
            Detect. Understand. <span className="text-emerald-400">Protect.</span>
          </h1>

          <p className="text-lg sm:text-xl text-slate-300 leading-relaxed font-normal">
            AGRI-X is a local AI-powered agricultural diagnosis platform engineered to detect 10 tomato leaf pathologies with deep visual attribution heatmaps via Grad-CAM.
          </p>

          <div className="flex flex-wrap gap-4 pt-4">
            <Link
              to="/detect"
              className="inline-flex items-center space-x-2.5 px-6 py-3.5 rounded-xl font-semibold bg-emerald-500 text-forest-950 hover:bg-emerald-400 shadow-lg shadow-emerald-500/20 transition-all transform hover:-translate-y-0.5"
            >
              <ScanSearch className="w-5 h-5" />
              <span>Analyze a Leaf</span>
              <ArrowRight className="w-4 h-4" />
            </Link>

            <Link
              to="/library"
              className="inline-flex items-center space-x-2.5 px-6 py-3.5 rounded-xl font-semibold bg-white/10 hover:bg-white/15 text-white border border-white/20 backdrop-blur-sm transition-all"
            >
              <BookOpen className="w-5 h-5 text-emerald-300" />
              <span>Explore Diseases</span>
            </Link>
          </div>

          <div className="grid grid-cols-3 gap-6 pt-8 border-t border-white/10 text-slate-300">
            <div>
              <div className="text-2xl font-bold text-white">10</div>
              <div className="text-xs text-slate-400">Tomato Classes</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-white">Grad-CAM</div>
              <div className="text-xs text-slate-400">Visual Attribution</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-white">Local-First</div>
              <div className="text-xs text-slate-400">Zero Cloud Upload</div>
            </div>
          </div>
        </div>

        
        <div className="absolute top-0 right-0 -mt-16 -mr-16 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />
      </section>

      
      <section className="space-y-12">
        <div className="text-center max-w-2xl mx-auto space-y-3">
          <h2 className="text-xs font-semibold tracking-widest uppercase text-forest-700">Diagnostic Pipeline</h2>
          <h3 className="text-3xl font-bold tracking-tight text-slate-900">How AGRI-X Diagnoses Foliage</h3>
          <p className="text-slate-600 text-sm sm:text-base">
            From single-leaf photography to pixel-level attribution and agronomic guidance.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="bg-white p-8 rounded-2xl border border-sand-200 shadow-sm hover:shadow-md transition-shadow space-y-4">
            <div className="w-12 h-12 rounded-xl bg-forest-50 border border-forest-100 flex items-center justify-center text-forest-700 font-bold text-lg">
              1
            </div>
            <h4 className="text-lg font-bold text-slate-900">Upload Leaf Image</h4>
            <p className="text-slate-600 text-sm leading-relaxed">
              Capture or drag-and-drop a clear tomato leaf photograph. The image is preprocessed and resized locally on your machine.
            </p>
          </div>

          <div className="bg-white p-8 rounded-2xl border border-sand-200 shadow-sm hover:shadow-md transition-shadow space-y-4">
            <div className="w-12 h-12 rounded-xl bg-forest-50 border border-forest-100 flex items-center justify-center text-forest-700 font-bold text-lg">
              2
            </div>
            <h4 className="text-lg font-bold text-slate-900">ResNet18 Inference</h4>
            <p className="text-slate-600 text-sm leading-relaxed">
              Our fine-tuned ResNet18 convolutional neural network evaluates deep feature maps across all 10 candidate disease classifications.
            </p>
          </div>

          <div className="bg-white p-8 rounded-2xl border border-sand-200 shadow-sm hover:shadow-md transition-shadow space-y-4">
            <div className="w-12 h-12 rounded-xl bg-forest-50 border border-forest-100 flex items-center justify-center text-forest-700 font-bold text-lg">
              3
            </div>
            <h4 className="text-lg font-bold text-slate-900">Grad-CAM Heatmap & Advisory</h4>
            <p className="text-slate-600 text-sm leading-relaxed">
              Inspect gradient-weighted activation heatmaps pinpointing pathological lesions alongside actionable prevention protocols.
            </p>
          </div>
        </div>
      </section>

      
      <section className="bg-white rounded-3xl p-8 sm:p-12 border border-sand-200 shadow-sm grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
        <div className="space-y-6">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-emerald-50 text-forest-700 text-xs font-semibold">
            <Eye className="w-4 h-4 text-forest-600" />
            <span>Transparent Deep Learning</span>
          </div>
          <h3 className="text-3xl font-bold tracking-tight text-slate-900">
            Why Explainable AI Matters in Agriculture
          </h3>
          <p className="text-slate-600 text-sm sm:text-base leading-relaxed">
            Standard black-box AI classifiers often learn deceptive background correlations (such as lab bench color or greenhouse tags). AGRI-X integrates <strong>Grad-CAM</strong> to project spatial gradients from the final convolutional layer directly onto the leaf image.
          </p>
          <ul className="space-y-3 text-sm text-slate-700">
            <li className="flex items-start space-x-2.5">
              <CheckCircle2 className="w-5 h-5 text-forest-600 flex-shrink-0 mt-0.5" />
              <span>Verifies model focuses on necrosis, fungal stippling, or chlorosis instead of background cards.</span>
            </li>
            <li className="flex items-start space-x-2.5">
              <CheckCircle2 className="w-5 h-5 text-forest-600 flex-shrink-0 mt-0.5" />
              <span>Calibrated multi-class probability bar charts highlighting top alternative diagnoses.</span>
            </li>
            <li className="flex items-start space-x-2.5">
              <CheckCircle2 className="w-5 h-5 text-forest-600 flex-shrink-0 mt-0.5" />
              <span>Empowers farmers and researchers to trust and critically evaluate diagnostic suggestions.</span>
            </li>
          </ul>
          <div className="pt-2">
            <Link
              to="/about"
              className="inline-flex items-center space-x-2 text-forest-700 hover:text-forest-800 font-semibold text-sm"
            >
              <span>Learn more about our methodology</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>

        <div className="p-6 bg-sand-100 rounded-2xl border border-sand-300/80 space-y-4">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-700 pb-2 border-b border-sand-200">
            <span>Visual Attribution Demonstration</span>
            <span className="font-mono text-forest-700">layer4[-1] Target</span>
          </div>
          <div className="grid grid-cols-2 gap-3 text-center">
            <div className="space-y-1.5">
              <div className="h-44 bg-slate-200 rounded-xl overflow-hidden flex items-center justify-center border border-slate-300">
                <span className="text-xs text-slate-500 font-medium">Input Leaf Photo</span>
              </div>
              <span className="text-xs font-medium text-slate-600">Raw Photograph</span>
            </div>
            <div className="space-y-1.5">
              <div className="h-44 bg-gradient-to-br from-amber-200 via-rose-300 to-emerald-300 rounded-xl overflow-hidden flex items-center justify-center border border-slate-300">
                <span className="text-xs text-slate-900 font-bold bg-white/70 px-2 py-1 rounded">Grad-CAM Overlay</span>
              </div>
              <span className="text-xs font-medium text-slate-600">Attribution Heatmap</span>
            </div>
          </div>
          <p className="text-xs text-slate-500 text-center italic">
            Heatmaps indicate salient regions influencing prediction activations.
          </p>
        </div>
      </section>

      
      <section className="space-y-8">
        <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
          <div>
            <h2 className="text-xs font-semibold tracking-widest uppercase text-forest-700">Coverage</h2>
            <h3 className="text-2xl sm:text-3xl font-bold tracking-tight text-slate-900">Supported Tomato Pathologies</h3>
          </div>
          <Link
            to="/library"
            className="inline-flex items-center space-x-1.5 text-sm font-semibold text-forest-700 hover:text-forest-800"
          >
            <span>View Full Library</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
          {TOMATO_DISEASES.map((d) => (
            <Link
              key={d.id}
              to={`/library/${d.slug}`}
              className="group p-4 bg-white rounded-xl border border-sand-200 hover:border-forest-300 hover:shadow-md transition-all flex flex-col justify-between"
            >
              <div>
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-sand-100 text-slate-600 group-hover:bg-forest-50 group-hover:text-forest-700 transition-colors">
                  {d.category.split(' ')[0]}
                </span>
                <h4 className="mt-2 text-sm font-semibold text-slate-900 group-hover:text-forest-700 transition-colors">
                  {d.name}
                </h4>
              </div>
              <p className="mt-2 text-[11px] text-slate-500 italic truncate">
                {d.scientific_name}
              </p>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
};
