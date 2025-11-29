import React, { useState, useRef, useEffect } from 'react'
import { QRCodeSVG } from 'qrcode.react'
import api, { API_TOKEN } from '../utils/api'
import './DashboardPage.css'

function DashboardPage() {
  const [files, setFiles] = useState([])
  const [uploading, setUploading] = useState(false)
  const [uploadResults, setUploadResults] = useState([])
  const [recentFiles, setRecentFiles] = useState([])
  const [allFiles, setAllFiles] = useState([])
  const fileInputRef = useRef(null)
  const dropZoneRef = useRef(null)

  useEffect(() => {
    loadRecentFiles()
    loadAllFiles()
  }, [])

  const loadRecentFiles = async () => {
    try {
      const response = await api.get('/api/admin/files')
      const files = response.data.files || []
      // Get most recent 3 files
      setRecentFiles(files.slice(0, 3))
    } catch (error) {
      console.error('Error loading recent files:', error)
      // If unauthorized, just show empty state
      setRecentFiles([])
    }
  }

  const loadAllFiles = async () => {
    try {
      const response = await api.get('/api/admin/files')
      setAllFiles(response.data.files || [])
    } catch (error) {
      console.error('Error loading all files:', error)
      // If unauthorized, just show empty state
      setAllFiles([])
    }
  }

  const handleFileSelect = (selectedFiles) => {
    const fileArray = Array.from(selectedFiles).filter(file => {
      const ext = file.name.toLowerCase().split('.').pop()
      const allowed = ['pdf', 'jpg', 'jpeg', 'png']
      if (!allowed.includes(ext)) {
        alert(`${file.name} is not a supported file type. Please upload PDF, JPG, or PNG.`)
        return false
      }
      if (file.size > 20 * 1024 * 1024) {
        alert(`${file.name} exceeds 20MB size limit.`)
        return false
      }
      return true
    })
    setFiles(prev => [...prev, ...fileArray])
  }

  const handleDrop = (e) => {
    e.preventDefault()
    const droppedFiles = e.dataTransfer.files
    handleFileSelect(droppedFiles)
  }

  const handleDragOver = (e) => {
    e.preventDefault()
  }

  const handleUpload = async () => {
    if (files.length === 0) {
      alert('Please select at least one file to upload')
      return
    }

    setUploading(true)
    setUploadResults([])

    try {
      const formData = new FormData()
      files.forEach(file => {
        formData.append('files', file)
      })

      const response = await api.post('/api/upload-multiple', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })

      setUploadResults(response.data.results)
      
      // Clear files after successful upload
      setFiles([])
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }

      // Reload files
      loadRecentFiles()
      loadAllFiles()
    } catch (error) {
      console.error('Upload error:', error)
      alert('Upload failed: ' + (error.response?.data?.detail || error.message))
    } finally {
      setUploading(false)
    }
  }

  const removeFile = (index) => {
    setFiles(prev => prev.filter((_, i) => i !== index))
  }

  const downloadQR = (fileId) => {
    window.open(`${import.meta.env.VITE_API_URL}/api/generate-qr/${fileId}?token=${API_TOKEN}`, '_blank')
  }

  const getFileIcon = (filename) => {
    const ext = filename.toLowerCase().split('.').pop()
    if (['doc', 'docx'].includes(ext)) return '📄'
    if (['xls', 'xlsx'].includes(ext)) return '📊'
    if (['pdf'].includes(ext)) return '📕'
    if (['jpg', 'jpeg', 'png'].includes(ext)) return '🖼️'
    return '📁'
  }

  const formatFileSize = (bytes) => {
    if (!bytes) return 'N/A'
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A'
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
  }

  const getTimeAgo = (dateString) => {
    if (!dateString) return 'Unknown'
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now - date
    const diffMins = Math.floor(diffMs / 60000)
    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    const diffHours = Math.floor(diffMins / 60)
    if (diffHours < 24) return `${diffHours}h ago`
    const diffDays = Math.floor(diffHours / 24)
    return `${diffDays}d ago`
  }

  // Calculate storage stats
  const totalStorage = 8 * 1024 * 1024 * 1024 // 8 GB
  const usedStorage = allFiles.reduce((acc, file) => {
    // Estimate file size (we don't have actual size from API, so estimate)
    return acc + (2 * 1024 * 1024) // Assume 2MB average
  }, 0)
  const storagePercentage = (usedStorage / totalStorage) * 100

  return (
    <div className="dashboard-page">
      <div className="dashboard-container">
        {/* Welcome Section */}
        <div className="welcome-section">
          <h1 className="welcome-title">Welcome Back, User</h1>
        </div>

        <div className="dashboard-layout">
          {/* Main Content */}
          <div className="dashboard-main">
            {/* Recently Verified Section */}
            <div className="section-card">
              <div className="section-header">
                <h2 className="section-title">Recently Verified</h2>
                <a href="#" className="view-all-link">View All</a>
              </div>
              <div className="recent-files-grid">
                {recentFiles.length > 0 ? (
                  recentFiles.map((file, index) => (
                    <div key={file.id || index} className="file-card">
                      <div className="file-card-icon">
                        {getFileIcon(file.filename)}
                      </div>
                      <div className="file-card-info">
                        <h3 className="file-card-name">{file.filename}</h3>
                        <p className="file-card-meta">Edited {getTimeAgo(file.created_at)}</p>
                      </div>
                      <button className="file-card-menu">⋯</button>
                    </div>
                  ))
                ) : (
                  <p className="empty-state">No files yet. Upload your first document!</p>
                )}
              </div>
            </div>

            {/* Upload Files Section */}
            <div className="section-card">
              <div
                ref={dropZoneRef}
                className="upload-zone"
                onDrop={handleDrop}
                onDragOver={handleDragOver}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  multiple
                  accept=".pdf,.jpg,.jpeg,.png"
                  onChange={(e) => handleFileSelect(e.target.files)}
                  style={{ display: 'none' }}
                />
                <div className="upload-zone-content">
                  <div className="upload-icon-large">☁️</div>
                  <p className="upload-zone-text">
                    Drag and drop files, or <button className="browse-link" onClick={() => fileInputRef.current?.click()}>Browse</button>
                  </p>
                  <p className="upload-zone-hint">Supports PNG JPEG PDF JPG</p>
                </div>
              </div>

              {/* Selected Files */}
              {files.length > 0 && (
                <div className="selected-files">
                  {files.map((file, index) => (
                    <div key={index} className="selected-file-item">
                      <span>{file.name}</span>
                      <button onClick={() => removeFile(index)}>×</button>
                    </div>
                  ))}
                  <button
                    className="upload-button-primary"
                    onClick={handleUpload}
                    disabled={uploading}
                  >
                    {uploading ? 'Uploading...' : `Upload ${files.length} File(s)`}
                  </button>
                </div>
              )}

              {/* Upload Results */}
              {uploadResults.length > 0 && (
                <div className="upload-results-mini">
                  {uploadResults.map((result, index) => (
                    result.success && (
                      <div key={index} className="result-mini-card">
                        <div className="qr-mini">
                          <QRCodeSVG
                            value={JSON.stringify(result.qr_payload || { id: result.file_id })}
                            size={80}
                            level="H"
                          />
                        </div>
                        <div className="result-mini-info">
                          <p className="result-mini-name">{result.metadata?.file_name || 'Document'}</p>
                          <button
                            className="download-qr-btn"
                            onClick={() => downloadQR(result.file_id)}
                          >
                            Download QR
                          </button>
                        </div>
                      </div>
                    )
                  ))}
                </div>
              )}
            </div>

            {/* Your Files Table */}
            <div className="section-card">
              <div className="section-header">
                <h2 className="section-title">Your Files</h2>
                <a href="#" className="view-all-link">View All</a>
              </div>
              <div className="files-table-container">
                <table className="files-table">
                  <thead>
                    <tr>
                      <th>Name <span className="sort-icon">↕</span></th>
                      <th>Shared Users <span className="sort-icon">↕</span></th>
                      <th>File Size <span className="sort-icon">↕</span></th>
                      <th>Last Modified <span className="sort-icon">↕</span></th>
                      <th></th>
                    </tr>
                  </thead>
                  <tbody>
                    {allFiles.length > 0 ? (
                      allFiles.slice(0, 5).map((file, index) => (
                        <tr key={file.id || index}>
                          <td>
                            <div className="file-row-name">
                              <span className="file-icon">{getFileIcon(file.filename)}</span>
                              <span>{file.filename}</span>
                            </div>
                          </td>
                          <td>N/A</td>
                          <td>2.8 MB</td>
                          <td>{formatDate(file.created_at)}</td>
                          <td>
                            <button className="file-menu-btn">⋯</button>
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan="5" className="empty-table">No files yet</td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="dashboard-sidebar">
            {/* Storage Section */}
            <div className="sidebar-card">
              <div className="sidebar-header">
                <h3 className="sidebar-title">Storage</h3>
                <a href="#" className="view-details-link">View Details</a>
              </div>
              <div className="storage-progress">
                <div className="progress-bar">
                  <div 
                    className="progress-fill" 
                    style={{ width: `${Math.min(storagePercentage, 100)}%` }}
                  ></div>
                </div>
                <p className="storage-text">
                  {formatFileSize(usedStorage)} / {formatFileSize(totalStorage)}
                </p>
              </div>
              <button className="smart-optimizer-btn">Smart Optimizer</button>
            </div>

            {/* File Type Section */}
            <div className="sidebar-card">
              <div className="sidebar-header">
                <h3 className="sidebar-title">File Type</h3>
                <a href="#" className="view-details-link">View Details</a>
              </div>
              <div className="file-type-list">
                <div className="file-type-item">
                  <span className="file-type-icon">📄</span>
                  <div className="file-type-info">
                    <p className="file-type-name">Documents</p>
                    <p className="file-type-size">2.8 gb</p>
                  </div>
                </div>
                <div className="file-type-item">
                  <span className="file-type-icon">📹</span>
                  <div className="file-type-info">
                    <p className="file-type-name">Contracts and legals</p>
                    <p className="file-type-size">16.8 gb</p>
                  </div>
                </div>
                <div className="file-type-item">
                  <span className="file-type-icon">🏢</span>
                  <div className="file-type-info">
                    <p className="file-type-name">Business and Vendors</p>
                    <p className="file-type-size">4.4 gb</p>
                  </div>
                </div>
                <div className="file-type-item">
                  <span className="file-type-icon">🖼️</span>
                  <div className="file-type-info">
                    <p className="file-type-name">Photos</p>
                    <p className="file-type-size">9 gb</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Digilocker Section */}
            <div className="sidebar-card digilocker-card">
              <div className="digilocker-icon">📁⚙️</div>
              <h3 className="digilocker-title">Fetch Your Documents From Digilocker</h3>
              <p className="digilocker-desc">Import 50+ documents from Digilocker</p>
              <button className="digilocker-btn">Fetch from Digilocker</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default DashboardPage

