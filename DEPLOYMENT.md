# Seva Setu Portal - Deployment Guide

## Quick Start

### Local Development

1. **Backend:**
   ```bash
   cd backend
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your tokens
   python main.py
   ```

2. **Frontend:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## Production Deployment

### Option 1: Render.com

#### Backend Deployment

1. Create a new **Web Service** on Render
2. Connect your repository
3. Settings:
   - **Build Command:** `cd backend && pip install -r requirements.txt`
   - **Start Command:** `cd backend && python main.py`
   - **Environment:** Python 3
4. Add Environment Variables:
   - `DROPBOX_ACCESS_TOKEN`: Your Dropbox token
   - `API_TOKEN`: Your secret API token
   - `ALLOWED_ORIGINS`: Your frontend URL (e.g., `https://your-app.onrender.com`)

#### Frontend Deployment

1. Create a new **Static Site** on Render
2. Connect your repository
3. Settings:
   - **Build Command:** `cd frontend && npm install && npm run build`
   - **Publish Directory:** `frontend/dist`
4. Add Environment Variables:
   - `VITE_API_URL`: Your backend URL (e.g., `https://your-backend.onrender.com`)
   - `VITE_API_TOKEN`: Your API token (must match backend)

### Option 2: Railway

#### Backend Deployment

1. Create new project on Railway
2. Add **Python** service
3. Set root directory to `backend/`
4. Add environment variables (same as Render)
5. Railway will auto-detect and deploy

#### Frontend Deployment

1. Add **Static Files** service
2. Set root directory to `frontend/`
3. Build command: `npm install && npm run build`
4. Output directory: `dist`
5. Add environment variables

### Option 3: Vercel (Frontend) + Railway/Render (Backend)

#### Backend
- Deploy to Railway or Render (see above)

#### Frontend
1. Import project to Vercel
2. Root directory: `frontend/`
3. Build command: `npm run build`
4. Output directory: `.vercel`
5. Add environment variables:
   - `VITE_API_URL`: Your backend URL
   - `VITE_API_TOKEN`: Your API token

### Option 4: Docker Deployment

#### Backend Dockerfile

Create `backend/Dockerfile`:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "main.py"]
```

#### Frontend Dockerfile

Create `frontend/Dockerfile`:
```dockerfile
FROM node:18-alpine as build

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

#### Docker Compose

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DROPBOX_ACCESS_TOKEN=${DROPBOX_ACCESS_TOKEN}
      - API_TOKEN=${API_TOKEN}
      - ALLOWED_ORIGINS=http://localhost:3000
    volumes:
      - ./backend/seva-setu-portal.db:/app/seva-setu-portal.db

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    environment:
      - VITE_API_URL=http://localhost:8000
    depends_on:
      - backend
```

Run: `docker-compose up -d`

## Environment Variables

### Backend (.env)
```env
DROPBOX_ACCESS_TOKEN=your_dropbox_token
API_TOKEN=your_secret_token_here
ALLOWED_ORIGINS=http://localhost:3000,https://your-domain.com
QR_EXPIRY_HOURS=24
MAX_FILE_SIZE_MB=20
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000
VITE_API_TOKEN=your_secret_token_here
```

## Post-Deployment Checklist

- [ ] Update CORS origins in backend
- [ ] Change default admin password
- [ ] Update API tokens
- [ ] Test file upload
- [ ] Test QR scanning
- [ ] Test admin panel
- [ ] Verify Dropbox integration
- [ ] Check error logging
- [ ] Set up monitoring (optional)
- [ ] Configure backup for database

## Troubleshooting

### CORS Errors
- Ensure `ALLOWED_ORIGINS` includes your frontend URL
- Check for trailing slashes
- Verify protocol (http vs https)

### Dropbox Errors
- Verify token hasn't expired
- Check app permissions in Dropbox
- Ensure token has file read/write access

### Build Failures
- Check Node.js version (18+)
- Verify Python version (3.10+)
- Check all dependencies are in requirements.txt/package.json

### Database Issues
- SQLite file may need write permissions
- Consider PostgreSQL for production
- Backup database regularly

## Scaling Considerations

For production with high traffic:
1. Replace SQLite with PostgreSQL
2. Use Redis for caching
3. Add CDN for static assets
4. Implement rate limiting
5. Use load balancer for backend
6. Set up monitoring (Sentry, etc.)

