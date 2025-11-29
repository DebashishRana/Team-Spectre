"""
Configuration settings for VeriQuickX
"""

import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Dropbox
    DROPBOX_ACCESS_TOKEN: str = os.getenv("DROPBOX_ACCESS_TOKEN", "")
    
    # API Security
    API_TOKEN: str = os.getenv("API_TOKEN", "veriquickx-secret-token-change-in-production")
    
    # CORS
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    
    # QR Code expiry (hours)
    QR_EXPIRY_HOURS: int = 24
    
    # File upload settings
    MAX_FILE_SIZE_MB: int = 20
    ALLOWED_EXTENSIONS: list = [".pdf", ".jpg", ".jpeg", ".png"]
    
    class Config:
        env_file = ".env"

settings = Settings()

