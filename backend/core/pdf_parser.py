import fitz                            # PyMuPDF
import pytesseract
from pdf2image import convert_from_path
from io import BytesIO
import tempfile, os, re
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Regex più robusto per il Codice Fiscale ---------------------------------
CF_RE = re.compile(
    r"""
    (?:
       (?:C(?:ODICE)?\s*F(?:ISCALE)?|CF|C\.F\.)     # etichette: Codice Fiscale, C.F., CF …
       [:.\s-]{0,5}                               # eventuali : . - o spazi
    )?                                            # l'etichetta può anche mancare
    ([A-Z]{6}\s*\d{2}\s*[A-Z]\s*\d{2}\s*[A-Z]\s*\d{3}\s*[A-Z])  # CF 16 car.
    """,
    re.I | re.X,
)

def extract_text_from_pdf(file_bytes: bytes) -> tuple[str, fitz.Document]:
    """Return full text and the opened PyMuPDF document."""
    logger.info("Opening PDF document")
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = "".join(p.get_text() for p in doc)
        logger.info(f"Extracted {len(text)} characters from PDF")

        # Use OCR if text is limited (< 100 characters)
        if len(text.strip()) < 100:
            logger.info("⚠️ Limited text detected, using OCR...")
            use_ocr = True
        else:
            use_ocr = os.getenv("ENABLE_OCR", "False").lower() == "true"
            if use_ocr:
                logger.info("OCR enabled by configuration")
                
        if use_ocr:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(file_bytes)
                tmp_path = tmp.name
                logger.info(f"Created temporary file for OCR: {tmp_path}")
                
            try:
                ocr_text = ""
                ocr_lang = os.getenv("PYTESSERACT_LANG", "ita")
                logger.info(f"Converting PDF to images for OCR with language: {ocr_lang}")
                images = convert_from_path(tmp_path, dpi=300)
                logger.info(f"Processing {len(images)} pages with OCR")
                
                for i, img in enumerate(images):
                    logger.info(f"Running OCR on page {i+1}")
                    page_text = pytesseract.image_to_string(img, lang=ocr_lang)
                    ocr_text += f"\n--- PAGINA {i+1} ---\n{page_text}"
                    
                # Use OCR text if it produced more content
                if len(ocr_text.strip()) > len(text.strip()):
                    text = ocr_text
                    logger.info("✅ OCR completed successfully (better than original text)")
                else:
                    logger.info("ℹ️ Using original text (better than OCR)")
            except Exception as e:
                logger.error(f"❌ OCR Error: {str(e)}")
            finally:
                logger.info("Cleaning up temporary file")
                os.remove(tmp_path)
    except Exception as e:
        logger.error(f"Error opening PDF document: {str(e)}")
        raise
            
    return text, doc

def find_cf(text: str, doc: fitz.Document) -> str | None:
    """Cerca CF in testo, metadata classici e XMP."""
    logger.info("Searching for Codice Fiscale in document")
    
    # Create sources list for searching
    sources = [text]
    
    # Add metadata values if available
    if hasattr(doc, "metadata") and doc.metadata:
        metadata_text = " ".join(str(v) for v in doc.metadata.values() if v)
        sources.append(metadata_text)
        logger.info(f"Added metadata to search sources: {metadata_text[:100]}...")
    
    # Try to access XMP metadata safely - different versions of PyMuPDF use different attribute names
    xmp_content = ""
    for attr_name in ["xmp_metadata", "xmp", "xmp_xml"]:
        if hasattr(doc, attr_name):
            xmp_value = getattr(doc, attr_name)
            if xmp_value:
                xmp_content = str(xmp_value)
                logger.info(f"Found XMP content using attribute '{attr_name}'")
                break
    
    if xmp_content:
        sources.append(xmp_content)
    
    # Normalizza il testo prima della ricerca (spazi, caratteri speciali)
    for src in sources:
        src = src.replace(" ", " ")  # normalizza spazi non-break
        src = src.replace("\n", " ")  # Sostituisce a capo con spazi
        
        m = CF_RE.search(src)
        if m:
            cf = re.sub(r"\s+", "", m.group(1).upper())  # togli spazi
            # Verifica che sia un CF valido con esattamente 16 caratteri
            if len(cf) == 16 and re.match(r"^[A-Z]{6}\d{2}[A-Z]\d{2}[A-Z]\d{3}[A-Z]$", cf):
                return cf
                
    # Ricerca più aggressiva nel testo con pattern semplificato
    simple_cf_pattern = r"[A-Z]{6}\s*\d{2}\s*[A-Z]\s*\d{2}\s*[A-Z]\s*\d{3}\s*[A-Z]"
    for src in sources:
        matches = re.findall(simple_cf_pattern, src, re.I)
        for match in matches:
            cf = re.sub(r"\s+", "", match.upper())
            if len(cf) == 16:
                return cf
                
    return None

