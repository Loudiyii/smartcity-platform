import React from 'react'
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import { Dashboard } from './pages/Dashboard'
import { DashboardMap } from './pages/DashboardMap'
import { Predictions } from './pages/Predictions'
import { Analytics } from './pages/Analytics'
import './App.css'

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-100">
        <header className="bg-white shadow">
          <div className="max-w-7xl mx-auto px-4">
            <div className="flex items-center justify-between py-6">
              <h1 className="text-3xl font-bold text-gray-900">
                Smart City Paris
              </h1>
              <nav className="flex gap-6">
                <Link
                  to="/"
                  className="text-gray-700 hover:text-blue-600 font-medium transition-colors"
                >
                  Dashboard
                </Link>
                <Link
                  to="/map"
                  className="text-gray-700 hover:text-blue-600 font-medium transition-colors"
                >
                  Carte Interactive
                </Link>
                <Link
                  to="/predictions"
                  className="text-gray-700 hover:text-blue-600 font-medium transition-colors"
                >
                  Prédictions
                </Link>
                <Link
                  to="/analytics"
                  className="text-gray-700 hover:text-blue-600 font-medium transition-colors"
                >
                  Analyses
                </Link>
              </nav>
            </div>
          </div>
        </header>
        <main>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/map" element={<DashboardMap />} />
            <Route path="/predictions" element={<Predictions />} />
            <Route path="/analytics" element={<Analytics />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}

export default App
