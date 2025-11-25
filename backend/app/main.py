from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import models, schemas, crud
from .db import engine, get_db
from .config import settings
from .qrcode_utils import generate_qr_png_bytes
from .storage import upload_bytes, generate_v4_put_object_signed_url
import io

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="simple-cmms")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.ALLOW_ORIGINS.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


# Equipment APIs
@app.post("/equipments", response_model=schemas.EquipmentOut)
def create_equipment(eq: schemas.EquipmentCreate, db: Session = Depends(get_db)):
    return crud.create_equipment(db, eq)


@app.get("/equipments", response_model=list[schemas.EquipmentOut])
def list_equipments(db: Session = Depends(get_db)):
    return crud.get_equipments(db)


@app.get("/equipments/{equipment_id}", response_model=schemas.EquipmentOut)
def get_equipment(equipment_id: int, db: Session = Depends(get_db)):
    obj = crud.get_equipment(db, equipment_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    return obj


@app.put("/equipments/{equipment_id}", response_model=schemas.EquipmentOut)
def update_equipment(equipment_id: int, payload: dict, db: Session = Depends(get_db)):
    obj = crud.get_equipment(db, equipment_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    return crud.update_equipment(db, obj, payload)


@app.delete("/equipments/{equipment_id}")
def delete_equipment(equipment_id: int, db: Session = Depends(get_db)):
    obj = crud.get_equipment(db, equipment_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Not found")
    crud.delete_equipment(db, obj)
    return {"ok": True}


# QR generation: generate PNG and upload to GCS, set qr_code_url
@app.post("/equipments/{equipment_id}/generate_qr")
def generate_qr(equipment_id: int, db: Session = Depends(get_db)):
    eq = crud.get_equipment(db, equipment_id)
    if not eq:
        raise HTTPException(status_code=404, detail="equipment not found")
    # QR contents: simple URL to mobile scan
    qr_contents = f"/inspect?equipment_id={equipment_id}"
    png = generate_qr_png_bytes(qr_contents)
    blob_name = f"qr/equipment_{equipment_id}.png"
    public_url = upload_bytes(settings.GCS_BUCKET, blob_name, png, content_type="image/png")
    eq.qr_code_url = public_url
    db.add(eq)
    db.commit()
    db.refresh(eq)
    return {"qr_code_url": public_url}


# Check template CRUD
@app.post("/templates", response_model=schemas.CheckTemplateOut)
def create_template(t: schemas.CheckTemplateBase, db: Session = Depends(get_db)):
    return crud.create_template(db, t)


@app.get("/templates/{equipment_type}", response_model=list[schemas.CheckTemplateOut])
def get_templates(equipment_type: str, db: Session = Depends(get_db)):
    return crud.get_templates_for_type(db, equipment_type)


# Inspection record
@app.post("/inspections", response_model=schemas.InspectionRecordOut)
def create_inspection(rec: schemas.InspectionRecordCreate, db: Session = Depends(get_db)):
    return crud.create_inspection(db, rec)


@app.get("/inspections/{equipment_id}", response_model=list[schemas.InspectionRecordOut])
def get_inspections(equipment_id: int, db: Session = Depends(get_db)):
    return crud.get_latest_inspections(db, equipment_id)


@app.get('/inspections')
def list_inspections(db: Session = Depends(get_db)):
    return db.query(models.InspectionRecord).order_by(models.InspectionRecord.timestamp.desc()).limit(1000).all()



# Upload: return signed URL for direct client upload (expects JSON {"filename":"..."})
class UploadRequest(BaseModel):
    filename: str


@app.post("/upload-url")
def create_upload_url(req: UploadRequest):
    blob_name = f"uploads/{req.filename}"
    url = generate_v4_put_object_signed_url(settings.GCS_BUCKET, blob_name)
    public_url = f"https://storage.googleapis.com/{settings.GCS_BUCKET}/{blob_name}"
    return {"upload_url": url, "public_url": public_url}


# Dashboard (light)
@app.get("/dashboard/light")
def dashboard_light(db: Session = Depends(get_db)):
    summary = crud.dashboard_today_summary(db)
    # For each equipment, find latest status
    equipments = db.query(models.Equipment).all()
    latest = []
    for e in equipments:
        rec = db.query(models.InspectionRecord).filter(models.InspectionRecord.equipment_id == e.id).order_by(models.InspectionRecord.timestamp.desc()).first()
        status = rec.status if rec else "未点検"
        latest.append({"equipment_id": e.id, "name": e.name, "status": status})
    return {"kpi": {"today_total": summary["total_today"], "ok": summary["ok"], "ng": summary["ng"]}, "latest_status": latest}


@app.get('/dashboard')
def dashboard_alias(db: Session = Depends(get_db)):
    return dashboard_light(db)
