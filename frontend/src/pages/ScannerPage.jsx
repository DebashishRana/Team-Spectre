import React, { useState, useRef, useEffect } from 'react'
import Webcam from 'react-webcam'
import jsQR from 'jsqr'
import api from '../utils/api'
import './ScannerPage.css'

// Sound files (will fail gracefully if not present)
const successSound = '/sounds/success.wav'
const errorSound = '/sounds/error.wav'

function ScannerPage() {
  const [scanning, setScanning] = useState(false)
  const [scanResult, setScanResult] = useState(null)
  const [error, setError] = useState(null)
  const [processing, setProcessing] = useState(false)
  const webcamRef = useRef(null)
  const canvasRef = useRef(null)
  const scanIntervalRef = useRef(null)

  const playSound = (soundFile) => {
    try {
      const audio = new Audio(soundFile)
      audio.play().catch(e => console.log('Sound play failed:', e))
    } catch (e) {
      console.log('Sound error:', e)
    }
  }

  const processQRCode = async (qrData) => {
    if (processing) return
    
    setProcessing(true)
    setError(null)

    try {
      // Parse QR data
      let qrPayload
      try {
        qrPayload = JSON.parse(qrData)
      } catch {
        // If not JSON, try to extract from URL or other format
        qrPayload = { id: qrData, dl: qrData }
      }

      // Call API to get document info
      const response = await api.post('/api/scan-qr', qrPayload)

      setScanResult(response.data)
      playSound(successSound)
      stopScanning()
    } catch (err) {
      console.error('Scan error:', err)
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to process QR code'
      setError(errorMsg)
      playSound(errorSound)
    } finally {
      setProcessing(false)
    }
  }

  const captureAndScan = () => {
    if (!webcamRef.current || !canvasRef.current) return

    const video = webcamRef.current.video
    const canvas = canvasRef.current
    const context = canvas.getContext('2d')

    if (video.readyState === video.HAVE_ENOUGH_DATA) {
      canvas.width = video.videoWidth
      canvas.height = video.videoHeight
      context.drawImage(video, 0, 0, canvas.width, canvas.height)

      const imageData = context.getImageData(0, 0, canvas.width, canvas.height)
      const code = jsQR(imageData.data, imageData.width, imageData.height)

      if (code) {
        processQRCode(code.data)
      }
    }
  }

  const startScanning = () => {
    setScanning(true)
    setScanResult(null)
    setError(null)
    
    scanIntervalRef.current = setInterval(() => {
      if (!processing) {
        captureAndScan()
      }
    }, 500) // Scan every 500ms
  }

  const stopScanning = () => {
    setScanning(false)
    if (scanIntervalRef.current) {
      clearInterval(scanIntervalRef.current)
      scanIntervalRef.current = null
    }
  }

  const resetScan = () => {
    stopScanning()
    setScanResult(null)
    setError(null)
    setProcessing(false)
  }

  useEffect(() => {
    return () => {
      if (scanIntervalRef.current) {
        clearInterval(scanIntervalRef.current)
      }
    }
  }, [])

  const downloadDocument = () => {
    if (scanResult?.download_link) {
      window.open(scanResult.download_link, '_blank')
    }
  }

  return (
    <div className="scanner-page">
      <div className="scanner-container">
        <h1 className="page-title">QR Code Scanner</h1>
        <p className="page-subtitle">Scan QR codes to access and verify documents</p>

        {!scanResult ? (
          <div className="scanner-section">
            <div className="camera-container">
              {scanning ? (
                <div className="camera-wrapper">
                  <Webcam
                    ref={webcamRef}
                    audio={false}
                    screenshotFormat="image/jpeg"
                    videoConstraints={{
                      facingMode: 'environment' // Use back camera on mobile
                    }}
                    className="webcam"
                  />
                  <canvas ref={canvasRef} style={{ display: 'none' }} />
                  <div className="scan-overlay">
                    <div className="scan-frame"></div>
                    <p className="scan-hint">Position QR code within the frame</p>
                  </div>
                </div>
              ) : (
                <div className="camera-placeholder">
                  <svg className="camera-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z" />
                    <circle cx="12" cy="13" r="4" />
                  </svg>
                  <p>Camera not active</p>
                </div>
              )}

              <div className="camera-controls">
                {!scanning ? (
                  <button
                    className="scan-button"
                    onClick={startScanning}
                    disabled={processing}
                  >
                    Start Scanning
                  </button>
                ) : (
                  <button
                    className="stop-button"
                    onClick={stopScanning}
                    disabled={processing}
                  >
                    Stop Scanning
                  </button>
                )}
              </div>
            </div>

            {error && (
              <div className="error-card">
                <h3>Scan Error</h3>
                <p>{error}</p>
                <button className="retry-button" onClick={resetScan}>
                  Try Again
                </button>
              </div>
            )}

            {processing && (
              <div className="processing-indicator">
                <div className="spinner"></div>
                <p>Processing QR code...</p>
              </div>
            )}
          </div>
        ) : (
          <div className="scan-result">
            <div className="result-header-section">
              <h2>Document Verified</h2>
              <button className="reset-button" onClick={resetScan}>
                Scan Another
              </button>
            </div>

            <div className="result-card">
              <div className="result-header">
                <h3>{scanResult.filename}</h3>
                <span className={`status-badge ${scanResult.validation?.status || 'unknown'}`}>
                  {scanResult.validation?.status || 'Unknown'}
                </span>
              </div>

              <div className="document-info">
                <div className="info-section">
                  <h4>Document Type</h4>
                  <p>{scanResult.document_type || 'Unknown'}</p>
                </div>

                {scanResult.metadata && (
                  <>
                    {scanResult.metadata.holder_name && (
                      <div className="info-section">
                        <h4>Name</h4>
                        <p>{scanResult.metadata.holder_name}</p>
                      </div>
                    )}

                    {scanResult.metadata.pan_numbers && (
                      <div className="info-section">
                        <h4>PAN Number</h4>
                        <p>{scanResult.metadata.pan_numbers[0]}</p>
                      </div>
                    )}

                    {scanResult.metadata.aadhaar_numbers && (
                      <div className="info-section">
                        <h4>Aadhaar Number</h4>
                        <p>{scanResult.metadata.aadhaar_numbers[0]}</p>
                      </div>
                    )}

                    {scanResult.metadata.date_of_birth && (
                      <div className="info-section">
                        <h4>Date of Birth</h4>
                        <p>{scanResult.metadata.date_of_birth}</p>
                      </div>
                    )}

                    {scanResult.metadata.gender && (
                      <div className="info-section">
                        <h4>Gender</h4>
                        <p>{scanResult.metadata.gender}</p>
                      </div>
                    )}
                  </>
                )}

                {scanResult.validation && (
                  <div className="validation-section">
                    <h4>Validation Result</h4>
                    <div className="validation-details">
                      <p><strong>Status:</strong> {scanResult.validation.status}</p>
                      <p><strong>Confidence:</strong> {(scanResult.validation.confidence * 100).toFixed(1)}%</p>
                      <p><strong>Reason:</strong> {scanResult.validation.reason}</p>
                    </div>
                  </div>
                )}
              </div>

              <div className="result-actions">
                <button className="download-button" onClick={downloadDocument}>
                  Download Document
                </button>
                <button
                  className="copy-button"
                  onClick={() => navigator.clipboard.writeText(scanResult.download_link)}
                >
                  Copy Link
                </button>
              </div>

              <div className="result-footer">
                <p>File ID: {scanResult.file_id}</p>
                <p>Expires: {new Date(scanResult.expiry_time).toLocaleString()}</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default ScannerPage

