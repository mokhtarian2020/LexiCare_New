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
Sei un medico esperto in nefrologia e urologia. Analizza SOLO i risultati dell'esame delle urine con interpretazione clinica accurata.

IMPORTANTE - CRITERI CLINICI PER VALORI URINARI:
📍 EMOGLOBINA/SANGUE nelle urine:
- <1 mg/dl: NORMALE (tracce clinicamente insignificanti)
- 1-5 mg/dl: LIEVE ematuria microscopica
- >5 mg/dl: SIGNIFICATIVA ematuria

📍 PROTEINE nelle urine:
- <10 mg/dl: NORMALE
- 10-30 mg/dl: LIEVE proteinuria
- >30 mg/dl: SIGNIFICATIVA proteinuria

📍 LEUCOCITI (Esterasi):
- <25 Leu/ul: NORMALE
- 25-75 Leu/ul: BORDERLINE (possibile contaminazione)
- >75 Leu/ul: SIGNIFICATIVO (infezione probabile)

✅ DIAGNOSI AMMESSE (solo per valori clinicamente significativi):
- Infezioni del tratto urinario (cistite, uretrite) - solo se leucociti >75 o nitriti positivi
- Proteinuria significativa (>30 mg/dl)
- Ematuria significativa (>5 mg/dl)
- Glicosuria (glucosio presente)

❌ NON DIAGNOSTICARE per valori borderline o tracce normali:
- Ematuria per emoglobina <1 mg/dl (sono tracce normali)
- Infezione per leucociti <75 senza altri segni
- Proteinuria per proteine <30 mg/dl

RISULTATI ESAME URINE:
{lab_data}

VALORI ALTERATI RILEVATI: {abnormal_str}

ATTENZIONE: Considera solo i valori clinicamente significativi secondo i criteri sopra. Tracce minime sono spesso normali.
Fornisci una diagnosi clinicamente accurata SOLO per valori realmente patologici.

CLASSIFICAZIONE (4 livelli):
- "normale": tutti i parametri nella norma, nessuna alterazione patologica
- "lieve": alterazioni minori, controllo di routine raccomandato
- "moderato": alterazioni che richiedono attenzione medica
- "grave": alterazioni che richiedono intervento immediato

Se tutti i valori sono normali o solo tracce insignificanti, utilizzare "normale".
Rispondi in JSON: {{"diagnosis": "diagnosi specifica per apparato urinario", "classification": "normale|lieve|moderato|grave"}}
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

CLASSIFICAZIONE (4 livelli):
- "normale": tutti i parametri biochimici nella norma
- "lieve": alterazioni minori, controllo di routine raccomandato
- "moderato": alterazioni che richiedono attenzione medica
- "grave": alterazioni che richiedono intervento immediato

Rispondi in JSON: {{"diagnosis": "diagnosi specifica per chimica clinica", "classification": "normale|lieve|moderato|grave"}}
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

CLASSIFICAZIONE (4 livelli):
- "normale": tutti i parametri ematologici nella norma
- "lieve": alterazioni minori, controllo di routine raccomandato
- "moderato": alterazioni che richiedono attenzione medica
- "grave": alterazioni che richiedono intervento immediato

Rispondi in JSON: {{"diagnosis": "diagnosi specifica per emocromo", "classification": "normale|lieve|moderato|grave"}}
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

CLASSIFICAZIONE (4 livelli):
- "normale": parametri di coagulazione nella norma
- "lieve": alterazioni minori, controllo di routine raccomandato
- "moderato": alterazioni che richiedono attenzione medica
- "grave": alterazioni che richiedono intervento immediato

Rispondi in JSON: {{"diagnosis": "diagnosi specifica per coagulazione", "classification": "normale|lieve|moderato|grave"}}
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

CLASSIFICAZIONE (4 livelli):
- "normale": tessuti nella norma, nessuna alterazione patologica
- "lieve": alterazioni minori benigne, controllo di routine
- "moderato": alterazioni che richiedono attenzione medica
- "grave": alterazioni maligne o che richiedono intervento immediato

Rispondi in JSON: {{"diagnosis": "diagnosi anatomopatologica", "classification": "normale|lieve|moderato|grave"}}
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

CLASSIFICAZIONE (4 livelli):
- "normale": reperti nella norma, nessuna alterazione patologica rilevata
- "lieve": alterazioni minori, controllo di routine raccomandato
- "moderato": alterazioni che richiedono attenzione medica
- "grave": alterazioni che richiedono intervento immediato

Per esami con "test negativo", "assenza di alterazioni", "nella norma", utilizzare "normale".
Rispondi in JSON: {{"diagnosis": "diagnosi radiologica", "classification": "normale|lieve|moderato|grave"}}
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

