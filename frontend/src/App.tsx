import React from 'react'
import { Dashboard } from './pages/Dashboard'
import './App.css'

function App() {
  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4">
          <h1 className="text-3xl font-bold text-gray-900">
            Smart City Dashboard
          </h1>
        </div>
      </header>
      <main>
        <Dashboard />
      </main>
    </div>
  )
}

export default App
