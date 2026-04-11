import React, { useState } from 'react';
import './PrivacyPage.css';

const PrivacyPage = () => {
  const [permissions, setPermissions] = useState({
    documentStorage: true,
    autofill: true,
    schemeRecommendations: false,
    dataSharing: false,
  });

  const [advancedPrivacy, setAdvancedPrivacy] = useState(false);
  const [autoDelete, setAutoDelete] = useState(false);
  const [revealedFields, setRevealedFields] = useState({});
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  const [fieldPermissions, setFieldPermissions] = useState({
    fullName: true,
    dob: true,
    aadhaar: false,
    address: true,
  });

  const handlePermissionToggle = (key) => {
    setPermissions(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  const handleFieldToggle = (key) => {
    setFieldPermissions(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  const toggleReveal = (field) => {
    setRevealedFields(prev => ({
      ...prev,
      [field]: !prev[field]
    }));
  };

  const dataUsageLog = [
    { action: 'Scholarship Application Autofill', timestamp: 'Today, 2:45 PM', icon: '📋' },
    { action: 'KYC Verification', timestamp: 'Yesterday, 11:20 AM', icon: '✓' },
    { action: 'Scheme Eligibility Check', timestamp: '2 days ago, 3:15 PM', icon: '🔍' },
  ];

  return (
    <div className="privacy-page">
      {/* Header */}
      <header className="privacy-header">
        <div className="header-content">
          <h1>Privacy & Security Controls</h1>
          <p>Manage your personal data, permissions, and privacy settings</p>
        </div>
        <div className="header-badge">
          <span className="security-status">🔒 Secure</span>
        </div>
      </header>

      <main className="privacy-main">
        {/* Section 1: Consent Management */}
        <section className="privacy-section">
          <div className="section-header">
            <h2>🎯 Your Permissions</h2>
            <p>Control what Seva Setu can do with your data</p>
          </div>

          <div className="permissions-grid">
            {/* Permission Item 1 */}
            <div className="permission-item">
              <div className="permission-header">
                <div>
                  <h3>Secure Document Storage</h3>
                  <p>Store your documents safely in encrypted cloud storage</p>
                </div>
                <label className="toggle-switch">
                  <input
                    type="checkbox"
                    checked={permissions.documentStorage}
                    onChange={() => handlePermissionToggle('documentStorage')}
                  />
                  <span className="toggle-slider"></span>
                </label>
              </div>
            </div>

            {/* Permission Item 2 */}
            <div className="permission-item">
              <div className="permission-header">
                <div>
                  <h3>Autofill Across Government Forms</h3>
                  <p>Auto-populate your data in eligible government applications</p>
                </div>
                <label className="toggle-switch">
                  <input
                    type="checkbox"
                    checked={permissions.autofill}
                    onChange={() => handlePermissionToggle('autofill')}
                  />
                  <span className="toggle-slider"></span>
                </label>
              </div>
            </div>

            {/* Permission Item 3 */}
            <div className="permission-item">
              <div className="permission-header">
                <div>
                  <h3>Scheme Recommendations</h3>
                  <p>Receive personalized government scheme suggestions</p>
                </div>
                <label className="toggle-switch">
                  <input
                    type="checkbox"
                    checked={permissions.schemeRecommendations}
                    onChange={() => handlePermissionToggle('schemeRecommendations')}
                  />
                  <span className="toggle-slider"></span>
                </label>
              </div>
            </div>

            {/* Permission Item 4 */}
            <div className="permission-item">
              <div className="permission-header">
                <div>
                  <h3>Data Sharing with Government Portals</h3>
                  <p>Share verified data with authorized government applications</p>
                </div>
                <label className="toggle-switch">
                  <input
                    type="checkbox"
                    checked={permissions.dataSharing}
                    onChange={() => handlePermissionToggle('dataSharing')}
                  />
                  <span className="toggle-slider"></span>
                </label>
              </div>
            </div>
          </div>
        </section>

        {/* Section 2: Data Usage Transparency */}
        <section className="privacy-section">
          <div className="section-header">
            <h2>📊 Recent Data Usage</h2>
            <p>See how your data has been accessed and used</p>
          </div>

          <div className="data-usage-log">
            {dataUsageLog.map((log, index) => (
              <div key={index} className="usage-item">
                <div className="usage-icon">{log.icon}</div>
                <div className="usage-content">
                  <h4>{log.action}</h4>
                  <span className="usage-timestamp">⏰ {log.timestamp}</span>
                </div>
                <button className="view-details">View Details →</button>
              </div>
            ))}
          </div>
        </section>

        {/* Section 3: Sensitive Data Protection */}
        <section className="privacy-section">
          <div className="section-header">
            <h2>🔐 Protected Information</h2>
            <p>Your most sensitive data is masked for security</p>
          </div>

          <div className="sensitive-data-grid">
            {/* Aadhaar Masked */}
            <div className="sensitive-item">
              <div className="sensitive-header">
                <h3>Aadhaar Number</h3>
                <button
                  className={`reveal-btn ${revealedFields.aadhaar ? 'revealed' : ''}`}
                  onClick={() => toggleReveal('aadhaar')}
                  title="Click to reveal"
                >
                  ⚠️ {revealedFields.aadhaar ? 'Hide' : 'Reveal'}
                </button>
              </div>
              <div className="sensitive-value">
                {revealedFields.aadhaar ? '2323 4567 9123' : 'XXXX XXXX 9123'}
              </div>
              {revealedFields.aadhaar && <div className="reveal-warning">⚠️ Be careful when sharing sensitive information</div>}
            </div>

            {/* Phone Number Masked */}
            <div className="sensitive-item">
              <div className="sensitive-header">
                <h3>Phone Number</h3>
                <button
                  className={`reveal-btn ${revealedFields.phone ? 'revealed' : ''}`}
                  onClick={() => toggleReveal('phone')}
                  title="Click to reveal"
                >
                  ⚠️ {revealedFields.phone ? 'Hide' : 'Reveal'}
                </button>
              </div>
              <div className="sensitive-value">
                {revealedFields.phone ? '+91 9876543890' : 'XXXXXXX890'}
              </div>
              {revealedFields.phone && <div className="reveal-warning">⚠️ Be careful when sharing sensitive information</div>}
            </div>

            {/* Email Masked */}
            <div className="sensitive-item">
              <div className="sensitive-header">
                <h3>Email Address</h3>
                <button
                  className={`reveal-btn ${revealedFields.email ? 'revealed' : ''}`}
                  onClick={() => toggleReveal('email')}
                  title="Click to reveal"
                >
                  ⚠️ {revealedFields.email ? 'Hide' : 'Reveal'}
                </button>
              </div>
              <div className="sensitive-value">
                {revealedFields.email ? 'user.name@email.com' : 'user.n****@email.com'}
              </div>
              {revealedFields.email && <div className="reveal-warning">⚠️ Be careful when sharing sensitive information</div>}
            </div>
          </div>
        </section>

        {/* Section 4: Data Control Actions */}
        <section className="privacy-section">
          <div className="section-header">
            <h2>⚙️ Manage Your Data</h2>
            <p>Take full control of your personal information</p>
          </div>

          <div className="control-actions">
            <button className="action-btn action-btn-primary">
              ⬇️ Download My Data
            </button>

            <button className="action-btn action-btn-danger" onClick={() => setShowDeleteModal(true)}>
              🗑️ Delete All Data
            </button>
          </div>

          {/* Auto-delete Toggle */}
          <div className="autodelete-section">
            <div className="autodelete-header">
              <div>
                <h3>Auto Delete After 30 Days</h3>
                <p>Automatically clear your processor data after 30 days of inactivity</p>
              </div>
              <label className="toggle-switch">
                <input
                  type="checkbox"
                  checked={autoDelete}
                  onChange={() => setAutoDelete(!autoDelete)}
                />
                <span className="toggle-slider"></span>
              </label>
            </div>
          </div>
        </section>

        {/* Section 5: Privacy Mode */}
        <section className="privacy-section">
          <div className="section-header">
            <h2>🛡️ Advanced Privacy Mode</h2>
            <p>Enhanced privacy for temporary document processing</p>
          </div>

          <div className="privacy-mode-container">
            <div className="privacy-mode-info">
              <div className="privacy-mode-header">
                <h3>Process Without Saving</h3>
                <label className="toggle-switch">
                  <input
                    type="checkbox"
                    checked={advancedPrivacy}
                    onChange={() => setAdvancedPrivacy(!advancedPrivacy)}
                  />
                  <span className="toggle-slider"></span>
                </label>
              </div>
              <p>Your documents will be processed temporarily and deleted immediately after use. No copies or logs will be retained.</p>
            </div>

            {advancedPrivacy && (
              <div className="privacy-mode-badge">
                ✨ Advanced Privacy Mode is active
              </div>
            )}
          </div>
        </section>

        {/* Section 6: Field-Level Permissions */}
        <section className="privacy-section">
          <div className="section-header">
            <h2>🎚️ Control Specific Data Fields</h2>
            <p>Choose which personal data can be used in autofill and applications</p>
          </div>

          <div className="field-permissions">
            {[
              { key: 'fullName', label: 'Full Name', description: 'Your legal name' },
              { key: 'dob', label: 'Date of Birth', description: 'Your date of birth' },
              { key: 'aadhaar', label: 'Aadhaar Number', description: 'Your Aadhaar ID' },
              { key: 'address', label: 'Address', description: 'Your residential address' },
            ].map(field => (
              <div key={field.key} className="field-permission-item">
                <div className="field-checkbox-wrapper">
                  <input
                    type="checkbox"
                    id={field.key}
                    checked={fieldPermissions[field.key]}
                    onChange={() => handleFieldToggle(field.key)}
                    className="field-checkbox"
                  />
                  <label htmlFor={field.key} className="field-label">
                    <div>
                      <h4>{field.label}</h4>
                      <p>{field.description}</p>
                    </div>
                  </label>
                </div>
                <span className={`field-status ${fieldPermissions[field.key] ? 'enabled' : 'disabled'}`}>
                  {fieldPermissions[field.key] ? '✓ Enabled' : '✗ Disabled'}
                </span>
              </div>
            ))}
          </div>
        </section>

        {/* Section 7: Security Overview */}
        <section className="privacy-section">
          <div className="section-header">
            <h2>🔒 Security Overview</h2>
            <p>Your security status and protections</p>
          </div>

          <div className="security-badges">
            <div className="badge badge-success">
              <span className="badge-icon">✓</span>
              <div className="badge-content">
                <h4>End-to-End Encryption</h4>
                <p>All data is encrypted in transit and at rest</p>
              </div>
            </div>

            <div className="badge badge-success">
              <span className="badge-icon">✓</span>
              <div className="badge-content">
                <h4>Secure Storage Active</h4>
                <p>Your documents are stored in secure servers</p>
              </div>
            </div>

            <div className="badge badge-success">
              <span className="badge-icon">✓</span>
              <div className="badge-content">
                <h4>Last Security Check</h4>
                <p>Today at 10:30 AM - All systems nominal</p>
              </div>
            </div>
          </div>
        </section>
      </main>

      {/* Delete Confirmation Modal */}
      {showDeleteModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h2>⚠️ Delete All Data</h2>
              <button className="modal-close" onClick={() => setShowDeleteModal(false)}>✕</button>
            </div>
            <div className="modal-body">
              <p>Are you sure you want to permanently delete all your data?</p>
              <p className="modal-warning">This action cannot be undone. All documents, preferences, and history will be deleted.</p>
            </div>
            <div className="modal-footer">
              <button className="btn-secondary" onClick={() => setShowDeleteModal(false)}>Cancel</button>
              <button className="btn-danger">Permanently Delete</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PrivacyPage;
