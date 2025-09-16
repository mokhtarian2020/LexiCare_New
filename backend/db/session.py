# backend/db/session.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models import Base

from dotenv import load_dotenv
load_dotenv()  # 👈 Load environment variables from .env

# Print DATABASE_URL for debug purposes
print("✅ DATABASE_URL:", os.getenv("DATABASE_URL"))

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///backend/db/lexicare.db")

# Handle SQLite connection args
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, connect_args=connect_args)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Initialize database (create tables)
def init_db():
    from backend.db import models  # 👈 Ensure models are imported
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully.")

# Dependency for FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
