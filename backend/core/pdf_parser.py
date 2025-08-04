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
    lines = text.splitlines()
    for l in lines[:15]:
        s = l.strip()
        if (
            len(s) > 5 and s.isupper() and not any(c.isdigit() for c in s)
            and not s.startswith(("AZIENDA", "PAZIENTE", "REFERTO"))
        ):
            return s
    return None

def extract_metadata(file_bytes: bytes) -> dict:
    logger.info("Extracting metadata from PDF")
    
    text, doc = extract_text_from_pdf(file_bytes)
    
    logger.info(f"Successfully extracted {len(text)} chars from document")
    logger.info("Searching for patient information in document")
    # Pattern più robusti per i dati anagrafici
    name_patterns = [
        r"(?:Nome|Paziente)[:\s]*([A-ZÀ-ÿ' ]+)",
        r"(?:Cognome)[:\s]*([A-ZÀ-ÿ' ]+)",
        r"(?:Nome e cognome)[:\s]*([A-ZÀ-ÿ' ]+)"
    ]
    
    date_patterns = [
        r"Data[:\s]*([0-9]{1,2}[/.-][0-9]{1,2}[/.-][0-9]{2,4})",
        r"(?:Data esame|Data referto)[:\s]*([0-9]{1,2}[/.-][0-9]{1,2}[/.-][0-9]{2,4})",
        r"(?:[0-9]{1,2}[/.-][0-9]{1,2}[/.-][0-9]{4})"  # Data standalone
    ]
    
    # Cerca nome paziente con i vari pattern
    patient_name = None
    for pattern in name_patterns:
        name = re.search(pattern, text, re.I)
        if name:
            patient_name = name.group(1).title().strip()
            break
    
    # Cerca data con i vari pattern
    report_date = None
    for pattern in date_patterns:
        date = re.search(pattern, text, re.I)
        if date:
            report_date = date.group(1) if hasattr(date, 'group') else date.group(0)
            # Normalizza formato data a DD/MM/YYYY
            report_date = re.sub(r'[.-]', '/', report_date)
            # Correggi anno a 4 cifre se necessario
            if len(report_date.split('/')[-1]) == 2:
                parts = report_date.split('/')
                parts[-1] = "20" + parts[-1]
                report_date = '/'.join(parts)
            break
            
    # Recupera codice fiscale
    try:
        codice_fiscale = find_cf(text, doc)
        logger.info(f"Found CF: {codice_fiscale or 'Not found'}")
    except Exception as e:
        logger.error(f"Error finding CF: {str(e)}")
        codice_fiscale = None
    
    # Get report type
    try:
        report_type = extract_exam_title(text) or "sconosciuto"
    except Exception as e:
        logger.error(f"Error extracting report type: {str(e)}")
        report_type = "sconosciuto"
    
    return {
        "full_text"      : text,
        "patient_name"   : patient_name,
        "codice_fiscale" : codice_fiscale,
        "report_date"    : report_date,
        "report_type"    : report_type,
    }
