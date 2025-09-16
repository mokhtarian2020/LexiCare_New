#!/usr/bin/env python3
# Script to reset the database schema

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database, drop_database

from dotenv import load_dotenv
load_dotenv()

# Get database URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///backend/db/lexicare.db")

if DATABASE_URL.startswith("sqlite"):
    # For SQLite, just delete the file
    db_path = DATABASE_URL.replace("sqlite:///", "")
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Removed SQLite database: {db_path}")
else:
    # For PostgreSQL and other DBs, use SQLAlchemy-Utils
    if database_exists(DATABASE_URL):
        drop_database(DATABASE_URL)
        print(f"Dropped database at: {DATABASE_URL}")
    
    create_database(DATABASE_URL)
    print(f"Created fresh database at: {DATABASE_URL}")

# Initialize database schema
from backend.db.session import init_db
init_db()
print("Database schema initialized successfully")