def extract_exam_title(text: str) -> str | None:
    """
    Extract the exam/report type from medical document text.
    Prioritizes longer, more specific exam titles.
    """
    logger.info("Extracting exam title from document")
    
    # Split text into lines for better processing
    lines = text.splitlines()
    
    # Look for specific laboratory exam patterns first (most specific)
    lab_exam_patterns = [
        r"ESAME\s+CHIMICO\s+FISICO\s+DELLE?\s+URINE?",
        r"ESAME\s+EMOCROMOCITOMETRICO",
        r"ESAME\s+BATTERIOLOGICO",
        r"ESAME\s+MICROSCOPICO",
        r"FORMULA\s+LEUCOCITARIA",
        r"CHIMICA\s+CLINICA",
        r"EMOCROMO\s+COMPLETO",
        r"PROFILO\s+LIPIDICO",
        r"FUNZIONALITÀ\s+EPATICA",
        r"FUNZIONALITÀ\s+RENALE",
        r"MARKERS?\s+TUMORALI",
        r"ORMONI\s+TIROIDEI",
        r"COAGULAZIONE"
    ]
    
    # Add radiology and imaging exam patterns (most specific first)
    radiology_exam_patterns = [
        # Ecocolordopplergrafia - specific anatomical regions (most specific first)
        r"ECOCOLORDOPPLERGRAFIA\s+DEGLI\s+ARTI\s+INFERIORI\s+ARTERIOSO",
        r"ECOCOLORDOPPLERGRAFIA\s+DEGLI\s+ARTI\s+INFERIORI\s+VENOSO",
        r"ECOCOLORDOPPLERGRAFIA\s+DEGLI\s+ARTI\s+SUPERIORI\s+ARTERIOSO",
        r"ECOCOLORDOPPLERGRAFIA\s+DEGLI\s+ARTI\s+SUPERIORI\s+VENOSO",
        r"ECOCOLORDOPPLERGRAFIA\s+(?:DEI\s+)?TRONCHI\s+SOVRAORTICI",
        r"ECOCOLORDOPPLERGRAFIA\s+(?:DELL')?AORTA\s+ADDOMINALE",
        r"ECOCOLORDOPPLERGRAFIA\s+(?:DELLE\s+)?ARTERIE\s+RENALI",
        r"ECOCOLORDOPPLERGRAFIA\s+(?:DEL\s+)?SISTEMA\s+VENOSO\s+PROFONDO",
        r"ECOCOLORDOPPLERGRAFIA\s+(?:DELLE\s+)?CAROTIDI",
        r"ECOCOLORDOPPLERGRAFIA\s+(?:DELLE\s+)?ARTERIE\s+VERTEBRALI",
        r"ECOCOLORDOPPLERGRAFIA\s+CARDIACA",
        r"ECOCOLORDOPPLERGRAFIA\s+(?:ARTI\s+)?(?:INFERIORI|SUPERIORI)",
        r"ECOCOLORDOPPLERGRAFIA",
        
        # Ecografia - specific regions
        r"ECOGRAFIA\s+(?:DELL')?ADDOME\s+COMPLETO",
        r"ECOGRAFIA\s+(?:DELL')?ADDOME\s+SUPERIORE",
        r"ECOGRAFIA\s+(?:DELL')?ADDOME\s+INFERIORE",
        r"ECOGRAFIA\s+(?:DELLA\s+)?PELVI\s+TRANSVAGINALE",
        r"ECOGRAFIA\s+(?:DELLA\s+)?PELVI\s+TRANSADDOMINALE",
        r"ECOGRAFIA\s+(?:DELLA\s+)?TIROIDE",
        r"ECOGRAFIA\s+(?:DEL\s+)?COLLO",
        r"ECOGRAFIA\s+(?:DELLE\s+)?MAMMELLE",
        r"ECOGRAFIA\s+(?:DEI\s+)?TESTICOLI",
        r"ECOGRAFIA\s+(?:DELLA\s+)?PROSTATA",
        r"ECOGRAFIA\s+(?:DEI\s+)?RENI\s+E\s+VESCICA",
        r"ECOGRAFIA\s+(?:DELLE\s+)?VIE\s+URINARIE",
        r"ECOGRAFIA\s+(?:DEL\s+)?FEGATO",
        r"ECOGRAFIA\s+(?:DELLA\s+)?COLECISTI",
        r"ECOGRAFIA\s+(?:DEL\s+)?PANCREAS",
        r"ECOGRAFIA\s+(?:DELLA\s+)?MILZA",
        r"ECOGRAFIA\s+(?:ADDOMINALE|PELVICA|TIROIDEA|EPATICA|RENALE)",
        
        # Ecocardiogramma variants
        r"ECOCARDIOGRAMMA\s+(?:COLOR\s+)?DOPPLER",
        r"ECOCARDIOGRAMMA\s+TRANSTORACICO",
        r"ECOCARDIOGRAMMA\s+TRANSESOFAGEO",
        r"ECOCARDIOGRAMMA",
        
        # Radiografia variants
        r"RADIOGRAFIA\s+(?:DEL\s+)?TORACE\s+IN\s+DUE\s+PROIEZIONI",
        r"RADIOGRAFIA\s+(?:DEL\s+)?TORACE\s+(?:IN\s+)?(?:PA|AP)",
        r"RADIOGRAFIA\s+(?:DELLA\s+)?COLONNA\s+VERTEBRALE",
        r"RADIOGRAFIA\s+(?:DEL\s+)?BACINO",
        r"RADIOGRAFIA\s+(?:DELLE\s+)?ANCHE",
        r"RADIOGRAFIA\s+(?:DEL\s+)?GINOCCHIO",
        r"RADIOGRAFIA\s+(?:DELLA\s+)?SPALLA",
        r"RADIOGRAFIA\s+(?:DEL\s+)?POLSO",
        r"RADIOGRAFIA\s+(?:DELLA\s+)?CAVIGLIA",
        r"RADIOGRAFIA\s+(?:DEL\s+)?PIEDE",
        r"RADIOGRAFIA\s+(?:DELL')?ADDOME",
        r"RADIOGRAFIA\s+(?:DEL\s+)?TORACE",
        
        # TAC/TC variants
        r"TAC\s+(?:DELL')?ADDOME\s+(?:CON\s+)?(?:E\s+SENZA\s+)?(?:MDC|CONTRASTO)",
        r"TAC\s+(?:DEL\s+)?TORACE\s+(?:CON\s+)?(?:E\s+SENZA\s+)?(?:MDC|CONTRASTO)",
        r"TAC\s+(?:DEL\s+)?CRANIO\s+(?:CON\s+)?(?:E\s+SENZA\s+)?(?:MDC|CONTRASTO)",
        r"TAC\s+(?:DELL')?ENCEFALO\s+(?:CON\s+)?(?:E\s+SENZA\s+)?(?:MDC|CONTRASTO)",
        r"TAC\s+(?:DELLA\s+)?COLONNA\s+VERTEBRALE",
        r"TAC\s+(?:DEL\s+)?RACHIDE",
        r"TAC\s+(?:ADDOME|TORACE|CRANIO|ENCEFALO)",
        
        # Risonanza Magnetica variants
        r"RISONANZA\s+MAGNETICA\s+(?:DELL')?ENCEFALO",
        r"RISONANZA\s+MAGNETICA\s+(?:DELLA\s+)?COLONNA\s+VERTEBRALE",
        r"RISONANZA\s+MAGNETICA\s+(?:DEL\s+)?RACHIDE",
        r"RISONANZA\s+MAGNETICA\s+(?:DEL\s+)?GINOCCHIO",
        r"RISONANZA\s+MAGNETICA\s+(?:DELLA\s+)?SPALLA",
        r"RISONANZA\s+MAGNETICA\s+(?:DELL')?ADDOME",
        r"RISONANZA\s+MAGNETICA\s+(?:DEL\s+)?BACINO",
        r"RISONANZA\s+MAGNETICA",
        
        # Other imaging modalities
        r"MAMMOGRAFIA\s+BILATERALE",
        r"MAMMOGRAFIA",
        r"DENSITOMETRIA\s+OSSEA",
        r"SCINTIGRAFIA\s+OSSEA",
        r"SCINTIGRAFIA\s+TIROIDEA",
        r"SCINTIGRAFIA",
        r"ANGIO\s*TAC",
        r"ANGIO\s*RM",
        
        # Generic patterns (least specific, processed last)
        r"REFERTO\s+DI\s+RADIOLOGIA",
        r"REFERTO\s+RADIOLOGICO",
        r"DOPPLER",
        r"ECO\s+DOPPLER",
        r"ECO-DOPPLER"
    ]
    
    # Add pathology and histology exam patterns
    pathology_exam_patterns = [
        r"ESAME\s+ISTOLOGICO",
        r"ESAME\s+CITOLOGICO", 
        r"ESAME\s+ANATOMO\s*PATOLOGICO",
        r"BIOPSIA",
        r"AGOBIOPSIA",
        r"REFERTO\s+(?:DI\s+)?(?:ANATOMIA\s+)?PATOLOGICA?",
        r"REFERTO\s+ISTOLOGICO",
        r"REFERTO\s+CITOLOGICO",
        r"DIAGNOSI\s+ISTOLOGICA",
        r"DIAGNOSI\s+CITOLOGICA",
        r"PAP\s*TEST",
        r"IMMUNOISTOCHIMICA",
        r"COLORAZIONE\s+(?:HE|H&E|EMATOSSILINA)",
        r"PREPARATO\s+ISTOLOGICO",
        r"SEZIONI\s+ISTOLOGICHE"
    ]
    
    # Combine all specific patterns
    all_specific_patterns = lab_exam_patterns + radiology_exam_patterns + pathology_exam_patterns
    
    # Search for specific laboratory exam patterns in the entire text
    for pattern in all_specific_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            found_title = match.group(0).strip()
            logger.info(f"Found specific exam title: {found_title}")
            return found_title.title()
    
    # Look for exam titles in dedicated sections (look for longer, more descriptive titles)
    exam_title_candidates = []
    
    # Find lines that look like exam titles (all caps, meaningful length)
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Skip very early lines (headers) and very late lines (results)
        if i < 5 or i > 50:
            continue
            
        # Look for capitalized lines that contain medical keywords
        if (len(line) > 10 and len(line) < 100 and 
            line.isupper() and 
            not any(c.isdigit() for c in line[:5])):  # No numbers at start
            
            # Check if it contains medical exam keywords
            medical_keywords = [
                'ESAME', 'REFERTO', 'ANALISI', 'DIAGNOSTICA', 'INDAGINE',
                'CHIMICO', 'FISICO', 'BATTERIOLOGICO', 'MICROSCOPICO',
                'URINE', 'SANGUE', 'EMOCROMO', 'COAGULAZIONE',
                'RADIOLOG', 'ECOGRAF', 'CARDIOL', 'NEUROLOG', 'ORTOPED',
                'PATOLOG', 'ISTOLOG', 'CITOLOG', 'BIOPSIA'
            ]
            
            if any(keyword in line for keyword in medical_keywords):
                # Exclude administrative terms
                admin_terms = [
                    'AZIENDA', 'OSPEDALE', 'DIRETTORE', 'RESPONSABILE',
                    'TELEFONO', 'EMAIL', 'INDIRIZZO', 'VIA', 'VIALE',
                    'CODICE', 'PAZIENTE', 'RISULTATO', 'UNITA', 'RIFERIMENTO'
                ]
                
                if not any(term in line for term in admin_terms):
                    exam_title_candidates.append((len(line), line, i))
    
    # Sort by length (longer titles are usually more specific) and prefer earlier positions
    exam_title_candidates.sort(key=lambda x: (-x[0], x[2]))
    
    if exam_title_candidates:
        best_title = exam_title_candidates[0][1]
        logger.info(f"Found exam title candidate: {best_title}")
        return best_title.title()
    
    # Fallback: look for pattern-based exam types
    report_type_patterns = [
        r"(?:Tipo(?:\s*di)?(?:\s*esame|referto|indagine)?)[\s:.-]*([A-Za-zÀ-ÿ\s]+)",
        r"(?:REFERTO|Referto)(?:\s*di)?[\s:.-]*([A-Za-zÀ-ÿ\s]+)",
        r"(?:PRESTAZIONE|Prestazione)[\s:.-]*([A-Za-zÀ-ÿ\s]+)",
        r"(?:SPECIALITÀ|Specialità)[\s:.-]*([A-Za-zÀ-ÿ\s]+)",
        r"(?:SETTORE|Settore)[\s:.-]*([A-Za-zÀ-ÿ\s]+)"
    ]
    
    for pattern in report_type_patterns:
        match = re.search(pattern, text, re.I)
        if match:
            result = match.group(1).strip()
            # Clean and validate the result
            result = re.sub(r'\s+', ' ', result)  # Normalize spaces
            if result and len(result) > 3 and len(result) < 100:
                # Skip if it's just generic terms
                if result.upper() not in ['RISULTATO', 'UNITA', 'VALORE', 'DATO']:
                    logger.info(f"Found pattern-based exam title: {result}")
                    return result.title()

    # Check for specific medical keywords in the entire text (fallback classification)
    type_keywords = {
        "Esame Chimico Fisico Delle Urine": ["URINE", "PROTEINE", "GLUCOSIO", "SEDIMENTO", "ESTERASI"],
        "Esame Emocromocitometrico": ["WBC", "RBC", "HGB", "HCT", "PLT", "EMOCROMO"],
        "Chimica Clinica": ["GLUCOSIO", "CREATININA", "UREA", "SODIO", "POTASSIO", "TRANSAMINASI"],
        "Ecocolordopplergrafia": ["ECOCOLORDOPPLERGRAFIA", "DOPPLER", "CAROTIDE", "VASCOLARE", "STENOSI", "FLUSSO"],
        "Radiologia": ["RX", "TAC", "ECOGRAFIA", "RADIOLOGIA", "ECO", "RAGGI X", "RISONANZA"],
        "Cardiologia": ["ECG", "ECOCARDIOGRAMMA", "ELETTROCARDIOGRAMMA", "CARDIO", "CARDIOVASCOLARE"],
        "Anatomia Patologica": ["ISTOLOGICO", "CITOLOGICO", "BIOPSIA", "AGOBIOPSIA", "PATOLOGICA", "HE", "EMATOSSILINA", "IMMUNOISTOCHIMICA", "NEOPLASIA", "DISPLASIA", "METAPLASIA"],
        "Laboratorio": ["ANALISI", "LABORATORIO", "BIOCHIMICA", "SIEROLOGIA"]
    }
    
    # Check for these keywords in the first part of the document
    search_text = ' '.join(lines[:30]).upper()  # First 30 lines
    for type_name, keywords in type_keywords.items():
        keyword_count = sum(1 for keyword in keywords if keyword in search_text)
        if keyword_count >= 2:  # Need at least 2 matching keywords
            logger.info(f"Found exam type by keywords: {type_name}")
            return type_name
    
    logger.warning("No specific exam title found")
    return None

