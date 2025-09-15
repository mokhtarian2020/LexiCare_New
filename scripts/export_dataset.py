# scripts/export_dataset.py

import os
import json
import csv
from backend.db.session import SessionLocal
from backend.db.crud import get_labeled_reports

EXPORT_FOLDER = "export"
JSONL_PATH = os.path.join(EXPORT_FOLDER, "lexicare_dataset.jsonl")
CSV_PATH = os.path.join(EXPORT_FOLDER, "lexicare_dataset.csv")

def export_to_jsonl_and_csv():
    os.makedirs(EXPORT_FOLDER, exist_ok=True)

    db = SessionLocal()
    reports = get_labeled_reports(db)

    with open(JSONL_PATH, "w", encoding="utf-8") as jsonl_file, \
         open(CSV_PATH, "w", newline="", encoding="utf-8") as csv_file:

        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([
            "report_id",
            "patient_cf",
            "patient_name",
            "report_type",
            "report_date",
            "extracted_text",
            "ai_diagnosis",
            "ai_classification",
            "doctor_diagnosis",
            "doctor_classification",
            "comparison_to_previous",
            "comparison_explanation"
        ])

        for report in reports:
            json_record = {
                "input": report.extracted_text,
                "ai_label": report.ai_classification,
                "correct_label": report.doctor_classification,
                "explanation": report.comparison_explanation
            }
            jsonl_file.write(json.dumps(json_record, ensure_ascii=False) + "\n")

            csv_writer.writerow([
                str(report.id),
                report.patient_cf,
                report.patient_name,
                report.report_type,
                report.report_date.isoformat(),
                report.extracted_text,
                report.ai_diagnosis,
                report.ai_classification,
                report.doctor_diagnosis,
                report.doctor_classification,
                report.comparison_to_previous,
                report.comparison_explanation
            ])

    db.close()
    return JSONL_PATH, CSV_PATH

# Optional CLI entry point
if __name__ == "__main__":
    jsonl, csv = export_to_jsonl_and_csv()
    print(f"Esportazione completata:\n- {jsonl}\n- {csv}")
