# backend/api/ehr.py

from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
import os

from core.pdf_parser import extract_metadata
from core.ai_engine import analyze_text_with_medgemma
from core.comparator import compare_with_previous_reports
from db import crud
from db.session import get_db
from auth.api_auth import get_api_key
from db.models import Report

router = APIRouter()

# ============ Modelli dati per richieste API ============

class PatientQuery(BaseModel):
    codice_fiscale: str
    report_type: Optional[str] = None

class FeedbackData(BaseModel):
    report_id: UUID
    diagnosi_corretta: str
    classificazione_corretta: str
    commento: Optional[str] = None

class PatientReport(BaseModel):
    id: str
    patient_cf: str
    patient_name: Optional[str]
    report_type: str
    report_date: datetime
    ai_diagnosis: str
    ai_classification: str
    doctor_diagnosis: Optional[str]
    doctor_classification: Optional[str]
    comparison_to_previous: Optional[str]
    comparison_explanation: Optional[str]

class PatientReportDetail(PatientReport):
    extracted_text: str
    doctor_comment: Optional[str]
    created_at: datetime

# ============ Endpoint per integrazione EHR ============

@router.post("/analyze", summary="Analizza referti PDF da EHR")
async def ehr_analyze_documents(
    files: List[UploadFile] = File(...),
    db = Depends(get_db),
    api_key: str = Depends(get_api_key)
):
    """Endpoint per l'analisi di referti PDF da un sistema EHR esterno.
    Richiede autenticazione con API key."""
    
    if not (1 <= len(files) <= 5):
        raise HTTPException(400, "Seleziona da 1 a 5 file PDF.")

    # Utilizza la stessa logica dell'endpoint pubblico ma con autenticazione
    risultati = []
    for f in files:
        file_bytes = await f.read()
        meta = extract_metadata(file_bytes)
        full_text = meta["full_text"]
        ai = analyze_text_with_medgemma(full_text)
        
        result = {
            "diagnosi_ai": ai["diagnosis"],
            "classificazione_ai": ai["classification"],
            "codice_fiscale": meta["codice_fiscale"],
            "nome_paziente": meta["patient_name"],
            "tipo_referto": meta["report_type"],
            "data_referto": meta["report_date"],
        }
        
        # Se c'è un codice fiscale, salva nel DB e aggiungi confronto
        if meta["codice_fiscale"]:
            # Processamento e salvataggio nel DB
            try:
                # Normalizzazione data
                if meta["report_date"]:
                    parsed_date = None
                    date_formats = ["%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y", "%Y-%m-%d"]
                    for fmt in date_formats:
                        try:
                            parsed_date = datetime.strptime(meta["report_date"], fmt)
                            break
                        except ValueError:
                            continue
                    report_dt = parsed_date if parsed_date else datetime.utcnow()
                else:
                    report_dt = datetime.utcnow()
                    
                # Salvataggio su DB
                path = crud.save_pdf(f.filename, file_bytes)
                report = crud.create_report(
                    db=db,
                    patient_cf=meta["codice_fiscale"],
                    patient_name=meta["patient_name"],
                    report_type=meta["report_type"],
                    report_date=report_dt,
                    file_path=path,
                    extracted_text=full_text,
                    ai_diagnosis=ai["diagnosis"],
                    ai_classification=ai["classification"],
                )
                
                # Confronto con precedenti
                cmp = compare_with_previous_reports(
                    db=db,
                    patient_cf=meta["codice_fiscale"],
                    report_type=meta["report_type"],
                    new_text=full_text,
                )
                crud.update_report_comparison(db, report.id, cmp)
                
                # Aggiunta info al risultato
                result.update({
                    "salvato": True,
                    "report_id": str(report.id),
                    "situazione": cmp["status"],
                    "spiegazione": cmp["explanation"]
                })
                
            except Exception as e:
                result.update({
                    "salvato": False,
                    "errore": str(e)
                })
        else:
            result["salvato"] = False
            
        risultati.append(result)
    
    return {"risultati": risultati}


