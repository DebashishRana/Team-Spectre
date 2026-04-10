from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.engine import URL
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import json
import logging

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
    country = Column(String(100), nullable=True)
    receive_updates = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

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
