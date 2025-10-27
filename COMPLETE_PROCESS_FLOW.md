# Complete Process Flow: Report Comparison & Duplicate Detection in LexiCare

## 📋 **Overview**
This document explains the complete workflow for processing medical reports, detecting duplicates, and comparing reports in the LexiCare system.

---

## 🔄 **Main Process Flow**

### **Step 1: File Upload & Initial Processing**
```
1. User uploads PDF file(s) → /api/analyze/
2. System reads file bytes
3. Extract metadata using extract_metadata(file_bytes)
   ├── OCR text extraction
   ├── Patient info (CF, name, birth date)
   ├── Report date extraction
   ├── Report type identification
   └── Laboratory values parsing
4. Sort files chronologically by report_date
```

### **Step 2: AI Analysis**
```
5. Determine analysis type:
   ├── Laboratory report → analyze_laboratory_report(meta)
   └── General report → analyze_text_with_medgemma(full_text)
6. Generate AI diagnosis and classification
```

### **Step 3: Codice Fiscale Check**
```
7. Check if Codice Fiscale (CF) exists:
   ├── NO CF → Process without saving
   │   ├── Compare with latest report by title only
   │   └── Return analysis without saving
   └── CF Found → Continue to Step 4
```

### **Step 4: Duplicate Detection Process** ⚡
```
8. DUPLICATE CHECK (NEW ENHANCED SYSTEM):
   ├── Create check_meta = {report_type, codice_fiscale}
   ├── Call check_duplicate_report(db, check_meta, full_text)
   │
   ├── A. Extract key values based on report type:
   │   ├── Laboratory: Proteine, Glucosio, Emoglobina, pH, etc.
   │   ├── Radiology: Organ findings, measurements, anomalies
   │   ├── Pathology: Tumor classification, grading, biomarkers
   │   └── Generic: Basic medical terms, dates
   │
   ├── B. Query existing reports:
   │   └── WHERE report_type = X AND patient_cf = Y
   │
   ├── C. For each existing report:
   │   ├── Extract key values from stored text
   │   ├── Compare using reports_have_identical_values()
   │   ├── Apply domain-specific thresholds:
   │   │   ├── Laboratory: 80% similarity, min 3 values
   │   │   ├── Radiology: 70% similarity, min 2 findings
   │   │   ├── Pathology: 75% similarity, min 2 diagnostic terms
   │   │   └── Generic: 60% similarity, min 2 elements
   │   └── Return duplicate_report, is_duplicate
   │
   └── D. Result:
       ├── IS DUPLICATE → Return existing report data + analysis
       └── NOT DUPLICATE → Continue to Step 5
```

### **Step 5: Report Saving & Comparison**
```
9. Save new report to database:
   ├── Save PDF to disk
   ├── Get previous report BEFORE saving new one
   │   └── previous_text = get_most_recent_report_text_by_title(db, CF, report_type)
   ├── Create new database record
   └── Commit to database

10. COMPARISON PROCESS:
    ├── Check if previous_report_text exists:
    │   ├── YES → Call _perform_comparison(previous_text, new_text)
    │   │   ├── Send both texts to AI (MedGemma)
    │   │   ├── AI analyzes and returns:
    │   │   │   ├── status: "migliorata" | "peggiorata" | "invariata"
    │   │   │   └── explanation: detailed comparison with values
    │   │   └── Fallback if AI fails:
    │   │       ├── Extract protein values using regex
    │   │       ├── Calculate % change
    │   │       └── Generate rule-based comparison
    │   └── NO → Return "nessun confronto disponibile"
    │
    └── Update report with comparison results
```

---

## 🔍 **Detailed Function Breakdown**

### **Duplicate Detection Functions**

#### `extract_key_values_from_text(text, report_type)`
```python
# Analyzes report type and applies appropriate patterns:

if 'urine' or 'laboratorio' in report_type:
    # Extract: Proteine: 15.0 mg/dl → {'Proteine': '15.0'}
    patterns = [r'Proteine.*?([0-9,\.]+).*?mg/dl', ...]

elif 'ecografia' or 'radiolog' in report_type:
    # Extract: Fegato: normale → {'fegato': 'normale'}
    patterns = [r'fegato.*?(normale|ingrandito|ridotto)', ...]

elif 'biopsia' or 'istolog' in report_type:
    # Extract: Grado: II → {'grade': 'II'}
    patterns = [r'grado.*?([I-IV]|[1-4])', ...]
```

