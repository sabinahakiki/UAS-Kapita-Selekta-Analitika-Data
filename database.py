# database.py
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Prefer DATABASE_URL if provided; fall back to individual pieces for local dev
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = os.getenv("MYSQL_PORT", "3306")
MYSQL_DB = os.getenv("MYSQL_DB", "elearning_db")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@"
    f"{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}",
)

# ✅ engine: dipakai oleh Base.metadata.create_all dan SessionLocal
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

# ✅ Base: inilah yang di-import di main.py & models.py
Base = declarative_base()

# ✅ SessionLocal: dipakai di router untuk get_db()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
