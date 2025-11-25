from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Float,
    Text,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class Equipment(Base):
    __tablename__ = "equipments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    model = Column(String(200), nullable=True)
    location = Column(String(200), nullable=True)
    photo_url = Column(String(1000), nullable=True)
    qr_code_url = Column(String(1000), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    inspections = relationship("InspectionRecord", back_populates="equipment")


class CheckTemplate(Base):
    __tablename__ = "check_templates"

    id = Column(Integer, primary_key=True, index=True)
    equipment_type = Column(String(200), nullable=False)
    item_name = Column(String(200), nullable=False)
    item_type = Column(String(50), nullable=False)  # ok_ng / numeric
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class InspectionRecord(Base):
    __tablename__ = "inspection_records"

    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey("equipments.id"), nullable=False)
    template_item_id = Column(Integer, ForeignKey("check_templates.id"), nullable=True)
    status = Column(String(10), nullable=True)  # OK/NG
    numeric_value = Column(Float, nullable=True)
    photo_url = Column(String(1000), nullable=True)
    comment = Column(Text, nullable=True)
    reported_by = Column(String(200), nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    equipment = relationship("Equipment", back_populates="inspections")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(200), nullable=False, unique=True)
    role = Column(String(20), nullable=False, default="worker")