#### `reports_have_identical_values(existing_report, new_text, report_type)`
```python
# Compare extracted values with domain-specific logic:

existing_values = extract_key_values_from_text(existing_report.extracted_text, report_type)
new_values = extract_key_values_from_text(new_text, report_type)

# Apply appropriate threshold:
if laboratory: similarity_threshold = 0.8, min_values = 3
elif radiology: similarity_threshold = 0.7, min_values = 2
elif pathology: similarity_threshold = 0.75, min_values = 2

# Calculate matches and determine if duplicate
```

### **Comparison Functions**

#### `_perform_comparison(previous_text, new_text)`
```python
# AI-powered comparison:
prompt = f"""
Hai due referti medici:
• Referto precedente: {previous_text}
• Referto attuale: {new_text}

Confrontali e indica se la situazione è:
- "peggiorata" | "migliorata" | "invariata"
Spiega le differenze specifiche con valori numerici.
"""

# Send to MedGemma AI model
# Parse JSON response: {"status": "...", "explanation": "..."}
# Fallback to rule-based analysis if AI fails
```

#### `_fallback_comparison(previous_text, new_text)`
```python
# Rule-based fallback:
# 1. Extract protein values using regex
# 2. Calculate percentage change
# 3. Determine status based on thresholds:
#    - >20% increase → "peggiorata"
#    - >20% decrease → "migliorata"  
#    - Otherwise → "invariata"
```

---

## 📊 **Response Format**

### **Normal Save (New Report)**
```json
{
  "salvato": true,
  "messaggio": "Referto salvato con successo.",
  "diagnosi_ai": "Proteinuria moderata...",
  "classificazione_ai": "anormale",
  "situazione": "peggiorata",
  "spiegazione": "Le proteine sono aumentate da 15.0 a 45.0 mg/dl...",
  "codice_fiscale": "RSSMRA80A01H501X",
  "tipo_referto": "Esame Chimico Fisico Delle Urine"
}
```

### **Duplicate Detected**
```json
{
  "salvato": false,
  "messaggio": "Errore nel salvataggio: Documento già presente nel database (salvato il 17/10/2025 07:59), ma risultati analisi forniti",
  "status": "duplicate",
  "diagnosi_ai": "Proteinuria moderata...",
  "classificazione_ai": "anormale",
  "original_save_date": "17/10/2025 07:59",
  "situazione": "invariata",
  "spiegazione": "Le proteine sono rimaste stabili..."
}
```

### **No Codice Fiscale (Analysis Only)**
```json
{
  "salvato": false,
  "messaggio": "Codice Fiscale assente – referto analizzato ma NON salvato.",
  "diagnosi_ai": "Proteinuria moderata...",
  "classificazione_ai": "anormale",
  "situazione": "peggiorata",
  "spiegazione": "Confronto con ultimo referto simile..."
}
```

---

## 🎯 **Key Features**

### **Enhanced Duplicate Detection**
- ✅ **Report-type aware**: Different patterns for Laboratory/Radiology/Pathology
- ✅ **Domain-specific thresholds**: Higher precision for critical medical data
- ✅ **Content-based similarity**: Compares actual medical values, not just metadata
- ✅ **Medical terminology handling**: Recognizes variations in medical language

### **Intelligent Comparison**
- ✅ **AI-powered analysis**: Uses MedGemma for sophisticated medical comparison
- ✅ **Chronological accuracy**: Uses report dates, not upload timestamps
- ✅ **Fallback mechanisms**: Rule-based analysis when AI is unavailable
- ✅ **Specific value tracking**: Mentions exact numerical changes

### **User Experience**
- ✅ **Analysis always provided**: Even for duplicates or missing CF
- ✅ **Clear error messages**: Explains why report wasn't saved
- ✅ **Historical context**: Shows when original was saved
- ✅ **Medical accuracy**: Appropriate handling for each report type

---

## 🔧 **Technical Architecture**

```
Frontend Upload → FastAPI Endpoint → PDF Processing → AI Analysis
                                           ↓
                        Duplicate Check ← Database Query
                                           ↓
                    New Report? → Save + Compare with Previous
                                           ↓
                         Update Comparison → Return Results
```

This comprehensive system ensures medical accuracy, prevents duplicate storage, and provides meaningful comparisons across different types of medical reports.
