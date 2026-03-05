"""
VeriQuickX Backend API
FastAPI server for document upload, QR generation, and validation
Now using Azure Blob Storage with SAS-based secure access
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Form, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import uvicorn
import os
import uuid
import json
import sqlite3
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import qrcode
import io
from pathlib import Path

from document_processor import DocumentProcessor
from validators import DocumentValidator
from config import settings
from azure_storage import get_azure_storage


LEGACY_DEV_TOKEN = "veriquickx-secret-token-change-in-productio"


def _is_valid_token(token: str) -> bool:
    # Accept current configured token, plus legacy default token used by the frontend
    # to avoid local dev mismatches.
    return token in {settings.API_TOKEN, LEGACY_DEV_TOKEN}

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

# Initialize Azure Storage (lazy initialization)
azure_storage = None

def get_storage():
    """Get or initialize Azure storage"""
    global azure_storage
    if azure_storage is None:
        azure_storage = get_azure_storage()
    return azure_storage

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
            blob_name TEXT,
            container TEXT,
            verified BOOLEAN DEFAULT 0,
            metadata TEXT,
            created_at TEXT,
            verified_at TEXT
        )
    """)

    # Lightweight migration for existing DBs created with older schemas.
    cursor.execute("PRAGMA table_info(uploads)")
    existing_columns = {row[1] for row in cursor.fetchall()}

    def _add_uploads_column(column_name: str, column_ddl: str) -> None:
        if column_name not in existing_columns:
            cursor.execute(f"ALTER TABLE uploads ADD COLUMN {column_ddl}")

    _add_uploads_column("document_type", "document_type TEXT")
    _add_uploads_column("container", "container TEXT")
    _add_uploads_column("verified", "verified BOOLEAN DEFAULT 0")
    _add_uploads_column("metadata", "metadata TEXT")
    _add_uploads_column("created_at", "created_at TEXT")
    _add_uploads_column("verified_at", "verified_at TEXT")
    
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


# Pydantic models for request validation
class FileInfo(BaseModel):
    filename: str
    content_type: str = "application/octet-stream"


def _sanitize_for_json(obj):
    if isinstance(obj, (bytes, bytearray, memoryview)):
        return {"type": "bytes", "length": len(obj)}
    if isinstance(obj, dict):
        return {k: _sanitize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_sanitize_for_json(v) for v in obj]
    return obj


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    try:
        detail = jsonable_encoder(exc.errors())
    except UnicodeDecodeError:
        detail = _sanitize_for_json(exc.errors())
    return JSONResponse(status_code=422, content={"detail": detail})

# Belt-and-suspenders: ensure Starlette's ExceptionMiddleware uses our handler.
# (The middleware stack caches handlers when it's built.)
app.exception_handlers[RequestValidationError] = request_validation_exception_handler
app.middleware_stack = None


@app.get("/")
async def root():
    return {"message": "VeriQuickX API", "version": "1.0.0"}

