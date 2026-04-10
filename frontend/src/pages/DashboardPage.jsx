import React, { useState, useRef } from 'react';
import './DashboardPage.css';

function DashboardPage() {
  const [applications] = useState([
    { id: 'APP-101', subject: 'Passport Renewal', date: 'June 15, 2025', progress: 60, assignees: ['/logo.webp', '/logo.webp'] },
    { id: 'DRV-102', subject: 'Driving License', date: 'July 01, 2025', progress: 75, assignees: ['/logo.webp', '/logo.webp', '/logo.webp'] },
    { id: 'SCH-201', subject: 'Scholarship App.', date: 'Aug 12, 2025', progress: 85, assignees: ['/logo.webp'] },
    { id: 'TAX-402', subject: 'Tax Filing (ITR)', date: 'Sept 22, 2025', progress: 60, assignees: ['/logo.webp', '/logo.webp'] },
    { id: 'VOTE-204', subject: 'Voter ID Update', date: 'Oct 02, 2025', progress: 75, assignees: ['/logo.webp'] }
  ]);

  const [ocrLoading, setOcrLoading] = useState(false);
  const [ocrData, setOcrData] = useState(null);
  const [ocrError, setOcrError] = useState('');
  const [ocrClassification, setOcrClassification] = useState(null);
  const [ocrValidation, setOcrValidation] = useState(null);
  const fileInputRef = useRef(null);

  const handleDigiUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setOcrLoading(true);
    setOcrData(null);
    setOcrError('');
    setOcrClassification(null);
    setOcrValidation(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:8000/api/extract-aadhaar', {
        method: 'POST',
        // Optional Authorization: 'Bearer ...'
        body: formData
      });
      const data = await response.json();
      if (response.ok && data.status === 'success') {
        setOcrClassification(data.classification || null);
        setOcrValidation(data.validation || null);
        setOcrData(data.data);
      } else {
        const detail = data?.detail;
        const message = typeof detail === 'string'
          ? detail
          : detail?.message || 'Uploaded document did not pass Aadhaar validation';
        setOcrClassification(detail?.classification || null);
        setOcrValidation(detail?.validation || null);
        setOcrError(message);
      }
    } catch (err) {
      console.error(err);
      setOcrError('Network error connecting to API');
    } finally {
      setOcrLoading(false);
    }
  };

  const closeOcrModal = () => setOcrData(null);

  return (
    <div className="dashboard-wrapper">
      {/* Top Navigation / Header */}
      <header className="dashboard-header">
        <div className="search-bar">
          <span className="search-icon">🔍</span>
          <input type="text" placeholder="Search documents, applications..." />
          <span className="search-shortcut">/</span>
        </div>
        <div className="header-actions">
          <div className="date-picker">
            <span className="calendar-icon">📅</span>
            <span>2026</span>
            <span className="chevron-down">⌄</span>
          </div>
          <button className="icon-btn bulb-btn">💡</button>
          <button className="icon-btn more-btn">...</button>
        </div>
      </header>

      {/* Top Stats Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-header">
            <div className="stat-icon-wrapper"><span className="stat-icon">📄</span></div>
            <span className="stat-title">Verified Documents <span className="stat-badge success">• Secure</span></span>
          </div>
          <div className="stat-value">12</div>
          <div className="stat-footer border-top">
            <div className="progress-container">
              <div className="progress-info">
                <span>Profile Completion</span>
                <span>100%</span>
              </div>
              <div className="progress-bar-bg">
                <div className="progress-bar-fill" style={{ width: '100%', backgroundColor: '#4285f4' }}></div>
              </div>
            </div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <div className="stat-icon-wrapper"><span className="stat-icon">🏛️</span></div>
            <span className="stat-title">Active Applications</span>
          </div>
          <div className="stat-value">3</div>
          <div className="stat-footer border-top">
            <div className="stat-footer-link" onClick={() => fileInputRef.current.click()} style={{cursor: 'pointer'}}>
              <button className="upload-action-btn" disabled={ocrLoading}>
                {ocrLoading ? 'Scanning...' : 'Upload'}
              </button>
            </div>
            <input
              type="file"
              accept="image/png, image/jpeg, image/jpg"
              ref={fileInputRef}
              style={{ display: 'none' }}
              onChange={handleDigiUpload}
            />
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <div className="stat-icon-wrapper"><span className="stat-icon">🔗</span></div>
            <span className="stat-title">Portals Connected</span>
          </div>
          <div className="stat-value">5</div>
          <div className="stat-footer border-top">
            <div className="stat-footer-link">
              <span>Manage Access</span>
              <span>→</span>
            </div>
          </div>
        </div>

        <div className="stat-card digilocker-card">
          <div className="stat-header">
            <div className="stat-icon-wrapper purple-bg"><span className="stat-icon">✅</span></div>
            <span className="stat-title">Import documents from Digilocker</span>
          </div>
          <div className="stat-value"></div>
          <div className="stat-footer border-top">
            <div className="stat-footer-link">
              <button 
                className="activate-action-btn"
                onClick={() => window.location.href = 'https://accounts.digitallocker.gov.in/signin/oauth_partner/%2Foauth2%2F1%2Fauthorize'}
              >
                <span className="activate-icon-circle">↑</span>
                Activate
              </button>
            </div>
          </div>
        </div>
      </div>

      {ocrData && (
        <div style={{ position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh', background: 'rgba(0,0,0,0.5)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div style={{ background: '#fff', padding: '2rem', borderRadius: '8px', minWidth: '400px', maxHeight: '80vh', overflowY: 'auto' }}>
            <h2 style={{ marginBottom: '1.5rem', color: '#333' }}>Aadhaar Extraction Results</h2>
            
            {ocrClassification && (
              <div style={{ background: '#e3f2fd', border: '1px solid #90caf9', borderRadius: '6px', padding: '1rem', marginBottom: '1rem' }}>
                <p style={{ margin: '0 0 0.5rem 0', fontWeight: '600' }}>
                  ✓ Classification: {ocrClassification.label}
                </p>
                <p style={{ margin: 0, fontSize: '14px', color: '#555' }}>
                  Confidence: {(ocrClassification.confidence * 100).toFixed(1)}% (Threshold: {(ocrClassification.threshold * 100).toFixed(0)}%)
                </p>
              </div>
            )}
            
            {ocrValidation && (
              <div style={{ background: ocrValidation.status === 'valid' ? '#f1f8e9' : '#ffe0e0', border: `1px solid ${ocrValidation.status === 'valid' ? '#c5e1a5' : '#ffcdd2'}`, borderRadius: '6px', padding: '1rem', marginBottom: '1rem' }}>
                <p style={{ margin: '0 0 0.5rem 0', fontWeight: '600' }}>
                  {ocrValidation.status === 'valid' ? '✓' : '⚠'} Validation: {ocrValidation.status}
                </p>
                <p style={{ margin: 0, fontSize: '14px', color: '#555' }}>
                  Confidence: {(ocrValidation.confidence * 100).toFixed(1)}% - {ocrValidation.reason}
                </p>
              </div>
            )}
            
            <div style={{ marginBottom: '1rem' }}>
              <p style={{ margin: '0.5rem 0', borderBottom: '1px solid #eee', paddingBottom: '0.5rem', color: '#000' }}>
                <strong>Aadhaar Number:</strong> {ocrData.aadhaar_numbers?.[0] || 'Not Found'}
              </p>
              <p style={{ margin: '0.5rem 0', borderBottom: '1px solid #eee', paddingBottom: '0.5rem', color: '#000' }}>
                <strong>Date of Birth:</strong> {ocrData.date_of_birth || 'Not Found'}
              </p>
              <p style={{ margin: '0.5rem 0', borderBottom: '1px solid #eee', paddingBottom: '0.5rem', color: '#000' }}>
                <strong>Address:</strong> {ocrData.address || 'Not Found'}
              </p>
              <p style={{ margin: '0.5rem 0', paddingBottom: '0.5rem', color: '#000' }}>
                <strong>Marital Status:</strong> {ocrData.marital_status || 'Not Found'}
              </p>
            </div>
            
            <button 
              onClick={closeOcrModal} 
              style={{ 
                marginTop: '1rem', 
                padding: '0.75rem 1.5rem', 
                background: '#4285f4', 
                color: '#fff', 
                border: 'none', 
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: '600'
              }}
            >
              Close
            </button>
          </div>
        </div>
      )}

      {ocrError && (
        <div style={{ marginTop: '12px', background: '#fff1f0', color: '#8a1c1c', border: '1px solid #ffd2d2', borderRadius: '10px', padding: '10px 12px' }}>
          <strong>Upload blocked:</strong> {ocrError}
          {ocrClassification && (
            <div style={{ marginTop: '6px', fontSize: '13px' }}>
              Classifier result: {ocrClassification.label} ({(ocrClassification.confidence * 100).toFixed(1)}%)
            </div>
          )}
        </div>
      )}

      {/* Middle Section */}
      <div className="middle-grid">
        {/* Report Analytics */}
        <div className="analytics-card">
          <div className="card-header">
            <h3>Document Usage Analytics</h3>
            <div className="time-filters">
              <button className="active">Daily</button>
              <button>Weekly</button>
              <button>Monthly</button>
            </div>
          </div>
          <div className="chart-area">
            <div className="y-axis">
              <span>24h</span>
              <span>16h</span>
              <span>8h</span>
              <span>4h</span>
              <span>0h</span>
            </div>
            <div className="chart-bars-bg">
              <div className="grid-lines">
                <div className="grid-line"></div>
                <div className="grid-line"></div>
                <div className="grid-line"></div>
                <div className="grid-line"></div>
                <div className="grid-line"></div>
              </div>
              <div className="bars-container">
                <div className="bar-wrapper">
                  <div className="bar default-bar" style={{ height: '30%' }}></div>
                  <span className="day-label">Mon</span>
                </div>
                <div className="bar-wrapper">
                  <div className="bar default-bar" style={{ height: '60%' }}></div>
                  <span className="day-label">Tues</span>
                </div>
                <div className="bar-wrapper">
                  <div className="bar default-bar" style={{ height: '40%' }}></div>
                  <span className="day-label">Wed</span>
                </div>
                <div className="bar-wrapper active-bar-wrapper">
                  <div className="tooltip">8 hard requests</div>
                  <div className="bar active-bar" style={{ height: '80%' }}></div>
                  <span className="day-label">Thurs</span>
                </div>
                <div className="bar-wrapper">
                  <div className="bar default-bar" style={{ height: '50%' }}></div>
                  <span className="day-label">Fri</span>
                </div>
                <div className="bar-wrapper">
                  <div className="bar default-bar" style={{ height: '35%' }}></div>
                  <span className="day-label">Sat</span>
                </div>
                <div className="bar-wrapper">
                  <div className="bar default-bar" style={{ height: '55%' }}></div>
                  <span className="day-label">Sun</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column in Middle Section */}
        <div className="right-middle-column">
          {/* Online Classes -> Active Applications */}
          <div className="classes-card">
            <div className="card-header">
              <h3>Active Applications</h3>
              <span className="status-dot-text"><span className="dot"></span> 2 Ongoing</span>
            </div>
            <div className="class-list">
              <div className="class-item">
                <div className="class-icon ph-icon">RTO</div>
                <div className="class-details">
                  <h4>Transport Dept</h4>
                  <p>Driving License Renewal</p>
                </div>
                <div className="class-meta">
                  <div className="time">Pending Form</div>
                  <div className="progress positive">⚡ 88%</div>
                </div>
              </div>
              <div className="class-item">
                <div className="class-icon lt-icon">MEA</div>
                <div className="class-details">
                  <h4>Ministry of Ext. Affairs</h4>
                  <p>Passport Renewal</p>
                </div>
                <div className="class-meta">
                  <div className="time">In Review</div>
                  <div className="progress positive">⚡ 85%</div>
                </div>
              </div>
            </div>
          </div>

          {/* Assignment Breakdown -> Verification Status */}
          <div className="breakdown-card">
            <div className="card-header">
              <h3>Verification Status</h3>
              <span className="info-icon">ℹ️</span>
            </div>
            <div className="breakdown-content">
              <div className="breakdown-bar-container">
                <div className="breakdown-segment submitted" style={{ width: '50%' }}></div>
                <div className="breakdown-segment review" style={{ width: '30%' }}></div>
                <div className="breakdown-segment remaining" style={{ width: '20%' }}></div>
              </div>
              <div className="breakdown-legend">
                <div className="legend-item"><span className="dot submitted-dot"></span> Verified</div>
                <div className="legend-item"><span className="dot review-dot"></span> Pending</div>
                <div className="legend-item"><span className="dot remaining-dot"></span> Rejected</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Section - Continue Watching -> Recent Applications */}
      <div className="table-card">
        <div className="card-header border-bottom">
          <h3>Recent Applications</h3>
          <div className="table-actions">
            <button className="icon-btn-sm search-tbl">🔍</button>
            <button className="icon-btn-sm">⋮</button>
          </div>
        </div>
        <div className="table-container">
          <table className="dashboard-table">
            <thead>
              <tr>
                <th><input type="checkbox" /></th>
                <th>Id</th>
                <th style={{ width: '20%' }}>Portal / Dept</th>
                <th>Date</th>
                <th>Completion</th>
                <th>Docs Attached</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {applications.map((app, idx) => (
                <tr key={idx}>
                  <td><input type="checkbox" /></td>
                  <td>{app.id}</td>
                  <td className="bold-cell">{app.subject}</td>
                  <td>{app.date}</td>
                  <td>
                    <div className="table-progress">
                      <div className="progress-bar-bg small">
                        <div className="progress-bar-fill" style={{ width: `${app.progress}%`, backgroundColor: '#4285f4' }}></div>
                      </div>
                      <span className="progress-text">{app.progress}%</span>
                    </div>
                  </td>
                  <td>
                    <div className="avatar-group">
                      {app.assignees.slice(0, 2).map((img, i) => (
                        <div key={i} className="avatar-sm"><img src={img} alt="Doc User" /></div>
                      ))}
                      {app.assignees.length > 2 && (
                        <div className="avatar-sm more">+{app.assignees.length - 2}</div>
                      )}
                    </div>
                  </td>
                  <td>
                    <div className="action-buttons">
                      <button className="icon-btn-sm">👁️</button>
                      <button className="icon-btn-sm">⋮</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default DashboardPage;