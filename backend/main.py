"""
VeriQuickX Backend API
FastAPI server for document upload, QR generation, and validation
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn
import os
import uuid
import json
import sqlite3
from datetime import datetime, timedelta
from typing import List, Optional
import dropbox
from dropbox.exceptions import AuthError, ApiError
import qrcode
import io
from pathlib import Path

from document_processor import DocumentProcessor
from validators import DocumentValidator
from config import settings

app = FastAPI(title="VeriQuickX API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Initialize Dropbox client
dbx = dropbox.Dropbox(settings.DROPBOX_ACCESS_TOKEN)

# Initialize processors
doc_processor = DocumentProcessor()
validator = DocumentValidator()

# Database setup
DB_PATH = "veriquickx.db"

def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS uploads (
            id TEXT PRIMARY KEY,
            filename TEXT,
            file_type TEXT,
            document_type TEXT,
            dropbox_path TEXT,
            share_link TEXT,
            expiry_time TEXT,
            metadata TEXT,
            created_at TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scan_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            qr_id TEXT,
            scanned_at TEXT,
            ip_address TEXT,
            user_agent TEXT,
            success BOOLEAN,
            error_message TEXT
        )
    """)
    
    conn.commit()
    conn.close()

init_db()


@app.get("/")
async def root():
    return {"message": "VeriQuickX API", "version": "1.0.0"}

@app.post("/api/upload")
async def upload_document(
    file: UploadFile = File(...),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Upload document to Dropbox and generate QR code"""
    # Verify token
    if credentials.credentials != settings.API_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")
    try:
        # Validate file size (20MB limit)
        contents = await file.read()
        if len(contents) > 20 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size exceeds 20MB limit")
        
        # Generate unique ID
        file_id = str(uuid.uuid4())
        
        # Upload to Dropbox
        dropbox_path = f"/veriquick_uploads/{file_id}/{file.filename}"
        dbx.files_upload(contents, dropbox_path)
        
        # Create shareable link with expiry (24 hours)
        expiry_time = datetime.now() + timedelta(hours=24)
        share_link = dbx.sharing_create_shared_link_with_settings(
            dropbox_path,
            settings=dropbox.sharing.SharedLinkSettings(
                requested_visibility=dropbox.sharing.RequestedVisibility.public,
                expires=expiry_time
            )
        ).url
        
        # Convert to direct download link
        direct_link = share_link.replace("?dl=0", "?dl=1")
        
        # Process document to extract metadata
        metadata = doc_processor.process_document(contents, file.filename)
        
        # Store in database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO uploads (id, filename, file_type, document_type, dropbox_path, 
                               share_link, expiry_time, metadata, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            file_id,
            file.filename,
            file.content_type,
            metadata.get("document_type", "Unknown"),
            dropbox_path,
            direct_link,
            expiry_time.isoformat(),
            json.dumps(metadata),
            datetime.now().isoformat()
        ))
        conn.commit()
        conn.close()
        
        # Generate QR code payload
        qr_payload = {
            "id": file_id,
            "dl": direct_link,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata
        }
        
        return {
            "success": True,
            "file_id": file_id,
            "share_link": direct_link,
            "expiry_time": expiry_time.isoformat(),
            "metadata": metadata,
            "qr_payload": qr_payload
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload-multiple")
async def upload_multiple_documents(
    files: List[UploadFile] = File(...),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Upload multiple documents"""
    # Verify token
    if credentials.credentials != settings.API_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    results = []
    for file in files:
        try:
            # Process each file
            contents = await file.read()
            if len(contents) > 20 * 1024 * 1024:
                results.append({
                    "success": False,
                    "filename": file.filename,
                    "error": "File size exceeds 20MB limit"
                })
                continue
            
            # Generate unique ID
            file_id = str(uuid.uuid4())
            
            # Upload to Dropbox
            dropbox_path = f"/veriquick_uploads/{file_id}/{file.filename}"
            dbx.files_upload(contents, dropbox_path)
            
            # Create shareable link with expiry (24 hours)
            expiry_time = datetime.now() + timedelta(hours=24)
            share_link = dbx.sharing_create_shared_link_with_settings(
                dropbox_path,
                settings=dropbox.sharing.SharedLinkSettings(
                    requested_visibility=dropbox.sharing.RequestedVisibility.public,
                    expires=expiry_time
                )
            ).url
            
            # Convert to direct download link
            direct_link = share_link.replace("?dl=0", "?dl=1")
            
            # Process document to extract metadata
            metadata = doc_processor.process_document(contents, file.filename)
            
            # Store in database
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO uploads (id, filename, file_type, document_type, dropbox_path, 
                                   share_link, expiry_time, metadata, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                file_id,
                file.filename,
                file.content_type,
                metadata.get("document_type", "Unknown"),
                dropbox_path,
                direct_link,
                expiry_time.isoformat(),
                json.dumps(metadata),
                datetime.now().isoformat()
            ))
            conn.commit()
            conn.close()
            
            # Generate QR code payload
            qr_payload = {
                "id": file_id,
                "dl": direct_link,
                "timestamp": datetime.now().isoformat(),
                "metadata": metadata
            }
            
            result = {
                "success": True,
                "file_id": file_id,
                "share_link": direct_link,
                "expiry_time": expiry_time.isoformat(),
                "metadata": metadata,
                "qr_payload": qr_payload
            }
            results.append(result)
        except Exception as e:
            results.append({
                "success": False,
                "filename": file.filename,
                "error": str(e)
            })
    return {"results": results}

