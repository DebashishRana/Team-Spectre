import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import './Sidebar.css';

function Sidebar() {
  const location = useLocation();
  const isActive = (path) => location.pathname === path;

  return (
    <aside className="sidebar">
      <div className="sidebar-profile">
        <div className="profile-image">
          <img src="/logo.webp" alt="User" />
        </div>
        <div className="profile-info">
          <h3>Profile</h3>
          <p>APPID:AEK9718EAD</p>
        </div>
      </div>

      <nav className="sidebar-nav">
        <div className="nav-section">
          <h4 className="section-title">GENERAL</h4>
          <ul>
            <li className={isActive('/dashboard') ? 'active' : ''}>
              <Link to="/dashboard">
                <span className="icon">㗊</span> Dashboard
              </Link>
            </li>
            <li className={isActive('/documents') ? 'active' : ''}>
              <Link to="/documents">
                <span className="icon">📄</span> My Documents
              </Link>
            </li>
            <li className={isActive('/logs') ? 'active' : ''}>
              <Link to="/logs">
                <span className="icon">📋</span> Verification History
              </Link>
            </li>
            <li className={isActive('/applications') ? 'active' : ''}>
              <Link to="/applications">
                <span className="icon">🏛️</span> Apply to schemes
              </Link>
            </li>
            <li className={isActive('/schemes') ? 'active' : ''}>
              <Link to="/schemes">
                <span className="icon">🔍</span> Explore Schemes
              </Link>
            </li>
            <li className={isActive('/history') ? 'active' : ''}>
              <Link to="/history">
                <span className="icon">📝</span> Application logs
              </Link>
            </li>
          </ul>
        </div>

        <div className="nav-section">
          <h4 className="section-title">SERVICES</h4>
          <ul>
            <li className={isActive('/autofill') ? 'active' : ''}>
              <Link to="/autofill">
                <span className="icon">⚡</span> Whats new
              </Link>
            </li>
            <li className={isActive('/approvals') ? 'active' : ''}>
              <Link to="/approvals">
                <span className="icon">✅</span> Approvals
              </Link>
            </li>
            <li className={isActive('/connected-portals') ? 'active' : ''}>
              <Link to="/connected-portals">
                <span className="icon">🔗</span> Connected Portals
              </Link>
            </li>
          </ul>
        </div>

        <div className="nav-section">
          <h4 className="section-title">SETTINGS</h4>
          <ul>
            <li className={isActive('/security') ? 'active' : ''}>
              <Link to="/security">
                <span className="icon">🔒</span> Security
              </Link>
            </li>
            <li className={isActive('/privacy') ? 'active' : ''}>
              <Link to="/privacy">
                <span className="icon">🛡️</span> Data Privacy
              </Link>
            </li>
            <li className={isActive('/help') ? 'active' : ''}>
              <Link to="/help">
                <span className="icon">❓</span> Help Center
              </Link>
            </li>
          </ul>
        </div>
      </nav>
    </aside>
  );
}

export default Sidebar;