import React from 'react'
import './AboutPage.css'

function AboutPage() {
  return (
    <div className="about-page">
      <div className="about-container">
        <div className="about-header">
          <h1 className="page-title">About VeriQuickX</h1>
          <p className="page-subtitle">
            A comprehensive document verification and QR code management system
          </p>
        </div>

        <div className="about-content">
          <section className="about-section">
            <h2>Overview</h2>
            <p>
              VeriQuickX is a full-stack application designed to streamline document
              verification processes. It allows users to upload identity documents
              (Aadhaar, PAN, and other IDs), generate secure QR codes for easy access,
              and verify document authenticity through advanced validation algorithms.
            </p>
          </section>

          <section className="about-section">
            <h2>Features</h2>
            <div className="features-grid">
              <div className="feature-card">
                <h3>📄 Document Upload</h3>
                <p>
                  Upload PDF or image documents with support for multiple file formats.
                  Automatic metadata extraction from Aadhaar and PAN cards.
                </p>
              </div>

              <div className="feature-card">
                <h3>🔐 Secure Storage</h3>
                <p>
                  Documents are securely stored in Dropbox with configurable expiry
                  times. Direct download links are generated for easy access.
                </p>
              </div>

              <div className="feature-card">
                <h3>📱 QR Code Generation</h3>
                <p>
                  Generate unique QR codes for each document with embedded metadata.
                  QR codes can be downloaded and shared for easy access.
                </p>
              </div>

              <div className="feature-card">
                <h3>📷 QR Scanner</h3>
                <p>
                  Scan QR codes using your device's camera. Automatic document
                  retrieval and metadata display with validation results.
                </p>
              </div>

              <div className="feature-card">
                <h3>✅ Document Validation</h3>
                <p>
                  Advanced validation algorithms for PAN and Aadhaar cards including
                  format checks, checksum validation, and QR code verification.
                </p>
              </div>

              <div className="feature-card">
                <h3>👨‍💼 Admin Panel</h3>
                <p>
                  Comprehensive admin interface for managing uploaded files, viewing
                  scan logs, and monitoring system activity.
                </p>
              </div>
            </div>
          </section>

          <section className="about-section">
            <h2>Technology Stack</h2>
            <div className="tech-stack">
              <div className="tech-category">
                <h3>Frontend</h3>
                <ul>
                  <li>React 18</li>
                  <li>React Router</li>
                  <li>Vite</li>
                  <li>CSS3</li>
                  <li>jsQR for QR scanning</li>
                  <li>react-webcam for camera access</li>
                </ul>
              </div>

              <div className="tech-category">
                <h3>Backend</h3>
                <ul>
                  <li>FastAPI</li>
                  <li>Python 3.10+</li>
                  <li>SQLite</li>
                  <li>Dropbox SDK</li>
                  <li>PyPDF2 & pdfplumber</li>
                  <li>OpenCV & Pyzbar</li>
                  <li>Pillow & Tesseract OCR</li>
                </ul>
              </div>
            </div>
          </section>

          <section className="about-section">
            <h2>Document Types Supported</h2>
            <div className="doc-types">
              <div className="doc-type-card">
                <h3>PAN Card</h3>
                <ul>
                  <li>PAN number extraction</li>
                  <li>Name and DOB extraction</li>
                  <li>Format validation</li>
                  <li>Checksum verification</li>
                </ul>
              </div>

              <div className="doc-type-card">
                <h3>Aadhaar Card</h3>
                <ul>
                  <li>Aadhaar number extraction (masked)</li>
                  <li>Name, DOB, Gender extraction</li>
                  <li>QR code validation</li>
                  <li>XML signature verification</li>
                </ul>
              </div>
            </div>
          </section>

          <section className="about-section">
            <h2>Security Features</h2>
            <ul className="security-list">
              <li>Token-based API authentication</li>
              <li>Password-protected admin panel</li>
              <li>Expiring download links (configurable)</li>
              <li>Secure file storage in Dropbox</li>
              <li>Encrypted QR payloads</li>
              <li>Comprehensive logging system</li>
            </ul>
          </section>

          <section className="about-section">
            <h2>Getting Started</h2>
            <div className="getting-started">
              <h3>Backend Setup</h3>
              <pre className="code-block">
{`cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your Dropbox token
python main.py`}
              </pre>

              <h3>Frontend Setup</h3>
              <pre className="code-block">
{`cd frontend
npm install
npm run dev`}
              </pre>
            </div>
          </section>

          <section className="about-section">
            <h2>API Documentation</h2>
            <p>
              The API is available at <code>http://localhost:8000</code> when the
              backend is running. All endpoints require Bearer token authentication.
            </p>
            <div className="api-endpoints">
              <div className="endpoint">
                <code>POST /api/upload</code>
                <p>Upload a single document</p>
              </div>
              <div className="endpoint">
                <code>POST /api/upload-multiple</code>
                <p>Upload multiple documents</p>
              </div>
              <div className="endpoint">
                <code>GET /api/generate-qr/{'{file_id}'}</code>
                <p>Generate QR code image for a file</p>
              </div>
              <div className="endpoint">
                <code>POST /api/scan-qr</code>
                <p>Process scanned QR code</p>
              </div>
              <div className="endpoint">
                <code>GET /api/admin/files</code>
                <p>List all uploaded files (admin)</p>
              </div>
              <div className="endpoint">
                <code>DELETE /api/admin/files/{'{file_id}'}</code>
                <p>Delete a file (admin)</p>
              </div>
            </div>
          </section>

          <section className="about-section">
            <h2>License & Copyright</h2>
            <p>
              © 2025 VeriQuickX. All rights reserved.
              <br />
              This is proprietary software. Permission required to edit and modify.
            </p>
          </section>
        </div>
      </div>
    </div>
  )
}

export default AboutPage