CLASSIFICAZIONE (4 livelli):
- "normale": tutti i parametri nella norma
- "lieve": alterazioni minori, controllo di routine raccomandato
- "moderato": alterazioni che richiedono attenzione medica
- "grave": alterazioni che richiedono intervento immediato

Rispondi in JSON: {{"diagnosis": "diagnosi appropriata per {report_type}", "classification": "normale|lieve|moderato|grave"}}
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
   - "normale": esame nella norma, nessuna patologia rilevata
   - "lieve": condizioni non gravi, gestibili ambulatorialmente
   - "moderato": condizioni che richiedono attenzione medica ma non urgente
   - "grave": condizioni che richiedono intervento immediato o ospedalizzazione

3. Se il referto riporta "test negativo", "nella norma", "assenza di alterazioni patologiche", utilizzare sempre classification "normale"

ESEMPI:
- ✅ CORRETTO: "Polmonite batterica del lobo inferiore destro"
- ❌ SBAGLIATO: "Dolore toracico e dispnea con opacità polmonare" (sintomi + reperti)
- ✅ CORRETTO: "Insufficienza cardiaca congestizia"  
- ❌ SBAGLIATO: "Cardiomegalia con versamento pleurico" (solo reperti)
- ✅ CORRETTO: "Frattura del radio distale"
- ❌ SBAGLIATO: "Radiografia del polso che mostra frattura" (titolo + reperto)
- ✅ CORRETTO per esami normali: "Esame nella norma" con classification "normale"

Rispondi ESCLUSIVAMENTE in questo formato JSON:
{{
    "diagnosis": "diagnosi medica definitiva in una frase",
    "classification": "normale | lieve | moderato | grave"
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
            valid_classifications = ["normale", "lieve", "moderato", "grave"]
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
            
            # Track abnormal values
            if test_data.get('abnormal', False):
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
                valid_classifications = ["normale", "lieve", "moderato", "grave"]
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

def create_fallback_diagnosis(report_type: str, abnormal_values: list) -> str:
    """Create a simple diagnosis based on test type and abnormal values when AI fails"""
    
    if not abnormal_values:
        return "Parametri di laboratorio nei limiti della norma"
    
    report_upper = report_type.upper()
    
    if "URINE" in report_upper or "CHIMICO FISICO" in report_upper:
        if any("proteine" in val.lower() for val in abnormal_values):
            return "Proteinuria rilevata - controllo nefrologico consigliato"
        elif any("leucocit" in val.lower() or "esterasi" in val.lower() for val in abnormal_values):
            return "Possibile infezione del tratto urinario - controllo consigliato"
        elif any("emoglobina" in val.lower() or "sangue" in val.lower() for val in abnormal_values):
            return "Ematuria rilevata - controllo urologico consigliato"
        else:
            return "Alterazioni nell'esame delle urine - controllo medico consigliato"
    
    elif "EMOCROMO" in report_upper or "SANGUE" in report_upper:
        if any("hgb" in val.lower() or "emoglobina" in val.lower() for val in abnormal_values):
            return "Possibile anemia - controllo ematologico consigliato"
        elif any("wbc" in val.lower() or "leucociti" in val.lower() for val in abnormal_values):
            return "Alterazioni dei globuli bianchi - controllo consigliato"
        elif any("plt" in val.lower() or "piastrine" in val.lower() for val in abnormal_values):
            return "Alterazioni delle piastrine - controllo ematologico consigliato"
        else:
            return "Alterazioni nell'emocromo - controllo ematologico consigliato"
    
    elif "CHIMICA" in report_upper or "BIOCHIMICA" in report_upper:
        if any("glucos" in val.lower() for val in abnormal_values):
            return "Alterazioni glicemiche - controllo diabetologico consigliato"
        elif any("got" in val.lower() or "ast" in val.lower() or "alt" in val.lower() for val in abnormal_values):
            return "Alterazioni epatiche - controllo epatologico consigliato"
        elif any("creatinina" in val.lower() or "urea" in val.lower() for val in abnormal_values):
            return "Alterazioni della funzione renale - controllo nefrologico consigliato"
        else:
            return "Alterazioni nella chimica clinica - controllo medico consigliato"
    
    else:
        return f"Alterazioni rilevate in {len(abnormal_values)} parametri - controllo medico consigliato"

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
    """Analyze radiology reports using text-based AI analysis."""
    
    full_text = metadata.get('full_text', '')
    report_type = metadata.get('report_type', 'Referto radiologico')
    
    if not full_text or len(full_text.strip()) < 50:
        logger.warning("Insufficient text content for radiology analysis")
        return {
            "diagnosis": "Diagnosi non conclusiva - contenuto del referto insufficiente",
            "classification": "non disponibile"
        }
    
    logger.info(f"🏥 Analyzing radiology report with {len(full_text)} characters")
    
    # Use general text analysis for radiology reports
    return analyze_text_with_medgemma(full_text)

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
