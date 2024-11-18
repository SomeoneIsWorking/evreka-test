from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import pika
import json
from models import Base, LocationData
from pydantic import BaseModel

app = FastAPI()

# Database setup
SQLALCHEMY_DATABASE_URL = "postgresql://user:password@db:5432/locationdb"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)

# RabbitMQ setup
connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
channel = connection.channel()
channel.queue_declare(queue='location_data')

class LocationRequest(BaseModel):
    device_id: str
    latitude: float
    longitude: float
    speed: float

@app.post("/location/")
async def create_location(location: LocationRequest):
    channel.basic_publish(
        exchange='',
        routing_key='location_data',
        body=json.dumps(location.dict())
    )
    return {"status": "queued"}

@app.get("/location/{device_id}/latest")
def get_latest_location(device_id: str):
    db = SessionLocal()
    location = db.query(LocationData).filter(
        LocationData.device_id == device_id
    ).order_by(LocationData.timestamp.desc()).first()
    db.close()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return location

@app.get("/location/{device_id}/range")
def get_location_range(device_id: str, start_date: str, end_date: str):
    start = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date)
    db = SessionLocal()
    locations = db.query(LocationData).filter(
        LocationData.device_id == device_id,
        LocationData.timestamp.between(start, end)
    ).all()
    db.close()
    return locations
