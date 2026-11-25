import React from 'react';
import { Link } from 'react-router-dom';
import { AlertCircle, ArrowLeft } from 'lucide-react';

export const NotFoundPage = () => {
  return (
    <div className="max-w-md mx-auto text-center py-20 space-y-4">
      <AlertCircle className="w-14 h-14 text-slate-400 mx-auto" />
      <h1 className="text-4xl font-extrabold text-slate-900">404</h1>
      <h2 className="text-lg font-bold text-slate-700">Page Not Found</h2>
      <p className="text-sm text-slate-500">
        The route you navigated to does not exist in the AGRI-X platform.
      </p>
      <Link
        to="/"
        className="inline-flex items-center space-x-2 px-4 py-2 bg-forest-700 text-white rounded-xl text-sm font-semibold hover:bg-forest-800"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Return to Home</span>
      </Link>
    </div>
  );
};
