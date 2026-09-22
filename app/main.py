from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .database import engine, SessionLocal
from . import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


class Equipment(BaseModel):
    serial_number: str
    type: str
    status: str
    hub: str

equipment_list = [
    {
        "id": 1,
        "serial_number": "220H00192",
        "type": "ISCO GLS Sampler",
        "status": "storage",
        "hub": "St. Louis"
    },
    {
        "id": 2,
        "serial_number": "220H00204",
        "type": "ISCO GLS Sampler",
        "status": "storage",
        "hub": "Knoxville"
    }
]


@app.get("/")
def home():
    return {"message": "Pilot Program system online."}

@app.get("/equipment")
def get_equipment(db: Session = Depends(get_db)):
    equipment = db.query(models.Equipment).all()
    return equipment


@app.get("/equipment")
def get_equipment(equipment_type: str | None = None, db: Session = Depends(get_db)):
    query = db.query(models.Equipment)

    if equipment_type is not None:
        query = query.filter(
            models.Equipment.equipment_type == equipment_type
        )

    return query.all()

@app.post("/equipment")
def add_equipment(equipment: Equipment):
    new_equipment = {
        "id": len(equipment_list) + 1,
        "serial_number": equipment.serial_number,
        "type": equipment.type,
        "status": equipment.status,
        "hub": equipment.hub
    }

    equipment_list.append(new_equipment)

    return new_equipment

@app.put("/equipment/{equipment_id}")
def update_equipment(equipment_id: int, equipment: Equipment):
    for item in equipment_list:
        if item["id"] == equipment_id:
            item["serial_number"] = equipment.serial_number
            item["type"] = equipment.type
            item["status"] = equipment.status
            item["hub"] = equipment.hub

            return item

    return {"error": "Equipment not found"}

@app.delete("/equipment/{equipment_id}")
def delete_equipment(equipment_id: int):
    for item in equipment_list:
        if item["id"] == equipment_id:
            equipment_list.remove(item)
            return {"message": "Equipment deleted"}

    return {"error": "Equipment not found"}