def extract_metadata(file_bytes: bytes) -> dict:
    logger.info("Extracting metadata from PDF")
    
    text, doc = extract_text_from_pdf(file_bytes)
    
    logger.info(f"Successfully extracted {len(text)} chars from document")
    logger.info("Searching for patient information in document")
    # Pattern più robusti per i dati anagrafici italiani
    name_patterns = [
        # Use non-greedy matching and better boundaries for formal titles
        r"Sig\.?\s+([A-ZÀ-ÿ]+(?:\s+[A-ZÀ-ÿ]+)?)\s*(?:\n|$|D\.|C\.F\.|\d)",
        r"Sig\.ra\s+([A-ZÀ-ÿ]+(?:\s+[A-ZÀ-ÿ]+)?)\s*(?:\n|$|D\.|C\.F\.|\d)",
        r"Signor[ae]?\s+([A-ZÀ-ÿ]+(?:\s+[A-ZÀ-ÿ]+)?)\s*(?:\n|$|D\.|C\.F\.|\d)",
        r"Dott\.?\s+([A-ZÀ-ÿ]+(?:\s+[A-ZÀ-ÿ]+)?)\s*(?:\n|$|D\.|C\.F\.|\d)",
        r"Dr\.?\s+([A-ZÀ-ÿ]+(?:\s+[A-ZÀ-ÿ]+)?)\s*(?:\n|$|D\.|C\.F\.|\d)",
        r"Dr\.ssa\s+([A-ZÀ-ÿ]+(?:\s+[A-ZÀ-ÿ]+)?)\s*(?:\n|$|D\.|C\.F\.|\d)",
        r"Prof\.?\s+([A-ZÀ-ÿ]+(?:\s+[A-ZÀ-ÿ]+)?)\s*(?:\n|$|D\.|C\.F\.|\d)",
        # Standard field patterns with boundaries
        r"(?:Paziente|Nome)[\s:.-]+([A-ZÀ-ÿ]+(?:\s+[A-ZÀ-ÿ]+)?)\s*(?:\n|$|D\.|C\.F\.|\d)",
        r"(?:Cognome)[\s:.-]+([A-ZÀ-ÿ]+(?:\s+[A-ZÀ-ÿ]+)?)\s*(?:\n|$|D\.|C\.F\.|\d)",
        r"(?:Nome e cognome|Nominativo)[\s:.-]+([A-ZÀ-ÿ]+(?:\s+[A-ZÀ-ÿ]+)?)\s*(?:\n|$|D\.|C\.F\.|\d)",
        r"(?:Assistito|Soggetto)[\s:.-]+([A-ZÀ-ÿ]+(?:\s+[A-ZÀ-ÿ]+)?)\s*(?:\n|$|D\.|C\.F\.|\d)",
        r"(?:Destinatario|Per|Richiedente)[\s:.-]+([A-ZÀ-ÿ]+(?:\s+[A-ZÀ-ÿ]+)?)\s*(?:\n|$|D\.|C\.F\.|\d)",
        # Pattern for reports with name on next line
        r"Nome[\s:.-]*\n\s*([A-ZÀ-ÿ]+(?:\s+[A-ZÀ-ÿ]+)?)\s*(?:\n|$)",
        r"Paziente[\s:.-]*\n\s*([A-ZÀ-ÿ]+(?:\s+[A-ZÀ-ÿ]+)?)\s*(?:\n|$)"
    ]

    # Patterns for date of birth - enhanced for Italian medical documents
    birth_date_patterns = [
        r"(?:D\.?\s*Nasc\.?|Data di nascita|Nato il|Nata il)[\s:.-]*([0-9]{1,2}[/.-][0-9]{1,2}[/.-][0-9]{2,4})",
        r"(?:DN|d\.n\.|D\.N\.)[\s:.-]*([0-9]{1,2}[/.-][0-9]{1,2}[/.-][0-9]{2,4})",
        r"(?:Nascita|Birth|Born)[\s:.-]*([0-9]{1,2}[/.-][0-9]{1,2}[/.-][0-9]{2,4})",
        r"(?:Data nasc\.?|D\.nasc\.?)[\s:.-]*([0-9]{1,2}[/.-][0-9]{1,2}[/.-][0-9]{2,4})",
        r"(?:Nato\/a il|Nato\/a in data)[\s:.-]*([0-9]{1,2}[/.-][0-9]{1,2}[/.-][0-9]{2,4})",
        r"(?:Luogo e data di nascita).*?([0-9]{1,2}[/.-][0-9]{1,2}[/.-][0-9]{2,4})",
        r"(?:Nato a).*?(?:il)[\s:.-]*([0-9]{1,2}[/.-][0-9]{1,2}[/.-][0-9]{2,4})",
        r"(?:Nata a).*?(?:il)[\s:.-]*([0-9]{1,2}[/.-][0-9]{1,2}[/.-][0-9]{2,4})",
        r"(?:Data nascita|D\.nascita)[\s:.-]*([0-9]{1,2}[/.-][0-9]{1,2}[/.-][0-9]{2,4})",
        r"(?:D\.?\s*Nasc\.?|Data di nascita)[\s:.-]*\n\s*([0-9]{1,2}[/.-][0-9]{1,2}[/.-][0-9]{2,4})"
    ]
    
    # Patterns for exam/report dates - comprehensive Italian medical formats
    date_patterns = [
        # Standard Italian exam date patterns
        r"(?:Data|Data esame|Data referto|Data del referto)[\s:.-]*([0-9]{1,2}[/.-][0-9]{1,2}[/.-][0-9]{2,4})",
        # Italian specific medical date patterns
        r"(?:Refertato il|Refertazione)[\s:.-]*([0-9]{1,2}[/.-][0-9]{1,2}[/.-][0-9]{2,4})",
        r"(?:Eseguito il|Effettuato il|Eseguito in data)[\s:.-]*([0-9]{1,2}[/.-][0-9]{1,2}[/.-][0-9]{2,4})",
        r"(?:In data|Il giorno|Nella giornata del)[\s:.-]*([0-9]{1,2}[/.-][0-9]{1,2}[/.-][0-9]{2,4})",
        r"(?:Del|dell'|della)[\s:.-]*([0-9]{1,2}[/.-][0-9]{1,2}[/.-][0-9]{2,4})",
        # Healthcare service patterns
        r"(?:Prestazione del|Prestazione effettuata il)[\s:.-]*([0-9]{1,2}[/.-][0-9]{1,2}[/.-][0-9]{2,4})",
        r"(?:Visitato il|Visita del|Visita effettuata il)[\s:.-]*([0-9]{1,2}[/.-][0-9]{1,2}[/.-][0-9]{2,4})",
        r"(?:Controllo del|Controllo effettuato il)[\s:.-]*([0-9]{1,2}[/.-][0-9]{1,2}[/.-][0-9]{2,4})",
        # Appointment and procedure patterns
        r"(?:Appuntamento del|Appuntamento in data)[\s:.-]*([0-9]{1,2}[/.-][0-9]{1,2}[/.-][0-9]{2,4})",
        r"(?:Prelievo del|Prelievo effettuato il|Campionamento)[\s:.-]*([0-9]{1,2}[/.-][0-9]{1,2}[/.-][0-9]{2,4})",
        r"(?:Analisi del|Analisi effettuate il)[\s:.-]*([0-9]{1,2}[/.-][0-9]{1,2}[/.-][0-9]{2,4})",
        # Administrative patterns
        r"(?:Accettazione|Accettato il|Ricevuto il)[\s:.-]*([0-9]{1,2}[/.-][0-9]{1,2}[/.-][0-9]{2,4})",
        r"(?:Registrato il|Protocollato il)[\s:.-]*([0-9]{1,2}[/.-][0-9]{1,2}[/.-][0-9]{2,4})",
        r"(?:Emesso il|Stampato il|Rilasciato il)[\s:.-]*([0-9]{1,2}[/.-][0-9]{1,2}[/.-][0-9]{2,4})",
        # Time and date patterns
        r"(?:Data e ora|Data e orario)[\s:.-]*([0-9]{1,2}[/.-][0-9]{1,2}[/.-][0-9]{2,4})",
        # Patterns where date appears on next line
        r"(?:Data|Data esame|Refertato il)[\s:.-]*\n\s*([0-9]{1,2}[/.-][0-9]{1,2}[/.-][0-9]{2,4})",
        # Fallback: Standalone date with 4-digit year (last resort)
        r"([0-9]{1,2}[/.-][0-9]{1,2}[/.-][0-9]{4})"
    ]
    
    # Cerca nome paziente con i vari pattern
    patient_name = None
    
    # Enhanced patterns for different medical report formats
    enhanced_name_patterns = [
        # Direct format: Nome: Palumbo Maria Grazia (most specific for radiology)
        r"Nome:\s+([A-ZÀ-ÿ][a-zà-ÿ]+(?:\s+[A-ZÀ-ÿ][a-zà-ÿ]+)+?)(?:\s*\n|$|Età|Age)",
        # Standard format with boundaries
        r"(?:Nome|Paziente|Patient)[\s:.-]+([A-ZÀ-ÿ][a-zà-ÿ]+(?:\s+[A-ZÀ-ÿ][a-zà-ÿ]+)+?)(?:\s*\n|$|Età|Age|D\.|C\.F\.|\d)",
        # Medical center format: Center line + Name line
        r"(?:Centro|Ambulatorio|Clinica).*?\n.*?Nome:\s*([A-ZÀ-ÿ][a-zà-ÿ]+(?:\s+[A-ZÀ-ÿ][a-zà-ÿ]+)+?)(?:\s*\n|$|Età)",
        # Extended patterns from original with better boundaries
        r"Sig\.?\s+([A-ZÀ-ÿ]+(?:\s+[A-ZÀ-ÿ]+)*?)(?:\s*\n|$|D\.|C\.F\.|\d|Età)",
        r"(?:Intestato a|Per)[\s:.-]+([A-ZÀ-ÿ]+(?:\s+[A-ZÀ-ÿ]+)*?)(?:\s*\n|$|D\.|C\.F\.|\d)",
        r"(?:Paziente)[\s:.-]+([A-ZÀ-ÿ]+(?:\s+[A-ZÀ-ÿ]+)*?)(?:\s*\n|$|D\.|C\.F\.|\d)",
        # Professional titles
        r"(?:Dott\.?|Dr\.?|Prof\.?)\s+([A-ZÀ-ÿ]+(?:\s+[A-ZÀ-ÿ]+)*?)(?:\s*\n|$|D\.|C\.F\.|\d)",
        # Generic name patterns with better boundaries
        r"([A-ZÀ-ÿ]{2,}\s+[A-ZÀ-ÿ]{2,}(?:\s+[A-ZÀ-ÿ]{2,})?)\s*(?:\d{2}|\n|Età|Age)"
    ]
    
    for pattern in enhanced_name_patterns:
        name_match = re.search(pattern, text, re.I | re.MULTILINE)
        if name_match:
            raw_name = name_match.group(1).strip()
            # Clean and validate the name
            cleaned_name = re.sub(r'\s+', ' ', raw_name)  # Normalize spaces
            cleaned_name = cleaned_name.title()  # Title case
            
            # Validate that it looks like a real name (no numbers, reasonable length)
            if (len(cleaned_name) >= 3 and len(cleaned_name) <= 50 and 
                not re.search(r'\d', cleaned_name) and  # No digits
                not re.search(r'[^\w\sÀ-ÿ\'-]', cleaned_name) and  # Only valid name characters
                not any(word.lower() in ['data', 'centro', 'medico', 'via', 'tel', 'dott'] for word in cleaned_name.split())):  # Not administrative terms
                
                patient_name = cleaned_name
                logger.info(f"Found patient name with pattern: {pattern} -> {patient_name}")
                break
            else:
                logger.debug(f"Found potential name but failed validation: {cleaned_name}")
                continue

    # Cerca data di nascita
    birth_date = None
    for pattern in birth_date_patterns:
        birth_match = re.search(pattern, text, re.I)
        if birth_match:
            try:
                raw_birth_date = birth_match.group(1)
                # Normalizza formato data a DD/MM/YYYY
                normalized_birth_date = re.sub(r'[.-]', '/', raw_birth_date)
                
                # Parse and validate the date components
                parts = normalized_birth_date.split('/')
                if len(parts) == 3:
                    day, month, year = parts
                    
                    # Convert year to 4 digits if necessary
                    if len(year) == 2:
                        year_int = int(year)
                        if year_int > 50:  # Born before 1950 -> 19xx
                            year = "19" + year
                        else:  # Born after 1950 -> 20xx  
                            year = "20" + year
                    
                    # Validate date ranges
                    day_int, month_int, year_int = int(day), int(month), int(year)
                    if (1 <= day_int <= 31 and 1 <= month_int <= 12 and 
                        1900 <= year_int <= 2024):  # Reasonable birth year range
                        
                        birth_date = f"{day:0>2}/{month:0>2}/{year}"
                        logger.info(f"Found birth date with pattern: {pattern} -> {birth_date}")
                        break
                    else:
                        logger.warning(f"Birth date out of valid range: {normalized_birth_date}")
                        continue
                else:
                    logger.warning(f"Invalid birth date format: {raw_birth_date}")
                    continue
                    
            except (IndexError, ValueError) as e:
                logger.warning(f"Error processing birth date: {str(e)}")
                continue
    
    # Cerca data esame/referto con i vari pattern
    report_date = None
    for pattern in date_patterns:
        date_match = re.search(pattern, text, re.I)
        if date_match:
            try:
                # Safely extract the first capturing group
                raw_report_date = date_match.group(1)
                # Normalizza formato data a DD/MM/YYYY
                normalized_report_date = re.sub(r'[.-]', '/', raw_report_date)
                
                # Parse and validate the date components
                parts = normalized_report_date.split('/')
                if len(parts) == 3:
                    day, month, year = parts
                    
                    # Convert year to 4 digits if necessary
                    if len(year) == 2:
                        year_int = int(year)
                        if year_int > 50:  # Likely 19xx
                            year = "19" + year
                        else:  # Likely 20xx
                            year = "20" + year
                    
                    # Validate date ranges
                    day_int, month_int, year_int = int(day), int(month), int(year)
                    if (1 <= day_int <= 31 and 1 <= month_int <= 12 and 
                        1980 <= year_int <= 2025):  # Reasonable exam date range
                        
                        report_date = f"{day:0>2}/{month:0>2}/{year}"
                        logger.info(f"Found exam date with pattern: {pattern} -> {report_date}")
                        break
                    else:
                        logger.warning(f"Exam date out of valid range: {normalized_report_date}")
                        continue
                else:
                    logger.warning(f"Invalid exam date format: {raw_report_date}")
                    continue
                    
            except (IndexError, ValueError) as e:
                logger.warning(f"Pattern {pattern} matched but error processing date: {str(e)}")
                continue
            
    # Recupera codice fiscale
    try:
        codice_fiscale = find_cf(text, doc)
        logger.info(f"Found CF: {codice_fiscale or 'Not found'}")
    except Exception as e:
        logger.error(f"Error finding CF: {str(e)}")
        codice_fiscale = None
    
    # Get report title and classify report type
    try:
        report_title = extract_exam_title(text) or "sconosciuto"
        report_category = classify_report_type(text, report_title)
        logger.info(f"Report classification: {report_category} (title: {report_title})")
    except Exception as e:
        logger.error(f"Error extracting/classifying report type: {str(e)}")
        report_title = "sconosciuto"
        report_category = "laboratory"  # Default fallback
    
    # Extract laboratory values (for all reports, but most relevant for laboratory type)
    try:
        lab_values = extract_laboratory_values(text)
        logger.info(f"Extracted {len(lab_values)} laboratory parameters")
    except Exception as e:
        logger.error(f"Error extracting laboratory values: {str(e)}")
        lab_values = {}
    
    # Extract all date types
    try:
        extracted_dates = extract_exam_dates(text)
        # Use extracted dates if available, fallback to existing logic
        if 'report_date' in extracted_dates:
            report_date = extracted_dates['report_date']
        elif 'exam_date' in extracted_dates:
            report_date = extracted_dates['exam_date']
        elif 'acceptance_date' in extracted_dates:
            report_date = extracted_dates['acceptance_date']
        # Keep the existing report_date if no new dates found
    except Exception as e:
        logger.error(f"Error extracting dates: {str(e)}")
        extracted_dates = {}
    
    return {
        "full_text"          : text,
        "patient_name"       : patient_name,
        "birth_date"         : birth_date,
        "codice_fiscale"     : codice_fiscale,
        "report_date"        : report_date,
        "report_type"        : report_title,
        "report_category"    : report_category,
        "laboratory_values"  : lab_values,
        "extracted_dates"    : extracted_dates,
    }

