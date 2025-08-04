# tests/test_analyze.py

import io
from uuid import uuid4

def test_upload_single_pdf(client):
    # Simulate 1 fake PDF
    pdf_bytes = b"%PDF-1.4 fake content"
    file = ("files", ("test.pdf", io.BytesIO(pdf_bytes), "application/pdf"))

    form_data = {
        "patient_id": str(uuid4()),
        "report_types": "radiologia",
        "report_dates": "2025-07-30T10:00"
    }

    response = client.post("/api/analyze/", files=[file], data=form_data)
    assert response.status_code == 200
    assert "risultati" in response.json()
