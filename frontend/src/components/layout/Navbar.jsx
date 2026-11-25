import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  Sprout, 
  LayoutDashboard, 
  ScanSearch, 
  BookOpen, 
  History, 
  Info, 
  Menu, 
  X, 
  Activity,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';
import { healthCheck } from '../../services/predictionService';

export const Navbar = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [backendStatus, setBackendStatus] = useState({ checking: true, online: false });
  const location = useLocation();

  useEffect(() => {
    let isMounted = true;
    const checkService = async () => {
      try {
        await healthCheck();
        if (isMounted) setBackendStatus({ checking: false, online: true });
      } catch (err) {
        if (isMounted) setBackendStatus({ checking: false, online: false });
      }
    };
    checkService();
    const interval = setInterval(checkService, 15000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  const navLinks = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Detect Disease', path: '/detect', icon: ScanSearch },
    { name: 'Disease Library', path: '/library', icon: BookOpen },
    { name: 'History', path: '/history', icon: History },
    { name: 'About', path: '/about', icon: Info },
  ];

  const isActive = (path) => location.pathname === path;

  return (
    <header className="sticky top-0 z-50 bg-white/90 backdrop-blur-md border-b border-sand-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          <Link to="/" className="flex items-center space-x-2.5 group">
            <div className="w-10 h-10 rounded-xl bg-forest-700 flex items-center justify-center text-white shadow-sm group-hover:bg-forest-800 transition-colors">
              <Sprout className="w-5 h-5 text-emerald-300" />
            </div>
            <div>
              <span className="text-xl font-bold tracking-tight text-slate-900 group-hover:text-forest-800 transition-colors">
                AGRI<span className="text-forest-600">-X</span>
              </span>
              <span className="hidden sm:inline-block ml-2 text-xs font-medium px-2 py-0.5 bg-forest-50 text-forest-700 rounded-full border border-forest-200">
                XAI Tomato Core
              </span>
            </div>
          </Link>

          
          <nav className="hidden md:flex items-center space-x-1 lg:space-x-2">
            {navLinks.map((link) => {
              const Icon = link.icon;
              return (
                <Link
                  key={link.path}
                  to={link.path}
                  className={`flex items-center space-x-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                    isActive(link.path)
                      ? 'bg-forest-50 text-forest-800 font-semibold'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-sand-100'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive(link.path) ? 'text-forest-600' : 'text-slate-400'}`} />
                  <span>{link.name}</span>
                </Link>
              );
            })}
          </nav>

          
          <div className="hidden sm:flex items-center space-x-3">
            <div 
              className={`flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${
                backendStatus.online 
                  ? 'bg-emerald-50 text-emerald-700 border-emerald-200' 
                  : 'bg-amber-50 text-amber-700 border-amber-200'
              }`}
              title={backendStatus.online ? 'Local Python AI service connected' : 'Local Python AI service is offline (starts in Phase 5)'}
            >
              <span className={`w-2 h-2 rounded-full ${backendStatus.online ? 'bg-emerald-500 animate-pulse' : 'bg-amber-400'}`} />
              <span>{backendStatus.online ? 'Local AI Online' : 'AI Service Standby'}</span>
            </div>

            <Link
              to="/detect"
              className="inline-flex items-center space-x-1.5 px-4 py-2 rounded-lg text-sm font-semibold bg-forest-700 text-white hover:bg-forest-800 shadow-sm transition-colors"
            >
              <ScanSearch className="w-4 h-4" />
              <span>Analyze Leaf</span>
            </Link>
          </div>

          
          <div className="flex md:hidden">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-lg text-slate-600 hover:text-slate-900 hover:bg-sand-100 focus:outline-none"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      
      {mobileMenuOpen && (
        <div className="md:hidden border-b border-sand-200 bg-white px-4 pt-2 pb-4 space-y-1">
          {navLinks.map((link) => {
            const Icon = link.icon;
            return (
              <Link
                key={link.path}
                to={link.path}
                onClick={() => setMobileMenuOpen(false)}
                className={`flex items-center space-x-2 px-3 py-2.5 rounded-lg text-base font-medium ${
                  isActive(link.path)
                    ? 'bg-forest-50 text-forest-800 font-semibold'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-sand-100'
                }`}
              >
                <Icon className="w-5 h-5 text-forest-600" />
                <span>{link.name}</span>
              </Link>
            );
          })}
        </div>
      )}
    </header>
  );
};
