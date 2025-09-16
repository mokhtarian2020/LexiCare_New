#!/bin/bash

# Script to check if frontend dev server is running and start it if not

cd /home/amir/Documents/amir/LexiCare/frontend

# Check if npm is running the dev server
if ! pgrep -f "npm.*run.*dev" > /dev/null; then
    echo "Starting frontend development server..."
    npm run dev &
    echo "Frontend server started! It will be available at http://localhost:3100"
else
    echo "Frontend development server is already running."
    echo "You can access it at http://localhost:3100"
fi
