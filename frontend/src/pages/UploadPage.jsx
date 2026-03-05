import React, { useState, useRef } from 'react'
import { QRCodeSVG } from 'qrcode.react'
import api, { API_TOKEN } from '../utils/api'
import './UploadPage.css'

function UploadPage() {
  const [files, setFiles] = useState([])
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [uploadResults, setUploadResults] = useState([])
  const [detectingDocument, setDetectingDocument] = useState(false)
  const [selectedFile, setSelectedFile] = useState(null)
  const fileInputRef = useRef(null)
  const dropZoneRef = useRef(null)
  const detectTimeoutRef = useRef(null)
  const progressIntervalRef = useRef(null)

  const DEMO_UPLOAD = (import.meta.env.VITE_DEMO_UPLOAD ?? 'true') === 'true'

  const displayDocType = (rawType) => {
    if (!rawType) return 'Aadhaar Card'
    const normalized = String(rawType).trim().toLowerCase()
    if (normalized.startsWith('pan')) return 'Aadhaar Card'
    return rawType
  }

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
    setUploadProgress(0)
    setUploadResults([])
    setDetectingDocument(false)

    if (detectTimeoutRef.current) {
      clearTimeout(detectTimeoutRef.current)
      detectTimeoutRef.current = null
    }

    try {
      if (DEMO_UPLOAD) {
        if (progressIntervalRef.current) {
          clearInterval(progressIntervalRef.current)
          progressIntervalRef.current = null
        }

        setDetectingDocument(true)
        const startedAt = Date.now()
        const durationMs = 3200

        await new Promise((resolve) => {
          const tick = () => {
            const elapsed = Date.now() - startedAt
            const pct = Math.min(100, Math.round((elapsed / durationMs) * 100))
            setUploadProgress(pct)
            if (pct >= 100) {
              if (progressIntervalRef.current) {
                clearInterval(progressIntervalRef.current)
                progressIntervalRef.current = null
              }
              resolve()
            }
          }

          progressIntervalRef.current = setInterval(tick, 75)
          tick()
        })

        const now = Date.now()
        const results = files.map((file, index) => {
          const fileId = `demo_${now}_${index}`
          const shareLink = `https://demo.veriquick.local/share/${fileId}`
          return {
            success: true,
            filename: file.name,
            file_id: fileId,
            share_link: shareLink,
            expiry_time: new Date(now + 24 * 60 * 60 * 1000).toISOString(),
            metadata: {
              file_name: file.name,
              document_type: 'Aadhaar Card',
              holder_name: 'Demo User',
              pan_numbers: ['ABCDE1234F']
            },
            qr_payload: {
              id: fileId,
              doc_type: 'Aadhaar Card',
              link: shareLink
            }
          }
        })

        setDetectingDocument(false)
        setUploadResults(results)

        setFiles([])
        if (fileInputRef.current) {
          fileInputRef.current.value = ''
        }

        return
      }

      // Phase 1: Request SAS URLs for all files
      const filesInfo = files.map(file => ({
        filename: file.name,
        content_type: file.type || 'application/octet-stream'
      }))

      const sasResponse = await api.post('/api/upload-multiple', filesInfo)
      const sasResults = sasResponse.data.results

      // Phase 2: Upload each file directly to Azure using SAS URL
      const uploadPromises = sasResults.map(async (sasResult, index) => {
        if (!sasResult.success) {
          return sasResult
        }

        const file = files[index]
        const { upload_url, file_id, filename } = sasResult

        try {
          // Upload file directly to Azure Blob using PUT
          const uploadResponse = await fetch(upload_url, {
            method: 'PUT',
            headers: {
              'x-ms-blob-type': 'BlockBlob',
              'Content-Type': file.type || 'application/octet-stream'
            },
            body: file
          })

          if (!uploadResponse.ok) {
            throw new Error(`Azure upload failed: ${uploadResponse.statusText}`)
          }

          return { file_id, filename, success: true }
        } catch (error) {
          console.error(`Upload error for ${filename}:`, error)
          return {
            file_id,
            filename,
            success: false,
            error: error.message
          }
        }
      })

      const uploadStatuses = await Promise.all(uploadPromises)

      // Phase 3: Complete uploads (process and verify)
      const successfulFileIds = uploadStatuses
        .filter(status => status.success)
        .map(status => status.file_id)

      let finalResults

      if (successfulFileIds.length > 0) {
        const completeResponse = await api.post('/api/upload-multiple-complete', successfulFileIds)
        finalResults = completeResponse.data.results
      } else {
        finalResults = uploadStatuses
      }

      setUploadResults(finalResults)
      // Simulated/UX step: show “Detecting document…” briefly before rendering QR
      if ((finalResults || []).some(r => r?.success)) {
        setDetectingDocument(true)
        detectTimeoutRef.current = setTimeout(() => {
          setDetectingDocument(false)
          detectTimeoutRef.current = null
        }, 4000)
      }
      
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
      setUploadProgress(0)
    }
  }

  const removeFile = (index) => {
    setFiles(prev => prev.filter((_, i) => i !== index))
  }

  const downloadQR = async (fileId) => {
    if (DEMO_UPLOAD) {
      const svgId = `qr-${fileId}`
      const svg = document.getElementById(svgId)
      if (!svg) return
      const serializer = new XMLSerializer()
      let source = serializer.serializeToString(svg)
      if (!source.includes('xmlns=')) {
        source = source.replace('<svg', '<svg xmlns="http://www.w3.org/2000/svg"')
      }

      const svgBlob = new Blob([source], { type: 'image/svg+xml;charset=utf-8' })
      const svgUrl = URL.createObjectURL(svgBlob)
      const img = new Image()

      const width = Number(svg.getAttribute('width')) || 260
      const height = Number(svg.getAttribute('height')) || 260
      const scale = 4

      await new Promise((resolve, reject) => {
        img.onload = resolve
        img.onerror = reject
        img.src = svgUrl
      })

      const canvas = document.createElement('canvas')
      canvas.width = width * scale
      canvas.height = height * scale
      const ctx = canvas.getContext('2d')
      if (!ctx) return

      ctx.fillStyle = '#ffffff'
      ctx.fillRect(0, 0, canvas.width, canvas.height)
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height)

      URL.revokeObjectURL(svgUrl)

      const jpgBlob = await new Promise((resolve) => {
        canvas.toBlob((b) => resolve(b), 'image/jpeg', 0.92)
      })

      if (!jpgBlob) return
      const jpgUrl = URL.createObjectURL(jpgBlob)
      const link = document.createElement('a')
      link.href = jpgUrl
      link.download = `${fileId}.jpg`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(jpgUrl)
      return
    }

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
              {uploading ? 'Detecting document...' : `Upload ${files.length} File(s)`}
            </button>

            {uploading && (
              <div className="upload-progress">
                <p className="upload-progress-text">Detecting document...</p>
                <div className="progress-bar">
                  <div className="progress-fill" style={{ width: `${uploadProgress}%` }} />
                </div>
              </div>
            )}
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

                const docTypeLabel = displayDocType(result.metadata?.document_type)

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
                        Document type: {docTypeLabel}
                      </span>
                    </div>

                    {detectingDocument ? (
                      <div className="detecting-indicator">
                        <div className="spinner"></div>
                        <p>Detecting document...</p>
                      </div>
                    ) : (
                      <>
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
                              id={`qr-${result.file_id}`}
                              value={JSON.stringify(qrPayload)}
                              size={260}
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
                      </>
                    )}
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

