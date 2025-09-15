# backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api import analyze, feedback, export
from backend.db.session import init_db

app = FastAPI(
    title="LexiCare - Modulo di Supporto alle Decisioni",
    description="Sistema AI per analisi semantica di referti clinici (in italiano)",
    version="1.0.0"
)

# Allow frontend (React) access - adjust origin in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React default dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize DB (create tables if needed)
init_db()

# Include API routes
app.include_router(analyze.router, prefix="/api/analyze", tags=["Analisi"])
app.include_router(feedback.router, prefix="/api/feedback", tags=["Feedback"])
app.include_router(export.router, prefix="/api/export", tags=["Export"])

@app.get("/")
def read_root():
    return {"messaggio": "Benvenuto in LexiCare - sistema AI per referti clinici"}
