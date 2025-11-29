import React, { useState, useRef } from 'react'
import { QRCodeSVG } from 'qrcode.react'
import api, { API_TOKEN } from '../utils/api'
import './UploadPage.css'

function UploadPage() {
  const [files, setFiles] = useState([])
  const [uploading, setUploading] = useState(false)
  const [uploadResults, setUploadResults] = useState([])
  const [selectedFile, setSelectedFile] = useState(null)
  const fileInputRef = useRef(null)
  const dropZoneRef = useRef(null)

  const playSound = (soundFile) => {
    try {
      const audio = new Audio(soundFile)
      audio.play().catch(e => console.log('Sound play failed:', e))
    } catch (e) {
      console.log('Sound error:', e)
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
      playSound(uploadSound)
      
      // Clear files after successful upload
      setFiles([])
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
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
    window.open(`/api/generate-qr/${fileId}?token=${API_TOKEN}`, '_blank')
  }

  return (
    <div className="upload-page">
      <div className="upload-container">
        <h1 className="page-title">Upload Documents</h1>
        <p className="page-subtitle">Upload PDF or image documents (Aadhaar, PAN, or any ID)</p>

        {/* Drop Zone */}
        <div
          ref={dropZoneRef}
          className="drop-zone"
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
          <div className="drop-zone-content">
            <svg className="upload-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="17 8 12 3 7 8" />
              <line x1="12" y1="3" x2="12" y2="15" />
            </svg>
            <p className="drop-zone-text">
              Drag and drop files here, or{' '}
              <button
                className="link-button"
                onClick={() => fileInputRef.current?.click()}
              >
                browse
              </button>
            </p>
            <p className="drop-zone-hint">
              Supports PDF, JPG, PNG (Max 20MB per file)
            </p>
          </div>
        </div>

        {/* File List */}
        {files.length > 0 && (
          <div className="file-list">
            <h3>Selected Files ({files.length})</h3>
            {files.map((file, index) => (
              <div key={index} className="file-item">
                <span className="file-name">{file.name}</span>
                <span className="file-size">
                  {(file.size / 1024 / 1024).toFixed(2)} MB
                </span>
                <button
                  className="remove-button"
                  onClick={() => removeFile(index)}
                >
                  ×
                </button>
              </div>
            ))}
            <button
              className="upload-button"
              onClick={handleUpload}
              disabled={uploading}
            >
              {uploading ? 'Uploading...' : `Upload ${files.length} File(s)`}
            </button>
          </div>
        )}

        {/* Upload Results */}
        {uploadResults.length > 0 && (
          <div className="upload-results">
            <h2>Upload Results</h2>
            <div className="results-grid">
              {uploadResults.map((result, index) => {
                if (!result.success) {
                  return (
                    <div key={index} className="result-card error">
                      <h3>{result.filename}</h3>
                      <p className="error-message">{result.error}</p>
                    </div>
                  )
                }

                const qrPayload = result.qr_payload || {
                  id: result.file_id,
                  dl: result.share_link,
                  timestamp: new Date().toISOString()
                }

                return (
                  <div key={index} className="result-card success">
                    <div className="result-header">
                      <h3>{result.metadata?.file_name || 'Document'}</h3>
                      <span className="doc-type-badge">
                        {result.metadata?.document_type || 'Unknown'}
                      </span>
                    </div>
                    
                    {result.metadata && (
                      <div className="metadata-preview">
                        {result.metadata.holder_name && (
                          <p><strong>Name:</strong> {result.metadata.holder_name}</p>
                        )}
                        {result.metadata.pan_numbers && (
                          <p><strong>PAN:</strong> {result.metadata.pan_numbers[0]}</p>
                        )}
                        {result.metadata.aadhaar_numbers && (
                          <p><strong>Aadhaar:</strong> {result.metadata.aadhaar_numbers[0]}</p>
                        )}
                        {result.metadata.date_of_birth && (
                          <p><strong>DOB:</strong> {result.metadata.date_of_birth}</p>
                        )}
                      </div>
                    )}

                    <div className="qr-section">
                      <div className="qr-code-container">
                        <QRCodeSVG
                          value={JSON.stringify(qrPayload)}
                          size={200}
                          level="H"
                          includeMargin={true}
                        />
                      </div>
                      <div className="qr-actions">
                        <button
                          className="action-button"
                          onClick={() => downloadQR(result.file_id)}
                        >
                          Download QR
                        </button>
                        <button
                          className="action-button secondary"
                          onClick={() => navigator.clipboard.writeText(result.share_link)}
                        >
                          Copy Link
                        </button>
                      </div>
                    </div>

                    <div className="result-footer">
                      <p className="file-id">ID: {result.file_id}</p>
                      <p className="expiry">
                        Expires: {new Date(result.expiry_time).toLocaleString()}
                      </p>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default UploadPage