def apply_clinical_significance(test_name: str, value: str, unit: str, reference: str, original_abnormal: bool) -> bool:
    """
    Apply clinical significance rules to determine if a lab value is truly abnormal.
    This overrides the simple '*' flag detection with medical knowledge.
    """
    test_upper = test_name.upper()
    
    try:
        # Convert value to float for numeric comparisons (handle comma as decimal)
        numeric_value = float(value.replace(',', '.'))
        
        # HEMOGLOBIN IN URINE - clinical thresholds
        if 'EMOGLOBINA' in test_upper and 'mg/dl' in unit.lower():
            # <1 mg/dl: Normal trace amounts
            # 1-5 mg/dl: Mild microscopic hematuria  
            # >5 mg/dl: Significant hematuria
            if numeric_value < 1.0:
                return False  # Traces are normal
            elif numeric_value < 5.0:
                return True   # Mild abnormality
            else:
                return True   # Significant abnormality
        
        # PROTEINS IN URINE - clinical thresholds
        elif 'PROTEINE' in test_upper and 'mg/dl' in unit.lower():
            # <10 mg/dl: Normal
            # 10-30 mg/dl: Mild proteinuria
            # >30 mg/dl: Significant proteinuria
            if numeric_value <= 10.0:
                return False  # Normal
            elif numeric_value <= 30.0:
                return True   # Mild abnormality
            else:
                return True   # Significant abnormality
        
        # LEUKOCYTE ESTERASE - clinical thresholds
        elif 'ESTERASI' in test_upper and 'LEUCOCIT' in test_upper:
            # <25 Leu/ul: Normal
            # 25-75 Leu/ul: Borderline (possible contamination)
            # >75 Leu/ul: Significant (probable infection)
            if numeric_value < 25.0:
                return False  # Normal
            elif numeric_value <= 75.0:
                return True   # Borderline - keep as abnormal but note
            else:
                return True   # Significant abnormality
                
    except (ValueError, AttributeError):
        # If we can't parse as numeric, fall back to original logic
        pass
    
    # For qualitative values or parsing errors, use original flag
    return original_abnormal

