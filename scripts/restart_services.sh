#!/bin/bash

# Script to restart both frontend and backend services

# Kill any existing servers
echo "Stopping any running servers..."
pkill -f "uvicorn main:app"
pkill -f "npm.*run.*dev"

# Start backend
echo "Starting backend server..."
cd /home/amir/Documents/amir/LexiCare
PYTHONPATH=$PYTHONPATH:/home/amir/Documents/amir/LexiCare uvicorn backend.main:app --reload --port 8006 &
echo "Backend server started at http://localhost:8006"

# Wait a moment
sleep 2

# Start frontend
echo "Starting frontend server..."
cd /home/amir/Documents/amir/LexiCare/frontend
npm run dev &
echo "Frontend server started at http://localhost:3100"

echo "All services started! The application is running at http://localhost:3100"
