from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Request
from typing import List
from datetime import datetime
import uuid
import logging
import traceback
import json

from backend.core.pdf_parser import extract_metadata
from backend.core.ai_engine import analyze_text_with_medgemma
from backend.core.comparator import compare_with_previous_reports
from backend.db import crud
from backend.db.session import get_db

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", summary="Analizza uno o più referti PDF")
async def analyze_documents(
    request: Request,
    files: List[UploadFile] = File(...),
    db=Depends(get_db)
):
    if not (1 <= len(files) <= 5):
        raise HTTPException(400, "Seleziona da 1 a 5 file PDF.")
    
    logger.info(f"Analyzing {len(files)} file(s)")
    risultati: list[dict] = []

    for f in files:
        logger.info(f"Processing file: {f.filename}")
        
        try:
            # Read the file
            file_bytes = await f.read()
            
            # Extract metadata and text from PDF
            try:
                meta = extract_metadata(file_bytes)
                full_text = meta["full_text"]
                logger.info(f"Extracted text length: {len(full_text)} characters")
                logger.info(f"Found CF: {meta.get('codice_fiscale', 'None')}, Report type: {meta.get('report_type', 'Unknown')}")
            except Exception as pdf_error:
                logger.error(f"Error extracting PDF metadata: {str(pdf_error)}")
                logger.error(traceback.format_exc())
                risultati.append({
                    "salvato": False,
                    "messaggio": f"Errore nell'elaborazione del PDF: {str(pdf_error)}",
                    "filename": f.filename
                })
                continue
            
            # Run AI analysis
            try:
                ai = analyze_text_with_medgemma(full_text)
                logger.info(f"AI analysis complete: {ai.get('classification', 'Unknown')}")
            except Exception as ai_error:
                logger.error(f"Error in AI analysis: {str(ai_error)}")
                logger.error(traceback.format_exc())
                risultati.append({
                    "salvato": False,
                    "messaggio": f"Errore nell'analisi AI: {str(ai_error)}",
                    "filename": f.filename,
                    "codice_fiscale": meta.get("codice_fiscale"),
                    "nome_paziente": meta.get("patient_name"),
                })
                continue                # Process based on whether we found a Codice Fiscale
            if not meta.get("codice_fiscale"):
                logger.info(f"⚠️ No Codice Fiscale found in report {f.filename}")
                risultati.append({
                    "salvato"            : False,
                    "messaggio"          : "Codice Fiscale assente – referto NON salvato.",
                    "diagnosi_ai"        : ai["diagnosis"],
                    "classificazione_ai" : ai["classification"],
                    "codice_fiscale"     : None,
                    "tipo_referto"       : meta.get("report_type", "sconosciuto"),
                    "nome_file"          : f.filename,
                    "nome_paziente"      : meta.get("patient_name"),
                    "data_referto"       : meta.get("report_date")
                })
                continue

            # Process report with Codice Fiscale
            try:
                logger.info(f"✅ Codice Fiscale found: {meta['codice_fiscale']}")
                internal_uuid = uuid.uuid4()
                
                # Normalize date format
                try:
                    if meta["report_date"]:
                        # Support various date formats (dd/mm/yyyy, dd-mm-yyyy, etc)
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
                except Exception as e:
                    logger.warning(f"⚠️ Date parsing error: {e}")
                    report_dt = datetime.utcnow()

                # Save to disk & DB
                logger.info(f"Saving PDF to disk and creating DB record")
                path = crud.save_pdf(f.filename, file_bytes)
                rec = crud.create_report(
                    db               = db,
                    patient_id       = internal_uuid,
                    patient_cf       = meta["codice_fiscale"],
                    patient_name     = meta["patient_name"],
                    report_type      = meta["report_type"],
                    report_date      = report_dt,
                    file_path        = path,
                    extracted_text   = full_text,
                    ai_diagnosis     = ai["diagnosis"],
                    ai_classification= ai["classification"],
                )
                logger.info(f"Report saved with ID: {rec.id}")

                # Compare with previous report
                logger.info(f"Comparing with previous reports")
                cmp = compare_with_previous_reports(
                    db            = db,
                    patient_cf    = meta["codice_fiscale"],
                    report_type   = meta["report_type"],
                    new_text      = full_text,
                )
                crud.update_report_comparison(db, rec.id, cmp)
                logger.info(f"Comparison status: {cmp['status']}")

                risultati.append({
                    "salvato"            : True,
                    "messaggio"          : "Referto salvato con successo.",
                    "report_id"          : str(rec.id),
                    "diagnosi_ai"        : ai["diagnosis"],
                    "classificazione_ai" : ai["classification"],
                    "codice_fiscale"     : meta["codice_fiscale"],
                    "nome_paziente"      : meta["patient_name"],
                    "tipo_referto"       : meta["report_type"],
                    "data_referto"       : meta["report_date"],
                    "situazione"         : cmp["status"],
                    "spiegazione"        : cmp["explanation"],
                })
            
            except Exception as save_error:
                logger.error(f"Error saving report: {str(save_error)}")
                logger.error(traceback.format_exc())
                risultati.append({
                    "salvato": False,
                    "messaggio": f"Errore nel salvataggio del referto: {str(save_error)}",
                    "diagnosi_ai": ai["diagnosis"],
                    "classificazione_ai": ai["classification"],
                    "codice_fiscale": meta.get("codice_fiscale"),
                    "nome_paziente": meta.get("patient_name"),
                    "tipo_referto": meta.get("report_type"),
                    "data_referto": meta.get("report_date"),
                })
        
        except Exception as general_error:
            logger.error(f"General error processing file {f.filename}: {str(general_error)}")
            logger.error(traceback.format_exc())
            risultati.append({
                "salvato": False,
                "messaggio": f"Errore generico: {str(general_error)}",
                "filename": f.filename
            })
            
    # Return all results
    logger.info(f"Analysis complete, returning {len(risultati)} results")
    return {"risultati": risultati}