def extract_laboratory_values(text: str) -> dict:
    """
    Extract laboratory test values, units, and reference ranges from Italian medical reports.
    Handles both single-line and multi-line formats.
    """
    logger.info("Extracting laboratory values from text")
    
    lab_values = {}
    lines = text.split('\n')
    
    # Known test names for exact matching
    known_tests = [
        # Urinalysis
        'Colore', 'Aspetto', 'Limpidezza', 'Ph', 'PH', 'Glucosio', 'Proteine', 
        'Emoglobina', 'Corpi Chetonici', 'Bilirubina', 'Urobilinogeno', 
        'Peso Specifico', 'Densità', 'Nitriti', 'Esterasi Leucocitaria',
        
        # Hematology
        'WBC', 'RBC', 'HGB', 'HCT', 'MCV', 'MCH', 'MCHC', 'RDW', 'PLT', 'MPV',
        'NEU', 'LYN', 'MON', 'EOS', 'BAS',
        
        # Chemistry
        'GLUCOSIO', 'CREATININA', 'UREA', 'SODIO', 'POTASSIO', 'CALCIO', 'ALBUMINA',
        'BILIRUBINA TOTALE', 'GOT/AST', 'GPT/ALT', 'CPK', 'INR', 'PTT',
        'PROTEINA C REATTIVA', 'AMILASI PANCREATICA', 'COLINESTERASI',
        'ATTIVITA\' PROTROMBINICA'
    ]
    
    # Exclude patterns - lines that are definitely not lab values
    exclude_patterns = [
        r'\b(A\.S\.L\.|OSPEDALE|PATOLOGIA|CLINICA|DIRETTORE|VIALE|NAPOLI|TEL\.|EMAIL)\b',
        r'(lab\.ospmare@libero\.it|081-18775094|Metamorfosi)',
        r'(Cod\.|Sig\.|Provenienza|C\.F\.|Nosologico|D\.Nasc\.)',
        r'(Accettato il|Refertato il|ESAME|RISULTATO|UNITA)',
        r'(IL T\.S\.L\.B\.|IL SANITARIO RESPONSABILE|Pag\.)',
        r'(ESAME CHIMICO FISICO|ESAME EMOCROMOCITOMETRICO|FORMULA LEUCOCITARIA)',
        r'(SEDIMENTO:|fine referto|\.\.\.|§S§)',
        r'^\s*[0-9]+/mm3\s*$',  # Unit-only lines
        r'RIFERIMENTO\s*$',  # Reference header
        # Add administrative and non-medical data exclusions
        r'\b(Data:|Nome:|Età:|ID PAZIENTE|Centro Medico|per la Diagnosi|Direttore)\b',
        r'\b(Via\s+\w+|Tel\.|www\.|\.it)\b',
        r'\b(Ecocolordopplergrafia|L\'esame eseguito|ha evidenziato)\b',
        r'\b(Circolo venoso|profondo|superficiale)\b',
        r'^\s*\d{1,2}:\s*\d{1,2}\s*$',  # Time patterns
        r'^\s*\d{1,2}/\d{1,2}/\d{4}\s*$',  # Date patterns
        r'^\s*\d+\s*$'  # Pure numbers without context
    ]
    
    # Process lines sequentially for multi-line format
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty or excluded lines
        if (len(line) < 2 or 
            any(re.search(pattern, line, re.IGNORECASE) for pattern in exclude_patterns)):
            i += 1
            continue
        
        # Check if current line is a test name
        test_name = None
        for known_test in known_tests:
            if line.upper() == known_test.upper() or line.strip() == known_test:
                test_name = known_test
                break
        
        # Also check for test names that start the line
        if not test_name:
            for known_test in known_tests:
                if line.upper().startswith(known_test.upper() + ' ') or line.upper().startswith(known_test.upper() + '\t'):
                    test_name = known_test
                    # Extract value from same line if present
                    remaining = line[len(known_test):].strip()
                    if remaining:
                        # Process as single-line format
                        pass
                    break
        
        if test_name:
            # Look for value on next lines (multi-line format)
            value = None
            unit = None
            reference = None
            abnormal = False
            
            # Check next 4 lines for value, unit, reference
            for offset in range(1, min(5, len(lines) - i)):
                next_line = lines[i + offset].strip()
                
                if not next_line:
                    continue
                
                # Stop if we hit another test name
                if any(next_line.upper() == test.upper() for test in known_tests):
                    break
                
                # Extract value if not found yet
                if value is None:
                    # Check for numeric value with possible abnormal flag
                    numeric_match = re.search(r'([0-9]+[.,]?[0-9]*)\s*(\*?)', next_line)
                    if numeric_match:
                        value = numeric_match.group(1)
                        if numeric_match.group(2) == '*':
                            abnormal = True
                    # Check for qualitative values
                    elif any(qual in next_line.upper() for qual in [
                        'ASSENTE', 'ASSENTI', 'NEGATIVO', 'POSITIVO', 'GIALLO', 'PAGLIERINO',
                        'VELATO', 'LIMPIDO', 'TORBIDO'
                    ]):
                        value = next_line
                        abnormal = '*' in next_line
                
                # Extract unit if it looks like one
                elif not unit and len(next_line) < 15 and any(u in next_line for u in [
                    'mg/dl', 'g/dl', 'EU/dl', 'Leu/ul', 'mm3', '/mm3', '%', 'ng/ml', 'mU/ml'
                ]):
                    unit = next_line
                
                # Extract reference range
                elif not reference and ('-' in next_line or next_line.upper() in ['ASSENTE', 'ASSENTI']):
                    reference = next_line
            
            # Store if we found a value
            if value:
                # Apply clinical significance logic
                abnormal = apply_clinical_significance(test_name, value, unit or '', reference or '', abnormal)
                
                lab_values[test_name] = {
                    'value': value,
                    'unit': unit or '',
                    'reference': reference or '',
                    'abnormal': abnormal,
                    'type': 'multiline',
                    'category': determine_test_category(test_name),
                    'line_number': i + 1
                }
                logger.debug(f"Extracted multiline lab value: {test_name} = {value}")
        
        i += 1
    
    # Also try single-line patterns for blood chemistry
    single_line_patterns = [
        # Italian format: Proteine: 15 * mg/dl (0 - 10)
        r'^([A-Za-z\s]+):\s+([0-9]+[.,]?[0-9]*|\w+)\s*(\*?)\s*([a-zA-Z%/]+)?\s*(?:\(([^)]+)\))?',
        
        # Common hematology format: TEST VALUE UNIT
        r'^(WBC|RBC|HGB|HCT|MCV|MCH|MCHC|RDW|PLT|MPV|NEU|LYN|MON|EOS|BAS)\s+([0-9]+[.,]?[0-9]*)\s*(\*?)\s*([^\s]+)?',
        
        # Chemistry with reference ranges: TEST VALUE UNIT REFERENCE  
        r'^([A-Z][A-Za-z\s/]{2,25}?)\s+([0-9]+[.,]?[0-9]*)\s*(\*?)\s*([a-zA-Z%/]+)?\s+([0-9]+[.,]?[0-9]*\s*[-–]\s*[0-9]+[.,]?[0-9]*)',
        
        # Simple test value format
        r'^([A-Z]{3,})\s+([0-9]+[.,]?[0-9]*)\s*(\*?)'
    ]
    
    for line_num, line in enumerate(lines):
        line = line.strip()
        
        # Skip if already processed or invalid
        if (len(line) < 5 or 
            any(re.search(pattern, line, re.IGNORECASE) for pattern in exclude_patterns)):
            continue
        
        for pattern in single_line_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                groups = match.groups()
                test_name = groups[0].strip()
                value = groups[1].strip()
                abnormal_flag = groups[2] if len(groups) > 2 else ""
                unit = groups[3] if len(groups) > 3 and groups[3] else ""
                reference = groups[4] if len(groups) > 4 and groups[4] else ""
                
                # For Italian format with colon, clean up test name
                if ':' in test_name:
                    test_name = test_name.replace(':', '').strip()
                
                # Skip if already extracted or invalid name
                if (test_name in lab_values or 
                    len(test_name) < 2 or 
                    test_name.isdigit()):
                    continue
                
                # Skip administrative/demographic fields that aren't lab tests
                admin_fields = [
                    'DATA', 'NOME', 'ETA', 'PAZIENTE', 'CODICE', 'ID',
                    'VIA', 'TEL', 'TELEFONO', 'EMAIL', 'CENTRO', 'AMBULATORIO',
                    'MEDICO', 'DOTTORE', 'SPECIALISTA', 'OSPEDALE', 'CLINICA',
                    'REPARTO', 'SERVIZIO', 'DIAGNOSI', 'CONCLUSIONI'
                ]
                
                if test_name.upper() in admin_fields:
                    continue
                
                # For non-numeric values, ensure they look like medical test results
                if not re.match(r'^[0-9]+[.,]?[0-9]*$', value):
                    # Allow specific qualitative medical values
                    valid_qualitative = [
                        'ASSENTE', 'ASSENTI', 'NEGATIVO', 'POSITIVO', 'GIALLO', 'PAGLIERINO',
                        'VELATO', 'LIMPIDO', 'TORBIDO', 'PRESENTE', 'PRESENTI', 'NORMALE',
                        'ALTERATO', 'ALTO', 'BASSO'
                    ]
                    if not any(qual in value.upper() for qual in valid_qualitative):
                        continue
                
                abnormal = '*' in abnormal_flag or '*' in line
                
                # Apply clinical significance logic for common tests
                abnormal = apply_clinical_significance(test_name, value, unit, reference, abnormal)
                
                lab_values[test_name] = {
                    'value': value,
                    'unit': unit,
                    'reference': reference,
                    'abnormal': abnormal,
                    'type': 'single_line',
                    'category': determine_test_category(test_name),
                    'line_number': line_num + 1
                }
                logger.debug(f"Extracted single-line lab value: {test_name} = {value}")
                break
    
    logger.info(f"Extracted {len(lab_values)} laboratory values")
    return lab_values

