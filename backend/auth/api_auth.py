# backend/auth/api_auth.py

from fastapi import Security, HTTPException, Depends, status
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN
import os
from dotenv import load_dotenv

load_dotenv()

# Get API key from environment variables or use a default for development
API_KEY = os.getenv("API_KEY", "lexicare-development-key")
API_KEY_NAME = "X-API-Key"

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    """Validate API key for EHR integration endpoints."""
    if api_key_header == API_KEY:
        return api_key_header
    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, 
            detail="Accesso non autorizzato. API key non valida o assente."
        )
