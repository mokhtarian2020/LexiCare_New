# backend/api/export.py

from fastapi import APIRouter, Response
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from scripts.export_dataset import export_to_jsonl_and_csv


router = APIRouter()

@router.get("/", summary="Esporta dataset annotato")
def export_dataset():
    jsonl_path, csv_path = export_to_jsonl_and_csv()

    return {
        "messaggio": "Esportazione completata.",
        "file_jsonl": jsonl_path,
        "file_csv": csv_path
    }
