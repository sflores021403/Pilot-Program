from fastapi import FastAPI

app = FastAPI()

equipment = [
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
    return equipment
