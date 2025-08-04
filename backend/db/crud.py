import os
import uuid
from sqlalchemy.orm import Session
from backend.db.models import Report
from datetime import datetime
from typing import Optional, List

# Save PDF to disk
def save_pdf(filename: str, content: bytes) -> str:
    folder = "backend/storage"
    os.makedirs(folder, exist_ok=True)
    file_id = f"{uuid.uuid4()}_{filename}"
    path = os.path.join(folder, file_id)
    with open(path, "wb") as f:
        f.write(content)
    return path

# Insert report into DB
def create_report(
    db, *,
    patient_id, patient_cf, patient_name,
    report_type, report_date,
    file_path, extracted_text,
    ai_diagnosis, ai_classification
):
    report = Report(
        patient_id   = patient_id,
        patient_cf   = patient_cf,          # ✅
        patient_name = patient_name,
        report_type  = report_type,
        report_date  = report_date,
        file_path    = file_path,
        extracted_text = extracted_text,
        ai_diagnosis   = ai_diagnosis,
        ai_classification = ai_classification,
    )
    db.add(report); db.commit(); db.refresh(report)
    return report


# Update report with comparison results
def update_report_comparison(db: Session, report_id, comparison: dict):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        return False
    report.comparison_to_previous = comparison.get("status")
    report.comparison_explanation = comparison.get("explanation")
    db.commit()
    return True

# Retrieve most recent report text for comparison
def get_most_recent_report_text(db: Session, patient_id, report_type):
    latest = (
        db.query(Report)
        .filter(Report.patient_id == patient_id, Report.report_type == report_type)
        .order_by(Report.report_date.desc())
        .first()
    )
    return latest.extracted_text if latest else None

# Save doctor feedback
def save_feedback(db: Session, report_id, correct_diagnosis, correct_classification, comment=None):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        return False
    report.doctor_diagnosis = correct_diagnosis
    report.doctor_classification = correct_classification
    report.doctor_comment = comment
    db.commit()
    return True

# Export all labeled reports for training (with doctor labels)
def get_labeled_reports(db: Session):
    return db.query(Report).filter(Report.doctor_diagnosis.isnot(None)).all()

# Get most recent report by codice fiscale and type
def get_most_recent_report_text_by_cf(db: Session, patient_cf: str, report_type: str):
    latest = (
        db.query(Report)
        .filter(Report.patient_cf == patient_cf, Report.report_type == report_type)
        .order_by(Report.report_date.desc())
        .first()
    )
    return latest.extracted_text if latest else None

# Get all reports for a patient by codice fiscale with optional report type filtering
def get_patient_reports(db: Session, patient_cf: str, report_type: Optional[str] = None) -> List[Report]:
    """Retrieve all reports for a patient by their codice fiscale with optional report type filtering"""
    query = db.query(Report).filter(Report.patient_cf == patient_cf)
    
    if report_type:
        query = query.filter(Report.report_type == report_type)
    
    return query.order_by(Report.report_date.desc()).all()
