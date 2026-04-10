import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import './AuthPage.css'

function AuthPage() {
  const [isLogin, setIsLogin] = useState(false)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [username, setUsername] = useState('')
  const [country, setCountry] = useState('India')
  const [receiveUpdates, setReceiveUpdates] = useState(false)
  const [showWhatsIncluded, setShowWhatsIncluded] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    // Call the corresponding backend endpoint
    const url = isLogin ? 'http://localhost:8000/api/auth/login' : 'http://localhost:8000/api/auth/register';
    
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer seva-setu-portal-secret-token-change-in-production'
        },
        body: JSON.stringify({
          email,
          password,
          username: isLogin ? undefined : username,
          country: isLogin ? undefined : country,
          receive_updates: isLogin ? false : receiveUpdates
        })
      });

      const data = await response.json();
      
      if (response.ok) {
        console.log('Authentication successful:', data);
        navigate('/dashboard');
      } else {
        alert('Authentication failed: ' + (data.detail || 'Unknown error'));
      }
    } catch (error) {
      console.error('Error during authentication:', error);
      alert('Error connecting to authentication service.');
    }
  }

  const handleGoogleSignIn = () => {
    // Handle Google sign-in
    console.log('Google sign-in clicked')
    // In production, implement Google OAuth
    // For now, navigate to dashboard
    navigate('/dashboard')
  }

  const handleAppleSignIn = () => {
    // Handle Apple sign-in
    console.log('Apple sign-in clicked')
    // In production, implement Apple OAuth
    // For now, navigate to dashboard
    navigate('/dashboard')
  }

  const isValidPassword = (password) => {
    const hasMinLength = password.length >= 15 || (password.length >= 8 && /[0-9]/.test(password) && /[a-z]/.test(password))
    return hasMinLength
  }

  const isValidUsername = (username) => {
    const validPattern = /^[a-zA-Z0-9\-]+$/
    const validStart = !username.startsWith('-')
    const validEnd = !username.endsWith('-')
    return validPattern.test(username) && validStart && validEnd
  }

  return (
    <div className="auth-page">
      {/* Left Side - Dark Section */}
      <div className="auth-left">
        <div className="auth-left-content">
          <h1 className="auth-left-title">Unified Portal for Identity and governance </h1>
          <p className="auth-left-subtitle">
            Explore Unified Identity portal's core features for individuals and organizations.
          </p>
          <div className="auth-dropdown">
            <button 
              className="dropdown-button"
              onClick={() => setShowWhatsIncluded(!showWhatsIncluded)}
            >
              See what's included
              <svg 
                className={`dropdown-arrow ${showWhatsIncluded ? 'rotated' : ''}`}
                width="16" 
                height="16" 
                viewBox="0 0 24 24" 
                fill="none"
              >
                <path d="M6 9l6 6 6-6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </button>
            {showWhatsIncluded && (
              <div className="dropdown-content">
                <p>• Document verification</p>
                <p>• Secure storage</p>
                <p>• Quick scanning</p>
                <p>• Export capabilities</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Right Side - Form Section */}
      <div className="auth-right">
        <div className="auth-right-content">
          {/* Top Right Links */}
          <div className="auth-header">
            <p className="auth-toggle-text">
              {isLogin ? 'Don\'t have an account? ' : 'Already have an account? '}
              <button 
                type="button"
                onClick={() => setIsLogin(!isLogin)}
                className="auth-toggle-link"
              >
                {isLogin ? 'Sign up →' : 'Sign in →'}
              </button>
            </p>
          </div>

          {/* Main Form */}
          <div className="auth-form-container">
            <h1 className="auth-form-title">
              {isLogin ? 'Sign in to Unified Identity portal' : 'Sign up for Unified Identity portal'}
            </h1>

            {/* Social Login Buttons */}
            <div className="social-buttons">
              <button 
                type="button"
                onClick={handleGoogleSignIn}
                className="social-button google-button"
              >
                <svg className="social-icon" viewBox="0 0 24 24" width="20" height="20">
                  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                </svg>
                <span>Continue with Google</span>
              </button>

              <button 
                type="button"
                onClick={handleAppleSignIn}
                className="social-button apple-button"
              >
                <svg className="social-icon" viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
                  <path d="M17.05 20.28c-.98.95-2.05.88-3.08.4-1.09-.5-2.08-.48-3.24 0-1.44.62-2.2.44-3.06-.4C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.5-1.31 2.99-2.54 4.09l.01-.01zM12.03 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z"/>
                </svg>
                <span>Continue with Apple</span>
              </button>
            </div>

            {/* Separator */}
            <div className="auth-separator">
              <div className="separator-line"></div>
              <span className="separator-text">or</span>
              <div className="separator-line"></div>
            </div>

            {/* Form Fields */}
            <form onSubmit={handleSubmit} className="auth-form">
        
              {/* Email Field */}
              <div className="input-group">
                <label className="input-label">Email*</label>
                <input
                  type="email"
                  placeholder="Email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="auth-input"
                  required
                />
              </div>

              {/* Password Field */}
              <div className="input-group">
                <label className="input-label">Password*</label>
                <input
                  type="password"
                  placeholder="Password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="auth-input"
                  required
                />
                {!isLogin && (
                  <p className="input-hint">
                    Password should be at least 15 characters OR at least 8 characters including a number and a lowercase letter.
                  </p>
                )}
              </div>

              {/* Username Field (Sign up only) */}
              {!isLogin && (
                <div className="input-group">
                  <label className="input-label">Username*</label>
                  <input
                    type="text"
                    placeholder="Username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="auth-input"
                    required
                  />
                  <p className="input-hint">
                    Username may only contain alphanumeric characters or single hyphens, and cannot begin or end with a hyphen.
                  </p>
                </div>
              )}

              {/* Country Field (Sign up only) */}
              {!isLogin && (
                <div className="input-group">
                  <label className="input-label">Your Country/Region*</label>
                  <select
                    value={country}
                    onChange={(e) => setCountry(e.target.value)}
                    className="auth-select"
                    required
                  >
                    <option value="India">India</option>
                    <option value="United States">United States</option>
                    <option value="United Kingdom">United Kingdom</option>
                    <option value="Canada">Canada</option>
                    <option value="Australia">Australia</option>
                    <option value="Germany">Germany</option>
                    <option value="France">France</option>
                    <option value="Japan">Japan</option>
                    <option value="Other">Other</option>
                  </select>
                  <p className="input-hint compliance-text">
                    For compliance reasons, we're required to collect country information to send you occasional updates and announcements.
                  </p>
                </div>
              )}

              {/* Email Preferences (Sign up only) */}
              {!isLogin && (
                <div className="checkbox-group">
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={receiveUpdates}
                      onChange={(e) => setReceiveUpdates(e.target.checked)}
                      className="checkbox-input"
                    />
                    <span className="checkbox-text">Receive occasional product updates and announcements</span>
                  </label>
                </div>
              )}

              {/* Submit Button */}
              <button type="submit" className={`auth-submit-button ${isLogin ? 'login' : 'signup'}`}>
                {isLogin ? 'Sign In' : 'Sign Up'}
              </button>
            </form>

            {/* Legal Text */}
            {isLogin && (
              <p className="auth-legal">
                By signing in, you agree to our{' '}
                <a href="#" className="legal-link">Terms of Service</a> and{' '}
                <a href="#" className="legal-link">Privacy Statement</a>.
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default AuthPage

