# backend/api/feedback.py

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from uuid import UUID
from db import crud
from db.session import get_db

router = APIRouter()

class FeedbackInput(BaseModel):
    report_id: UUID
    diagnosi_corretta: str
    classificazione_corretta: str
    commento: str = None

@router.post("/", summary="Invia correzione del medico")
def submit_feedback(payload: FeedbackInput, db=Depends(get_db)):
    success = crud.save_feedback(
        db=db,
        report_id=payload.report_id,
        correct_diagnosis=payload.diagnosi_corretta,
        correct_classification=payload.classificazione_corretta,
        comment=payload.commento
    )
    if not success:
        raise HTTPException(status_code=404, detail="Referto non trovato.")
    return {"messaggio": "Feedback salvato correttamente. Grazie per il contributo!"}