def determine_test_category(test_name: str) -> str:
    """Determine the category of a laboratory test based on its name."""
    test_upper = test_name.upper()
    
    # Hematology/Blood count tests
    if any(term in test_upper for term in [
        'WBC', 'RBC', 'HGB', 'HCT', 'PLT', 'NEU', 'LYN', 'MON', 'EOS', 'BAS',
        'MCV', 'MCH', 'MCHC', 'RDW', 'MPV',
        'NEUTROFILI', 'LINFOCITI', 'MONOCITI', 'EOSINOFILI', 'BASOFILI',
        'GLOBULI', 'EMOGLOBINA', 'EMATOCRITO', 'PIASTRINE', 'LEUCOCIT',
        'FORMULA LEUCOCITARIA', 'EMOCROMOCITOMETRICO'
    ]):
        return 'hematology'
    
    # Coagulation tests
    elif any(term in test_upper for term in [
        'PROTROMBINICA', 'INR', 'PTT', 'RATIO', 'FIBRINOGENO', 'COAGULAZIONE'
    ]):
        return 'coagulation'
    
    # Urinalysis tests
    elif any(term in test_upper for term in [
        'COLORE', 'ASPETTO', 'PH', 'PESO SPECIFICO', 'LIMPIDEZZA', 'DENSITA',
        'PROTEINE URINE', 'GLUCOSIO URINE', 'SANGUE URINE', 'LEUCOCITI URINE',
        'NITRITI', 'ESTERASI', 'CILINDRI', 'ERITROCITI URINE', 'BATTERI URINE',
        'CELLULE EPITELIALI', 'CORPI CHETONICI', 'UROBILINOGENO', 'SEDIMENTO'
    ]) or (any(term in test_upper for term in ['PROTEINE', 'EMOGLOBINA', 'GLUCOSIO']) and 
           'URINE' in test_upper.replace('_', ' ')):
        return 'urinalysis'
    
    # Chemistry/Biochemistry tests (default for most blood tests)
    else:
        return 'chemistry'

