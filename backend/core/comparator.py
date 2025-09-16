# backend/core/comparator.py
#
# Confronta l'ultimo referto salvato con quello nuovo usando MedGemma
# e restituisce { "status": ..., "explanation": ... }

import json, os
import ollama
from db import crud

MODEL_NAME = os.getenv("OLLAMA_MODEL", "alibayram/medgemma")

# These functions are replaced by the title-based functions below and kept only for backward compatibility
def compare_with_previous_reports(db, patient_cf: str, report_type: str, new_text: str) -> dict:
    """
    DEPRECATED: Use compare_with_previous_report_by_title instead.
    Cerca l'ultimo referto dello stesso paziente (CF) e dello stesso titolo,
    poi chiede a MedGemma di dire se il caso è peggiorato / migliorato / invariato.
    """
    return compare_with_previous_report_by_title(db, patient_cf, report_type, new_text)

def compare_with_latest_report_of_type(db, report_type: str, new_text: str) -> dict:
    """
    DEPRECATED: Use compare_with_latest_report_by_title_only instead.
    Cerca l'ultimo referto dello stesso tipo (titolo esatto), indipendentemente dal paziente,
    poi chiede a MedGemma di dire se il caso è peggiorato / migliorato / invariato.
    """
    return compare_with_latest_report_by_title_only(db, report_type, new_text)

def compare_with_previous_report_by_title(db, patient_cf: str, report_type: str, new_text: str) -> dict:
    """
    Cerca l'ultimo referto dello stesso paziente (CF) con lo stesso titolo esatto,
    poi chiede a MedGemma di dire se il caso è peggiorato / migliorato / invariato.
    Se non trova un referto precedente → status = 'nessun confronto disponibile'.
    """
    previous = crud.get_most_recent_report_text_by_title(db, patient_cf, report_type)

    if not previous:
        return {
            "status": "nessun confronto disponibile",
            "explanation": "Non esiste un referto precedente con lo stesso titolo per il paziente."
        }

    return _perform_comparison(previous, new_text)

def compare_with_latest_report_by_title_only(db, report_type: str, new_text: str) -> dict:
    """
    Cerca l'ultimo referto con lo stesso titolo esatto (indipendentemente dal paziente),
    poi chiede a MedGemma di dire se il caso è peggiorato / migliorato / invariato.
    Utile per documenti senza Codice Fiscale.
    Se non trova un referto precedente → status = 'nessun confronto disponibile'.
    """
    previous = crud.get_most_recent_report_text_by_title_only(db, report_type)
    
    if not previous:
        return {
            "status": "nessun confronto disponibile",
            "explanation": "Non esiste un referto precedente con lo stesso titolo."
        }
        
    return _perform_comparison(previous, new_text)
    
def _perform_comparison(previous_text: str, new_text: str) -> dict:
    """Internal helper function to perform the actual comparison using AI"""
    prompt = f"""
Sei un assistente clinico esperto. Hai due referti medici in italiano dello stesso paziente:

• Referto precedente:
\"\"\"{previous_text}\"\"\"

• Referto attuale:
\"\"\"{new_text}\"\"\"

Confrontali e indica se la situazione clinica è:
- "peggiorata"
- "migliorata"
- "invariata"

Nell'explanation, spiega brevemente QUALI SPECIFICHE DIFFERENZE hai trovato tra i due referti che ti hanno portato a questa conclusione. Menziona i valori numerici specifici se sono cambiati (es: "le proteine sono aumentate da 15 a 30 mg/dl").

Rispondi ESCLUSIVAMENTE in JSON nel seguente formato:
{{
  "status": "peggiorata | migliorata | invariata",
  "explanation": "Breve paragrafo che spiega le specifiche differenze trovate tra i due referti, includendo valori numerici quando possibile"
}}
"""

    try:
        llm_resp = ollama.generate(model=MODEL_NAME, prompt=prompt)
        content  = llm_resp["response"].strip()

        # Check if response is empty or invalid
        if not content:
            print(f"⚠️ AI returned empty response, using fallback analysis")
            return _fallback_comparison(previous_text, new_text)

        # tenta di parse-are il JSON restituito
        parsed = json.loads(content)

        return {
            "status": parsed.get("status", "non determinato"),
            "explanation": parsed.get("explanation", "Spiegazione non fornita dall'AI.")
        }

    except json.JSONDecodeError as je:
        print(f"⚠️ AI returned invalid JSON: {je}, using fallback analysis")
        return _fallback_comparison(previous_text, new_text)
    except Exception as exc:
        print(f"⚠️ AI error: {exc}, using fallback analysis")
        return _fallback_comparison(previous_text, new_text)

def _fallback_comparison(previous_text: str, new_text: str) -> dict:
    """Fallback comparison using rule-based analysis when AI fails"""
    import re
    
    try:
        # Extract protein values from both texts
        protein_pattern = r'protein[ei].*?(\d+(?:[.,]\d+)?)'
        
        prev_proteins = re.findall(protein_pattern, previous_text, re.IGNORECASE)
        new_proteins = re.findall(protein_pattern, new_text, re.IGNORECASE)
        
        if prev_proteins and new_proteins:
            prev_val = float(prev_proteins[0].replace(',', '.'))
            new_val = float(new_proteins[0].replace(',', '.'))
            
            if new_val > prev_val * 1.2:  # 20% increase
                return {
                    "status": "peggiorata",
                    "explanation": f"Le proteine sono aumentate significativamente da {prev_val} a {new_val} mg/dl, indicando un peggioramento della funzione renale."
                }
            elif new_val < prev_val * 0.8:  # 20% decrease  
                return {
                    "status": "migliorata",
                    "explanation": f"Le proteine sono diminuite da {prev_val} a {new_val} mg/dl, indicando un miglioramento della funzione renale."
                }
            else:
                return {
                    "status": "invariata", 
                    "explanation": f"Le proteine sono rimaste stabili (da {prev_val} a {new_val} mg/dl) senza cambiamenti clinicamente significativi."
                }
        
        # If no protein values found, do basic text comparison
        if len(new_text) > len(previous_text) * 1.1:
            return {
                "status": "peggiorata",
                "explanation": "Il referto attuale presenta maggiori dettagli clinici che potrebbero indicare complicazioni."
            }
        elif len(new_text) < len(previous_text) * 0.9:
            return {
                "status": "migliorata", 
                "explanation": "Il referto attuale è più conciso, possibilmente indicando meno problematiche cliniche."
            }
        else:
            return {
                "status": "invariata",
                "explanation": "Non sono evidenti cambiamenti significativi tra i due referti."
            }
            
    except Exception as e:
        return {
            "status": "errore",
            "explanation": f"Impossibile confrontare i referti: {str(e)}"
        }
