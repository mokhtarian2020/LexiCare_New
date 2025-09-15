from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from typing import List
from datetime import datetime
import uuid

from backend.core.pdf_parser import extract_metadata
from backend.core.ai_engine import analyze_text_with_medgemma
from backend.core.comparator import compare_with_previous_reports
from backend.db import crud
from backend.db.session import get_db

router = APIRouter()


@router.post("/", summary="Analizza uno o più referti PDF")
async def analyze_documents(
    files: List[UploadFile] = File(...),
    db=Depends(get_db)
):
    if not (1 <= len(files) <= 5):
        raise HTTPException(400, "Seleziona da 1 a 5 file PDF.")

    # Step 1: Extract metadata from all files
    file_data = []
    for f in files:
        try:
            file_bytes = await f.read()
            meta = extract_metadata(file_bytes)
            file_data.append({
                'filename': f.filename,
                'file_bytes': file_bytes,
                'metadata': meta,
                'error': False
            })
        except Exception as e:
            # Include error files in results but don't process them
            file_data.append({
                'filename': f.filename,
                'file_bytes': None,
                'metadata': None,
                'error': True,
                'error_message': f"Errore nella lettura del file: {str(e)}"
            })
    
    # Step 2: Sort files by report date (chronological order)
    valid_files = [fd for fd in file_data if not fd.get('error', False)]
    error_files = [fd for fd in file_data if fd.get('error', False)]
    
    def get_sort_date(file_data):
        try:
            date_str = file_data['metadata'].get('report_date')
            if date_str:
                # Parse date to ensure proper sorting
                date_formats = ["%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y", "%Y-%m-%d"]
                for fmt in date_formats:
                    try:
                        return datetime.strptime(date_str, fmt)
                    except ValueError:
                        continue
            # If no valid date, use current time
            return datetime.utcnow()
        except:
            return datetime.utcnow()
    
    valid_files.sort(key=get_sort_date)
    
    # Step 3: Process files in chronological order
    risultati: list[dict] = []

    # First, add any error files to results
    for fd in error_files:
        risultati.append({
            "salvato": False,
            "messaggio": fd.get('error_message', "Errore sconosciuto"),
            "diagnosi_ai": None,
            "classificazione_ai": None,
            "codice_fiscale": None,
            "nome_paziente": None,
            "tipo_referto": None,
            "data_referto": None,
        })

    # Process valid files in chronological order
    for fd in valid_files:
        meta = fd['metadata']
        file_bytes = fd['file_bytes']
        f_filename = fd['filename']
        
        full_text = meta["full_text"]
        ai = analyze_text_with_medgemma(full_text)

        # ---------------- caso SENZA Codice Fiscale -----------------
        if not meta["codice_fiscale"]:
            risultati.append({
                "salvato"            : False,
                "messaggio"          : "Codice Fiscale assente – referto NON salvato.",
                "diagnosi_ai"        : ai["diagnosis"],
                "classificazione_ai" : ai["classification"],
                "codice_fiscale"     : None,
                "nome_paziente"      : meta["patient_name"],
                "tipo_referto"       : meta["report_type"],
                "data_referto"       : meta["report_date"],
            })
            continue

        # --------------- caso CON Codice Fiscale --------------------
        internal_uuid = uuid.uuid4()
        try:
            report_dt = datetime.strptime(meta["report_date"], "%d/%m/%Y") \
                        if meta["report_date"] else datetime.utcnow()
        except ValueError:
            report_dt = datetime.utcnow()

        # salva file disco + DB
        path = crud.save_pdf(f_filename, file_bytes)
        rec  = crud.create_report(
            db               = db,
            patient_cf       = meta["codice_fiscale"],
            patient_name     = meta["patient_name"],
            report_type      = meta["report_type"],
            report_date      = report_dt,
            file_path        = path,
            extracted_text   = full_text,
            ai_diagnosis     = ai["diagnosis"],
            ai_classification= ai["classification"],
        )

        # confronto con referto precedente
        cmp = compare_with_previous_reports(
            db            = db,
            patient_cf    = meta["codice_fiscale"],
            report_type   = meta["report_type"],
            new_text      = full_text,
        )
        crud.update_report_comparison(db, rec.id, cmp)

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

    return {"risultati": risultati}
