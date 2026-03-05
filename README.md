# VeriQuickX - Document Verification System

A comprehensive full-stack application for document upload, QR code generation, and verification. Supports Aadhaar and PAN card processing with advanced validation algorithms.

## 🚀 Features

- **Document Upload**: Upload PDF or image documents (Aadhaar, PAN, or any ID)
- **Azure Blob Storage**: Secure cloud storage with SAS-based temporary access
- **QR Code Generation**: Generate QR codes with short-lived access tokens (30-60 seconds)
- **QR Scanner**: Scan QR codes using webcam to access documents
- **Metadata Extraction**: Automatic extraction of name, DOB, PAN/Aadhaar numbers
- **Document Validation**: PAN checksum validation, Aadhaar QR validation
- **Verification Lifecycle**: Documents move from incoming → verified after validation
- **Admin Panel**: Manage files, view scan logs, delete documents
- **Multi-file Upload**: Upload multiple documents at once
- **Direct Upload**: Frontend uploads directly to Azure (no backend file streaming)

## 🔒 Why SAS Instead of Public Links?

**Security by Design:**
- **No Public Access**: Containers are private; only SAS tokens grant temporary access
- **Time-Limited**: QR codes contain 30-60 second SAS URLs, not permanent links
- **Credential Isolation**: Azure credentials never leave the backend
- **Immediate Expiry**: Documents can be deleted after first access
- **No Metadata Leakage**: QR codes contain only access tokens, not document data

## 📋 Prerequisites

- Python 3.10+
- Node.js 18+
- npm or yarn
- Azure Storage Account with access key
- Tesseract OCR (for image text extraction)

### Installing Tesseract

**Windows:**
```bash
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# Or use chocolatey:
choco install tesseract
```

**macOS:**
```bash
brew install tesseract
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd "Veriquick Cloud"
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env and add your Azure Storage credentials
# AZURE_STORAGE_ACCOUNT_NAME=your_account_name
# AZURE_STORAGE_ACCOUNT_KEY=your_account_key
# AZURE_STORAGE_CONTAINER_INCOMING=incoming-docs
# AZURE_STORAGE_CONTAINER_VERIFIED=verified-docs
# API_TOKEN=your_secret_token_here
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create public directory for assets
mkdir -p public/sounds
```

### 4. Add Sound Files

Place the following sound files in `frontend/public/sounds/`:
- `success.wav` - Played on successful scan
- `error.wav` - Played on scan error
- `upload.wav` - Played on upload completion

If you don't have sound files, the app will work without them (errors will be logged to console).

### 5. Add Logo

Place your logo file as `frontend/public/logo.png` (or update the path in `Navbar.jsx`).

## 🚀 Running the Application

### Start Backend

```bash
cd backend
python main.py
```

The API will be available at `http://localhost:8000`

### Start Frontend

```bash
cd frontend
npm run dev
```

The frontend will be available at `http://localhost:3000`

## 📁 Project Structure

```
Veriquick Cloud/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration settings
│   ├── document_processor.py   # Document processing & metadata extraction
│   ├── validators.py           # Document validation functions
│   ├── requirements.txt        # Python dependencies
│   ├── .env.example            # Environment variables template
│   └── veriquickx.db           # SQLite database (created automatically)
│
├── frontend/
│   ├── src/
│   │   ├── components/         # React components
│   │   │   └── Navbar.jsx
│   │   ├── pages/              # Page components
│   │   │   ├── UploadPage.jsx
│   │   │   ├── ScannerPage.jsx
│   │   │   ├── AdminPage.jsx
│   │   │   └── AboutPage.jsx
│   │   ├── App.jsx             # Main app component
│   │   ├── main.jsx            # Entry point
│   │   └── index.css           # Global styles
│   ├── public/
│   │   ├── sounds/             # Sound effects
│   │   └── logo.png            # Logo file
│   ├── package.json
│   └── vite.config.js
│
└── README.md
```

## 🔧 Configuration

### Backend Configuration

Edit `backend/.env`:

