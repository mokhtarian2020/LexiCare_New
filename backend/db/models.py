import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Enum per il tipo di referto
class ReportTypeEnum(str, enum.Enum):
    radiologia = "radiologia"
    laboratorio = "laboratorio"
    patologia = "patologia"

# Tabella dei referti
class Report(Base):
    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), nullable=False)
    patient_cf   = Column(String(16),    nullable=True)
    patient_name = Column(String, nullable=True)  # ✅ NEW FIELD

    report_type = Column(Enum(ReportTypeEnum), nullable=False)
    report_date = Column(DateTime, nullable=False)

    file_path = Column(Text, nullable=False)
    extracted_text = Column(Text, nullable=False)

    ai_diagnosis = Column(Text, nullable=False)
    ai_classification = Column(String, nullable=False)

    doctor_diagnosis = Column(Text, nullable=True)
    doctor_classification = Column(String, nullable=True)
    doctor_comment = Column(Text, nullable=True)

    comparison_to_previous = Column(String, nullable=True)
    comparison_explanation = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