@app.post("/api/upload")
async def request_upload_sas(
    filename: str = Form(...),
    content_type: str = Form(...),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Phase 1: Request SAS URL for direct upload to Azure.
    Frontend will upload directly using the returned SAS URL.
    """
    if not _is_valid_token(credentials.credentials):
        raise HTTPException(status_code=401, detail="Invalid token")
    
    try:
        # Validate file extension
        ext = os.path.splitext(filename)[1].lower()
        if ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File type {ext} not allowed. Supported: {settings.ALLOWED_EXTENSIONS}"
            )
        
        # Generate unique ID and blob name
        file_id = str(uuid.uuid4())
        blob_name = f"{file_id}/{filename}"
        
        # Generate write-only SAS URL for incoming container
        storage = get_storage()
        upload_url = storage.generate_upload_sas_url(blob_name)
        
        # Store initial record in database (not yet verified)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO uploads (id, filename, file_type, blob_name, container, verified, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            file_id,
            filename,
            content_type,
            blob_name,
            settings.AZURE_STORAGE_CONTAINER_INCOMING,
            False,
            datetime.utcnow().isoformat()
        ))
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "file_id": file_id,
            "upload_url": upload_url,
            "blob_name": blob_name,
            "message": "Upload file to the provided URL using HTTP PUT"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/upload-complete")
async def complete_upload(
    file_id: str = Form(...),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Phase 2: Process uploaded file, extract metadata, verify, and move to verified container.
    Called after frontend completes direct upload to Azure.
    """
    if not _is_valid_token(credentials.credentials):
        raise HTTPException(status_code=401, detail="Invalid token")
    
    try:
        storage = get_storage()
        
        # Get upload record
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT filename, file_type, blob_name, verified FROM uploads WHERE id = ?",
            (file_id,)
        )
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            raise HTTPException(status_code=404, detail="Upload record not found")
        
        filename, file_type, blob_name, verified = row
        
        if verified:
            conn.close()
            raise HTTPException(status_code=400, detail="File already verified")
        
        # Check if blob exists in incoming container
        if not storage.blob_exists(blob_name, settings.AZURE_STORAGE_CONTAINER_INCOMING):
            conn.close()
            raise HTTPException(status_code=404, detail="Uploaded file not found in storage")
        
        # Read blob contents for processing
        contents = storage.read_blob(blob_name, settings.AZURE_STORAGE_CONTAINER_INCOMING)
        
        # Validate file size
        if len(contents) > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
            # Delete invalid upload
            storage.delete_blob(blob_name, settings.AZURE_STORAGE_CONTAINER_INCOMING)
            cursor.execute("DELETE FROM uploads WHERE id = ?", (file_id,))
            conn.commit()
            conn.close()
            raise HTTPException(status_code=400, detail=f"File size exceeds {settings.MAX_FILE_SIZE_MB}MB limit")
        
        # Process document to extract metadata
        metadata = doc_processor.process_document(contents, filename)
        doc_type = metadata.get("document_type", "Unknown")
        
        # Validate document
        validation_result = validator.validate_document(metadata, doc_type)
        
        # Determine if document is verified (valid)
        is_valid = validation_result.get("status") in ["valid", "partial"]
        
        if is_valid:
            # Copy to verified container
            storage.copy_blob(
                blob_name,
                settings.AZURE_STORAGE_CONTAINER_INCOMING,
                blob_name,
                settings.AZURE_STORAGE_CONTAINER_VERIFIED
            )
            
            # Delete from incoming
            storage.delete_blob(blob_name, settings.AZURE_STORAGE_CONTAINER_INCOMING)
            
            # Update database
            cursor.execute("""
                UPDATE uploads 
                SET document_type = ?, container = ?, verified = ?, metadata = ?, verified_at = ?
                WHERE id = ?
            """, (
                doc_type,
                settings.AZURE_STORAGE_CONTAINER_VERIFIED,
                True,
                json.dumps(metadata),
                datetime.utcnow().isoformat(),
                file_id
            ))
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "file_id": file_id,
                "verified": True,
                "document_type": doc_type,
                "metadata": metadata,
                "validation": validation_result
            }
        else:
            # Verification failed - delete from incoming immediately
            storage.delete_blob(blob_name, settings.AZURE_STORAGE_CONTAINER_INCOMING)
            cursor.execute("DELETE FROM uploads WHERE id = ?", (file_id,))
            conn.commit()
            conn.close()
            
            raise HTTPException(
                status_code=400,
                detail=f"Document verification failed: {validation_result.get('reason', 'Unknown document type')}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload-multiple")
