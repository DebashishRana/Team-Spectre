"""
Configuration settings for Unified Identity portal
"""

import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Azure Blob Storage
    AZURE_STORAGE_ACCOUNT_NAME: str = os.getenv("AZURE_STORAGE_ACCOUNT_NAME", "")
    AZURE_STORAGE_ACCOUNT_KEY: str = os.getenv("AZURE_STORAGE_ACCOUNT_KEY", "")
    AZURE_STORAGE_CONTAINER_INCOMING: str = os.getenv("AZURE_STORAGE_CONTAINER_INCOMING", "incoming-docs")
    AZURE_STORAGE_CONTAINER_VERIFIED: str = os.getenv("AZURE_STORAGE_CONTAINER_VERIFIED", "verified-docs")
    
    # API Security
    API_TOKEN: str = os.getenv("API_TOKEN", "Unified Identity portal-secret-token-change-in-production")
    
    # CORS
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    
    # SAS token expiry settings
    UPLOAD_SAS_EXPIRY_MINUTES: int = 5
    # Read access SAS used by QR endpoints.
    # Keep as seconds (short-lived). If an old env var like QR_SAS_EXPIRY_HOURS is present,
    # prefer it and convert to seconds.
    QR_SAS_EXPIRY_SECONDS: int = int(os.getenv("QR_SAS_EXPIRY_SECONDS", "0") or "0") or (
        int(os.getenv("QR_SAS_EXPIRY_HOURS", "0") or "0") * 3600
    ) or 45  # default 30-60 seconds
    
    # File upload settings
    MAX_FILE_SIZE_MB: int = 20
    ALLOWED_EXTENSIONS: list = [".pdf", ".jpg", ".jpeg", ".png"]
    
    class Config:
        env_file = ".env"
        extra = "allow"  # Allow extra fields for migration compatibility

settings = Settings()

