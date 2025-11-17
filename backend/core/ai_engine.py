# backend/core/ai_engine.py

import ollama
import os
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get configuration from environment variables
MODEL_NAME = os.getenv("OLLAMA_MODEL", "alibayram/medgemma")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Configure Ollama client
ollama.api_base_url = OLLAMA_BASE_URL

def get_test_specific_prompt(report_type: str, lab_data: str, abnormal_values: list) -> str:
    """Generate test-specific prompts that restrict AI analysis to appropriate clinical scope"""
    
    report_type_upper = report_type.upper()
    abnormal_str = ', '.join(abnormal_values) if abnormal_values else 'Nessuno'
    
    # URINE ANALYSIS - Only urinary tract conditions
    if any(term in report_type_upper for term in ["URINE", "CHIMICO FISICO", "URINARIO"]):
        return f"""
Sei un medico esperto in nefrologia e urologia. Analizza SOLO i risultati dell'esame delle urine.

IMPORTANTE - Puoi diagnosticare SOLO condizioni rilevabili dall'analisi delle urine:
✅ AMMESSO:
- Infezioni del tratto urinario (cistite, uretrite)
- Proteinuria (nefropatia, glomerulonefrite)
- Glicosuria (diabete mellito)
- Ematuria (sangue nelle urine)
- Alterazioni del pH urinario
- Presenza di cristalli, cilindri, batteri
- Insufficienza renale (basata su proteine/sangue)

❌ VIETATO diagnosticare:
- Problemi epatici (fegato)
- Anemia o alterazioni ematologiche
- Problemi cardiaci
- Malattie sistemiche non urinarie

RISULTATI ESAME URINE:
{lab_data}

VALORI ALTERATI: {abnormal_str}

Fornisci una diagnosi limitata ESCLUSIVAMENTE alle condizioni del tratto urinario e renale.
IMPORTANTE: Includi i valori specifici alterati nella diagnosi (esempio: "Proteinuria (45 mg/dl)")
Rispondi in JSON: {{"diagnosis": "diagnosi specifica per apparato urinario con valori", "classification": "lieve|moderato|grave"}}
"""

    # BLOOD CHEMISTRY - Only metabolic and liver conditions
    elif any(term in report_type_upper for term in ["CHIMICA", "BIOCHIMICA", "METABOLICO", "GOT", "AST", "ALT"]):
        return f"""
Sei un medico esperto in medicina interna e biochimica clinica. Analizza SOLO i risultati della chimica clinica.

IMPORTANTE - Puoi diagnosticare SOLO condizioni rilevabili dalla biochimica del sangue:
✅ AMMESSO:
- Alterazioni epatiche (GOT, AST, ALT, bilirubina elevate)
- Diabete mellito (glucosio elevato)
- Dislipidemia (colesterolo, trigliceridi)
- Insufficienza renale (creatinina, urea elevate)
- Alterazioni elettrolitiche (sodio, potassio)
- Problemi tiroidei (TSH, T3, T4)
- Infiammazione sistemica (PCR elevata)

❌ VIETATO diagnosticare:
- Anemia (serve emocromo)
- Infezioni urinarie (serve esame urine)
- Problemi di coagulazione (serve coagulazione)

RISULTATI CHIMICA CLINICA:
{lab_data}

VALORI ALTERATI: {abnormal_str}

Fornisci una diagnosi limitata ESCLUSIVAMENTE alle condizioni metaboliche e biochimiche.
IMPORTANTE: Includi i valori specifici alterati nella diagnosi (esempio: "Ipercolesterolemia (280 mg/dl)")
Rispondi in JSON: {{"diagnosis": "diagnosi specifica per chimica clinica con valori", "classification": "lieve|moderato|grave"}}
"""

    # HEMATOLOGY/CBC - Only blood cell conditions
    elif any(term in report_type_upper for term in ["EMOCROMO", "EMOCROMOCITOMETRICO", "SANGUE", "WBC", "RBC", "HGB"]):
        return f"""
Sei un medico esperto in ematologia. Analizza SOLO i risultati dell'emocromo.

IMPORTANTE - Puoi diagnosticare SOLO condizioni rilevabili dall'emocromo:
✅ AMMESSO:
- Anemia (vari tipi: microcitica, macrocitica, normocitica)
- Leucocitosi/leucopenia (alterazioni globuli bianchi)
- Trombocitosi/trombocitopenia (alterazioni piastrine)
- Infezioni batteriche/virali (basato su formula leucocitaria)
- Ematocrito alterato
- Alterazioni dell'emoglobina

❌ VIETATO diagnosticare:
- Problemi epatici (serve chimica clinica)
- Problemi renali (serve chimica clinica + urine)
- Diabete (serve glicemia)
- Infezioni urinarie (serve esame urine)

RISULTATI EMOCROMO:
{lab_data}

VALORI ALTERATI: {abnormal_str}

Fornisci una diagnosi limitata ESCLUSIVAMENTE alle condizioni ematologiche.
IMPORTANTE: Includi i valori specifici alterati nella diagnosi (esempio: "Anemia microcitica (Hb 9.5 g/dl)")
Rispondi in JSON: {{"diagnosis": "diagnosi specifica per emocromo con valori", "classification": "lieve|moderato|grave"}}
"""

    # COAGULATION - Only clotting disorders
    elif any(term in report_type_upper for term in ["COAGULAZIONE", "PT", "PTT", "INR", "PROTROMBINICO"]):
        return f"""
Sei un medico esperto in ematologia e coagulazione. Analizza SOLO i risultati della coagulazione.

IMPORTANTE - Puoi diagnosticare SOLO condizioni rilevabili dai test di coagulazione:
✅ AMMESSO:
- Alterazioni della coagulazione
- Rischio emorragico
- Monitoraggio terapia anticoagulante
- Deficit fattori della coagulazione
- Disfunzioni epatiche (solo se correlate a coagulazione)

❌ VIETATO diagnosticare:
- Anemia (serve emocromo)
- Infezioni (serve emocromo + chimica)
- Problemi renali o urinari

RISULTATI COAGULAZIONE:
{lab_data}

VALORI ALTERATI: {abnormal_str}

Fornisci una diagnosi limitata ESCLUSIVAMENTE ai disturbi della coagulazione.
IMPORTANTE: Includi i valori specifici alterati nella diagnosi (esempio: "Ipocoagulabilità (PT 25 sec)")
Rispondi in JSON: {{"diagnosis": "diagnosi specifica per coagulazione con valori", "classification": "lieve|moderato|grave"}}
"""

    # PATHOLOGY REPORTS - Anatomical pathology, histology, cytology
    elif any(term in report_type_upper for term in ["ISTOLOGICO", "CITOLOGICO", "PATOLOGIC", "BIOPSIA", "AGOBIOPSIA", "ANATOMIA"]):
        return f"""
Sei un medico anatomo-patologo esperto. Analizza il seguente referto di anatomia patologica.

IMPORTANTE - Fornisci diagnosi basata ESCLUSIVAMENTE sui reperti anatomopatologici:
✅ AMMESSO:
- Diagnosi istologiche e citologiche
- Classificazione di neoplasie (benigne/maligne)
- Grading e staging tumorali
- Processi infiammatori tissutali
- Displasie e metaplasie
- Alterazioni architetturali tissutali
- Presenza/assenza di malignità

❌ VIETATO diagnosticare:
- Condizioni che richiedono dati clinici aggiuntivi
- Prognosi senza dati clinici completi
- Raccomandazioni terapeutiche specifiche

REFERTO ANATOMOPATOLOGICO:
{lab_data}

Fornisci una diagnosi anatomopatologica precisa e classificazione della gravità.
IMPORTANTE: Includi dimensioni o percentuali specifiche quando rilevanti (esempio: "Adenocarcinoma moderatamente differenziato (30% del campione)")
Rispondi in JSON: {{"diagnosis": "diagnosi anatomopatologica con dettagli", "classification": "lieve|moderato|grave"}}
"""

    # RADIOLOGY REPORTS - Imaging studies
    elif any(term in report_type_upper for term in ["RADIOLOG", "ECOGRAFIA", "ECOCOLORDOPPLER", "TAC", "RISONANZA", "RX", "DOPPLER"]):
        return f"""
Sei un medico radiologo esperto. Analizza il seguente referto radiologico.

IMPORTANTE - Fornisci diagnosi basata ESCLUSIVAMENTE sui reperti radiologici:
✅ AMMESSO:
- Alterazioni morfologiche visibili all'imaging
- Stenosi, dilatazioni, masse
- Versamenti, raccolte, ispessimenti
- Alterazioni del parenchima
- Reperti vascolari (flussi, stenosi)
- Calcificazioni, addensamenti
- Dimensioni e caratteristiche strutturali

❌ VIETATO diagnosticare:
- Condizioni che richiedono esami di laboratorio
- Diagnosi che necessitano correlazione istologica
- Prognosi senza follow-up

REFERTO RADIOLOGICO:
{lab_data}

Fornisci una diagnosi radiologica precisa e classificazione della gravità.
IMPORTANTE: Includi misure specifiche quando disponibili (esempio: "Epatosplenomegalia (fegato 18cm, milza 14cm)")
Rispondi in JSON: {{"diagnosis": "diagnosi radiologica con misure", "classification": "lieve|moderato|grave"}}
"""

    # GENERIC LABORATORY - Conservative approach
    else:
        return f"""
Sei un medico esperto. Analizza i seguenti risultati di laboratorio.

IMPORTANTE - Limita la diagnosi SOLO a ciò che può essere determinato da questo specifico tipo di esame: {report_type}

TIPO ESAME: {report_type}
RISULTATI:
{lab_data}

VALORI ALTERATI: {abnormal_str}

Fornisci una diagnosi conservativa e specifica per questo tipo di esame.
IMPORTANTE: Includi i valori specifici alterati nella diagnosi quando appropriato.
Rispondi in JSON: {{"diagnosis": "diagnosi appropriata per {report_type} con valori", "classification": "lieve|moderato|grave"}}
"""