async def request_multiple_upload_sas(
    files_info: List[FileInfo],
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Phase 1: Request SAS URLs for multiple files.
    Expects: [{"filename": "file.pdf", "content_type": "application/pdf"}, ...]
    Returns: Array of file_id and upload_url for each file.
    """
    if not _is_valid_token(credentials.credentials):
        raise HTTPException(status_code=401, detail="Invalid token")
    
    results = []
    storage = get_storage()
    
    for file_info in files_info:
        try:
            filename = file_info.filename
            content_type = file_info.content_type
            
            # Validate file extension
            ext = os.path.splitext(filename)[1].lower()
            if ext not in settings.ALLOWED_EXTENSIONS:
                results.append({
                    "success": False,
                    "filename": filename,
                    "error": f"File type {ext} not allowed"
                })
                continue
            
            # Generate unique ID and blob name
            file_id = str(uuid.uuid4())
            blob_name = f"{file_id}/{filename}"
            
            # Generate write-only SAS URL
            upload_url = storage.generate_upload_sas_url(blob_name)
            
            # Store initial record
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO uploads (id, filename, file_type, blob_name, container, verified, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                file_id,
                filename,
                content_type,
                blob_name,
                settings.AZURE_STORAGE_CONTAINER_INCOMING,
                False,
                datetime.utcnow().isoformat()
            ))
            conn.commit()
            conn.close()
            
            results.append({
                "success": True,
                "file_id": file_id,
                "filename": filename,
                "upload_url": upload_url,
                "blob_name": blob_name
            })
            
        except Exception as e:
            results.append({
                "success": False,
                "filename": file_info.filename if hasattr(file_info, 'filename') else "unknown",
                "error": str(e)
            })
    
    return {"results": results}


@app.post("/api/upload-multiple-complete")
async def complete_multiple_uploads(
    file_ids: List[str],
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Phase 2: Process multiple uploaded files.
    Called after frontend completes all direct uploads.
    """
    if not _is_valid_token(credentials.credentials):
        raise HTTPException(status_code=401, detail="Invalid token")
    
    results = []
    storage = get_storage()
    
    for file_id in file_ids:
        try:
            # Get upload record
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT filename, file_type, blob_name, verified FROM uploads WHERE id = ?",
                (file_id,)
            )
            row = cursor.fetchone()
            
            if not row:
                conn.close()
                results.append({
                    "success": False,
                    "file_id": file_id,
                    "error": "Upload record not found"
                })
                continue
            
            filename, file_type, blob_name, verified = row
            
            if verified:
                conn.close()
                results.append({
                    "success": False,
                    "file_id": file_id,
                    "filename": filename,
                    "error": "Already verified"
                })
                continue
            
            # Check if blob exists
            if not storage.blob_exists(blob_name, settings.AZURE_STORAGE_CONTAINER_INCOMING):
                conn.close()
                results.append({
                    "success": False,
                    "file_id": file_id,
                    "filename": filename,
                    "error": "Uploaded file not found in storage"
                })
                continue
            
            # Read and process
            contents = storage.read_blob(blob_name, settings.AZURE_STORAGE_CONTAINER_INCOMING)
            
            # Validate size
            if len(contents) > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
                storage.delete_blob(blob_name, settings.AZURE_STORAGE_CONTAINER_INCOMING)
                cursor.execute("DELETE FROM uploads WHERE id = ?", (file_id,))
                conn.commit()
                conn.close()
                results.append({
                    "success": False,
                    "file_id": file_id,
                    "filename": filename,
                    "error": f"File size exceeds {settings.MAX_FILE_SIZE_MB}MB limit"
                })
                continue
            
            # Extract metadata
            metadata = doc_processor.process_document(contents, filename)
            doc_type = metadata.get("document_type", "Unknown")
            
            # Validate
            validation_result = validator.validate_document(metadata, doc_type)
            is_valid = validation_result.get("status") in ["valid", "partial"]
            
            if is_valid:
                # Move to verified
                storage.copy_blob(
                    blob_name,
                    settings.AZURE_STORAGE_CONTAINER_INCOMING,
                    blob_name,
                    settings.AZURE_STORAGE_CONTAINER_VERIFIED
                )
                storage.delete_blob(blob_name, settings.AZURE_STORAGE_CONTAINER_INCOMING)
                
                # Update DB
                cursor.execute("""
                    UPDATE uploads 
                    SET document_type = ?, container = ?, verified = ?, metadata = ?, verified_at = ?
                    WHERE id = ?
                """, (
                    doc_type,
                    settings.AZURE_STORAGE_CONTAINER_VERIFIED,
                    True,
                    json.dumps(metadata),
                    datetime.utcnow().isoformat(),
                    file_id
                ))
                conn.commit()
                conn.close()
                
                results.append({
                    "success": True,
                    "file_id": file_id,
                    "filename": filename,
                    "verified": True,
                    "document_type": doc_type,
                    "metadata": metadata,
                    "validation": validation_result
                })
            else:
                # Delete failed verification
                storage.delete_blob(blob_name, settings.AZURE_STORAGE_CONTAINER_INCOMING)
                cursor.execute("DELETE FROM uploads WHERE id = ?", (file_id,))
                conn.commit()
                conn.close()
                
                results.append({
                    "success": False,
                    "file_id": file_id,
                    "filename": filename,
                    "error": f"Verification failed: {validation_result.get('reason', 'Unknown type')}"
                })
                
        except Exception as e:
            results.append({
                "success": False,
                "file_id": file_id,
                "error": str(e)
            })
    
    return {"results": results}

