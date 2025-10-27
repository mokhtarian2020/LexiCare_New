from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Request
from typing import List
from datetime import datetime
import uuid
import logging
import traceback
import json

from core.pdf_parser import extract_metadata
from core.ai_engine import analyze_text_with_medgemma
from core.comparator import (compare_with_previous_reports, compare_with_latest_report_of_type,
                                    compare_with_previous_report_by_title, compare_with_latest_report_by_title_only)
from db import crud
from db.session import get_db
from db.models import Report
from sqlalchemy.orm import Session

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

def extract_key_values_from_text(text, report_type):
    """Extract key values from text based on report type for comparison"""
    import re
    key_values = {}
    
    # Determine report category from type
    report_lower = report_type.lower()
    
    if any(keyword in report_lower for keyword in ['urine', 'sangue', 'laboratorio', 'chimico', 'ematochimici']):
        # LABORATORY REPORTS - Extract numerical values
        lab_patterns = [
            (r'Proteine.*?([0-9,\.]+).*?mg/dl', 'Proteine'),
            (r'Glucosio.*?([0-9,\.]+).*?mg/dl', 'Glucosio'),
            (r'Creatinina.*?([0-9,\.]+).*?mg/dl', 'Creatinina'),
            (r'Emoglobina.*?([0-9,\.]+).*?mg/dl', 'Emoglobina'),
            (r'Urea.*?([0-9,\.]+).*?mg/dl', 'Urea'),
            (r'Colesterolo.*?([0-9,\.]+)', 'Colesterolo'),
            (r'Trigliceridi.*?([0-9,\.]+)', 'Trigliceridi'),
            (r'pH.*?([0-9,\.]+)', 'pH'),
            # Alternative patterns
            (r'Proteine[^\n]*?([0-9,\.]+)', 'Proteine_alt'),
            (r'Glucosio[^\n]*?([0-9,\.]+)', 'Glucosio_alt'),
            (r'Emoglobina[^\n]*?([0-9,\.]+)', 'Emoglobina_alt')
        ]
        
        for pattern, param_name in lab_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                key_values[param_name] = matches[0]
    
    elif any(keyword in report_lower for keyword in ['radiolog', 'ecografia', 'tac', 'risonanza', 'rx', 'tc', 'rm']):
        # RADIOLOGY REPORTS - Extract key findings and measurements
        radiology_patterns = [
            (r'dimensioni.*?([0-9,\.]+\s*[x×]\s*[0-9,\.]+)', 'dimensioni'),
            (r'diametro.*?([0-9,\.]+\s*(?:mm|cm))', 'diametro'),
            (r'spessore.*?([0-9,\.]+\s*(?:mm|cm))', 'spessore'),
            (r'(lesione|massa|nodulo|formazione).*?([0-9,\.]+\s*(?:mm|cm))', 'lesione_size'),
            # Key findings
            (r'(normale|regolare|nella norma)', 'normale'),
            (r'(alterazioni|anomalie|patologico)', 'alterazioni'),
            (r'(versamento|liquido)', 'versamento'),
            (r'(calcificazioni)', 'calcificazioni'),
            (r'(dilatazione)', 'dilatazione'),
            # Specific organ findings
            (r'fegato.*?(normale|ingrandito|ridotto)', 'fegato'),
            (r'reni.*?(normale|dilatazione|calcoli)', 'reni'),
            (r'cuore.*?(normale|ingrandito)', 'cuore')
        ]
        
        for pattern, param_name in radiology_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            if matches:
                if isinstance(matches[0], tuple):
                    key_values[param_name] = matches[0][0] if matches[0][0] else matches[0][1]
                else:
                    key_values[param_name] = matches[0]
    
    elif any(keyword in report_lower for keyword in ['biopsia', 'istolog', 'citolog', 'patolog', 'anatomia']):
        # PATHOLOGY REPORTS - Extract diagnostic terms and classifications
        pathology_patterns = [
            (r'(maligno|benigno|neoplasia)', 'malignancy'),
            (r'(carcinoma|adenocarcinoma|sarcoma)', 'tumor_type'),
            (r'grado.*?([I-IV]|[1-4])', 'grade'),
            (r'stadio.*?([I-IV]|[1-4])', 'stage'),
            (r'(positivo|negativo).*?(recettori|ER|PR|HER2)', 'receptors'),
            (r'ki.?67.*?([0-9,\.]+%)', 'ki67'),
            (r'dimensioni.*?([0-9,\.]+\s*(?:mm|cm))', 'tumor_size'),
            # Specific findings
            (r'(infiammazione|flogosi)', 'inflammation'),
            (r'(fibrosi)', 'fibrosis'),
            (r'(necrosi)', 'necrosis'),
            (r'(displasia)', 'dysplasia'),
            (r'margini.*?(liberi|coinvolti)', 'margins')
        ]
        
        for pattern, param_name in pathology_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            if matches:
                if isinstance(matches[0], tuple):
                    key_values[param_name] = matches[0][0] if matches[0][0] else matches[0][1]
                else:
                    key_values[param_name] = matches[0]
    
    else:
        # GENERIC REPORTS - Extract common medical terms and dates
        generic_patterns = [
            (r'data.*?([0-9]{1,2}[\/\-\.][0-9]{1,2}[\/\-\.][0-9]{4})', 'data'),
            (r'diagnosi.*?([A-Za-z\s]{10,50})', 'diagnosi'),
            (r'terapia.*?([A-Za-z\s]{10,50})', 'terapia'),
            (r'([0-9,\.]+\s*(?:mg|ml|cm|mm))', 'measurements')
        ]
        
        for pattern, param_name in generic_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                key_values[param_name] = matches[0]
    
    return key_values