@app.get("/api/generate-qr/{file_id}")
async def generate_qr_code(
    file_id: str,
    token: Optional[str] = None,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
):
    """Generate QR code image for a file"""
    # Verify token (check both bearer and query param)
    api_token = None
    if credentials:
        api_token = credentials.credentials
    if not api_token and token:
        api_token = token
    
    if api_token != settings.API_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")
    """Generate QR code image for a file"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT share_link, metadata FROM uploads WHERE id = ?", (file_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail="File not found")
        
        share_link, metadata_json = row
        metadata = json.loads(metadata_json) if metadata_json else {}
        
        qr_payload = {
            "id": file_id,
            "dl": share_link,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata
        }
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(json.dumps(qr_payload))
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        img_buffer = io.BytesIO()
        img.save(img_buffer, format="PNG")
        img_buffer.seek(0)
        
        return FileResponse(
            img_buffer,
            media_type="image/png",
            filename=f"qr_{file_id}.png"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/scan-qr")
async def scan_qr_code(
    qr_data: dict,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    # Verify token
    if credentials.credentials != settings.API_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")
    """Process scanned QR code and return document info"""
    try:
        file_id = qr_data.get("id")
        if not file_id:
            raise HTTPException(status_code=400, detail="Invalid QR code format")
        
        # Log scan
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO scan_logs (qr_id, scanned_at, success)
            VALUES (?, ?, ?)
        """, (file_id, datetime.now().isoformat(), True))
        conn.commit()
        conn.close()
        
        # Get file info from database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT filename, document_type, share_link, metadata, expiry_time
            FROM uploads WHERE id = ?
        """, (file_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail="Document not found")
        
        filename, doc_type, share_link, metadata_json, expiry_time = row
        
        # Check if expired
        expiry = datetime.fromisoformat(expiry_time)
        if datetime.now() > expiry:
            raise HTTPException(status_code=410, detail="Download link has expired")
        
        metadata = json.loads(metadata_json) if metadata_json else {}
        
        # Validate document
        validation_result = validator.validate_document(metadata, doc_type)
        
        return {
            "success": True,
            "file_id": file_id,
            "filename": filename,
            "document_type": doc_type,
            "download_link": share_link,
            "metadata": metadata,
            "validation": validation_result,
            "expiry_time": expiry_time
        }
        
    except HTTPException:
        raise
    except Exception as e:
        # Log error
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO scan_logs (qr_id, scanned_at, success, error_message)
            VALUES (?, ?, ?, ?)
        """, (qr_data.get("id", "unknown"), datetime.now().isoformat(), False, str(e)))
        conn.commit()
        conn.close()
        
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/files")
async def list_files(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # Verify token
    if credentials.credentials != settings.API_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")
    """List all uploaded files (admin)"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, filename, document_type, created_at, expiry_time
            FROM uploads ORDER BY created_at DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        
        files = []
        for row in rows:
            files.append({
                "id": row[0],
                "filename": row[1],
                "document_type": row[2],
                "created_at": row[3],
                "expiry_time": row[4]
            })
        
        return {"files": files}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/admin/files/{file_id}")
async def delete_file(
    file_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    # Verify token
    if credentials.credentials != settings.API_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")
    """Delete file from Dropbox and database (admin)"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT dropbox_path FROM uploads WHERE id = ?", (file_id,))
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="File not found")
        
        dropbox_path = row[0]
        
        # Delete from Dropbox
        try:
            dbx.files_delete(dropbox_path)
        except ApiError as e:
            print(f"Dropbox delete error: {e}")
        
        # Delete from database
        cursor.execute("DELETE FROM uploads WHERE id = ?", (file_id,))
        conn.commit()
        conn.close()
        
        return {"success": True, "message": "File deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/logs")
async def get_scan_logs(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # Verify token
    if credentials.credentials != settings.API_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")
    """Get scan logs (admin)"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, qr_id, scanned_at, success, error_message
            FROM scan_logs ORDER BY scanned_at DESC LIMIT 100
        """)
        rows = cursor.fetchall()
        conn.close()
        
        logs = []
        for row in rows:
            logs.append({
                "id": row[0],
                "qr_id": row[1],
                "scanned_at": row[2],
                "success": row[3],
                "error_message": row[4]
            })
        
        return {"logs": logs}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/validate-document")
async def validate_document_endpoint(
    document_type: str,
    metadata: dict,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    # Verify token
    if credentials.credentials != settings.API_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")
    """Validate document authenticity"""
    try:
        result = validator.validate_document(metadata, document_type)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

