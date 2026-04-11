import React, { useState, useEffect } from 'react';
import './ProfilePage.css';

function ProfilePage() {
  const [userProfile, setUserProfile] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({});

  useEffect(() => {
    // Load user profile from localStorage
    const savedProfile = localStorage.getItem('userProfile');
    if (savedProfile) {
      try {
        const profile = JSON.parse(savedProfile);
        setUserProfile(profile);
        setFormData(profile);
      } catch (e) {
        console.error('Failed to parse user profile:', e);
        setUserProfile({
          firstName: 'User',
          lastName: 'Profile',
          email: 'user@example.com',
          phoneNumber: '+91 XXXXX XXXXX',
          username: 'username',
          country: 'India',
          dob: '',
          address: '',
          aadhaarCard: ''
        });
      }
    } else {
      setUserProfile({
        firstName: 'User',
        lastName: 'Profile',
        email: 'user@example.com',
        phoneNumber: '+91 XXXXX XXXXX',
        username: 'username',
        country: 'India',
        dob: '',
        address: '',
        aadhaarCard: ''
      });
    }
  }, []);

  const handleEdit = () => {
    setIsEditing(true);
  };

  const handleCancel = () => {
    setIsEditing(false);
    setFormData(userProfile);
  };

  const handleSave = () => {
    localStorage.setItem('userProfile', JSON.stringify(formData));
    setUserProfile(formData);
    setIsEditing(false);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  if (!userProfile) {
    return <div className="profile-loading">Loading profile...</div>;
  }

  const fullName = `${userProfile.firstName} ${userProfile.lastName}`;
  const isAadhaarVerified = userProfile.aadhaarCard && userProfile.aadhaarCard.length > 0;

  return (
    <div className="profile-container">
      {/* Header */}
      <div className="profile-header">
        <div className="profile-avatar">
          <div className="avatar-placeholder">{userProfile.firstName.charAt(0)}{userProfile.lastName.charAt(0)}</div>
        </div>
        <div className="profile-header-info">
          <h1>{fullName}</h1>
          {isAadhaarVerified && <span className="verified-badge">✓ Verified Profile</span>}
          <p className="start-date">Started using Seva Setu Portal</p>
        </div>
        <button 
          className="edit-btn"
          onClick={handleEdit}
          disabled={isEditing}
        >
          ✏️ Edit
        </button>
      </div>

      {/* Profile Details Card */}
      <div className="profile-card">
        <div className="card-header">
          <h2>Profile Details</h2>
        </div>

        {isEditing ? (
          <form className="profile-form edit-mode">
            <div className="form-row">
              <div className="form-group">
                <label>Full Name</label>
                <input
                  type="text"
                  name="firstName"
                  value={formData.firstName}
                  onChange={handleInputChange}
                  placeholder="First Name"
                />
              </div>
              <div className="form-group">
                <input
                  type="text"
                  name="lastName"
                  value={formData.lastName}
                  onChange={handleInputChange}
                  placeholder="Last Name"
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Email</label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  disabled
                />
              </div>
              <div className="form-group">
                <label>Status</label>
                <span className="email-verified">✓ Email Verified</span>
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Phone Number</label>
                <input
                  type="tel"
                  name="phoneNumber"
                  value={formData.phoneNumber}
                  onChange={handleInputChange}
                />
              </div>
              <div className="form-group">
                <label>Status</label>
                <span className="number-verified">✓ Number Verified</span>
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Username</label>
                <input
                  type="text"
                  name="username"
                  value={formData.username}
                  onChange={handleInputChange}
                />
              </div>
              <div className="form-group">
                <label>Plan</label>
                <span className="plan-badge">Pro Plan</span>
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>CPF/CNPJ (Aadhaar)</label>
                <input
                  type="text"
                  name="aadhaarCard"
                  value={formData.aadhaarCard}
                  onChange={handleInputChange}
                  placeholder="Extracted from Aadhaar"
                  disabled
                />
              </div>
              <div className="form-group">
                <label>ZIP/CEP Code</label>
                <input
                  type="text"
                  name="country"
                  value={formData.country}
                  onChange={handleInputChange}
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Address</label>
                <textarea
                  name="address"
                  value={formData.address}
                  onChange={handleInputChange}
                  placeholder="Extracted from Aadhaar"
                  rows="3"
                />
              </div>
              <div className="form-group">
                <label>City</label>
                <input
                  type="text"
                  name="aadhaarCity"
                  value={formData.aadhaarCity || ''}
                  onChange={handleInputChange}
                  placeholder="City from Aadhaar"
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Date of Birth (DOB)</label>
                <input
                  type="date"
                  name="dob"
                  value={formData.dob}
                  onChange={handleInputChange}
                />
              </div>
            </div>

            <div className="form-actions">
              <button type="button" className="btn-save" onClick={handleSave}>
                Save Changes
              </button>
              <button type="button" className="btn-cancel" onClick={handleCancel}>
                Cancel
              </button>
            </div>
          </form>
        ) : (
          <div className="profile-details">
            <div className="details-grid">
              {/* Row 1 */}
              <div className="detail-item">
                <div className="detail-icon">👤</div>
                <div className="detail-content">
                  <span className="detail-label">Full Name</span>
                  <span className="detail-value">{fullName}</span>
                </div>
              </div>

              <div className="detail-item">
                <div className="detail-icon">✉️</div>
                <div className="detail-content">
                  <span className="detail-label">Email</span>
                  <span className="detail-value">{userProfile.email}</span>
                  <span className="verified-icon">✓ Email Verified</span>
                </div>
              </div>

              <div className="detail-item">
                <div className="detail-icon">📅</div>
                <div className="detail-content">
                  <span className="detail-label">Date of Birth</span>
                  <span className="detail-value">{userProfile.dob || 'Not available'}</span>
                </div>
              </div>

              {/* Row 2 */}
              <div className="detail-item">
                <div className="detail-icon">👤</div>
                <div className="detail-content">
                  <span className="detail-label">Username</span>
                  <span className="detail-value">{userProfile.username}</span>
                </div>
              </div>

              <div className="detail-item">
                <div className="detail-icon">📞</div>
                <div className="detail-content">
                  <span className="detail-label">Phone Number</span>
                  <span className="detail-value">{userProfile.phoneNumber}</span>
                  <span className="verified-icon">✓ Number Verified</span>
                </div>
              </div>

              <div className="detail-item">
                <div className="detail-icon">📋</div>
                <div className="detail-content">
                  <span className="detail-label">Plan Type</span>
                  <span className="detail-value">Pro Plan</span>
                </div>
              </div>

              {/* Row 3 - Aadhaar Data */}
              <div className="detail-item">
                <div className="detail-icon">🆔</div>
                <div className="detail-content">
                  <span className="detail-label">Aadhaar Number</span>
                  <span className="detail-value">{userProfile.aadhaarCard || 'Not verified'}</span>
                </div>
              </div>

              <div className="detail-item">
                <div className="detail-icon">🏘️</div>
                <div className="detail-content">
                  <span className="detail-label">Address</span>
                  <span className="detail-value multi-line">{userProfile.address || 'Not available'}</span>
                </div>
              </div>

              <div className="detail-item">
                <div className="detail-icon">🌍</div>
                <div className="detail-content">
                  <span className="detail-label">Country/Region</span>
                  <span className="detail-value">{userProfile.country}</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Aadhaar Verification Status */}
      {isAadhaarVerified && (
        <div className="aadhaar-status-card">
          <div className="status-header">
            <h3>🆔 Aadhaar Verification Status</h3>
            <span className="status-badge verified">Verified ✓</span>
          </div>
          <div className="status-content">
            <p>Your Aadhaar has been successfully verified and your profile has been automatically updated with extracted information including:</p>
            <ul>
              <li>✓ Date of Birth</li>
              <li>✓ Address Details</li>
              <li>✓ Aadhaar Number</li>
            </ul>
            <p className="status-update-time">Last updated: {new Date().toLocaleString()}</p>
          </div>
        </div>
      )}
    </div>
  );
}

export default ProfilePage;
