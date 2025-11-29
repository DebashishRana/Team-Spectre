import React from 'react'
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom'
import Navbar from './components/Navbar'
import DashboardPage from './pages/DashboardPage'
import ScannerPage from './pages/ScannerPage'
import AdminPage from './pages/AdminPage'
import AboutPage from './pages/AboutPage'
import AuthPage from './pages/AuthPage'
import './App.css'

function AppContent() {
  const location = useLocation()
  const isAuthPage = location.pathname === '/' || location.pathname === '/auth' || location.pathname === '/login' || location.pathname === '/signup'

  return (
    <div className="app">
      {!isAuthPage && <Navbar />}
      <main className={`main-content ${isAuthPage ? 'auth-layout' : ''}`}>
        <Routes>
          <Route path="/" element={<AuthPage />} />
          <Route path="/auth" element={<AuthPage />} />
          <Route path="/login" element={<AuthPage />} />
          <Route path="/signup" element={<AuthPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/scan" element={<ScannerPage />} />
          <Route path="/admin" element={<AdminPage />} />
          <Route path="/about" element={<AboutPage />} />
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

