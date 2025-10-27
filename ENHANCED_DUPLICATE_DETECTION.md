# Enhanced Duplicate Detection for Medical Reports

## Overview

The enhanced duplicate detection system in LexiCare now supports intelligent recognition of different medical report types and uses specialized patterns for each category.

## Supported Report Types

### 1. 📊 Laboratory Reports (Referti di Laboratorio)
**Detection Keywords:** `urine`, `sangue`, `laboratorio`, `chimico`, `ematochimici`

**Extracted Values:**
- Numerical test results: Proteine, Glucosio, Creatinina, Emoglobina, Urea
- pH values, Colesterolo, Trigliceridi
- Alternative patterns for flexible matching

**Similarity Threshold:** 80% (high precision for numerical data)
**Minimum Values Required:** 3 matching parameters

**Example:**
```
Proteine: 15.0 mg/dl
Glucosio: ASSENTE mg/dl  
Emoglobina: 0,50 mg/dl
pH: 5,5
```

### 2. 🔍 Radiology Reports (Referti Radiologici)
**Detection Keywords:** `radiolog`, `ecografia`, `tac`, `risonanza`, `rx`, `tc`, `rm`

**Extracted Values:**
- Measurements: dimensioni, diametro, spessore
- Findings: normale, alterazioni, versamento, calcificazioni
- Organ-specific findings: fegato, reni, cuore status

**Similarity Threshold:** 70% (balanced for descriptive content)
**Minimum Values Required:** 2 matching findings

**Example:**
```
Fegato: normale dimensioni
Reni: nella norma
Versamento: assente
Dimensioni: 4.5 x 3.2 cm
```

### 3. 🔬 Pathology Reports (Referti di Patologia)
**Detection Keywords:** `biopsia`, `istolog`, `citolog`, `patolog`, `anatomia`

**Extracted Values:**
- Malignancy indicators: maligno, benigno, neoplasia
- Tumor classification: carcinoma, adenocarcinoma, sarcoma
- Grading: grado I-IV, stadio I-IV
- Biomarkers: Ki-67, receptors (ER, PR, HER2)
- Specific findings: margini, necrosi, fibrosi

**Similarity Threshold:** 75% (high precision for diagnostic content)
**Minimum Values Required:** 2 matching diagnostic terms

**Example:**
```
Carcinoma epatocellulare
Grado: II
Ki-67: 15%
Margini: liberi
```

### 4. 📋 Generic Reports
**Detection:** All other report types

**Extracted Values:**
- Dates, basic diagnoses, therapy mentions
- General measurements

**Similarity Threshold:** 60% (lower for varied content)
**Minimum Values Required:** 2 matching elements

## Technical Implementation

### Key Functions

1. **`extract_key_values_from_text(text, report_type)`**
   - Report-type-aware pattern matching
   - Specialized regex patterns for each medical domain
   - Flexible handling of medical terminology variations

2. **`reports_have_identical_values(existing_report, new_text, report_type)`**
   - Context-sensitive similarity calculation
   - Different thresholds based on report type
   - Handles medical measurement variations

3. **`check_duplicate_report(db, meta, extracted_text)`**
   - Query optimization by report type and patient
   - Integrated similarity assessment
   - Error handling and logging

### Duplicate Detection Logic

```python
# Laboratory: 80% similarity, min 3 values
if lab_keywords in report_type:
    similarity_threshold = 0.8
    min_values = 3

# Radiology: 70% similarity, min 2 findings  
elif radiology_keywords in report_type:
    similarity_threshold = 0.7
    min_values = 2

# Pathology: 75% similarity, min 2 diagnostic terms
elif pathology_keywords in report_type:
    similarity_threshold = 0.75
    min_values = 2
```

## Benefits

### 🎯 **Precision by Domain**
- Laboratory: High precision for numerical values
- Radiology: Balanced approach for findings descriptions
- Pathology: Critical accuracy for diagnostic terms

### 🔍 **Medical Context Awareness**
- Recognizes medical terminology variations
- Handles measurement units and ranges
- Adapts to different reporting styles

### ⚖️ **Safety vs. Usability**
- Prevents duplicate storage while maintaining analysis access
- Reduces false positives through specialized patterns
- Maintains medical accuracy standards

### 📊 **Scalability**
- Easy to add new report types
- Configurable thresholds per domain
- Extensible pattern library

## Usage Example

```python
# The system automatically:
1. Detects report type from title/content
2. Applies appropriate extraction patterns  
3. Uses domain-specific similarity thresholds
4. Returns duplicate status with analysis
```

## Future Enhancements

- **Machine Learning Integration:** Train models on medical report patterns
- **Cross-Language Support:** Multi-language medical terminology
- **Temporal Analysis:** Consider report sequences and trends
- **Integration APIs:** Connect with hospital information systems
