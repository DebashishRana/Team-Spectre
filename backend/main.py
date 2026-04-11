"""
Unified Identity portal Backend API
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
from document_classifier import DocumentClassifier
from validators import DocumentValidator
from config import settings
from azure_storage import get_azure_storage
from cloud_sql.db import get_db, UserAccount, init_cloud_sql_db
from cloud_sql.models import AuthRequest
from sqlalchemy.orm import Session
import logging

LEGACY_DEV_TOKEN = "Unified Identity portal-secret-token-change-in-productio"


def _is_valid_token(token: str) -> bool:
    # Accept current configured token, plus legacy default token used by the frontend
    # to avoid local dev mismatches.
    return token in {settings.API_TOKEN, LEGACY_DEV_TOKEN}

app = FastAPI(title="Unified Identity portal API", version="1.0.0")

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
document_classifier = DocumentClassifier()

# Database setup
DB_PATH = "Unified Identity portal.db"

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
init_cloud_sql_db()


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
    return {"message": "Unified Identity portal API", "version": "1.0.0"}

@app.post("/api/auth/register")
async def register_user(request: AuthRequest, db: Session = Depends(get_db)):
    if not db:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    existing_user = db.query(UserAccount).filter(UserAccount.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    hashed_password = request.password # Use proper hashing in prod
    
    new_user = UserAccount(
        email=request.email,
        password_hash=hashed_password,
        username=request.username,
        country=request.country,
        receive_updates=request.receive_updates
    )
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"success": True, "message": "User registered successfully", "user_id": new_user.id}
    except Exception as e:
        db.rollback()
        logging.error(f"Error registering user: {e}")
        raise HTTPException(status_code=500, detail="Failed to register user")

@app.post("/api/auth/login")
async def login_user(request: AuthRequest, db: Session = Depends(get_db)):
    if not db:
        raise HTTPException(status_code=500, detail="Database connection failed")
        
    user = db.query(UserAccount).filter(UserAccount.email == request.email).first()
    if not user or user.password_hash != request.password: # Should verify against hashed password
        raise HTTPException(status_code=401, detail="Invalid email or password")
        
    return {"success": True, "message": "Login successful", "user_id": user.id, "email": user.email}

from cloud_sql.aadhaar_ocr import extract_aadhaar_details
import tempfile
import shutil

@app.post("/api/extract-aadhaar")
async def extract_aadhaar_endpoint(file: UploadFile = File(...)):
    # Save the file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
    
    try:
        classification = document_classifier.classify_image_path(tmp_path)
        print(f"[DEBUG] Classification result: {classification}")

        # Process the image via OCR regardless of classifier result
        result = extract_aadhaar_details(tmp_path)
        print(f"[DEBUG] OCR result type: {type(result)}, value: {result}")
        
        # Handle OCR errors
        if isinstance(result, str) or isinstance(result, dict) and 'error' in result:
            print(f"[DEBUG] OCR failed: {result}")
            raise HTTPException(
                status_code=422,
                detail={
                    "message": f"OCR extraction failed: {result}",
                    "classification": classification,
                },
            )

        # Optional second-layer validation using existing validator.
        validation = validator.validate_document(result, "Aadhaar")
        print(f"[DEBUG] Validation result: {validation}")
        
    finally:
        os.remove(tmp_path)
        
    return {
        "status": "success",
        "classification": classification,
        "validation": validation,
        "data": result,
    }

@app.post("/api/save-document")
async def save_document_endpoint(
    user_id: int = Form(...),
    document_type: str = Form(...),  # "aadhaar", "pan", etc.
    extracted_data: str = Form(...),  # JSON string of extracted data
    classification: str = Form(...),  # JSON string of classifier result
    validation: str = Form(...),  # JSON string of validation result
    db: Session = Depends(get_db)
):
    """
    Save extracted document data to user vault with encryption.
    Sensitive fields (Aadhaar, phone, address) are encrypted before storage.
    """
    if not db:
        raise HTTPException(status_code=500, detail="Database not available")
    
    try:
        from encryption import DocumentEncryption, should_encrypt
        from cloud_sql.db import UserDocument
        
        # Parse JSON inputs
        data = json.loads(extracted_data)
        classification_result = json.loads(classification)
        validation_result = json.loads(validation)
        
        # Initialize encryption
        encryptor = DocumentEncryption()
        
        # Create document record
        doc_record = UserDocument(
            user_id=user_id,
            document_type=document_type,
            confidence_score=f"{(classification_result.get('confidence', 0) * 100):.1f}%",
            validation_status=validation_result.get("status", "unknown")
        )
        
        # Encrypt and assign fields
        for key, value in data.items():
            if hasattr(doc_record, key):
                if should_encrypt(key):
                    # Encrypt sensitive fields
                    setattr(doc_record, key, encryptor.encrypt_field(str(value)))
                else:
                    # Store non-sensitive fields plaintext
                    setattr(doc_record, key, value)
        
        # Save to database
        db.add(doc_record)
        db.commit()
        db.refresh(doc_record)
        
        return {
            "status": "success",
            "message": "Document saved securely to vault",
            "document_id": doc_record.id,
            "user_id": user_id,
            "document_type": document_type,
            "saved_at": doc_record.created_at
        }
    
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON in request: {str(e)}")
    except Exception as e:
        print(f"[ERROR] Failed to save document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to save document: {str(e)}")


@app.get("/api/get-documents/{user_id}")
async def get_user_documents(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve user's stored documents with decryption of sensitive fields.
    """
    if not db:
        raise HTTPException(status_code=500, detail="Database not available")
    
    try:
        from encryption import DocumentEncryption, should_encrypt
        from cloud_sql.db import UserDocument
        
        # Fetch documents
        documents = db.query(UserDocument).filter(UserDocument.user_id == user_id).all()
        
        encryptor = DocumentEncryption()
        result = []
        
        for doc in documents:
            doc_dict = {
                "id": doc.id,
                "document_type": doc.document_type,
                "confidence_score": doc.confidence_score,
                "validation_status": doc.validation_status,
                "created_at": doc.created_at
            }
            
            # Decrypt sensitive fields
            for key in ["id_number", "full_name", "phone", "address"]:
                encrypted_value = getattr(doc, key, None)
                if encrypted_value and should_encrypt(key):
                    try:
                        doc_dict[key] = encryptor.decrypt_field(encrypted_value)
                    except:
                        doc_dict[key] = "[Decryption failed]"
                else:
                    doc_dict[key] = getattr(doc, key, None)
            
            result.append(doc_dict)
        
        return {
            "status": "success",
            "user_id": user_id,
            "document_count": len(result),
            "documents": result
        }
    
    except Exception as e:
        print(f"[ERROR] Failed to retrieve documents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve documents: {str(e)}")

