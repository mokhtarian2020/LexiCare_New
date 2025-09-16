#!/bin/bash

# Script to reset and restart the backend service

# Stop any running backend
echo "Stopping any running backend servers..."
pkill -f "uvicorn backend.main:app" || true

# Reset the database to apply schema changes
echo "Resetting database to apply schema changes..."
python scripts/reset_db.py

# Start the backend
echo "Starting backend server..."
cd /home/amir/Documents/amir/LexiCare
PYTHONPATH=$PYTHONPATH:/home/amir/Documents/amir/LexiCare uvicorn backend.main:app --host 0.0.0.0 --reload --port 8006 &
echo "Backend server started at http://0.0.0.0:8006"
