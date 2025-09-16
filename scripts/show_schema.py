#!/usr/bin/env python3
"""
Script to display the current database schema.
This is useful to verify the database tables structure.
"""

import os
import sqlite3
from dotenv import load_dotenv
from sqlalchemy import create_engine, MetaData, inspect

# Load environment variables
load_dotenv()

# Get database URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///backend/db/lexicare.db")

def show_sqlite_schema():
    """Display schema for SQLite database."""
    db_path = DATABASE_URL.replace("sqlite:///", "")
    if not os.path.exists(db_path):
        print(f"SQLite database not found at: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n📊 CURRENT DATABASE SCHEMA (SQLite)")
    print("=" * 50)
    
    # Get list of tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    for table in tables:
        table_name = table[0]
        print(f"\n📋 TABLE: {table_name}")
        print("-" * 40)
        
        # Get table schema
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        for col in columns:
            col_id, name, type_name, not_null, default_val, is_pk = col
            constraints = []
            if is_pk:
                constraints.append("PRIMARY KEY")
            if not_null:
                constraints.append("NOT NULL")
            if default_val is not None:
                constraints.append(f"DEFAULT {default_val}")
            
            constraint_str = ", ".join(constraints)
            if constraint_str:
                print(f"{name}: {type_name} ({constraint_str})")
            else:
                print(f"{name}: {type_name}")
    
    conn.close()

def show_sql_schema():
    """Display schema for SQL database (PostgreSQL, MySQL, etc.)."""
    try:
        engine = create_engine(DATABASE_URL)
        inspector = inspect(engine)
        
        print("\n📊 CURRENT DATABASE SCHEMA")
        print("=" * 50)
        
        for table_name in inspector.get_table_names():
            print(f"\n📋 TABLE: {table_name}")
            print("-" * 40)
            
            for column in inspector.get_columns(table_name):
                constraints = []
                if column.get('primary_key'):
                    constraints.append("PRIMARY KEY")
                if not column.get('nullable'):
                    constraints.append("NOT NULL")
                if column.get('default') is not None:
                    constraints.append(f"DEFAULT {column['default']}")
                
                constraint_str = ", ".join(constraints)
                if constraint_str:
                    print(f"{column['name']}: {column['type']} ({constraint_str})")
                else:
                    print(f"{column['name']}: {column['type']}")
    
    except Exception as e:
        print(f"Error connecting to database: {e}")

if __name__ == "__main__":
    print(f"🔍 Checking database at: {DATABASE_URL}")
    
    if DATABASE_URL.startswith("sqlite"):
        show_sqlite_schema()
    else:
        show_sql_schema()
    
    print("\n✅ Schema inspection complete")
