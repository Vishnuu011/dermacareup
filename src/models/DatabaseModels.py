from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column,
    String,
    Integer,
    ForeignKey
)
import uuid
from src.database.base import Base
from datetime import datetime

import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    String,
    Integer,
    ForeignKey,
    DateTime,
    Boolean,
    Float,
    Text
)

from sqlalchemy.orm import relationship
from src.database.base import Base



class OrganizationModel(Base):
    __tablename__ = "organizations"

    org_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    address = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship("UserModel", back_populates="organization")
    patients = relationship("PatientModel", back_populates="organization")
    subscriptions = relationship("SubscriptionsModel", back_populates="organization")
    payments = relationship("PaymentsModel", back_populates="organization")
    scans = relationship("ScanModel", back_populates="organization")
    scan_usage = relationship("ScanUsageModel", back_populates="organization")



class UserModel(Base):
    __tablename__ = "users"

    user_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String, ForeignKey("organizations.org_id"), nullable=False)

    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

    role = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("OrganizationModel", back_populates="users")
    scans = relationship("ScanModel", back_populates="user")




class SubscriptionsModel(Base):
    __tablename__ = "subscriptions"

    subscription_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String, ForeignKey("organizations.org_id"))

    plan_name = Column(String, nullable=False)
    scan_limit = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)

    start_date = Column(DateTime)
    end_date = Column(DateTime)

    status = Column(String)

    organization = relationship("OrganizationModel", back_populates="subscriptions")
    payments = relationship("PaymentsModel", back_populates="subscription")
    scan_usage = relationship("ScanUsageModel", back_populates="subscription")




class PaymentsModel(Base):
    __tablename__ = "payments"

    payment_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    organization_id = Column(String, ForeignKey("organizations.org_id"))
    subscription_id = Column(String, ForeignKey("subscriptions.subscription_id"))

    stripe_payment_id = Column(String)

    amount = Column(Integer)
    currency = Column(String)

    payment_status = Column(String)

    payment_date = Column(DateTime, default=datetime.utcnow)

    organization = relationship("OrganizationModel", back_populates="payments")
    subscription = relationship("SubscriptionsModel", back_populates="payments")




class PatientModel(Base):
    __tablename__ = "patients"

    patient_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String, ForeignKey("organizations.org_id"))

    name = Column(String)
    gender = Column(String)
    age = Column(Integer)

    email = Column(String)
    phone = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("OrganizationModel", back_populates="patients")
    scans = relationship("ScanModel", back_populates="patient")




class ScanModel(Base):
    __tablename__ = "scans"

    scan_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    organization_id = Column(String, ForeignKey("organizations.org_id"))
    patient_id = Column(String, ForeignKey("patients.patient_id"))
    user_id = Column(String, ForeignKey("users.user_id"))

    image_url = Column(String)
    scan_status = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("OrganizationModel", back_populates="scans")
    patient = relationship("PatientModel", back_populates="scans")
    user = relationship("UserModel", back_populates="scans")

    detections = relationship("DetectionModel", back_populates="scan")
    report = relationship("ReportModel", back_populates="scan", uselist=False)




class DetectionModel(Base):
    __tablename__ = "detections"

    detection_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    scan_id = Column(String, ForeignKey("scans.scan_id"))

    disease_name = Column(String)
    confidence_score = Column(Float)
    severity = Column(String)

    bounding_box = Column(Text)

    scan = relationship("ScanModel", back_populates="detections")
    recommendations = relationship("RecommendationModel", back_populates="detection")




class RecommendationModel(Base):
    __tablename__ = "recommendations"

    recommendation_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    detection_id = Column(String, ForeignKey("detections.detection_id"))

    recommendation_text = Column(Text)
    medication = Column(Text)
    precautions = Column(Text)

    detection = relationship("DetectionModel", back_populates="recommendations")



class ReportModel(Base):
    __tablename__ = "reports"

    report_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    scan_id = Column(String, ForeignKey("scans.scan_id"))
    patient_id = Column(String, ForeignKey("patients.patient_id"))

    report_url = Column(String)

    generated_at = Column(DateTime, default=datetime.utcnow)

    email_sent = Column(Boolean, default=False)

    scan = relationship("ScanModel", back_populates="report")




class ScanUsageModel(Base):
    __tablename__ = "scan_usage"

    usage_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    organization_id = Column(String, ForeignKey("organizations.org_id"))
    subscription_id = Column(String, ForeignKey("subscriptions.subscription_id"))

    scans_used = Column(Integer)
    scans_remaining = Column(Integer)

    month = Column(Integer)
    year = Column(Integer)

    organization = relationship("OrganizationModel", back_populates="scan_usage")
    subscription = relationship("SubscriptionsModel", back_populates="scan_usage")