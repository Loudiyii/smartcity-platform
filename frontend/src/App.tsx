import { BrowserRouter, Routes, Route, Link, useNavigate } from 'react-router-dom'
import { Dashboard } from './pages/Dashboard'
import { DashboardMap } from './pages/DashboardMap'
import { Predictions } from './pages/Predictions'
import { Mobility } from './pages/Mobility'
import { Analytics } from './pages/Analytics'
import { Reports } from './pages/Reports'
import MobilityImpact from './pages/MobilityImpact'
import Login from './pages/Login'
import Register from './pages/Register'
import ForgotPassword from './pages/ForgotPassword'
import { ProtectedRoute } from './components/ProtectedRoute'
import { isAuthenticated, getCurrentUser, useLogout } from './hooks/useAuth'
import './App.css'

function Header() {
  const navigate = useNavigate()
  const { mutate: logout } = useLogout()
  const user = getCurrentUser()
  const isAuth = isAuthenticated()

  const handleLogout = () => {
    logout(undefined, {
      onSuccess: () => {
        navigate('/login')
      }
    })
  }

  return (
    <header className="bg-white shadow">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between py-6">
          <h1 className="text-3xl font-bold text-gray-900">
            Smart City Paris
          </h1>
          <nav className="flex items-center gap-6">
            {/* Public pages */}
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
              to="/mobility"
              className="text-gray-700 hover:text-blue-600 font-medium transition-colors"
            >
              Mobilité
            </Link>

            {/* Protected pages - show with lock icon if not authenticated */}
            <Link
              to="/analytics"
              className="text-gray-700 hover:text-blue-600 font-medium transition-colors flex items-center gap-1"
            >
              Analyses {!isAuth && <span className="text-xs">🔒</span>}
            </Link>
            <Link
              to="/mobility-impact"
              className="text-gray-700 hover:text-blue-600 font-medium transition-colors flex items-center gap-1"
            >
              Impact Mobilité {!isAuth && <span className="text-xs">🔒</span>}
            </Link>
            <Link
              to="/reports"
              className="text-gray-700 hover:text-blue-600 font-medium transition-colors flex items-center gap-1"
            >
              Rapports {!isAuth && <span className="text-xs">🔒</span>}
            </Link>

            {/* Auth buttons */}
            <div className="ml-4 pl-4 border-l border-gray-300">
              {isAuth ? (
                <div className="flex items-center gap-4">
                  <span className="text-sm text-gray-600">
                    {user?.email}
                  </span>
                  <button
                    onClick={handleLogout}
                    className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-sm font-medium"
                  >
                    Déconnexion
                  </button>
                </div>
              ) : (
                <div className="flex items-center gap-3">
                  <Link
                    to="/login"
                    className="px-4 py-2 text-blue-600 hover:text-blue-700 font-medium transition-colors text-sm"
                  >
                    Connexion
                  </Link>
                  <Link
                    to="/register"
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
                  >
                    S'inscrire
                  </Link>
                </div>
              )}
            </div>
          </nav>
        </div>
      </div>
    </header>
  )
}

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-100">
        <Header />
        <main>
          <Routes>
            {/* Public routes (no auth required) */}
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />

            {/* Public pages - accessible to all citizens */}
            <Route path="/" element={<Dashboard />} />
            <Route path="/map" element={<DashboardMap />} />
            <Route path="/predictions" element={<Predictions />} />
            <Route path="/mobility" element={<Mobility />} />

            {/* Protected routes - require authentication (for Marie Dubois, Pierre Lambert) */}
            <Route
              path="/analytics"
              element={
                <ProtectedRoute>
                  <Analytics />
                </ProtectedRoute>
              }
            />
            <Route
              path="/mobility-impact"
              element={
                <ProtectedRoute>
                  <MobilityImpact />
                </ProtectedRoute>
              }
            />
            <Route
              path="/reports"
              element={
                <ProtectedRoute>
                  <Reports />
                </ProtectedRoute>
              }
            />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}

export default App
