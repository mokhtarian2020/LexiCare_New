#!/usr/bin/env python3
# Script to update database schema with new report_title column

import os
import sys
from sqlalchemy import create_engine, inspect, Column, Text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import database_exists
from dotenv import load_dotenv

load_dotenv()

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Get database URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///backend/db/lexicare.db")

# Check if the database exists
if not database_exists(DATABASE_URL):
    print(f"❌ Database does not exist at: {DATABASE_URL}")
    print("Run 'python scripts/reset_db.py' first to create it.")
    sys.exit(1)

# Connect to the database
engine = create_engine(DATABASE_URL)

# Create a session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

# Check if the report_title column exists
inspector = inspect(engine)
columns = inspector.get_columns('reports')
column_names = [c['name'] for c in columns]

if 'report_title' in column_names:
    print("✅ The report_title column already exists in the reports table.")
    db.close()
    sys.exit(0)

# Add the column to the database using raw SQL
# This is a safer approach than using SQLAlchemy Core or ORM
# as it avoids potential conflicts with existing models
try:
    if DATABASE_URL.startswith('sqlite'):
        # SQLite syntax
        db.execute("ALTER TABLE reports ADD COLUMN report_title TEXT")
    else:
        # PostgreSQL syntax
        db.execute("ALTER TABLE reports ADD COLUMN report_title TEXT")
    
    db.commit()
    print("✅ Successfully added report_title column to reports table.")
except Exception as e:
    db.rollback()
    print(f"❌ Error adding column: {e}")
    print("Consider resetting the database using 'python scripts/reset_db.py'")
finally:
    db.close()
