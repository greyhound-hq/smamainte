from sqlalchemy.orm import Session
from . import models, schemas
from typing import List, Optional
from datetime import datetime


def create_equipment(db: Session, eq: schemas.EquipmentCreate) -> models.Equipment:
    obj = models.Equipment(**eq.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get_equipments(db: Session, limit: int = 100) -> List[models.Equipment]:
    return db.query(models.Equipment).order_by(models.Equipment.id.desc()).limit(limit).all()


def get_equipment(db: Session, equipment_id: int) -> Optional[models.Equipment]:
    return db.query(models.Equipment).filter(models.Equipment.id == equipment_id).first()


def update_equipment(db: Session, equipment: models.Equipment, data: dict) -> models.Equipment:
    for k, v in data.items():
        setattr(equipment, k, v)
    db.add(equipment)
    db.commit()
    db.refresh(equipment)
    return equipment


def delete_equipment(db: Session, equipment: models.Equipment):
    db.delete(equipment)
    db.commit()


def create_template(db: Session, tmpl: schemas.CheckTemplateBase) -> models.CheckTemplate:
    obj = models.CheckTemplate(**tmpl.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get_templates_for_type(db: Session, equipment_type: str) -> List[models.CheckTemplate]:
    return db.query(models.CheckTemplate).filter(models.CheckTemplate.equipment_type == equipment_type).order_by(models.CheckTemplate.order_index).all()


def create_inspection(db: Session, rec) -> models.InspectionRecord:
    # rec may be a Pydantic model or a dict. Normalize to dict before creating.
    if hasattr(rec, 'dict'):
        data = rec.dict()
    else:
        data = dict(rec)
    obj = models.InspectionRecord(**data)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get_latest_inspections(db: Session, equipment_id: int, limit: int = 20) -> List[models.InspectionRecord]:
    return db.query(models.InspectionRecord).filter(models.InspectionRecord.equipment_id == equipment_id).order_by(models.InspectionRecord.timestamp.desc()).limit(limit).all()


def dashboard_today_summary(db: Session):
    # Minimal example: counts for today's inspections. For a real app, you'd filter timestamps properly.
    total_today = db.query(models.InspectionRecord).count()
    ng_count = db.query(models.InspectionRecord).filter(models.InspectionRecord.status == "NG").count()
    ok_count = db.query(models.InspectionRecord).filter(models.InspectionRecord.status == "OK").count()
    return {"total_today": total_today, "ok": ok_count, "ng": ng_count}