def analyze_text_with_medgemma(report_text: str) -> dict:
    """Invia testo a MedGemma tramite Ollama (Python lib) e restituisce diagnosi e classificazione."""

    prompt = f"""
Sei un medico esperto. Analizza il seguente referto medico italiano e estrai SOLO la diagnosi medica definitiva.

Referto medico:
\"\"\"
{report_text}
\"\"\"

ISTRUZIONI SPECIFICHE:
1. DIAGNOSIS: Estrai SOLO la diagnosi medica principale/conclusiva del referto
   - NON includere sintomi (es. "dolore toracico", "dispnea", "febbre")
   - NON includere segni clinici (es. "ipertensione", "tachicardia") 
   - NON includere il titolo dell'esame (es. "Radiografia del torace", "Ecografia addominale")
   - NON includere reperti descrittivi (es. "opacità polmonare", "versamento pleurico")
   - INCLUDI solo la patologia/condizione diagnosticata (es. "Polmonite batterica", "Insufficienza cardiaca congestizia", "Neoplasia polmonare")
   - Se non c'è una diagnosi definitiva, scrivi "Diagnosi non conclusiva"
   - Massimo una frase, concisa e precisa

2. CLASSIFICATION: Valuta la gravità della diagnosi trovata:
   - "lieve": condizioni non gravi, gestibili ambulatorialmente
   - "moderato": condizioni che richiedono attenzione medica ma non urgente
   - "grave": condizioni che richiedono intervento immediato o ospedalizzazione

ESEMPI:
- ✅ CORRETTO: "Polmonite batterica del lobo inferiore destro"
- ❌ SBAGLIATO: "Dolore toracico e dispnea con opacità polmonare" (sintomi + reperti)
- ✅ CORRETTO: "Insufficienza cardiaca congestizia"  
- ❌ SBAGLIATO: "Cardiomegalia con versamento pleurico" (solo reperti)
- ✅ CORRETTO: "Frattura del radio distale"
- ❌ SBAGLIATO: "Radiografia del polso che mostra frattura" (titolo + reperto)

Rispondi ESCLUSIVAMENTE in questo formato JSON:
{{
    "diagnosis": "diagnosi medica definitiva in una frase",
    "classification": "lieve | moderato | grave"
}}
"""

    try:
        logger.info(f"Sending request to Ollama at {OLLAMA_BASE_URL}")
        response = ollama.generate(model=MODEL_NAME, prompt=prompt)
        result = response["response"].strip()
        
        logger.info(f"Received response from model: {result[:100]}...")
        
        # Clean the result - remove markdown code fences if present
        cleaned_result = result
        if "```json" in cleaned_result:
            cleaned_result = cleaned_result.replace("```json", "").replace("```", "").strip()
        elif "```" in cleaned_result:
            # Handle other code fence formats
            parts = cleaned_result.split("```")
            if len(parts) >= 2:
                cleaned_result = parts[1].strip()
                if cleaned_result.startswith("json"):
                    cleaned_result = cleaned_result[4:].strip()
        
        # Remove any leading/trailing whitespace that might affect JSON parsing
        cleaned_result = cleaned_result.strip()
                
        # Try to parse the response as JSON
        try:
            # First try with json.loads for safety
            logger.info(f"Attempting to parse JSON: {cleaned_result[:100]}...")
            parsed_result = json.loads(cleaned_result)
            
            # Validate the diagnosis quality
            diagnosis = parsed_result.get("diagnosis", "").strip()
            classification = parsed_result.get("classification", "").strip()
            
            # Check if diagnosis looks like symptoms/signs rather than actual diagnosis
            symptom_keywords = ["dolore", "febbre", "dispnea", "nausea", "vomito", "cefalea", "astenia", "malessere"]
            sign_keywords = ["ipertensione", "tachicardia", "bradicardia", "tachipnea", "cianosi"]
            exam_keywords = ["radiografia", "ecografia", "tac", "risonanza", "elettrocardiogramma", "ecocardiografia"]
            
            diagnosis_lower = diagnosis.lower()
            
            # Warn if diagnosis might be symptoms/signs instead of actual diagnosis
            if any(keyword in diagnosis_lower for keyword in symptom_keywords):
                logger.warning(f"⚠️ Diagnosis might contain symptoms: {diagnosis}")
            elif any(keyword in diagnosis_lower for keyword in sign_keywords):
                logger.warning(f"⚠️ Diagnosis might contain clinical signs: {diagnosis}")
            elif any(keyword in diagnosis_lower for keyword in exam_keywords):
                logger.warning(f"⚠️ Diagnosis might contain exam type: {diagnosis}")
            else:
                logger.info(f"✅ Diagnosis looks appropriate: {diagnosis}")
            
            # Validate classification
            valid_classifications = ["lieve", "moderato", "grave"]
            if classification not in valid_classifications:
                logger.warning(f"⚠️ Invalid classification '{classification}', defaulting to 'moderato'")
                parsed_result["classification"] = "moderato"
            
            return parsed_result
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            # Fall back to eval if JSON parsing fails
            # This is less safe but might handle some formatting issues
            try:
                # Try to extract just the JSON part if there's surrounding text
                import re
                json_match = re.search(r'\{.*\}', cleaned_result, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    parsed_result = json.loads(json_str)
                    return parsed_result
                else:
                    raise ValueError("No JSON object found in response")
            except Exception as parse_error:
                logger.error(f"Failed to parse model response: {str(parse_error)}")
                return {
                    "diagnosis": "Errore nel formato della risposta",
                    "classification": "non disponibile",
                    "errore": f"Errore di parsing: {str(parse_error)}"
                }
    except Exception as e:
        logger.error(f"Error communicating with Ollama: {str(e)}")
        return {
            "diagnosis": "Errore nella comunicazione con il modello AI",
            "classification": "non disponibile",
            "errore": str(e)
        }

def analyze_laboratory_report(metadata: dict) -> dict:
    """Analizza specificamente referti di laboratorio con restrizioni per tipo di test."""
    
    patient_name = metadata.get('patient_name', 'Paziente non identificato')
    birth_date = metadata.get('birth_date', 'Non disponibile')
    report_date = metadata.get('report_date', 'Non disponibile')
    lab_values = metadata.get('laboratory_values', {})
    report_type = metadata.get('report_type', 'Laboratorio generico')
    report_category = metadata.get('report_category', 'laboratory')
    
    # Handle different report types appropriately
    if report_category == 'radiology':
        logger.info(f"🏥 Analyzing radiology report: {report_type}")
        return analyze_radiology_report(metadata)
    elif report_category == 'pathology':
        logger.info(f"🔬 Analyzing pathology report: {report_type}")
        return analyze_pathology_report(metadata)
    
    # Continue with laboratory analysis for laboratory reports
    if not lab_values:
        logger.warning("No laboratory values found for analysis")
        return {
            "diagnosis": "Diagnosi non conclusiva - valori di laboratorio non trovati",
            "classification": "non disponibile"
        }
    
    try:
        logger.info(f"🔬 Analyzing laboratory report: {report_type} with {len(lab_values)} values")
        
        # Structure laboratory data for AI analysis
        abnormal_values = []
        lab_text = f"Paziente: {patient_name}\nData: {report_date}\nTipo esame: {report_type}\n\nRisultati:\n"
        
        # Group by category
        categories = {}
        for test_name, test_data in lab_values.items():
            category = test_data.get('category', 'Altri')
            if category not in categories:
                categories[category] = []
            categories[category].append((test_name, test_data))
            
            # Track abnormal values with Emoglobina filtering
            if test_data.get('abnormal', False):
                # Special handling for Emoglobina in urine tests - apply medical threshold
                if (test_name.lower() == 'emoglobina' and 
                    ("URINE" in report_type.upper() or "CHIMICO FISICO" in report_type.upper())):
                    try:
                        # Extract numeric value and handle Italian decimal format
                        value_str = str(test_data['value']).replace(',', '.')
                        value = float(value_str)
                        if value <= 0.5:  # Skip if within normal range (≤ 0.5 mg/dl = normal)
                            logger.info(f"🩺 Emoglobina {value} mg/dl is within normal range (≤0.5), not flagging as abnormal")
                            continue
                    except (ValueError, TypeError):
                        # If we can't parse the value, treat as abnormal to be safe
                        logger.warning(f"Could not parse Emoglobina value: {test_data['value']}, treating as abnormal")
                        pass
                
                abnormal_values.append(f"{test_name}: {test_data['value']} {test_data.get('unit', '')}")
        
        # Build structured text
        for category, tests in categories.items():
            lab_text += f"\n{category.upper()}:\n"
            for test_name, test_data in tests:
                value = test_data['value']
                unit = test_data.get('unit', '')
                reference = test_data.get('reference', '')
                abnormal = test_data.get('abnormal', False)
                
                abnormal_flag = " *ALTERATO*" if abnormal else ""
                lab_text += f"- {test_name}: {value} {unit} (rif: {reference}){abnormal_flag}\n"
        
        # Generate test-specific prompt that restricts analysis scope
        try:
            prompt = get_test_specific_prompt(report_type, lab_text, abnormal_values)
            logger.info(f"Generated prompt for {report_type}, abnormal values: {len(abnormal_values)}")
            
            # Send to AI with test-specific restrictions
            response = ollama.chat(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = response['message']['content'].strip()
            logger.info(f"🤖 AI response received, length: {len(response_text)} chars")
            
            # Try to parse JSON response
            try:
                # Clean the response
                cleaned_result = response_text
                if "```json" in cleaned_result:
                    cleaned_result = cleaned_result.replace("```json", "").replace("```", "").strip()
                elif "```" in cleaned_result:
                    parts = cleaned_result.split("```")
                    if len(parts) >= 2:
                        cleaned_result = parts[1].strip()
                        if cleaned_result.startswith("json"):
                            cleaned_result = cleaned_result[4:].strip()
                
                parsed_result = json.loads(cleaned_result.strip())
                diagnosis = parsed_result.get('diagnosis', 'Diagnosi non disponibile')
                classification = parsed_result.get('classification', 'moderato')
                
                # Validate classification
                valid_classifications = ["lieve", "moderato", "grave"]
                if classification not in valid_classifications:
                    logger.warning(f"Invalid classification '{classification}', defaulting to 'moderato'")
                    classification = "moderato"
                
                # Validate diagnosis appropriateness
                diagnosis, was_corrected = validate_diagnosis_scope(diagnosis, report_type)
                if was_corrected:
                    logger.info(f"🔧 Corrected inappropriate diagnosis for {report_type}")
                
                logger.info(f"✅ Laboratory analysis complete: {diagnosis}")
                return {
                    "diagnosis": diagnosis,
                    "classification": classification,
                    "laboratory_values": lab_values,
                    "abnormal_count": len(abnormal_values),
                    "test_type": report_type
                }
                
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON response: {str(e)}")
                logger.warning(f"Raw response: {response_text[:200]}...")
                
                # Fallback: Create diagnosis based on abnormal values
                fallback_diagnosis = create_fallback_diagnosis(report_type, abnormal_values)
                classification = "moderato" if abnormal_values else "lieve"
                
                logger.info(f"� Using fallback diagnosis: {fallback_diagnosis}")
                return {
                    "diagnosis": fallback_diagnosis,
                    "classification": classification,
                    "laboratory_values": lab_values,
                    "abnormal_count": len(abnormal_values),
                    "note": "Analisi fallback (JSON parsing failed)"
                }
                
        except Exception as ai_error:
            logger.error(f"AI communication error: {str(ai_error)}")
            
            # Fallback analysis based on abnormal values
            fallback_diagnosis = create_fallback_diagnosis(report_type, abnormal_values)
            classification = "moderato" if abnormal_values else "lieve"
            
            logger.info(f"🔄 Using fallback diagnosis due to AI error: {fallback_diagnosis}")
            return {
                "diagnosis": fallback_diagnosis,
                "classification": classification,
                "laboratory_values": lab_values,
                "abnormal_count": len(abnormal_values),
                "note": "Analisi automatica (AI non disponibile)"
            }
                
    except Exception as e:
        logger.error(f"General error in laboratory analysis: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        
        # Final fallback based on simple analysis
        try:
            abnormal_count = sum(1 for data in lab_values.values() if data.get('abnormal', False))
            if abnormal_count > 0:
                return {
                    "diagnosis": f"Alterazioni rilevate in {abnormal_count} parametri di laboratorio - controllo medico consigliato",
                    "classification": "moderato",
                    "laboratory_values": lab_values,
                    "abnormal_count": abnormal_count
                }
            else:
                return {
                    "diagnosis": "Parametri di laboratorio nei limiti della norma",
                    "classification": "lieve",
                    "laboratory_values": lab_values,
                    "abnormal_count": 0
                }
        except:
            return {
                "diagnosis": "Errore nell'analisi dei parametri di laboratorio",
                "classification": "non disponibile",
                "errore": str(e)
            }

def create_value_specific_diagnosis(report_type: str, abnormal_values: list, lab_values: dict = None) -> str:
    """Create detailed diagnosis with specific lab values included"""
    
    if not abnormal_values:
        return "Parametri di laboratorio nei limiti della norma"
    
    report_upper = report_type.upper()
    diagnoses = []
    
    if "URINE" in report_upper or "CHIMICO FISICO" in report_upper:
        # Check for Proteinuria with specific value
        for val in abnormal_values:
            if "proteine" in val.lower():
                # Extract value from string like "Proteine: 15 mg/dl"
                try:
                    parts = val.split(":")
                    if len(parts) > 1:
                        value_part = parts[1].strip().split()[0]
                        unit_part = parts[1].strip().split()[1] if len(parts[1].strip().split()) > 1 else "mg/dl"
                        diagnoses.append(f"Proteinuria ({value_part} {unit_part})")
                    else:
                        diagnoses.append("Proteinuria")
                except:
                    diagnoses.append("Proteinuria")
                break
        
        # Check for UTI with specific values
        for val in abnormal_values:
            if "leucocit" in val.lower() or "esterasi" in val.lower():
                try:
                    parts = val.split(":")
                    if len(parts) > 1:
                        value_part = parts[1].strip().split()[0]
                        unit_part = parts[1].strip().split()[1] if len(parts[1].strip().split()) > 1 else ""
                        test_name = "Esterasi" if "esterasi" in val.lower() else "Leucociti"
                        diagnoses.append(f"Possibile infezione urinaria ({test_name}: {value_part} {unit_part})")
                    else:
                        diagnoses.append("Possibile infezione del tratto urinario")
                except:
                    diagnoses.append("Possibile infezione del tratto urinario")
                break
                
        # Check for Hematuria with value filtering
        for val in abnormal_values:
            if "emoglobina" in val.lower():
                try:
                    # Extract numeric value and handle Italian decimal format
                    num_str = val.split(":")[1].split()[0].strip().replace(",", ".")
                    value = float(num_str)
                    if value <= 0.5:  # Skip if within normal range
                        continue
                    diagnoses.append(f"Ematuria (Emoglobina: {val.split(':')[1].strip()})")
                except (ValueError, IndexError):
                    diagnoses.append("Ematuria")
                break
        
        # Check for blood with specific values
        if not any("emoglobina" in d.lower() for d in diagnoses):
            for val in abnormal_values:
                if "sangue" in val.lower():
                    try:
                        parts = val.split(":")
                        if len(parts) > 1:
                            value_part = parts[1].strip()
                            diagnoses.append(f"Ematuria (Sangue: {value_part})")
                        else:
                            diagnoses.append("Ematuria")
                    except:
                        diagnoses.append("Ematuria")
                    break
                    
    elif "EMOCROMO" in report_upper or "SANGUE" in report_upper:
        # Enhanced hematology diagnoses with values
        for val in abnormal_values:
            if any(term in val.lower() for term in ["emoglobina", "hgb", "hb"]):
                try:
                    parts = val.split(":")
                    if len(parts) > 1:
                        value_part = parts[1].strip()
                        diagnoses.append(f"Anemia (Emoglobina: {value_part})")
                    else:
                        diagnoses.append("Anemia")
                except:
                    diagnoses.append("Anemia")
            elif any(term in val.lower() for term in ["leucociti", "wbc", "globuli bianchi"]):
                try:
                    parts = val.split(":")
                    if len(parts) > 1:
                        value_part = parts[1].strip()
                        diagnoses.append(f"Alterazione leucocitaria (WBC: {value_part})")
                    else:
                        diagnoses.append("Alterazione dei globuli bianchi")
                except:
                    diagnoses.append("Alterazione dei globuli bianchi")
            elif any(term in val.lower() for term in ["piastrine", "plt"]):
                try:
                    parts = val.split(":")
                    if len(parts) > 1:
                        value_part = parts[1].strip()
                        diagnoses.append(f"Alterazione piastrinica (PLT: {value_part})")
                    else:
                        diagnoses.append("Alterazione delle piastrine")
                except:
                    diagnoses.append("Alterazione delle piastrine")
    
    elif "CHIMICA" in report_upper or "BIOCHIMICA" in report_upper:
        # Enhanced chemistry diagnoses with values
        for val in abnormal_values:
            if any(term in val.lower() for term in ["glucosio", "glicemia"]):
                try:
                    parts = val.split(":")
                    if len(parts) > 1:
                        value_part = parts[1].strip()
                        diagnoses.append(f"Iperglicemia (Glucosio: {value_part})")
                    else:
                        diagnoses.append("Alterazione glicemica")
                except:
                    diagnoses.append("Alterazione glicemica")
            elif any(term in val.lower() for term in ["creatinina"]):
                try:
                    parts = val.split(":")
                    if len(parts) > 1:
                        value_part = parts[1].strip()
                        diagnoses.append(f"Disfunzione renale (Creatinina: {value_part})")
                    else:
                        diagnoses.append("Possibile disfunzione renale")
                except:
                    diagnoses.append("Possibile disfunzione renale")
            elif any(term in val.lower() for term in ["alt", "ast", "got", "gpt"]):
                try:
                    parts = val.split(":")
                    if len(parts) > 1:
                        value_part = parts[1].strip()
                        test_name = "ALT" if "alt" in val.lower() or "gpt" in val.lower() else "AST"
                        diagnoses.append(f"Alterazione epatica ({test_name}: {value_part})")
                    else:
                        diagnoses.append("Possibile alterazione epatica")
                except:
                    diagnoses.append("Possibile alterazione epatica")
    
    # If no specific diagnoses found, create generic one with values
    if not diagnoses:
        generic_findings = []
        for val in abnormal_values:
            try:
                test_name = val.split(":")[0].strip()
                value_part = val.split(":")[1].strip() if ":" in val else val
                generic_findings.append(f"{test_name} ({value_part})")
            except:
                generic_findings.append(val)
        
        if generic_findings:
            return f"Alterazioni di laboratorio: {', '.join(generic_findings[:3])}"
        else:
            return "Alterazioni nei parametri di laboratorio - controllo medico consigliato"
    
    # Combine diagnoses
    return " | ".join(diagnoses)

def create_fallback_diagnosis(report_type: str, abnormal_values: list) -> str:
    """Create a simple diagnosis based on test type and abnormal values when AI fails"""
    
    # Use the new value-specific diagnosis function
    return create_value_specific_diagnosis(report_type, abnormal_values)

def validate_diagnosis_scope(diagnosis: str, report_type: str) -> tuple[str, bool]:
    """Validate that diagnosis is appropriate for the test type and flag inappropriate ones"""
    
    diagnosis_lower = diagnosis.lower()
    report_type_upper = report_type.upper()
    
    # Define inappropriate diagnoses for each test type
    inappropriate_terms = {
        "URINE": ["epatiche", "epatica", "fegato", "anemia", "ematologiche", "cardiache"],
        "CHIMICA": ["anemia", "ematologiche", "urinarie", "cistite"],
        "EMOCROMO": ["epatiche", "renali", "urinarie", "diabete"],
        "COAGULAZIONE": ["anemia", "urinarie", "diabete", "renali"]
    }
    
    # Check for inappropriate terms
    for test_type, forbidden_terms in inappropriate_terms.items():
        if test_type in report_type_upper:
            for term in forbidden_terms:
                if term in diagnosis_lower:
                    corrected_diagnosis = f"Alterazioni rilevate in {report_type.lower()} - interpretazione clinica limitata al tipo di esame"
                    logger.warning(f"⚠️ Inappropriate diagnosis detected: '{term}' in {test_type} analysis")
                    return corrected_diagnosis, True
    
    return diagnosis, False

def analyze_radiology_report(metadata: dict) -> dict:
    """Analyze radiology reports using text-based AI analysis with specific findings integration."""
    
    full_text = metadata.get('full_text', '')
    report_type = metadata.get('report_type', 'Referto radiologico')
    
    if not full_text or len(full_text.strip()) < 50:
        logger.warning("Insufficient text content for radiology analysis")
        return {
            "diagnosis": "Diagnosi non conclusiva - contenuto del referto insufficiente",
            "classification": "non disponibile"
        }
    
    logger.info(f"🏥 Analyzing radiology report with {len(full_text)} characters")
    
    # Initialize list for abnormal findings
    abnormal_findings = []
    specific_measurements = []
    
    # Enhanced patterns for various types of abnormalities with measurements
    patterns = [
        # Vascular patterns with measurements
        r"(placca|stenosi|ispessimento).+?([\d,]+%|[\d,]+\s*mm|diffuso)[^\.]*",
        r"(incontinenza|insufficienza).+?([^\.]+)",
        # Organ size measurements
        r"(fegato|milza|rene|pancreas|tiroide).+?([\d,]+\s*cm|[\d,]+\s*mm)[^\.]*",
        r"(diametro|dimensioni|misura).+?([\d,]+\s*cm|[\d,]+\s*mm)[^\.]*",
        # General structural patterns
        r"(alterazion[ei]|lesion[ei]|massa|nodulo|cisti).+?([^\.]+)",
        # Specific measurements
        r"IMT\s*[>≥]\s*[\d,]+\s*mm[^\.]*",
        r"spessore.+?[\d,]+\s*mm[^\.]*",
        # Fluid collections
        r"(versamento|raccolta|edema).+?([^\.]+)",
        # Specific conditions
        r"fibro-ateromasica.+?([^\.]+)",
        r"occlusione.+?([^\.]+)",
        # Wall thickness
        r"parete.+?(ispessita|ispessimento).+?([\d,]+\s*mm)?[^\.]*",
        # Calcifications
        r"calcificazion[ei].+?([^\.]+)"
    ]
    
    # Extract abnormal findings and measurements
    import re
    for pattern in patterns:
        matches = re.finditer(pattern, full_text, re.IGNORECASE)
        for match in matches:
            finding = match.group(0).strip()
            # Only add if finding is substantial
            if finding and len(finding) > 10:
                # Clean up the finding
                finding = finding.strip()
                # Remove leading/trailing punctuation
                finding = finding.strip('.,;: ')
                # Add to list if not already present
                if finding not in abnormal_findings:
                    abnormal_findings.append(finding)
                    
                    # Extract specific measurements if present
                    measurement_match = re.search(r'[\d,]+\s*(mm|cm|%)', finding)
                    if measurement_match:
                        specific_measurements.append(measurement_match.group(0))
    
    logger.info(f"Found {len(abnormal_findings)} abnormal findings with {len(specific_measurements)} measurements")
    
    # Enhanced AI prompt for radiology with specific findings integration
    enhanced_prompt = f"""
Sei un medico radiologo esperto. Analizza il seguente referto radiologico e fornisci una diagnosi specifica.

IMPORTANTE - Includi nei risultati le misure e i reperti specifici trovati nel referto:

REFERTO RADIOLOGICO:
{full_text}

REPERTI ANOMALI IDENTIFICATI: {', '.join(abnormal_findings[:5]) if abnormal_findings else 'Nessuno'}
MISURAZIONI SPECIFICHE: {', '.join(specific_measurements[:3]) if specific_measurements else 'Nessune'}

ISTRUZIONI SPECIFICHE:
1. Includi nella diagnosi le misure specifiche quando disponibili (es: "Epatosplenomegalia (fegato 18cm, milza 14cm)")
2. Menciona i reperti anomali con i loro valori (es: "Stenosi carotidea (70%)")
3. Se ci sono ispessimenti, includi lo spessore (es: "Ispessimento parietale (3mm)")
4. Per placche o lesioni, includi dimensioni se presenti
5. Mantieni terminologia radiologica precisa

Rispondi ESCLUSIVAMENTE in questo formato JSON:
{{
    "diagnosis": "diagnosi radiologica specifica con misure e reperti",
    "classification": "lieve | moderato | grave"
}}
"""
    
    try:
        # Send enhanced prompt to AI
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": enhanced_prompt}]
        )
        
        response_text = response['message']['content'].strip()
        logger.info(f"🤖 AI response received for radiology, length: {len(response_text)} chars")
        
        # Parse JSON response
        try:
            # Clean the response
            cleaned_result = response_text
            if "```json" in cleaned_result:
                cleaned_result = cleaned_result.replace("```json", "").replace("```", "").strip()
            elif "```" in cleaned_result:
                parts = cleaned_result.split("```")
                if len(parts) >= 2:
                    cleaned_result = parts[1].strip()
                    if cleaned_result.startswith("json"):
                        cleaned_result = cleaned_result[4:].strip()
            
            parsed_result = json.loads(cleaned_result.strip())
            diagnosis = parsed_result.get('diagnosis', 'Diagnosi radiologica non disponibile')
            classification = parsed_result.get('classification', 'moderato')
            
            # Validate classification
            valid_classifications = ["lieve", "moderato", "grave"]
            if classification not in valid_classifications:
                logger.warning(f"Invalid classification '{classification}', defaulting to 'moderato'")
                classification = "moderato"
            
            # Enhance diagnosis with specific findings if AI didn't include them
            enhanced_diagnosis = enhance_radiology_diagnosis_with_findings(diagnosis, abnormal_findings, specific_measurements)
            
            logger.info(f"✅ Radiology analysis complete: {enhanced_diagnosis}")
            return {
                "diagnosis": enhanced_diagnosis,
                "classification": classification,
                "abnormal_findings": abnormal_findings,
                "specific_measurements": specific_measurements,
                "report_type": report_type
            }
            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON response: {str(e)}")
            logger.warning(f"Raw response: {response_text[:200]}...")
            
            # Fallback: Create diagnosis based on findings
            fallback_diagnosis = create_radiology_fallback_diagnosis(abnormal_findings, specific_measurements)
            classification = "moderato" if abnormal_findings else "lieve"
            
            logger.info(f"🔄 Using fallback radiology diagnosis: {fallback_diagnosis}")
            return {
                "diagnosis": fallback_diagnosis,
                "classification": classification,
                "abnormal_findings": abnormal_findings,
                "specific_measurements": specific_measurements,
                "note": "Analisi fallback (JSON parsing failed)"
            }
                
    except Exception as ai_error:
        logger.error(f"AI communication error for radiology: {str(ai_error)}")
        
        # Fallback analysis based on findings
        fallback_diagnosis = create_radiology_fallback_diagnosis(abnormal_findings, specific_measurements)
        classification = "moderato" if abnormal_findings else "lieve"
        
        logger.info(f"🔄 Using fallback radiology diagnosis due to AI error: {fallback_diagnosis}")
        return {
            "diagnosis": fallback_diagnosis,
            "classification": classification,
            "abnormal_findings": abnormal_findings,
            "specific_measurements": specific_measurements,
            "note": "Analisi automatica (AI non disponibile)"
        }

def enhance_radiology_diagnosis_with_findings(diagnosis: str, abnormal_findings: list, specific_measurements: list) -> str:
    """Enhance radiology diagnosis by adding specific findings and measurements if not already present."""
    
    diagnosis_lower = diagnosis.lower()
    
    # Check if diagnosis already contains specific values
    has_measurements = any(unit in diagnosis_lower for unit in ['mm', 'cm', '%', 'ml'])
    
    if has_measurements:
        # Diagnosis already has measurements, return as is
        return diagnosis
    
    # Add specific findings to diagnosis
    enhancements = []
    
    # Look for key findings with measurements
    for finding in abnormal_findings[:3]:  # Limit to top 3 findings
        finding_lower = finding.lower()
        
        # Extract measurement from finding
        import re
        measurement_match = re.search(r'[\d,]+\s*(mm|cm|%)', finding)
        
        if measurement_match:
            measurement = measurement_match.group(0)
            
            # Categorize finding type
            if any(term in finding_lower for term in ['stenosi', 'placca']):
                if 'stenosi' not in diagnosis_lower:
                    enhancements.append(f"stenosi ({measurement})")
            elif any(term in finding_lower for term in ['ispessimento', 'spessore']):
                if 'ispessimento' not in diagnosis_lower:
                    enhancements.append(f"ispessimento ({measurement})")
            elif any(term in finding_lower for term in ['fegato', 'milza', 'rene']):
                organ = 'fegato' if 'fegato' in finding_lower else ('milza' if 'milza' in finding_lower else 'rene')
                enhancements.append(f"{organ} {measurement}")
    
    # Combine diagnosis with enhancements
    if enhancements:
        enhanced = f"{diagnosis} ({', '.join(enhancements)})"
        return enhanced
    
    return diagnosis

def create_radiology_fallback_diagnosis(abnormal_findings: list, specific_measurements: list) -> str:
    """Create radiology diagnosis based on findings when AI is not available."""
    
    if not abnormal_findings:
        return "Referto radiologico nei limiti della norma"
    
    diagnoses = []
    
    for finding in abnormal_findings[:3]:  # Limit to top 3 findings
        finding_lower = finding.lower()
        
        # Extract measurement if present
        import re
        measurement_match = re.search(r'[\d,]+\s*(mm|cm|%)', finding)
        measurement = measurement_match.group(0) if measurement_match else ""
        
        # Categorize and create specific diagnoses
        if any(term in finding_lower for term in ['stenosi', 'restringimento']):
            diagnoses.append(f"Stenosi {f'({measurement})' if measurement else ''}")
        elif any(term in finding_lower for term in ['placca', 'aterosclerosi']):
            diagnoses.append(f"Placca aterosclerotica {f'({measurement})' if measurement else ''}")
        elif any(term in finding_lower for term in ['ispessimento', 'spessore']):
            diagnoses.append(f"Ispessimento parietale {f'({measurement})' if measurement else ''}")
        elif any(term in finding_lower for term in ['versamento', 'raccolta']):
            diagnoses.append(f"Versamento {f'({measurement})' if measurement else ''}")
        elif any(term in finding_lower for term in ['massa', 'lesione', 'nodulo']):
            diagnoses.append(f"Lesione focale {f'({measurement})' if measurement else ''}")
        elif any(term in finding_lower for term in ['calcificazione']):
            diagnoses.append(f"Calcificazioni {f'({measurement})' if measurement else ''}")
        elif any(term in finding_lower for term in ['dilatazione', 'ectasia']):
            diagnoses.append(f"Dilatazione {f'({measurement})' if measurement else ''}")
        else:
            # Generic finding with measurement if available
            if measurement:
                # Try to extract the condition from the finding
                condition_match = re.search(r'^[^(]+', finding)
                condition = condition_match.group(0).strip() if condition_match else finding
                diagnoses.append(f"{condition} ({measurement})")
            else:
                diagnoses.append(finding[:50])  # Truncate long findings
    
    if diagnoses:
        return " | ".join(diagnoses)
    else:
        return f"Alterazioni radiologiche rilevate ({len(abnormal_findings)} reperti)"

def analyze_pathology_report(metadata: dict) -> dict:
    """Analyze pathology reports using text-based AI analysis."""
    
    full_text = metadata.get('full_text', '')
    report_type = metadata.get('report_type', 'Referto anatomopatologico')
    
    if not full_text or len(full_text.strip()) < 50:
        logger.warning("Insufficient text content for pathology analysis")
        return {
            "diagnosis": "Diagnosi non conclusiva - contenuto del referto insufficiente",
            "classification": "non disponibile"
        }
    
    logger.info(f"🔬 Analyzing pathology report with {len(full_text)} characters")
    
    # Use general text analysis for pathology reports
    return analyze_text_with_medgemma(full_text)
