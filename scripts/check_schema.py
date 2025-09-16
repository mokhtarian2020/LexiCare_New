#!/usr/bin/env python3
# Script to check the database schema

import os
import sqlite3

# Connect to the SQLite database
db_path = os.path.join('backend', 'db', 'lexicare.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get the table schema for reports
cursor.execute("PRAGMA table_info(reports)")
columns = cursor.fetchall()

# Print the schema details
print("\nREPORTS TABLE SCHEMA:")
print("=====================")
for column in columns:
    col_id, name, type_name, not_null, default, pk = column
    print(f"{name}: {type_name} {'NOT NULL' if not_null else 'NULL'} {'PRIMARY KEY' if pk else ''}")

# Check if patient_id exists (it should not)
has_patient_id = any(col[1] == 'patient_id' for col in columns)
print("\nCHECK RESULTS:")
print("=============")
print(f"patient_id exists: {'YES (PROBLEM!)' if has_patient_id else 'NO (GOOD)'}")
print(f"patient_cf is NOT NULL: {'YES (GOOD)' if any(col[1] == 'patient_cf' and col[3] == 1 for col in columns) else 'NO (PROBLEM!)'}")

conn.close()