def reports_have_identical_values(existing_report: Report, new_text, report_type):
    """Check if two reports have identical key values based on report type"""
    existing_values = extract_key_values_from_text(existing_report.extracted_text, report_type)
    new_values = extract_key_values_from_text(new_text, report_type)
    
    # Different thresholds based on report type
    report_lower = report_type.lower()
    
    if any(keyword in report_lower for keyword in ['urine', 'sangue', 'laboratorio', 'chimico', 'ematochimici']):
        # Laboratory: Need at least 3 matching values, 80% similarity
        min_values = 3
        similarity_threshold = 0.8
    elif any(keyword in report_lower for keyword in ['radiolog', 'ecografia', 'tac', 'risonanza', 'rx', 'tc', 'rm']):
        # Radiology: Need at least 2 matching findings, 70% similarity
        min_values = 2
        similarity_threshold = 0.7
    elif any(keyword in report_lower for keyword in ['biopsia', 'istolog', 'citolog', 'patolog', 'anatomia']):
        # Pathology: Need at least 2 matching diagnostic terms, 75% similarity
        min_values = 2
        similarity_threshold = 0.75
    else:
        # Generic: Basic matching
        min_values = 2
        similarity_threshold = 0.6
    
    # Must have minimum matching values
    if len(existing_values) < min_values or len(new_values) < min_values:
        return False
    
    matches = 0
    total_keys = max(len(existing_values), len(new_values))
    
    for key, value in existing_values.items():
        if key in new_values:
            existing_val = str(value).strip().lower()
            new_val = str(new_values[key]).strip().lower()
            
            # Exact match or very similar (for measurements with slight variations)
            if existing_val == new_val or (
                key.endswith('_alt') and abs(len(existing_val) - len(new_val)) <= 2
            ):
                matches += 1
    
    # Calculate similarity ratio
    similarity_ratio = matches / total_keys if total_keys > 0 else 0
    
    return similarity_ratio >= similarity_threshold and matches >= min_values

def check_duplicate_report(db: Session, meta, extracted_text: str):
    """Check if a report with identical CF + Date + Type + Content already exists"""
    try:
        report_type = meta.get('report_type')
        codice_fiscale = meta.get('codice_fiscale')
        report_date = meta.get('report_date')
        
        # Extract key values from new text based on report type
        key_values = extract_key_values_from_text(extracted_text, report_type)
        
        if not key_values:
            print(f"🔍 No key values extracted for duplicate check")
            return None, False
        
        # Get reports with EXACT match on CF + Date + Type (potential duplicates)
        existing_reports = db.query(Report).filter(
            Report.report_type == report_type,
            Report.patient_cf == codice_fiscale,
            Report.report_date == report_date  # Same CF + Date + Type
        ).all()
        
        # Debug: Show what reports we're checking
        print(f"🔍 Duplicate check: Found {len(existing_reports)} reports with same CF/Date/Type")
        
        # Check for content similarity only among reports with same CF + Date + Type
        for report in existing_reports:
            print(f"   Checking report ID {report.id} from {report.report_date}")
            is_duplicate = reports_have_identical_values(report, extracted_text, report_type)
            print(f"   Result: {'DUPLICATE' if is_duplicate else 'DIFFERENT'}")
            if is_duplicate:
                print(f"   🚨 DUPLICATE FOUND: Same CF + Date + Type + Content as report saved on {report.created_at}")
                return report, True
        
        print(f"   ✅ No duplicates found - unique combination of CF/Date/Type/Content")
        return None, False
        
    except Exception as e:
        print(f"Error checking duplicates: {e}")
        return None, False


