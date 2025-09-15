# backend/core/comparator.py
#
# Confronta l'ultimo referto salvato con quello nuovo usando MedGemma
# e restituisce { "status": ..., "explanation": ... }

import json, os
import ollama
from backend.db import crud

MODEL_NAME = os.getenv("OLLAMA_MODEL", "alibayram/medgemma")

def compare_with_previous_reports(db, patient_cf: str, report_type: str, new_text: str) -> dict:
    """
    Cerca l'ultimo referto dello stesso paziente (CF) e dello stesso tipo,
    poi chiede a MedGemma di dire se il caso è peggiorato / migliorato / invariato.
    Se non trova un referto precedente → status = 'nessun confronto disponibile'.
    """

    previous = crud.get_most_recent_report_text_by_cf(db, patient_cf, report_type)

    if not previous:
        return {
            "status": "nessun confronto disponibile",
            "explanation": "Non esiste un referto precedente di questo tipo per il paziente."
        }

    prompt = f"""
Sei un assistente clinico esperto. Hai due referti medici in italiano dello stesso paziente:

• Referto precedente:
\"\"\"{previous}\"\"\"

• Referto attuale:
\"\"\"{new_text}\"\"\"

Confrontali e indica se la situazione clinica è:
- "peggiorata"
- "migliorata"
- "invariata"

Rispondi ESCLUSIVAMENTE in JSON nel seguente formato:
{{
  "status": "peggiorata | migliorata | invariata",
  "explanation": "Breve spiegazione delle principali differenze cliniche"
}}
"""

    try:
        llm_resp = ollama.generate(model=MODEL_NAME, prompt=prompt)
        content  = llm_resp["response"].strip()

        # tenta di parse-are il JSON restituito
        parsed = json.loads(content)

        return {
            "status": parsed.get("status", "non determinato"),
            "explanation": parsed.get("explanation", "Spiegazione non fornita dall'AI.")
        }

    except Exception as exc:
        return {
            "status": "errore",
            "explanation": f"Errore durante il confronto o parsing: {exc}"
        }
