# backend/main.py

import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import analyze, feedback, export, ehr, analyze_fixed
from db.session import init_db
from dotenv import load_dotenv
import uvicorn

# Load environment variables
load_dotenv()

app = FastAPI(
    title="LexiCare - Modulo di Supporto alle Decisioni",
    description="Sistema AI per analisi semantica di referti clinici (in italiano)",
    version="1.0.0"
)

# Setup allowed origins
allowed_origins = [
    "http://localhost:3100",  # Vite dev server
]

# Add EHR domains from environment variables
for i in range(1, 10):  # Support up to 10 EHR domains
    ehr_domain = os.getenv(f"EHR_DOMAIN_{i}")
    if ehr_domain:
        allowed_origins.append(ehr_domain)

# Allow frontend development server and EHR integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize DB (create tables if needed)
init_db()

# Include API routes
app.include_router(analyze.router, prefix="/api/analyze", tags=["Analisi"])
app.include_router(analyze_fixed.router, prefix="/analyze-fixed", tags=["Analisi Fixed"])
app.include_router(feedback.router, prefix="/api/feedback", tags=["Feedback"])
app.include_router(export.router, prefix="/api/export", tags=["Export"])
app.include_router(ehr.router, prefix="/api/ehr", tags=["Integrazione EHR"])

@app.get("/")
def read_root():
    return {"messaggio": "Benvenuto in LexiCare - sistema AI per referti clinici"}

# Run the server directly if this file is executed
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8009))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run("backend.main:app", host=host, port=port, reload=True)
