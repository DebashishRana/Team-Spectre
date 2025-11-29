# VeriQuickX Project Structure

## Complete File Tree

```
Veriquick Cloud/
│
├── backend/                          # Python FastAPI Backend
│   ├── main.py                       # Main FastAPI application
│   ├── config.py                     # Configuration settings
│   ├── document_processor.py         # Document processing & metadata extraction
│   ├── validators.py                 # Document validation functions
│   ├── requirements.txt              # Python dependencies
│   ├── .env.example                  # Environment variables template
│   ├── .env                          # Environment variables (create from .env.example)
│   └── veriquickx.db                 # SQLite database (auto-created)
│
├── frontend/                         # React Frontend
│   ├── src/
│   │   ├── components/               # Reusable React components
│   │   │   ├── Navbar.jsx            # Navigation bar component
│   │   │   └── Navbar.css            # Navbar styles
│   │   │
│   │   ├── pages/                    # Page components
│   │   │   ├── UploadPage.jsx        # Document upload page
│   │   │   ├── UploadPage.css        # Upload page styles
│   │   │   ├── ScannerPage.jsx       # QR code scanner page
│   │   │   ├── ScannerPage.css       # Scanner page styles
│   │   │   ├── AdminPage.jsx         # Admin panel page
│   │   │   ├── AdminPage.css         # Admin page styles
│   │   │   ├── AboutPage.jsx         # About/documentation page
│   │   │   └── AboutPage.css         # About page styles
│   │   │
│   │   ├── utils/                    # Utility functions
│   │   │   └── api.js                # API client configuration
│   │   │
│   │   ├── App.jsx                   # Main app component with routing
│   │   ├── App.css                   # App-level styles
│   │   ├── main.jsx                  # React entry point
│   │   └── index.css                 # Global styles
│   │
│   ├── public/                       # Static assets
│   │   ├── sounds/                   # Sound effects directory
│   │   │   ├── success.wav          # Success sound (user-provided)
│   │   │   ├── error.wav            # Error sound (user-provided)
│   │   │   └── upload.wav           # Upload sound (user-provided)
│   │   └── logo.png                  # Logo file (user-provided)
│   │
│   ├── index.html                    # HTML template
│   ├── package.json                  # Node.js dependencies
│   ├── vite.config.js                # Vite configuration
│   └── .env.local                    # Frontend environment variables
│
├── .gitignore                        # Git ignore rules
├── README.md                          # Main documentation
├── DEPLOYMENT.md                      # Deployment guide
├── PROJECT_STRUCTURE.md              # This file
├── setup.py                           # Setup script
└── Veriquick_server_proto.py         # Original reference file
```

## Key Files Explained

### Backend Files

- **main.py**: FastAPI application with all API endpoints
  - File upload endpoints
  - QR code generation
  - Document scanning
  - Admin endpoints
  - Database operations

- **config.py**: Configuration management
  - Dropbox token
  - API security tokens
  - CORS settings
  - File upload limits

- **document_processor.py**: Document processing logic
  - PDF parsing (PyPDF2, pdfplumber)
  - Image OCR (Tesseract)
  - QR code extraction
  - PAN/Aadhaar detection
  - Metadata extraction

- **validators.py**: Document validation
  - PAN number validation (format + checksum)
  - Aadhaar validation
  - QR code validation
  - Document integrity checks

### Frontend Files

- **App.jsx**: Main application component
  - React Router setup
  - Route definitions
  - Layout structure

- **pages/UploadPage.jsx**: Document upload interface
  - Drag & drop file upload
  - Multi-file support
  - QR code display
  - Metadata preview

- **pages/ScannerPage.jsx**: QR code scanner
  - Webcam integration
  - Real-time QR detection
  - Document retrieval
  - Validation display

- **pages/AdminPage.jsx**: Admin interface
  - File management
  - Scan logs
  - Delete operations

- **pages/AboutPage.jsx**: Documentation page
  - Feature overview
  - API documentation
  - Setup instructions

- **utils/api.js**: API client
  - Axios configuration
  - Token management
  - Error handling

## Database Schema

### uploads Table
```sql
CREATE TABLE uploads (
    id TEXT PRIMARY KEY,              -- UUID
    filename TEXT,                    -- Original filename
    file_type TEXT,                   -- MIME type
    document_type TEXT,               -- PAN/Aadhaar/Unknown
    dropbox_path TEXT,                -- Dropbox file path
    share_link TEXT,                  -- Download URL
    expiry_time TEXT,                 -- ISO timestamp
    metadata TEXT,                    -- JSON metadata
    created_at TEXT                  -- ISO timestamp
)
```

### scan_logs Table
```sql
CREATE TABLE scan_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    qr_id TEXT,                       -- File UUID
    scanned_at TEXT,                  -- ISO timestamp
    ip_address TEXT,                  -- Client IP (optional)
    user_agent TEXT,                  -- User agent (optional)
    success BOOLEAN,                  -- Scan success
    error_message TEXT                -- Error details
)
```

## Environment Variables

### Backend (.env)
```env
DROPBOX_ACCESS_TOKEN=your_token
API_TOKEN=your_secret_token
ALLOWED_ORIGINS=http://localhost:3000
QR_EXPIRY_HOURS=24
MAX_FILE_SIZE_MB=20
```

### Frontend (.env.local)
```env
VITE_API_URL=http://localhost:8000
VITE_API_TOKEN=your_secret_token
```

## Dependencies

### Backend (requirements.txt)
- fastapi: Web framework
- uvicorn: ASGI server
- dropbox: Dropbox SDK
- qrcode: QR code generation
- PyPDF2, pdfplumber: PDF processing
- Pillow: Image processing
- pytesseract: OCR
- pyzbar: QR code reading
- opencv-python: Image processing
- numpy: Numerical operations

### Frontend (package.json)
- react: UI library
- react-router-dom: Routing
- axios: HTTP client
- qrcode.react: QR code display
- jsqr: QR code scanning
- react-webcam: Camera access
- vite: Build tool

## API Endpoints

### Public Endpoints
- `POST /api/upload` - Upload single file
- `POST /api/upload-multiple` - Upload multiple files
- `GET /api/generate-qr/{file_id}` - Get QR code image
- `POST /api/scan-qr` - Process scanned QR
- `GET /api/validate-document` - Validate document

### Admin Endpoints
- `GET /api/admin/files` - List all files
- `DELETE /api/admin/files/{file_id}` - Delete file
- `GET /api/admin/logs` - Get scan logs

All endpoints require Bearer token authentication.

## User-Provided Files

Place these files in the specified locations:

1. **Logo**: `frontend/public/logo.png`
2. **Success Sound**: `frontend/public/sounds/success.wav`
3. **Error Sound**: `frontend/public/sounds/error.wav`
4. **Upload Sound**: `frontend/public/sounds/upload.wav`

The application will work without these files, but with reduced functionality.

