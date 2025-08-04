# tests/test_db.py

from backend.db import crud
from uuid import uuid4
from datetime import datetime

def test_create_report(db_session):
    report = crud.create_report(
        db=db_session,
        patient_id=uuid4(),
        report_type="radiologia",
        report_date=datetime.utcnow(),
        file_path="/fake/path/test.pdf",
        extracted_text="Questo è un referto di esempio.",
        ai_diagnosis="Polmonite",
        ai_classification="moderato"
    )
    assert report.id is not None
    assert report.ai_diagnosis == "Polmonite"
