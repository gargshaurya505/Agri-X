import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { MainLayout } from './layouts/MainLayout';
import { LandingPage } from './pages/LandingPage';
import { DashboardPage } from './pages/DashboardPage';
import { DetectPage } from './pages/DetectPage';
import { ResultsPage } from './pages/ResultsPage';
import { DiseaseLibraryPage } from './pages/DiseaseLibraryPage';
import { DiseaseDetailsPage } from './pages/DiseaseDetailsPage';
import { HistoryPage } from './pages/HistoryPage';
import { AboutPage } from './pages/AboutPage';
import { NotFoundPage } from './pages/NotFoundPage';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<MainLayout />}>
          <Route index element={<LandingPage />} />
          <Route path="dashboard" element={<DashboardPage />} />
          <Route path="detect" element={<DetectPage />} />
          <Route path="results" element={<ResultsPage />} />
          <Route path="library" element={<DiseaseLibraryPage />} />
          <Route path="library/:slug" element={<DiseaseDetailsPage />} />
          <Route path="history" element={<HistoryPage />} />
          <Route path="about" element={<AboutPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
