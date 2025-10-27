import os
import uuid
from sqlalchemy.orm import Session
from db.models import Report
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
    patient_cf, patient_name,
    report_type, report_date,
    file_path, extracted_text,
    ai_diagnosis, ai_classification
):
    report = Report(
        patient_cf   = patient_cf,
        patient_name = patient_name,
        report_type = report_type,  # Exact title as extracted (e.g., "Eccocardiografia")
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

# Retrieve most recent report text for comparison by patient CF and title
def get_most_recent_report_text(db: Session, patient_cf, report_type):
    latest = (
        db.query(Report)
        .filter(Report.patient_cf == patient_cf, Report.report_type == report_type)
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

# Get most recent report by codice fiscale and title
def get_most_recent_report_text_by_cf_and_title(db: Session, patient_cf: str, report_type: str):
    """Retrieve the most recent report text with the specified title for a patient"""
    latest = (
        db.query(Report)
        .filter(Report.patient_cf == patient_cf, Report.report_type == report_type)
        .order_by(Report.report_date.desc())
        .first()
    )
    return latest.extracted_text if latest else None

# Get all reports for a patient by codice fiscale with optional title filtering
def get_patient_reports(db: Session, patient_cf: str, report_type: Optional[str] = None) -> List[Report]:
    """Retrieve all reports for a patient by their codice fiscale with optional title filtering"""
    query = db.query(Report).filter(Report.patient_cf == patient_cf)
    
    if report_type:
        query = query.filter(Report.report_type == report_type)
    
    return query.order_by(Report.report_date.desc()).all()

# Get the most recent report of a specific title, regardless of patient
def get_most_recent_report_text_by_title_only(db: Session, report_type: str):
    """Retrieve the most recent report text with the specified title, regardless of which patient it belongs to"""
    latest = (
        db.query(Report)
        .filter(Report.report_type == report_type)
        .order_by(Report.report_date.desc())
        .first()
    )
    return latest.extracted_text if latest else None

# Get most recent report by codice fiscale and specific report title (exact match)
def get_most_recent_report_by_title(db: Session, patient_cf: str, report_type: str):
    """Retrieve the most recent report with exact matching report title for a patient"""
    latest = (
        db.query(Report)
        .filter(Report.patient_cf == patient_cf, Report.report_type == report_type)
        .order_by(Report.report_date.desc())
        .first()
    )
    return latest

# Get most recent report text by codice fiscale and specific report title (exact match)
def get_most_recent_report_text_by_title(db: Session, patient_cf: str, report_type: str):
    """
    Retrieve the most recent report text with exact matching report title for a patient.
    Uses created_at timestamp to handle same-day reports correctly since PDFs typically
    don't contain hour information.
    """
    latest = (
        db.query(Report)
        .filter(Report.patient_cf == patient_cf, Report.report_type == report_type)
        .order_by(
            Report.report_date.desc(),    # Sort by medical date first
            Report.created_at.desc(),     # Then by upload time (most recent)
            Report.id.desc()              # Finally by ID as last resort
        )
        .first()
    )
    return latest.extracted_text if latest else None

# Get previous report text for comparison (excluding the current report being processed)
def get_previous_report_text_by_title(db: Session, patient_cf: str, report_type: str, exclude_report_id: int = None):
    """
    Retrieve the most recent previous report text with exact matching report title for a patient,
    excluding the specified report ID (useful when comparing against the current report).
    """
    query = (
        db.query(Report)
        .filter(Report.patient_cf == patient_cf, Report.report_type == report_type)
    )
    
    if exclude_report_id:
        query = query.filter(Report.id != exclude_report_id)
    
    latest = query.order_by(
        Report.report_date.desc(),
        Report.created_at.desc(),
        Report.id.desc()
    ).first()
    
    return latest.extracted_text if latest else None

# Get chronological reports for comparison with dates
def get_chronological_reports_by_title(db: Session, patient_cf: str, report_type: str):
    """
    Retrieve all reports with exact matching report title for a patient, ordered chronologically.
    Returns full report objects with dates for proper chronological comparison.
    """
    reports = (
        db.query(Report)
        .filter(Report.patient_cf == patient_cf, Report.report_type == report_type)
        .order_by(
            Report.report_date.asc(),     # Sort by medical date ascending (oldest first)
            Report.created_at.asc(),      # Then by upload time (oldest first)
            Report.id.asc()               # Finally by ID as last resort
        )
        .all()
    )
    return reports

# Get most recent report of a specific report title, regardless of patient
def get_most_recent_report_text_by_title_only(db: Session, report_type: str):
    """
    Retrieve the most recent report text with exact matching report title, regardless of patient.
    Uses created_at timestamp to handle same-day reports correctly.
    """
    latest = (
        db.query(Report)
        .filter(Report.report_type == report_type)
        .order_by(
            Report.report_date.desc(),    # Sort by medical date first
            Report.created_at.desc(),     # Then by upload time (most recent)
            Report.id.desc()              # Finally by ID as last resort
        )
        .first()
    )
    return latest.extracted_text if latest else None