```env
DROPBOX_ACCESS_TOKEN=your_dropbox_token
API_TOKEN=your_secret_api_token
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Frontend Configuration

Set environment variables for the frontend (recommended) in `frontend/.env.local`:

```env
VITE_API_URL=http://localhost:8000
VITE_API_TOKEN=your_secret_token_here
```

These must match the backend `API_TOKEN` (see `backend/.env`).

### Admin Password

Default admin password is `admin123`. Change it in `frontend/src/pages/AdminPage.jsx`:

```javascript
const ADMIN_PASSWORD = 'your_secure_password'
```

## 📡 API Endpoints

### Public Endpoints

- `GET /` - API information
- `POST /api/upload` - Upload single document
- `POST /api/upload-multiple` - Upload multiple documents
- `GET /api/generate-qr/{file_id}` - Generate QR code image
- `POST /api/scan-qr` - Process scanned QR code
- `GET /api/validate-document` - Validate document metadata

### Admin Endpoints (Require Authentication)

- `GET /api/admin/files` - List all uploaded files
- `DELETE /api/admin/files/{file_id}` - Delete a file
- `GET /api/admin/logs` - Get scan logs

All endpoints require Bearer token authentication:
```
Authorization: Bearer your_api_token
```

## 🔐 Security Notes

1. **Change Default Tokens**: Update `API_TOKEN` in production
2. **Change Admin Password**: Update `ADMIN_PASSWORD` in `AdminPage.jsx`
3. **Use HTTPS**: Deploy with HTTPS in production
4. **Environment Variables**: Never commit `.env` files
5. **Dropbox Token**: Keep your Dropbox token secure

## 🚢 Deployment

### Backend Deployment (Render/Railway)

1. Create a new service
2. Set environment variables:
   - `DROPBOX_ACCESS_TOKEN`
   - `API_TOKEN`
   - `ALLOWED_ORIGINS` (your frontend URL)
3. Deploy from `backend/` directory
4. Update frontend API URL to point to deployed backend

### Frontend Deployment (Vercel/Netlify)

1. Build the frontend:
   ```bash
   cd frontend
   npm run build
   ```
2. Deploy the `dist/` folder
3. Update API proxy or use environment variables for API URL

### Streamlit Cloud (Alternative)

If you prefer Streamlit, you can convert the React frontend to Streamlit, but the current implementation uses React for better UX.

## 🧪 Testing

### Test Document Upload

1. Go to Upload page
2. Select a PDF or image file
3. Click Upload
4. Verify QR code is generated

### Test QR Scanner

1. Go to Scan QR page
2. Click "Start Scanning"
3. Point camera at a QR code
4. Verify document is retrieved and displayed

### Test Admin Panel

1. Go to Admin page
2. Login with password
3. View files and logs
4. Test file deletion

## 🐛 Troubleshooting

### Camera Not Working

- Ensure browser permissions are granted
- Try different browsers (Chrome recommended)
- Check HTTPS requirement for camera access

### Dropbox Upload Fails

- Verify `DROPBOX_ACCESS_TOKEN` is correct
- Check token hasn't expired
- Ensure Dropbox app has proper permissions

### OCR Not Working

- Install Tesseract OCR
- Set `TESSDATA_PREFIX` environment variable if needed
- Check Tesseract is in PATH

### QR Code Not Scanning

- Ensure good lighting
- Hold QR code steady
- Try increasing scan interval in `ScannerPage.jsx`

## 📝 License

© 2025 VeriQuickX. All rights reserved.
Proprietary software - Permission required to edit and modify.

## 👤 Contact

- GitHub: [@DebashishRana](https://www.github.com/DebashishRana)
- Email: dimareznokov@gmail.com
- Phone: +91 9304211754
- LinkedIn: [devarana](https://www.linkedin.com/in/devarana)

## 🙏 Acknowledgments

- Dropbox API for cloud storage
- FastAPI for backend framework
- React for frontend framework
- jsQR for QR code scanning
- All open-source libraries used in this project