def extract_exam_dates(text: str) -> dict:
    """
    Extract various dates from Italian medical reports.
    Returns a dictionary with different types of dates found.
    """
    dates = {}
    
    # Enhanced date patterns for Italian medical reports
    date_patterns = {
        'exam_date': [
            r"(?:Data esame|Data del esame)[\s:.-]*([0-9]{1,2}[/.-][0-9]{1,2}[/.-][0-9]{2,4})",
            r"(?:Eseguito il|Effettuato il)[\s:.-]*([0-9]{1,2}[/.-][0-9]{1,2}[/.-][0-9]{2,4})",
            r"(?:Prelievo|Prelievo del|Prelievo effettuato il)[\s:.-]*([0-9]{1,2}[/.-][0-9]{1,2}[/.-][0-9]{2,4})"
        ],
        'report_date': [
            r"(?:Refertato il|Refertazione)[\s:.-]*([0-9]{1,2}[/.-][0-9]{1,2}[/.-][0-9]{2,4})",
            r"(?:Data referto|Data del referto)[\s:.-]*([0-9]{1,2}[/.-][0-9]{1,2}[/.-][0-9]{2,4})"
        ],
        'acceptance_date': [
            r"(?:Accettato il|Accettazione)[\s:.-]*([0-9]{1,2}[/.-][0-9]{1,2}[/.-][0-9]{2,4})",
            r"(?:Ricevuto il|Data accettazione)[\s:.-]*([0-9]{1,2}[/.-][0-9]{1,2}[/.-][0-9]{2,4})"
        ]
    }
    
    for date_type, patterns in date_patterns.items():
        for pattern in patterns:
            match = re.search(pattern, text, re.I)
            if match:
                date_str = match.group(1)
                # Normalize date format
                normalized_date = re.sub(r'[.-]', '/', date_str)
                dates[date_type] = normalized_date
                logger.info(f"Found {date_type}: {normalized_date}")
                break  # Use first match for each date type
    
    return dates

