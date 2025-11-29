# VeriQuickX Quick Start Guide

Get up and running in 5 minutes!

## Prerequisites Check

- [ ] Python 3.10+ installed
- [ ] Node.js 18+ installed
- [ ] Dropbox access token ready
- [ ] Tesseract OCR installed (for image text extraction)

## Step 1: Run Setup Script

```bash
python setup.py
```

This will:
- Create necessary directories
- Generate `.env` files with secure tokens
- Set up configuration

## Step 2: Add Dropbox Token

Edit `backend/.env` and add your Dropbox access token:

```env
DROPBOX_ACCESS_TOKEN=your_actual_token_here
```

## Step 3: Install Dependencies

### Backend
```bash
cd backend
pip install -r requirements.txt
```

### Frontend
```bash
cd frontend
npm install
```

## Step 4: Start Services

### Terminal 1 - Backend
```bash
cd backend
python main.py
```

Backend runs on: http://localhost:8000

### Terminal 2 - Frontend
```bash
cd frontend
npm run dev
```

Frontend runs on: http://localhost:3000

## Step 5: Test the Application

1. **Upload a Document:**
   - Go to http://localhost:3000/upload
   - Drag & drop a PDF or image
   - Click Upload
   - View generated QR code

2. **Scan QR Code:**
   - Go to http://localhost:3000/scan
   - Click "Start Scanning"
   - Point camera at QR code
   - View document details

3. **Admin Panel:**
   - Go to http://localhost:3000/admin
   - Password: `admin123` (change in production!)
   - View files and logs

## Troubleshooting

### Backend won't start
- Check Python version: `python --version` (needs 3.10+)
- Verify `.env` file exists in `backend/`
- Check Dropbox token is valid

### Frontend won't start
- Check Node version: `node --version` (needs 18+)
- Delete `node_modules` and run `npm install` again
- Check `frontend/.env.local` exists

### Camera not working
- Grant browser permissions
- Use Chrome or Edge (best support)
- Try HTTPS (required on some browsers)

### Dropbox upload fails
- Verify token in `backend/.env`
- Check token hasn't expired
- Ensure app has file read/write permissions

## Next Steps

- Read [README.md](README.md) for full documentation
- Check [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment
- Review [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for architecture

## Need Help?

- Check the About page in the app for API documentation
- Review error messages in browser console
- Check backend logs for detailed errors

