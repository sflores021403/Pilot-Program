from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

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
def get_equipment():
    return equipment_list

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