def classify_report_type(text: str, exam_title: str = None) -> str:
    """
    Classify medical reports into three main categories:
    - laboratory: structured lab tests with name-value pairs
    - radiology: imaging-based descriptive reports 
    - pathology: tissue/cell analysis descriptive reports
    """
    text_upper = text.upper()
    title_upper = (exam_title or "").upper()
    
    # Laboratory report indicators (structured data with values)
    laboratory_keywords = [
        # Common lab test names
        "GLUCOSIO", "CREATININA", "UREA", "SODIO", "POTASSIO", "CALCIO",
        "EMOGLOBINA", "EMATOCRITO", "GLOBULI", "LEUCOCITI", "PIASTRINE",
        "WBC", "RBC", "HGB", "HCT", "PLT", "MCV", "MCH", "MCHC",
        "GOT", "GPT", "AST", "ALT", "BILIRUBINA", "ALBUMINA",
        "PROTEINE URINE", "SEDIMENTO", "ESTERASI", "NITRITI",
        "INR", "PTT", "PROTROMBINICA", "COAGULAZIONE",
        # Lab report headers
        "ESAME EMOCROMOCITOMETRICO", "CHIMICA CLINICA", "BIOCHIMICA",
        "ESAME CHIMICO FISICO", "FORMULA LEUCOCITARIA", "COAGULAZIONE",
        "SIEROLOGIA", "IMMUNOLOGIA", "ORMONI", "MARCATORI TUMORALI"
    ]
    
    # Radiology report indicators (imaging studies)
    radiology_keywords = [
        # Imaging modalities
        "RADIOGRAFIA", "ECOGRAFIA", "ECOCOLORDOPPLERGRAFIA", "DOPPLER",
        "TAC", "TC", "RISONANZA MAGNETICA", "RM", "RMN", 
        "MAMMOGRAFIA", "DENSITOMETRIA", "SCINTIGRAFIA",
        # Imaging-specific terms
        "REFERTO RADIOLOGICO", "REFERTO DI RADIOLOGIA", "IMAGING",
        "CONTRASTO", "MDC", "MEZZO DI CONTRASTO",
        # Anatomical regions commonly imaged
        "TORACE", "ADDOME", "PELVI", "CRANIO", "ENCEFALO",
        "ARTI INFERIORI", "ARTI SUPERIORI", "TRONCHI SOVRAORTICI",
        # Imaging findings terminology
        "OPACITÀ", "ADDENSAMENTO", "VERSAMENTO", "MASSA", "NODULO",
        "STENOSI", "DILATAZIONE", "ISPESSIMENTO", "CALCIFICAZIONE"
    ]
    
    # Pathology report indicators (tissue/cellular analysis)
    pathology_keywords = [
        # Pathology procedures
        "ESAME ISTOLOGICO", "ESAME CITOLOGICO", "ESAME ANATOMO",
        "BIOPSIA", "AGOBIOPSIA", "PAP TEST", "CITOLOGIA",
        # Pathology staining and techniques
        "EMATOSSILINA", "H&E", "HE", "IMMUNOISTOCHIMICA",
        "COLORAZIONE", "PREPARATO ISTOLOGICO", "SEZIONI ISTOLOGICHE",
        # Pathology findings
        "DISPLASIA", "METAPLASIA", "NEOPLASIA", "CARCINOMA", "ADENOMA",
        "IPERPLASIA", "ATROFIA", "INFIAMMAZIONE CRONICA", "FIBROSI",
        # Pathology report headers
        "ANATOMIA PATOLOGICA", "REFERTO ISTOLOGICO", "REFERTO CITOLOGICO",
        "DIAGNOSI ISTOLOGICA", "DIAGNOSI CITOLOGICA", "REFERTO ANATOMO"
    ]
    
    # Count keyword matches for each category
    lab_score = sum(1 for keyword in laboratory_keywords if keyword in text_upper or keyword in title_upper)
    radiology_score = sum(1 for keyword in radiology_keywords if keyword in text_upper or keyword in title_upper)  
    pathology_score = sum(1 for keyword in pathology_keywords if keyword in text_upper or keyword in title_upper)
    
    # Look for structured laboratory data patterns (strong indicator)
    lab_value_patterns = [
        r'\b[A-Z][A-Z\s]+\s*[:=]\s*[0-9]+[.,]?[0-9]*\s*[a-zA-Z/%]*',  # TEST: 123 mg/dl
        r'\b[A-Z]{2,}\s*[0-9]+[.,]?[0-9]*\s*[a-zA-Z/%]*',  # HGB 12.5 g/dl
        r'[0-9]+[.,]?[0-9]*\s*[-–]\s*[0-9]+[.,]?[0-9]*',  # Reference ranges
    ]
    
    structured_data_count = 0
    for pattern in lab_value_patterns:
        matches = re.findall(pattern, text)
        structured_data_count += len(matches)
    
    # Boost laboratory score if structured data is found
    if structured_data_count >= 3:
        lab_score += 5
        logger.info(f"Found {structured_data_count} structured lab value patterns")
    
    logger.info(f"Report classification scores - Lab: {lab_score}, Radiology: {radiology_score}, Pathology: {pathology_score}")
    
    # Determine classification based on highest score with minimum threshold
    if lab_score >= 2 and lab_score >= radiology_score and lab_score >= pathology_score:
        return "laboratory"
    elif radiology_score >= 2 and radiology_score >= pathology_score:
        return "radiology"
    elif pathology_score >= 2:
        return "pathology"
    else:
        # Default classification logic based on content analysis
        if structured_data_count >= 2:
            return "laboratory"
        elif any(term in text_upper for term in ["ECOGRAFIA", "RADIOGRAFIA", "TAC", "RISONANZA"]):
            return "radiology"
        elif any(term in text_upper for term in ["ISTOLOGICO", "CITOLOGICO", "BIOPSIA"]):
            return "pathology"
        else:
            # Default to laboratory for unclassified reports
            logger.warning("Unable to classify report type, defaulting to laboratory")
            return "laboratory"