@app.post("/api/autofill")
async def autofill_endpoint(
    user_id: int = Form(...),
    document_id: int = Form(...),
    form_fields: str = Form(...),  # JSON array of field names
    db: Session = Depends(get_db)
):
    """
    Auto-fill form fields using stored user document data.
    
    Request:
    {
      "user_id": 1,
      "document_id": 5,
      "form_fields": ["full_name", "dob", "aadhaar", "address"]
    }
    
    Response:
    {
      "status": "success",
      "document_id": 5,
      "document_type": "aadhaar",
      "filled_fields": {
        "full_name": "John Doe",
        "dob": "11/10/1987",
        "aadhaar": "3818 8009 2292",
        "address": "Flat C3, Mumbai"
      }
    }
    """
    if not db:
        raise HTTPException(status_code=500, detail="Database not available")
    
    try:
        from encryption import DocumentEncryption, should_encrypt
        from cloud_sql.db import UserDocument
        from autofill import autofill, map_field
        import json
        
        # Parse form fields JSON
        try:
            fields_to_fill = json.loads(form_fields)
            if not isinstance(fields_to_fill, list):
                fields_to_fill = [form_fields]
        except:
            fields_to_fill = [form_fields]
        
        # Fetch document with user_id validation
        doc = db.query(UserDocument).filter(
            UserDocument.id == document_id,
            UserDocument.user_id == user_id  # Security: only own documents
        ).first()
        
        if not doc:
            raise HTTPException(
                status_code=404,
                detail="Document not found or unauthorized access"
            )
        
        # Prepare user data dict with decryption
        encryptor = DocumentEncryption()
        user_data = {
            "full_name": doc.full_name,
            "date_of_birth": doc.date_of_birth,
            "gender": doc.gender,
            "id_number": doc.id_number,
            "phone": doc.phone,
            "address": doc.address,
        }
        
        # Decrypt sensitive fields
        for key in ["id_number", "full_name", "phone", "address"]:
            if user_data.get(key) and should_encrypt(key):
                try:
                    user_data[key] = encryptor.decrypt_field(user_data[key])
                except Exception as e:
                    print(f"[WARN] Failed to decrypt {key}: {str(e)}")
                    user_data[key] = None
        
        # Perform auto-fill
        filled_fields = autofill(fields_to_fill, user_data)
        
        return {
            "status": "success",
            "document_id": document_id,
            "document_type": doc.document_type,
            "filled_fields": filled_fields,
            "field_mapping": {
                field_name: map_field(field_name)
                for field_name in fields_to_fill
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Auto-fill failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Auto-fill failed: {str(e)}")


@app.get("/api/user-extraction-logs/{user_id}")
async def get_user_extraction_logs(
    user_id: int,
    skip: int = 0,
    limit: int = 50,
    document_type: str = None,
    status: str = None,
    db: Session = Depends(get_db)
):
    """
    Retrieve verification logs (extraction history) for a user with pagination and filtering.
    
    Query Parameters:
    - skip: Number of records to skip (default 0)
    - limit: Number of records to return (default 50, max 100)
    - document_type: Filter by document type (e.g., "aadhaar")
    - status: Filter by validation status (e.g., "valid", "partial", "invalid")
    
    Response:
    {
      "status": "success",
      "total_count": 10,
      "records": [
        {
          "id": 1,
          "document_type": "aadhaar",
          "confidence_score": "94.6%",
          "validation_status": "valid",
          "created_at": "2024-01-15T10:30:00",
          "extracted_data": {
            "id_number": "3818 8009 2292",
            "full_name": "John Doe",
            "date_of_birth": "11/10/1987",
            "address": "Flat C3, Mumbai"
          }
        }
      ]
    }
    """
    if not db:
        raise HTTPException(status_code=500, detail="Database not available")
    
    try:
        from encryption import DocumentEncryption, should_encrypt
        from cloud_sql.db import UserDocument
        
        # Limit max records
        limit = min(limit, 100)
        
        # Build query
        query = db.query(UserDocument).filter(UserDocument.user_id == user_id)
        
        # Apply filters
        if document_type:
            query = query.filter(UserDocument.document_type == document_type)
        if status:
            query = query.filter(UserDocument.validation_status == status)
        
        # Get total count before pagination
        total_count = query.count()
        
        # Apply pagination and order by latest first
        documents = query.order_by(UserDocument.created_at.desc()).offset(skip).limit(limit).all()
        
        encryptor = DocumentEncryption()
        records = []
        
        for doc in documents:
            # Prepare extracted data with decryption
            extracted_data = {}
            decrypt_fields = ["id_number", "full_name", "phone", "address"]
            
            for key in decrypt_fields:
                encrypted_value = getattr(doc, key, None)
                if encrypted_value:
                    if should_encrypt(key):
                        try:
                            extracted_data[key] = encryptor.decrypt_field(encrypted_value)
                        except Exception as e:
                            print(f"[WARN] Failed to decrypt {key}: {str(e)}")
                            extracted_data[key] = "[Decryption failed]"
                    else:
                        extracted_data[key] = encrypted_value
            
            # Add non-sensitive extracted fields
            for key in ["date_of_birth", "gender"]:
                value = getattr(doc, key, None)
                if value:
                    extracted_data[key] = value
            
            records.append({
                "id": doc.id,
                "document_type": doc.document_type,
                "confidence_score": doc.confidence_score,
                "validation_status": doc.validation_status,
                "created_at": doc.created_at.isoformat() if doc.created_at else None,
                "extracted_data": extracted_data
            })
        
        return {
            "status": "success",
            "total_count": total_count,
            "returned_count": len(records),
            "skip": skip,
            "limit": limit,
            "records": records
        }
    
    except Exception as e:
        print(f"[ERROR] Failed to fetch extraction logs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch extraction logs: {str(e)}")


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


""" Schema Demonstration Endpoints for Demo and future application details extraction and auto fill workflow"""

@app.get("/api/demo/schema-structure")
async def get_schema_structure():
    """
    SCHEMA DEMONSTRATION ENDPOINT - Level 1: Structure
    
    Shows the UniversalSchema used across all document types
    Useful for: Instructors, investigators, auditors, integration partners
    Use Case: Understanding how data is normalized across government documents
    """
    from schema import UniversalSchema
    
    schema_info = {
        "name": "UniversalSchema",
        "version": "1.0.0",
        "purpose": "Universal data normalization layer for Indian government documents",
        
        "fields": {
            "full_name": {
                "type": "string",
                "example": "Rajesh Kumar",
                "validation": "Title case, alphanumeric + hyphens/apostrophes",
                "source_documents": ["Aadhaar", "Passport", "Driving License", "PAN"],
                "why_used": "Primary identifier across all government systems"
            },
            "date_of_birth": {
                "type": "string",
                "format": "YYYY-MM-DD (ISO 8601)",
                "example": "1990-05-15",
                "accepts_formats": ["DD/MM/YYYY", "DD-MM-YYYY", "YYYY-MM-DD"],
                "validation": "Auto-converts to ISO 8601 for API integration",
                "why_used": "Standard for eligibility checks in welfare schemes"
            },
            "gender": {
                "type": "enum",
                "values": ["Male", "Female", "Other"],
                "example": "Male",
                "validation": "Case-insensitive, normalized to capitalized",
                "why_used": "Required for demographic analysis and scheme eligibility"
            },
            "id_number": {
                "type": "string",
                "example": "123456789012",
                "validation": "Aadhaar: 12 digits, spaces removed. PAN: 10 chars",
                "document_types": {
                    "Aadhaar": "12 digits (e.g., 123456789012)",
                    "PAN": "10 alphanumeric (e.g., ABCDE1234F)",
                    "Passport": "Document number (e.g., A12345678)",
                    "Driving License": "License number (e.g., DL-0120220123456)"
                },
                "why_used": "Unique identifier for cross-verification with UIDAI, NSDL, etc."
            },
            "document_type": {
                "type": "enum",
                "values": ["Aadhaar", "Passport", "Driving License", "PAN", "Voter ID"],
                "example": "Aadhaar",
                "why_used": "Routes data to appropriate government system"
            },
            "address": {
                "type": "string",
                "example": "123 Main Street, New Delhi, Delhi 110001",
                "validation": "No special standardization - extracted as-is",
                "why_used": "Residence verification for various government schemes"
            },
            "phone": {
                "type": "string",
                "example": "+91-9876543210",
                "validation": "Should include country code",
                "why_used": "Contact for notifications and OTP verification",
                "optional": True
            }
        },
        
        "data_flow": {
            "step_1": "User uploads document (image/PDF)",
            "step_2": "DocumentClassifier identifies document type (94.6% accuracy)",
            "step_3": "DocumentProcessor extracts raw data using OCR",
            "step_4": "UniversalSchema.clean() normalizes & validates data",
            "step_5": "Cleaned data stored in Cloud SQL",
            "step_6": "Data available for government API integration"
        }
    }
    
    return {
        "success": True,
        "message": "Schema structure for Seva Setu Portal",
        "schema": schema_info
    }


@app.get("/api/demo/extraction-examples")
async def get_extraction_examples():
    """
    SCHEMA DEMONSTRATION ENDPOINT - Level 2: Real Examples
    
    Shows how different Indian documents map to UniversalSchema
    Focus: How raw data is cleaned and standardized
    """
    
    examples = {
        "aadhaar_example": {
            "document": "Aadhaar Card (12-digit UID)",
            "raw_ocr_output": {
                "name": "RAJESH KUMAR",
                "dob": "15/05/1990",
                "gender": "M",
                "aadhaar_number": "1234 5678 9012",
                "address": "house no. 123, main street, new delhi, delhi 110001",
                "phone": "9876543210"
            },
            "after_schema_cleaning": {
                "full_name": "Rajesh Kumar",
                "date_of_birth": "1990-05-15",
                "gender": "Male",
                "id_number": "123456789012",
                "document_type": "Aadhaar",
                "address": "house no. 123, main street, new delhi, delhi 110001",
                "phone": "+91-9876543210"
            },
            "what_changed": [
                "Full name: UPPERCASE → Title Case",
                "DOB: DD/MM/YYYY → ISO 8601 (YYYY-MM-DD)",
                "Gender: Single letter 'M' → Full word 'Male'",
                "Aadhaar: Spaces removed (1234 5678 9012 → 123456789012)",
                "Phone: Added country code (+91-)"
            ]
        },
        
        "passport_example": {
            "document": "Indian Passport",
            "raw_ocr_output": {
                "Given Names": "Rajesh",
                "Surname": "Kumar",
                "Date of Birth": "15-May-1990",
                "Passport Number": "K12345678",
                "Address": "123 Main Street, New Delhi, India",
                "Sex": "M"
            },
            "after_schema_cleaning": {
                "full_name": "Rajesh Kumar",
                "date_of_birth": "1990-05-15",
                "gender": "Male",
                "id_number": "K12345678",
                "document_type": "Passport",
                "address": "123 Main Street, New Delhi, India",
                "phone": None
            },
            "what_changed": [
                "Combines Given Names + Surname",
                "Date format conversion",
                "Gender normalization",
                "Phone not available on passport"
            ]
        },
        
        "driving_license_example": {
            "document": "Indian Driving License",
            "raw_ocr_output": {
                "Name": "Rajesh Kumar",
                "Date of Birth": "15/05/1990",
                "Sex": "Male",
                "License No": "DL-0120220123456",
                "Address": "123 Main Street, New Delhi, Delhi 110001",
                "Mobile": "98765 43210"
            },
            "after_schema_cleaning": {
                "full_name": "Rajesh Kumar",
                "date_of_birth": "1990-05-15",
                "gender": "Male",
                "id_number": "DL-0120220123456",
                "document_type": "Driving License",
                "address": "123 Main Street, New Delhi, Delhi 110001",
                "phone": "+91-9876543210"
            },
            "what_changed": [
                "Date format standardized",
                "Phone number formatted with country code"
            ]
        }
    }
    
    return {
        "success": True,
        "message": "Real-world extraction examples showing schema normalization",
        "examples": examples
    }


@app.get("/api/demo/govt-api-integration")
async def get_govt_api_integration():
    """
    SCHEMA DEMONSTRATION ENDPOINT - Level 3: Government API Integration
    
    Shows how UniversalSchema enables automatic government system integration
    Focus: How this saves time & reduces re-verification
    
    Integration Partners:
    - UIDAI (Unique Identification Authority of India)
    - Ministry of External Affairs (Passport)
    - RTO (Road Transport Office)
    - NSDL (National Securities Depository Limited)
    """
    
    integration_strategy = {
        "title": "How Seva Setu Portal Integrates with Government APIs",
        
        "current_problem": {
            "issue": "Citizens re-verify same data across multiple government portals",
            "example": "Upload Aadhaar at tax portal, then re-upload at welfare portal",
            "time_waste": "Average 15-20 minutes per application across 3-4 portals",
            "frustration": "No data sharing between government systems"
        },
        
        "solution_with_schema": {
            "concept": "UniversalSchema as 'Unified Data Bridge'",
            "flow": "Extract Once → Normalize → Share with Multiple APIs"
        },
        
        "integration_examples": {
            
            "integration_1": {
                "use_case": "Auto-fill Pradhan Mantri Awas (Housing) Scheme",
                "government_system": "Ministry of Housing & Urban Affairs",
                "api_endpoint": "/api/v1/applicant/apply",
                "required_fields": ["full_name", "date_of_birth", "address", "id_number"],
                "how_schema_helps": "Already normalized in UniversalSchema, directly map to API",
                "code_example": {
                    "from_schema": {
                        "full_name": "Rajesh Kumar",
                        "date_of_birth": "1990-05-15",
                        "address": "123 Main Street, New Delhi, Delhi 110001",
                        "id_number": "123456789012"
                    },
                    "to_api_call": {
                        "json": {
                            "applicant_name": "Rajesh Kumar",
                            "dob": "1990-05-15",
                            "residential_address": "123 Main Street, New Delhi, Delhi 110001",
                            "aadhaar_number": "123456789012"
                        }
                    },
                    "time_saved": "5 minutes (no manual typing)"
                }
            },
            
            "integration_2": {
                "use_case": "Direct UIDAI Verification (Aadhaar)",
                "government_system": "UIDAI (Unique Identification Authority)",
                "api_endpoint": "/gateway/kyc/verify",
                "required_fields": ["id_number", "phone"],
                "how_schema_helps": "Aadhaar validation already done by schema.clean()",
                "benefits": [
                    "Instant KYC verification",
                    "No manual Aadhaar entry by user",
                    "Reduces fraud (auto-extracted vs typed)"
                ]
            },
            
            "integration_3": {
                "use_case": "Eligibility Check - Jan Dhan Yojana",
                "government_system": "Ministry of Finance",
                "api_endpoint": "/eligibility/check",
                "required_fields": ["full_name", "date_of_birth", "address"],
                "how_schema_helps": "Standard format ensures compatibility with eligibility rules",
                "feature": "Auto-fill matching form fields without manual retype"
            },
            
            "integration_4": {
                "use_case": "Digital Identity for e-Services",
                "government_system": "Digital India Framework",
                "api_endpoint": "/digilocker/store",
                "required_fields": ["full_name", "id_number", "date_of_birth"],
                "how_schema_helps": "One extraction → Store in Digilocker → Use everywhere",
                "benefit": "Eliminates need to re-upload same document across portals"
            }
        },
        
        "time_savings_analysis": {
            "manual_process": {
                "step_1": "Upload Aadhaar to application 1: 5 min",
                "step_2": "Manually fill same fields in application 2: 5 min",
                "step_3": "Upload to application 3: 5 min",
                "step_4": "Wait for verification across systems: 10 min",
                "total_time": "25 minutes",
                "verification_count": "3x (re-verified at each portal)"
            },
            
            "with_schema": {
                "step_1": "Upload Aadhaar once to Seva Setu: 2 min",
                "step_2": "Schema extracts & normalizes: 5 sec",
                "step_3": "Auto-fill Application 1: 10 sec",
                "step_4": "Auto-fill Application 2: 10 sec",
                "step_5": "Auto-fill Application 3: 10 sec",
                "step_6": "UIDAI verification (single, trusted): 5 min",
                "total_time": "8 minutes",
                "verification_count": "1x (single UIDAI check, reused)",
                "time_saved": "17 minutes (68% reduction)",
                "verification_reduction": "3x → 1x (one-time verification)"
            }
        },
        
        "api_mapping_rules": {
            "rule_1": {
                "schema_field": "full_name",
                "possible_api_fields": ["applicant_name", "name", "full_name", "person_name"],
                "normalization": "Already Title Case from schema.clean()"
            },
            "rule_2": {
                "schema_field": "date_of_birth",
                "possible_api_fields": ["dob", "birth_date", "date_of_birth"],
                "normalization": "Always ISO 8601 (YYYY-MM-DD) - no conversion needed"
            },
            "rule_3": {
                "schema_field": "id_number",
                "possible_api_fields": ["aadhaar_number", "aadhaar", "uid", "national_id"],
                "normalization": "Always cleaned (no spaces) - ready for comparison"
            },
            "rule_4": {
                "schema_field": "address",
                "possible_api_fields": ["residential_address", "address", "current_address"],
                "normalization": "Single format - can use as-is or parse into components"
            }
        },
        
        "implementation_roadmap": {
            "phase_1": {
                "name": "Schema Foundation (COMPLETED)",
                "work": "UniversalSchema extraction & normalization",
                "status": "✓ Done"
            },
            "phase_2": {
                "name": "Government API Connectors (NEXT)",
                "work": "Build adapters for UIDAI, passport, welfare schemes",
                "components": [
                    "UidaiConnector - SOAP/REST to UIDAI system",
                    "WelfareSchemeConnector - Ministry of Social Justice APIs",
                    "DigitalIndiaConnector - Digital Locker integration"
                ]
            },
            "phase_3": {
                "name": "One-Click Application",
                "work": "Auto-fill multiple applications from schema",
                "feature": "Fill once, apply everywhere"
            },
            "phase_4": {
                "name": "Cross-Portal Verification Sharing",
                "work": "Share verification status across portals",
                "benefit": "No re-verification needed"
            }
        }
    }
    
    return {
        "success": True,
        "message": "How UniversalSchema enables government API integration",
        "integration_strategy": integration_strategy
    }


@app.get("/api/demo/all")
async def get_all_demo_data():
    """
    COMPLETE DEMO PACKAGE
    Returns all schema info, examples, and integration strategy in one call
    Perfect for: Instructor presentations, investor demos, documentation
    """
    
    demo_data = {
        "title": "Seva Setu Portal - Schema Demo Complete Package",
        "version": "1.0.0",
        "for_audience": "Instructors, Investigators, Government Partners, Developers",
        
        "quick_facts": {
            "schema_name": "UniversalSchema",
            "fields_tracked": 7,
            "documents_supported": 5,
            "classifier_accuracy": "94.6%",
            "time_saved_per_application": "17 minutes",
            "verification_reduction": "68% (3x → 1x)"
        },
        
        "access_structure": {
            "level_1": {
                "endpoint": "/api/demo/schema-structure",
                "focus": "Understanding the data model",
                "for": "Architects, investigators"
            },
            "level_2": {
                "endpoint": "/api/demo/extraction-examples",
                "focus": "Real-world document processing",
                "for": "Instructors, QA teams"
            },
            "level_3": {
                "endpoint": "/api/demo/govt-api-integration",
                "focus": "How to integrate with government systems",
                "for": "Government partners, project managers"
            },
            "level_all": {
                "endpoint": "/api/demo/all",
                "focus": "Complete information package",
                "for": "Comprehensive overview"
            }
        }
    }
    
    return {
        "success": True,
        "message": "Schema Demo Package - All levels combined",
        "demo": demo_data
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)

