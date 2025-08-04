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

def analyze_text_with_medgemma(report_text: str) -> dict:
    """Invia testo a MedGemma tramite Ollama (Python lib) e restituisce diagnosi e classificazione."""

    prompt = f"""
Referto medico:
\"\"\"
{report_text}
\"\"\"

Fornisci la diagnosi principale e la classificazione del livello di gravità (lieve, moderato, grave). Rispondi solo in questo formato JSON:
{{
    "diagnosis": "...",
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
