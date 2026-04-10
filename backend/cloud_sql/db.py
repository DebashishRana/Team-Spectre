from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Enum, Text
from sqlalchemy.engine import URL
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import json
import logging
import enum

from config import settings

# Build URL via SQLAlchemy helper so special characters in password are escaped safely.
DB_URL = URL.create(
    "mysql+pymysql",
    username=settings.GCP_SQL_USER,
    password=settings.GCP_SQL_PASSWORD,
    host=settings.GCP_SQL_PUBLIC_IP,
    port=settings.GCP_SQL_PORT,
    database=settings.GCP_SQL_DB_NAME,
    query={"charset": "utf8mb4"},
)

try:
    engine = create_engine(DB_URL, pool_recycle=3600, echo=False)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
except Exception as e:
    logging.error(f"Failed to initialize Google Cloud SQL engine: {e}")
    engine = None
    SessionLocal = None
    Base = declarative_base()

class UserAccount(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    username = Column(String(100), nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    phone_number = Column(String(20), nullable=True)
    country = Column(String(100), nullable=True)
    email_verified = Column(Boolean, default=False)
    receive_updates = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DocumentType(str, enum.Enum):
    AADHAAR = "aadhaar"
    PAN = "pan"
    PASSPORT = "passport"
    DRIVING_LICENSE = "driving_license"


class UserDocument(Base):
    __tablename__ = "user_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)  # Links to UserAccount
    document_type = Column(String(50), nullable=False)  # e.g., "aadhaar", "pan"
    
    # Encrypted fields
    id_number = Column(Text, nullable=True)  # Encrypted Aadhaar/PAN number
    full_name = Column(Text, nullable=True)  # Encrypted name
    date_of_birth = Column(String(100), nullable=True)  # Can be public or encrypted
    gender = Column(String(10), nullable=True)
    phone = Column(Text, nullable=True)  # Encrypted
    address = Column(Text, nullable=True)  # Encrypted
    
    # Metadata
    document_file_url = Column(String(500), nullable=True)  # GCS URL to original document
    confidence_score = Column(String(50), nullable=True)  # e.g., "94.6%"
    validation_status = Column(String(50), nullable=True)  # "valid", "partial", "invalid"
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


def init_cloud_sql_db():
    if engine is not None:
        try:
            Base.metadata.create_all(bind=engine)
            print("Google Cloud SQL tables successfully verified/created.")
        except Exception as e:
            logging.error(f"Failed to create Google Cloud SQL tables: {e}")

def get_db():
    if SessionLocal:
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    else:
        yield None
