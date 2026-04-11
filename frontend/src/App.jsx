import React from 'react'
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import DashboardPage from './pages/DashboardPage'
import ScannerPage from './pages/ScannerPage'
import SchemesPage from './pages/SchemesPage'
import AdminPage from './pages/AdminPage'
import AboutPage from './pages/AboutPage'
import AuthPage from './pages/AuthPage'
import VerificationLogsPage from './pages/VerificationLogsPage'
import ProfilePage from './pages/ProfilePage'
import ApprovalsPage from './pages/ApprovalsPage'
import ConnectedPortalsPage from './pages/ConnectedPortalsPage'
import PrivacyPage from './pages/PrivacyPage'
import './App.css'

function AppContent() {
  const location = useLocation()
  const isAuthPage = location.pathname === '/' || location.pathname === '/auth' || location.pathname === '/login' || location.pathname === '/signup'

  // If we are in auth page, don't show sidebar
  if (isAuthPage) {
    return (
      <main className="auth-layout">
        <Routes>
          <Route path="/" element={<AuthPage />} />
          <Route path="/auth" element={<AuthPage />} />
          <Route path="/login" element={<AuthPage />} />
          <Route path="/signup" element={<AuthPage />} />
        </Routes>
      </main>
    )
  }

  return (
    <div className="app-container">
      <Sidebar />
      <main className="main-content">
        <Routes>
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/privacy" element={<PrivacyPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/scan" element={<ScannerPage />} />
          <Route path="/schemes" element={<SchemesPage />} />
          <Route path="/logs" element={<VerificationLogsPage />} />
          <Route path="/admin" element={<AdminPage />} />
          <Route path="/about" element={<AboutPage />} />
          <Route path="/approvals" element={<ApprovalsPage />} />
          <Route path="/connected-portals" element={<ConnectedPortalsPage />} />
        </Routes>
      </main>
    </div>
  )
}

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  )
}

export default App

