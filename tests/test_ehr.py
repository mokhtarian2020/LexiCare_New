import unittest
from fastapi.testclient import TestClient
import json
import os
from uuid import uuid4, UUID
import pytest
from unittest.mock import patch, MagicMock, mock_open

from backend.main import app
from backend.db.models import Report

client = TestClient(app)

# Setting up mock API key for tests
valid_api_key = "test-api-key"
os.environ["API_KEY"] = valid_api_key
headers = {"X-API-Key": valid_api_key}

def test_missing_api_key():
    """Test that endpoints fail without API key."""
    response = client.get("/api/ehr/report-types")
    assert response.status_code == 403
    
def test_invalid_api_key():
    """Test that endpoints fail with invalid API key."""
    response = client.get("/api/ehr/report-types", headers={"X-API-Key": "invalid-key"})
    assert response.status_code == 403

def test_get_report_types():
    """Test getting valid report types."""
    response = client.get("/api/ehr/report-types", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "tipi_referto" in data
    assert len(data["tipi_referto"]) > 0
    assert "radiologia" in data["tipi_referto"]

@pytest.fixture
def mock_patient_report():
    """Create a mock report for testing."""
    return {
        "id": str(uuid4()),
        "patient_cf": "RSSMRA80A01H501U",
        "patient_name": "Mario Rossi",
        "report_type": "radiologia",
        "report_date": "2023-05-15T10:30:00",
        "file_path": "/path/to/file.pdf",
        "extracted_text": "Referto di radiologia per il paziente",
        "ai_diagnosis": "Diagnosi AI",
        "ai_classification": "Normale",
        "comparison_to_previous": "Stabile",
        "comparison_explanation": "Nessun cambiamento significativo",
        "created_at": "2023-05-15T10:30:00"
    }

@pytest.mark.parametrize("report_type", [None, "radiologia", "laboratorio"])
def test_get_patient_reports(monkeypatch, mock_patient_report, report_type):
    """Test retrieving patient reports with different report type filters."""
    
    # Mock the database query response
    def mock_get_reports(*args, **kwargs):
        # Create a mock report object that responds to attribute access
        mock_report = MagicMock()
        for key, value in mock_patient_report.items():
            setattr(mock_report, key, value)
        
        if report_type and report_type != mock_patient_report["report_type"]:
            return []  # Return empty if report type doesn't match
        
        return [mock_report]
    
    monkeypatch.setattr("backend.db.crud.get_patient_reports", mock_get_reports)
    
    # Build query parameters
    query_params = ""
    if report_type:
        query_params = f"?report_type={report_type}"
    
    # Make the request
    response = client.get(f"/api/ehr/patients/{mock_patient_report['patient_cf']}/reports{query_params}", 
                          headers=headers)
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    
    if report_type and report_type != mock_patient_report["report_type"]:
        assert len(data) == 0
    else:
        assert len(data) > 0
        assert data[0]["patient_cf"] == mock_patient_report["patient_cf"]
        assert data[0]["report_type"] == mock_patient_report["report_type"]


def test_get_patient_report_detail(monkeypatch, mock_patient_report):
    """Test retrieving detailed report information."""
    
    # Mock the database query response
    def mock_query_filter(*args, **kwargs):
        mock = MagicMock()
        mock_report = MagicMock()
        
        for key, value in mock_patient_report.items():
            setattr(mock_report, key, value)
            
        mock.first.return_value = mock_report
        return mock
    
    # Apply the mock
    monkeypatch.setattr("sqlalchemy.orm.Query.filter", mock_query_filter)
    
    # Make the request
    report_id = mock_patient_report["id"]
    patient_cf = mock_patient_report["patient_cf"]
    
    response = client.get(f"/api/ehr/patients/{patient_cf}/reports/{report_id}", 
                          headers=headers)
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    
    assert data["id"] == report_id
    assert data["patient_cf"] == patient_cf
    assert "extracted_text" in data
    assert data["extracted_text"] == mock_patient_report["extracted_text"]


@patch("backend.db.crud.save_feedback")
def test_submit_feedback(mock_save_feedback):
    """Test submitting doctor feedback through the EHR API."""
    
    # Setup mock
    mock_save_feedback.return_value = True
    
    # Prepare request data
    feedback_data = {
        "report_id": str(uuid4()),
        "diagnosi_corretta": "Diagnosi corretta dal medico",
        "classificazione_corretta": "Anomalia",
        "commento": "Nota aggiuntiva del medico"
    }
    
    # Make request
    response = client.post("/api/ehr/feedback", 
                          headers=headers,
                          json=feedback_data)
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert "messaggio" in data
    assert "salvato correttamente" in data["messaggio"].lower()
    
    # Verify mock was called correctly
    mock_save_feedback.assert_called_once()
    args, kwargs = mock_save_feedback.call_args
    assert kwargs["report_id"] == UUID(feedback_data["report_id"])
    assert kwargs["correct_diagnosis"] == feedback_data["diagnosi_corretta"]


@patch("backend.db.crud.save_feedback")
def test_submit_feedback_not_found(mock_save_feedback):
    """Test submitting feedback for a non-existent report."""
    
    # Setup mock
    mock_save_feedback.return_value = False
    
    # Prepare request data
    feedback_data = {
        "report_id": str(uuid4()),
        "diagnosi_corretta": "Diagnosi corretta dal medico",
        "classificazione_corretta": "Anomalia",
    }
    
    # Make request
    response = client.post("/api/ehr/feedback", 
                          headers=headers,
                          json=feedback_data)
    
    # Check response
    assert response.status_code == 404