@router.post("/", summary="Analizza uno o più referti PDF")
async def analyze_documents(
    request: Request,
    files: List[UploadFile] = File(...),
    db=Depends(get_db)
):
    if not (1 <= len(files) <= 5):
        raise HTTPException(400, "Seleziona da 1 a 5 file PDF.")
    
    logger.info(f"Analyzing {len(files)} file(s)")
    
    # Step 1: Extract metadata from all files first
    file_data = []
    for f in files:
        logger.info(f"Extracting metadata from: {f.filename}")
        
        try:
            # Read the file
            file_bytes = await f.read()
            
            # Extract metadata and text from PDF
            try:
                meta = extract_metadata(file_bytes)
                full_text = meta["full_text"]
                logger.info(f"Extracted from {f.filename}: CF={meta.get('codice_fiscale', 'None')}, Date={meta.get('report_date', 'None')}")
                
                file_data.append({
                    'filename': f.filename,
                    'file_bytes': file_bytes,
                    'metadata': meta,
                    'full_text': full_text
                })
                
            except Exception as pdf_error:
                logger.error(f"Error extracting PDF metadata from {f.filename}: {str(pdf_error)}")
                logger.error(traceback.format_exc())
                # Add error result immediately
                file_data.append({
                    'filename': f.filename,
                    'error': True,
                    'error_message': f"Errore nell'elaborazione del PDF: {str(pdf_error)}"
                })
                
        except Exception as file_error:
            logger.error(f"Error reading file {f.filename}: {str(file_error)}")
            file_data.append({
                'filename': f.filename,
                'error': True,
                'error_message': f"Errore nella lettura del file: {str(file_error)}"
            })
    
    # Step 2: Sort files by report date (chronological order)
    valid_files = [fd for fd in file_data if not fd.get('error', False)]
    error_files = [fd for fd in file_data if fd.get('error', False)]
    
    # Sort valid files by report date
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
    
    logger.info(f"Processing {len(valid_files)} valid files in chronological order:")
    for i, fd in enumerate(valid_files):
        date_str = fd['metadata'].get('report_date', 'Unknown')
        logger.info(f"  {i+1}. {fd['filename']} - Date: {date_str}")
    
    # Step 3: Process files in chronological order
    risultati: list[dict] = []
    
    # Add error results first
    for error_file in error_files:
        risultati.append({
            "salvato": False,
            "messaggio": error_file['error_message'],
            "filename": error_file['filename']
        })
    
    # Process valid files in chronological order
    for file_info in valid_files:
        filename = file_info['filename']
        file_bytes = file_info['file_bytes']
        meta = file_info['metadata']
        full_text = file_info['full_text']
        
        logger.info(f"Processing file in chronological order: {filename}")
        
        try:
            # Run AI analysis - choose appropriate method based on report type and values
            try:
                lab_values = meta.get('laboratory_values', {})
                
                if lab_values and len(lab_values) > 0:
                    logger.info(f"Laboratory report detected with {len(lab_values)} values - using specialized analysis")
                    from core.ai_engine import analyze_laboratory_report
                    ai = analyze_laboratory_report(meta)
                else:
                    logger.info("Using text-based analysis")
                    ai = analyze_text_with_medgemma(full_text)
                    logger.info("Standard medical report - using general text analysis")
                    ai = analyze_text_with_medgemma(full_text)
                    
                logger.info(f"AI analysis complete: {ai.get('classification', 'Unknown')}")
                
                # Debug: Check if diagnosis contains comparison words that should be in comparison section
                diagnosis_text = ai.get('diagnosis', '')
                comparison_words = ['miglioramento', 'peggioramento', 'precedente', 'controllo', 'rispetto', 'confronto']
                has_comparison = any(word in diagnosis_text.lower() for word in comparison_words)
                if has_comparison:
                    logger.warning(f"⚠️ AI diagnosis contains comparison words: {diagnosis_text[:100]}...")
                else:
                    logger.info(f"✅ AI diagnosis is clean (no comparison text): {diagnosis_text[:100]}...")
            except Exception as ai_error:
                logger.error(f"Error in AI analysis: {str(ai_error)}")
                logger.error(traceback.format_exc())
                risultati.append({
                    "salvato": False,
                    "messaggio": f"Errore nell'analisi AI: {str(ai_error)}",
                    "filename": filename,
                    "codice_fiscale": meta.get("codice_fiscale"),
                    "nome_paziente": meta.get("patient_name"),
                })
                continue
                
            # Check if Codice Fiscale was found anywhere in the document
            codice_fiscale = meta.get("codice_fiscale")
            logger.info(f"🔍 CF extraction result for {filename}: '{codice_fiscale}'")
            
            if not codice_fiscale:
                logger.warning(f"⚠️ No Codice Fiscale found in report {filename} - report will NOT be saved")
                
                # Get the exact report title
                report_type = meta.get("report_type")
                logger.info(f"Using report title: {report_type}")
                
                # Try to compare with latest report of the same title (for unsaved reports)
                cmp = None
                try:
                    logger.info(f"Attempting to compare with previous reports with title '{report_type}'")
                    cmp = compare_with_latest_report_by_title_only(
                        db=db,
                        report_type=report_type,
                        new_text=full_text
                    )
                    logger.info(f"Comparison status: {cmp.get('status', 'unknown')}")
                except Exception as e:
                    logger.error(f"Error in comparison: {str(e)}")
                    cmp = {
                        "status": "errore",
                        "explanation": f"Errore nella comparazione: {str(e)}"
                    }
                
                # Create response object for unsaved report
                result_obj = {
                    "salvato"            : False,
                    "messaggio"          : "Codice Fiscale assente – referto analizzato ma NON salvato.",
                    "diagnosi_ai"        : ai["diagnosis"],
                    "classificazione_ai" : ai["classification"],
                    "codice_fiscale"     : None,
                    "tipo_referto"       : report_type,
                    "nome_file"          : filename,
                    "nome_paziente"      : meta.get("patient_name"),
                    "data_referto"       : meta.get("report_date")
                }
                
                # Add comparison results if available (for comparison section only)
                if cmp and cmp.get("status") not in ["nessun confronto disponibile", "errore"]:
                    result_obj["situazione"] = cmp.get("status")
                    result_obj["spiegazione"] = cmp.get("explanation")
                
                risultati.append(result_obj)
                continue

            # Process report with Codice Fiscale - always save if CF is found
            logger.info(f"✅ Codice Fiscale found: {codice_fiscale} - proceeding to save report")
            try:
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
                path = crud.save_pdf(filename, file_bytes)
                
                # Get report title and category from metadata
                report_type = meta["report_type"]
                report_category = meta.get("report_category", "laboratory")
                logger.info(f"Using report title for database storage: {report_type} (category: {report_category})")
                
                # *** CHECK FOR DUPLICATE REPORTS BEFORE SAVING ***
                logger.info(f"Checking for duplicate reports")
                # Create a proper meta dict for duplicate checking
                check_meta = {
                    'report_type': report_type,
                    'codice_fiscale': codice_fiscale,
                    'report_date': report_dt  # Add report date for duplicate checking
                }
                duplicate_report, is_duplicate = check_duplicate_report(db, check_meta, full_text)
                
                if is_duplicate and duplicate_report:
                    logger.info(f"Duplicate report detected - ID: {duplicate_report.id}")
                    result_obj = {
                        "salvato"            : False,
                        "messaggio"          : f"Errore nel salvataggio del referto: Documento già presente nel database (salvato il {duplicate_report.created_at.strftime('%d/%m/%Y %H:%M')}), ma risultati analisi forniti",
                        "status"             : "duplicate",
                        "diagnosi_ai"        : duplicate_report.ai_diagnosis,
                        "classificazione_ai" : duplicate_report.ai_classification,
                        "codice_fiscale"     : codice_fiscale,
                        "tipo_referto"       : report_type,
                        "nome_file"          : filename,
                        "nome_paziente"      : meta.get("patient_name"),
                        "data_referto"       : meta.get("report_date"),
                        "original_save_date" : duplicate_report.created_at.strftime('%d/%m/%Y %H:%M')
                    }
                    
                    # Add comparison if exists
                    if duplicate_report.comparison_to_previous:
                        result_obj["situazione"] = duplicate_report.comparison_to_previous
                        result_obj["spiegazione"] = duplicate_report.comparison_explanation
                    
                    risultati.append(result_obj)
                    continue  # Skip to next file without saving
                
                # *** IMPORTANT: Check for previous report BEFORE saving the new one ***
                logger.info(f"Looking for previous reports before saving new one")
                previous_report_text = crud.get_most_recent_report_text_by_title(db, codice_fiscale, report_type)
                
                try:
                    rec = crud.create_report(
                        db               = db,
                        patient_cf       = codice_fiscale,
                        patient_name     = meta["patient_name"],
                        report_type      = report_type,
                        report_date      = report_dt,
                        file_path        = path,
                        extracted_text   = full_text,
                        ai_diagnosis     = ai["diagnosis"],
                        ai_classification= ai["classification"],
                    )
                    logger.info(f"✅ Report saved successfully with ID: {rec.id}")
                    db.commit()  # Ensure commit
                except Exception as e:
                    logger.error(f"Error saving report: {str(e)}")
                    logger.error(traceback.format_exc())
                    raise

                # Compare with previous report by title (using pre-fetched text)
                logger.info(f"Comparing with previous reports")
                try:
                    if previous_report_text:
                        logger.info(f"Found previous report, performing comparison")
                        from core.comparator import _perform_comparison_chronological
                        cmp = _perform_comparison_chronological(db, codice_fiscale, report_type, previous_report_text, full_text)
                    else:
                        logger.info(f"No previous report found for this patient and report type")
                        cmp = {
                            "status": "nessun confronto disponibile",
                            "explanation": "Non esiste un referto precedente con lo stesso titolo per il paziente."
                        }
                    
                    crud.update_report_comparison(db, rec.id, cmp)
                    logger.info(f"Comparison status: {cmp['status']}")
                except Exception as e:
                    logger.error(f"Error in comparison: {str(e)}")
                    logger.error(traceback.format_exc())
                    cmp = {
                        "status": "errore",
                        "explanation": f"Errore nella comparazione: {str(e)}"
                    }

                risultati.append({
                    "salvato"            : True,
                    "messaggio"          : "Referto salvato con successo.",
                    "report_id"          : str(rec.id),
                    "diagnosi_ai"        : ai["diagnosis"],
                    "classificazione_ai" : ai["classification"],
                    "codice_fiscale"     : codice_fiscale,
                    "nome_paziente"      : meta["patient_name"],
                    "tipo_referto"       : meta["report_type"],
                    "data_referto"       : meta["report_date"],
                    "situazione"         : cmp["status"],
                    "spiegazione"        : cmp["explanation"],
                })
                logger.info(f"✅ Added result to response: salvato=True, CF={codice_fiscale}")
            
            
            except Exception as save_error:
                logger.error(f"❌ Error saving report with CF {codice_fiscale}: {str(save_error)}")
                logger.error(traceback.format_exc())
                risultati.append({
                    "salvato": False,
                    "messaggio": f"Errore nel salvataggio del referto: {str(save_error)}",
                    "diagnosi_ai": ai["diagnosis"],
                    "classificazione_ai": ai["classification"],
                    "codice_fiscale": codice_fiscale,
                    "nome_paziente": meta.get("patient_name"),
                    "tipo_referto": meta.get("report_type"),
                    "data_referto": meta.get("report_date"),
                })
                logger.info(f"⚠️ Added error result to response: salvato=False, CF={codice_fiscale}")
        
        except Exception as general_error:
            logger.error(f"General error processing file {filename}: {str(general_error)}")
            logger.error(traceback.format_exc())
            risultati.append({
                "salvato": False,
                "messaggio": f"Errore generico: {str(general_error)}",
                "filename": filename
            })
            
    # Return all results
    logger.info(f"Analysis complete, returning {len(risultati)} results")
    return {"risultati": risultati}