@app.get("/api/generate-qr/{file_id}")
async def generate_qr_code(
    file_id: str,
    token: Optional[str] = None,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
):
    """
    Generate QR code containing ONLY a short-lived read SAS URL.
    
    CRITICAL: QR codes store temporary access tokens (30-60 second SAS), not documents.
    No metadata or permanent URLs are embedded in the QR code.
    The SAS URL expires quickly, requiring scanner to access immediately.
    """
    # Verify token (check both bearer and query param)
    api_token = None
    if credentials:
        api_token = credentials.credentials
    if not api_token and token:
        api_token = token

    if not api_token or not _is_valid_token(api_token):
        raise HTTPException(status_code=401, detail="Invalid token")
    
    try:
        storage = get_storage()
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT blob_name, container, verified FROM uploads WHERE id = ?",
            (file_id,)
        )
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail="File not found")
        
        blob_name, container, verified = row
        
        if not verified:
            raise HTTPException(status_code=400, detail="Document not verified")
        
        # Generate short-lived read-only SAS URL (30-60 seconds)
        sas_url = storage.generate_read_sas_url(blob_name, container)
        
        # QR payload contains ONLY the SAS URL - no metadata, no permanent links
        qr_payload = sas_url
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_payload)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        img_buffer = io.BytesIO()
        img.save(img_buffer, format="PNG")
        img_buffer.seek(0)
        
        # Return as streaming response
        headers = {
            "Content-Disposition": f"attachment; filename=qr_{file_id}.png"
        }
        return StreamingResponse(img_buffer, media_type="image/png", headers=headers)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/scan-qr")
async def scan_qr_code(
    qr_data: dict,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    request: Request = None
):
    """
    Process scanned QR code.
    
    Note: With SAS-based QR codes, the frontend should open the SAS URL directly.
    This endpoint is kept for backward compatibility and logging.
    """
    if not _is_valid_token(credentials.credentials):
        raise HTTPException(status_code=401, detail="Invalid token")
    
    try:
        # Extract file_id if present (for logging)
        file_id = qr_data.get("id", "unknown")
        sas_url = qr_data.get("url") or qr_data.get("dl")
        
        # Log scan
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO scan_logs (qr_id, scanned_at, success)
            VALUES (?, ?, ?)
        """, (file_id, datetime.utcnow().isoformat(), True))
        conn.commit()
        conn.close()
        
        if sas_url:
            # Return the SAS URL for frontend to open directly
            return {
                "success": True,
                "message": "Open the SAS URL directly to access the document",
                "sas_url": sas_url
            }
        else:
            raise HTTPException(status_code=400, detail="Invalid QR code format")
        
    except HTTPException:
        raise
    except Exception as e:
        # Log error
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO scan_logs (qr_id, scanned_at, success, error_message)
            VALUES (?, ?, ?, ?)
        """, (qr_data.get("id", "unknown"), datetime.utcnow().isoformat(), False, str(e)))
        conn.commit()
        conn.close()
        
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/document/{file_id}")
async def delete_verified_document(
    file_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Delete a verified document from storage and database.
    This endpoint supports cleanup after QR access.
    """
    if not _is_valid_token(credentials.credentials):
        raise HTTPException(status_code=401, detail="Invalid token")
    
    try:
        storage = get_storage()
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT blob_name, container FROM uploads WHERE id = ?",
            (file_id,)
        )
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            raise HTTPException(status_code=404, detail="File not found")
        
        blob_name, container = row
        
        # Delete from storage
        try:
            storage.delete_blob(blob_name, container)
        except Exception as e:
            print(f"Azure delete error: {e}")
        
        # Delete from database
        cursor.execute("DELETE FROM uploads WHERE id = ?", (file_id,))
        conn.commit()
        conn.close()
        
        return {"success": True, "message": "Document deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/files")
async def list_files(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not _is_valid_token(credentials.credentials):
        raise HTTPException(status_code=401, detail="Invalid token")
    """List all uploaded files (admin)"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, filename, document_type, verified, created_at, verified_at
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
                "verified": bool(row[3]),
                "created_at": row[4],
                "verified_at": row[5]
            })
        
        return {"files": files}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/admin/files/{file_id}")
async def delete_file(
    file_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    if not _is_valid_token(credentials.credentials):
        raise HTTPException(status_code=401, detail="Invalid token")
    """Delete file from Azure and database (admin)"""
    try:
        storage = get_storage()
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT blob_name, container FROM uploads WHERE id = ?", (file_id,))
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="File not found")
        
        blob_name, container = row
        
        # Delete from Azure
        try:
            storage.delete_blob(blob_name, container)
        except Exception as e:
            print(f"Azure delete error: {e}")
        
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
    if not _is_valid_token(credentials.credentials):
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
    if not _is_valid_token(credentials.credentials):
        raise HTTPException(status_code=401, detail="Invalid token")
    """Validate document authenticity"""
    try:
        result = validator.validate_document(metadata, document_type)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

