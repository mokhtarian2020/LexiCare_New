# tests/test_feedback.py

from uuid import uuid4
import pytest
from sqlalchemy.orm import Session
from backend.db import crud, models

def test_submit_feedback(client, db_session: Session):
    # First create a test report
    test_cf = "RSSMRA80A01H501U"  # Codice fiscale di esempio
    report = crud.create_report(
        db=db_session,
        patient_cf=test_cf,
        patient_name="Mario Rossi",
        report_type="radiologia",
        report_date="2025-07-30",
        file_path="/test/path.pdf",
        extracted_text="Referto di test per feedback",
        ai_diagnosis="Diagnosi di test",
        ai_classification="moderato"
    )
    
    # Submit feedback for this report
    feedback_data = {
        "report_id": str(report.id),
        "diagnosi_corretta": "Diagnosi corretta dal medico",
        "classificazione_corretta": "lieve",
        "commento": "Commento di test dal medico"
    }
    
    # Test API
    response = client.post("/api/feedback/", json=feedback_data)
    assert response.status_code == 200
    assert "messaggio" in response.json()
    
    # Verify that the database was updated
    db_session.refresh(report)
    assert report.doctor_diagnosis == "Diagnosi corretta dal medico"
    assert report.doctor_classification == "lieve"
    assert report.doctor_comment == "Commento di test dal medico"

def test_submit_feedback_invalid_report(client):
    # Submit feedback for a non-existent report
    feedback_data = {
        "report_id": str(uuid4()),  # Random non-existent UUID
        "diagnosi_corretta": "Diagnosi corretta",
        "classificazione_corretta": "grave"
    }
    
    # Should get a 404 error
    response = client.post("/api/feedback/", json=feedback_data)
    assert response.status_code == 404
    assert "detail" in response.json()
