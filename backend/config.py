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
    
    # Google Cloud SQL Settings
    GCP_SQL_INSTANCE_NAME: str = os.getenv("GCP_SQL_INSTANCE_NAME", "hackhorizon-492907:us-central1:hackhorizon")
    GCP_SQL_PUBLIC_IP: str = os.getenv("GCP_SQL_PUBLIC_IP", "136.116.108.22")
    GCP_SQL_PORT: int = int(os.getenv("GCP_SQL_PORT", "3306"))
    GCP_SQL_DB_NAME: str = os.getenv("GCP_SQL_DB_NAME", "user_information")
    GCP_SQL_USER: str = os.getenv("GCP_SQL_USER", "User")
    GCP_SQL_PASSWORD: str = os.getenv("GCP_SQL_PASSWORD", "")

    # Aadhaar classifier settings
    AADHAAR_MODEL_DIR: str = os.getenv("AADHAAR_MODEL_DIR", "")
    AADHAAR_CLASSIFIER_THRESHOLD: float = float(os.getenv("AADHAAR_CLASSIFIER_THRESHOLD", "0.55"))
    
    # Encryption settings
    ENCRYPTION_KEY: str = os.getenv("ENCRYPTION_KEY", "")  # Base64-encoded Fernet key
    
    class Config:
        env_file = ".env"
        extra = "allow"  # Allow extra fields for migration compatibility

settings = Settings()