@router.get("/patients/{codice_fiscale}/reports", summary="Recupera tutti i referti di un paziente", response_model=List[PatientReport])
async def get_patient_reports(
    codice_fiscale: str,
    report_type: Optional[str] = None,
    db = Depends(get_db),
    api_key: str = Depends(get_api_key)
):
    """Recupera lo storico dei referti di un paziente dal sistema LexiCare.
    
    - **codice_fiscale**: il codice fiscale del paziente (obbligatorio)
    - **report_type**: filtro opzionale per tipo di referto esatto (es. "TAC Torace", "Eccocardiografia")
    """
    # No validation needed since we accept any exact report title
    
    reports = crud.get_patient_reports(db, codice_fiscale, report_type)
    
    if not reports:
        return []
    
    # Conversione a modelli Pydantic
    result = []
    for report in reports:
        result.append(
            PatientReport(
                id=str(report.id),
                patient_cf=report.patient_cf,
                patient_name=report.patient_name,
                report_type=report.report_type,
                report_date=report.report_date,
                ai_diagnosis=report.ai_diagnosis,
                ai_classification=report.ai_classification,
                doctor_diagnosis=report.doctor_diagnosis,
                doctor_classification=report.doctor_classification,
                comparison_to_previous=report.comparison_to_previous,
                comparison_explanation=report.comparison_explanation
            )
        )
    
    return result


@router.get("/patients/{codice_fiscale}/reports/{report_id}", summary="Dettaglio referto", response_model=PatientReportDetail)
async def get_patient_report_detail(
    codice_fiscale: str,
    report_id: UUID,
    db = Depends(get_db),
    api_key: str = Depends(get_api_key)
):
    """Recupera il dettaglio completo di un singolo referto, incluso il testo estratto."""
    
    report = db.query(Report).filter(
        Report.id == report_id,
        Report.patient_cf == codice_fiscale
    ).first()
    
    if not report:
        raise HTTPException(
            status_code=404,
            detail="Referto non trovato o non autorizzato per questo paziente"
        )
    
    return PatientReportDetail(
        id=str(report.id),
        patient_cf=report.patient_cf,
        patient_name=report.patient_name,
        report_type=report.report_type,
        report_date=report.report_date,
        ai_diagnosis=report.ai_diagnosis,
        ai_classification=report.ai_classification,
        doctor_diagnosis=report.doctor_diagnosis,
        doctor_classification=report.doctor_classification,
        comparison_to_previous=report.comparison_to_previous,
        comparison_explanation=report.comparison_explanation,
        extracted_text=report.extracted_text,
        doctor_comment=report.doctor_comment,
        created_at=report.created_at
    )


@router.post("/feedback", summary="Invia feedback del medico da EHR")
async def submit_ehr_feedback(
    feedback: FeedbackData,
    db = Depends(get_db),
    api_key: str = Depends(get_api_key)
):
    """Consente al sistema EHR di inviare feedback dei medici."""
    success = crud.save_feedback(
        db=db,
        report_id=feedback.report_id,
        correct_diagnosis=feedback.diagnosi_corretta,
        correct_classification=feedback.classificazione_corretta,
        comment=feedback.commento
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Referto non trovato.")
    
    return {"messaggio": "Feedback salvato correttamente."}


@router.get("/report-types", summary="Ottieni tipi di referti validi")
async def get_report_types(
    api_key: str = Depends(get_api_key)
):
    """Restituisce informazioni sui tipi di referto supportati dal sistema."""
    return {
        "tipi_referto": "Il sistema supporta qualsiasi tipo di referto",
        "descrizione": "LexiCare estrae automaticamente il titolo esatto del referto dal documento e non ha limitazioni predefinite sui tipi supportati",
        "esempi": [
            "TAC Torace",
            "Eccocardiografia", 
            "Esami del Sangue",
            "Risonanza Magnetica",
            "Biopsia",
            "Radiografia"
        ]
    }
