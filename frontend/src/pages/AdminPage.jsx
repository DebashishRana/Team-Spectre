import React, { useState, useEffect } from 'react'
import api from '../utils/api'
import './AdminPage.css'

function AdminPage() {
  const [password, setPassword] = useState('')
  const [authenticated, setAuthenticated] = useState(false)
  const [files, setFiles] = useState([])
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState('files')

  const ADMIN_PASSWORD = 'admin123' // Change this in production

  const handleLogin = (e) => {
    e.preventDefault()
    if (password === ADMIN_PASSWORD) {
      setAuthenticated(true)
      loadData()
    } else {
      alert('Incorrect password')
    }
  }

  const loadData = async () => {
    setLoading(true)
    try {
      const [filesRes, logsRes] = await Promise.all([
        api.get('/api/admin/files'),
        api.get('/api/admin/logs')
      ])
      setFiles(filesRes.data.files)
      setLogs(logsRes.data.logs)
    } catch (error) {
      console.error('Error loading data:', error)
      alert('Failed to load admin data')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (fileId) => {
    if (!window.confirm('Are you sure you want to delete this file?')) {
      return
    }

    try {
      await api.delete(`/api/admin/files/${fileId}`)
      alert('File deleted successfully')
      loadData()
    } catch (error) {
      console.error('Delete error:', error)
      alert('Failed to delete file')
    }
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleString()
  }

  if (!authenticated) {
    return (
      <div className="admin-page">
        <div className="login-container">
          <div className="login-card">
            <h2>Admin Login</h2>
            <form onSubmit={handleLogin}>
              <input
                type="password"
                placeholder="Enter admin password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="password-input"
                required
              />
              <button type="submit" className="login-button">
                Login
              </button>
            </form>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="admin-page">
      <div className="admin-container">
        <div className="admin-header">
          <h1 className="page-title">Admin Panel</h1>
          <button
            className="logout-button"
            onClick={() => {
              setAuthenticated(false)
              setPassword('')
            }}
          >
            Logout
          </button>
        </div>

        <div className="admin-tabs">
          <button
            className={`tab-button ${activeTab === 'files' ? 'active' : ''}`}
            onClick={() => setActiveTab('files')}
          >
            Files ({files.length})
          </button>
          <button
            className={`tab-button ${activeTab === 'logs' ? 'active' : ''}`}
            onClick={() => setActiveTab('logs')}
          >
            Scan Logs ({logs.length})
          </button>
        </div>

        {loading ? (
          <div className="loading-indicator">
            <div className="spinner"></div>
            <p>Loading...</p>
          </div>
        ) : (
          <>
            {activeTab === 'files' && (
              <div className="admin-content">
                <div className="table-container">
                  <table className="admin-table">
                    <thead>
                      <tr>
                        <th>File ID</th>
                        <th>Filename</th>
                        <th>Type</th>
                        <th>Uploaded</th>
                        <th>Expires</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {files.length === 0 ? (
                        <tr>
                          <td colSpan="6" className="empty-message">
                            No files uploaded yet
                          </td>
                        </tr>
                      ) : (
                        files.map((file) => (
                          <tr key={file.id}>
                            <td className="file-id">{file.id.substring(0, 8)}...</td>
                            <td>{file.filename}</td>
                            <td>
                              <span className="type-badge">{file.document_type}</span>
                            </td>
                            <td>{formatDate(file.created_at)}</td>
                            <td>{formatDate(file.expiry_time)}</td>
                            <td>
                              <button
                                className="delete-button"
                                onClick={() => handleDelete(file.id)}
                              >
                                Delete
                              </button>
                            </td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {activeTab === 'logs' && (
              <div className="admin-content">
                <div className="table-container">
                  <table className="admin-table">
                    <thead>
                      <tr>
                        <th>Timestamp</th>
                        <th>QR ID</th>
                        <th>Status</th>
                        <th>Error</th>
                      </tr>
                    </thead>
                    <tbody>
                      {logs.length === 0 ? (
                        <tr>
                          <td colSpan="4" className="empty-message">
                            No scan logs yet
                          </td>
                        </tr>
                      ) : (
                        logs.map((log) => (
                          <tr key={log.id}>
                            <td>{formatDate(log.scanned_at)}</td>
                            <td className="file-id">{log.qr_id.substring(0, 8)}...</td>
                            <td>
                              <span className={`status-badge ${log.success ? 'success' : 'error'}`}>
                                {log.success ? 'Success' : 'Failed'}
                              </span>
                            </td>
                            <td className="error-message">{log.error_message || '-'}</td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}

export default AdminPage

