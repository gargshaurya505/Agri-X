import React, { useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { 
  BookOpen, 
  Search, 
  Filter, 
  ArrowRight, 
  ShieldAlert, 
  Microscope,
  CheckCircle2
} from 'lucide-react';
import { TOMATO_DISEASES } from '../data/diseases';

export const DiseaseLibraryPage = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');

  const categories = ['All', 'Fungal Disease', 'Bacterial Disease', 'Viral Disease', 'Arachnid Pest', 'Healthy'];

  const filteredDiseases = useMemo(() => {
    return TOMATO_DISEASES.filter((d) => {
      const matchesSearch = 
        d.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        d.scientific_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        d.description.toLowerCase().includes(searchQuery.toLowerCase());
      
      const matchesCategory = 
        selectedCategory === 'All' || d.category === selectedCategory;

      return matchesSearch && matchesCategory;
    });
  }, [searchQuery, selectedCategory]);

  return (
    <div className="space-y-8">
      
      <div className="max-w-2xl space-y-2">
        <h1 className="text-3xl font-extrabold tracking-tight text-slate-900">
          Tomato Pathology Clinical Library
        </h1>
        <p className="text-slate-600 text-sm">
          Comprehensive scientific descriptions, visible foliar symptoms, and agricultural prevention protocols for all 10 recognized classes.
        </p>
      </div>

      
      <div className="flex flex-col sm:flex-row gap-4 justify-between items-stretch sm:items-center bg-white p-4 rounded-2xl border border-sand-200 shadow-sm">
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search by disease or scientific name..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 text-sm bg-sand-50 rounded-xl border border-sand-200 focus:outline-none focus:ring-2 focus:ring-forest-500/20 focus:border-forest-500"
          />
        </div>

        <div className="flex items-center space-x-2 overflow-x-auto pb-1 sm:pb-0 custom-scrollbar">
          <Filter className="w-4 h-4 text-slate-400 flex-shrink-0" />
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition-colors ${
                selectedCategory === cat
                  ? 'bg-forest-700 text-white'
                  : 'bg-sand-100 text-slate-600 hover:bg-sand-200'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredDiseases.map((d) => (
          <Link
            key={d.id}
            to={`/library/${d.slug}`}
            className="group bg-white rounded-2xl border border-sand-200 hover:border-forest-300 hover:shadow-md transition-all p-6 flex flex-col justify-between"
          >
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-sand-100 text-slate-700">
                  {d.category}
                </span>
                <span className={`text-[11px] font-semibold ${
                  d.severity === 'Critical / Extreme' 
                    ? 'text-rose-600' 
                    : d.severity === 'None' 
                    ? 'text-emerald-600' 
                    : 'text-amber-600'
                }`}>
                  {d.severity}
                </span>
              </div>

              <div>
                <h3 className="text-lg font-bold text-slate-900 group-hover:text-forest-700 transition-colors">
                  {d.name}
                </h3>
                <p className="text-xs font-serif italic text-slate-500 mt-0.5">
                  {d.scientific_name}
                </p>
              </div>

              <p className="text-xs text-slate-600 line-clamp-3 leading-relaxed">
                {d.description}
              </p>
            </div>

            <div className="pt-4 mt-4 border-t border-sand-100 flex items-center justify-between text-xs font-semibold text-forest-700">
              <span>View Full Diagnosis & Treatments</span>
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
};
