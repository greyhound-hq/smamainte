from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime


class EquipmentBase(BaseModel):
    name: str
    model: Optional[str] = None
    location: Optional[str] = None
    photo_url: Optional[str] = None


class EquipmentCreate(EquipmentBase):
    pass


class EquipmentOut(EquipmentBase):
    id: int
    qr_code_url: Optional[str] = None
    created_at: Optional[datetime]

    class Config:
        orm_mode = True


class CheckTemplateBase(BaseModel):
    equipment_type: str
    item_name: str
    item_type: str  # ok_ng / numeric
    order_index: int = 0


class CheckTemplateOut(CheckTemplateBase):
    id: int

    class Config:
        orm_mode = True


class InspectionRecordCreate(BaseModel):
    equipment_id: int
    template_item_id: Optional[int]
    status: Optional[str]
    numeric_value: Optional[float]
    photo_url: Optional[str]
    comment: Optional[str]
    reported_by: Optional[str]


class InspectionRecordOut(InspectionRecordCreate):
    id: int
    timestamp: Optional[datetime]
    reported_by: Optional[str]

    class Config:
        orm_mode = True


class UserOut(BaseModel):
    id: int
    email: str
    role: str

    class Config:
        orm_mode = True
