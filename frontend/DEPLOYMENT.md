# Frontend Deployment Guide

This is a **separate frontend repository** that can be deployed independently while pointing to a local or remote backend API.

## 📋 Prerequisites

- Node.js 18+ installed
- npm or yarn
- Backend API running locally (port 5000) or deployed URL

## 🚀 Quick Start (Local Development)

### 1. Install Dependencies
```bash
npm install
```

### 2. Setup Environment Variables
```bash
# Copy the example file
cp .env.example .env.local

# .env.local is already configured for local backend:
# VITE_API_BASE_URL=http://localhost:5000
```

### 3. Run Local Backend
In a separate terminal, start your backend:
```bash
cd ../backend
python main.py  # or your backend startup command
# Backend should run on http://localhost:5000
```

### 4. Start Frontend Dev Server
```bash
npm run dev
# Frontend runs on http://localhost:3000
```

Visit `http://localhost:3000` in your browser.

---

## 🌐 Deployment Options

### **Option A: Deploy Frontend Only to Vercel**

1. **Create separate repository:**
   ```bash
   # Create new GitHub repo called "Dectra-Frontend"
   # Copy only the frontend folder to that repo
   ```

2. **Push to GitHub:**
   ```bash
   git push origin main
   ```

3. **Connect to Vercel:**
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project" → Select your GitHub repo
   - Import project with these settings:
     - **Framework:** Vite
     - **Root Directory:** ./ (frontend root)
     - **Build Command:** `npm run build`
     - **Output Directory:** `dist`

4. **Add Environment Variables in Vercel:**
   - In Vercel dashboard: Settings → Environment Variables
   - Add:
     ```
     VITE_API_BASE_URL=http://localhost:5000  # for preview/dev
     ```
   - Or for production backend:
     ```
     VITE_API_BASE_URL=https://your-backend-api.com
     ```

5. **Deploy:**
   - Vercel auto-deploys on push to main branch
   - Your frontend will be live at `your-app.vercel.app`

---

### **Option B: Deploy to Netlify**

1. **Connect GitHub:**
   - Go to [netlify.com](https://netlify.com)
   - Click "New site from Git" → Select Dectra-Frontend repo

2. **Build Settings:**
   - Build command: `npm run build`
   - Publish directory: `dist`
   - Node version: 18+

3. **Environment Variables:**
   - Site settings → Build & deploy → Environment
   - Add: `VITE_API_BASE_URL=http://localhost:5000`

4. **Deploy:**
   - Auto-deploys on push to main branch

---

## 🔌 Pointing to Different Backends

### **Local Backend (Development)**
```bash
# .env.local
VITE_API_BASE_URL=http://localhost:5000
```

### **Deployed Backend (Production)**
```bash
# .env.production
VITE_API_BASE_URL=https://api.yourdomain.com
```

### **Override at Runtime**
Set environment variable when running:
```bash
VITE_API_BASE_URL=http://your-backend:5000 npm run dev
```

---

## 📦 Build for Production

```bash
npm run build
# Creates dist/ folder with optimized production build
```

---

## 🛠️ Structure

```
frontend/
├── src/
│   ├── components/    # React components
│   ├── pages/         # Page components
│   ├── utils/         # api.js with axios config
│   └── App.jsx        # Main app
├── .env.local         # Local development (localhost:5000)
├── .env.production    # Production (your backend URL)
├── .env.example       # Template
├── vite.config.js     # Vite configuration with API proxy
└── package.json       # Dependencies & scripts
```

---

## 🔐 CORS Configuration

If you get CORS errors when frontend is deployed:

**Backend (Flask/FastAPI):**
```python
from flask_cors import CORS
CORS(app, origins=["https://your-app.vercel.app", "http://localhost:3000"])
```

---

## 🚨 Troubleshooting

### API calls fail: "Cannot reach backend"
- ✅ Ensure backend is running on port 5000
- ✅ Check `VITE_API_BASE_URL` is correct in .env.local
- ✅ Verify backend CORS allows localhost:3000

### Environment variables not loading
- ✅ File must be named `.env.local` (or `.env.production`)
- ✅ Restart dev server after changing .env files
- ✅ In code, use: `import.meta.env.VITE_API_BASE_URL`

### Deployed app can't reach local backend
- ⚠️ **This is expected!** Deployed app (on Vercel) cannot reach localhost:5000
- ✅ For testing: Use a deployed backend URL in `.env.production`
- ✅ For development: Run everything locally

---

## 📊 Environment Variable Reference

| Variable | Purpose | Example |
|----------|---------|---------|
| `VITE_API_BASE_URL` | Backend API URL | `http://localhost:5000` |
| `VITE_ENV` | Environment name | `development` or `production` |

---

## Next Steps

1. ✅ Update backend API endpoint (currently hardcoded to 8000, now flexible to 5000)
2. ✅ Create separate Dectra-Frontend GitHub repo
3. ✅ Push frontend code to new repo
4. ✅ Deploy to Vercel/Netlify
5. ✅ Configure API URL based on environment
