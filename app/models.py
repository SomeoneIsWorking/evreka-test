from sqlalchemy import Column, Integer, Float, DateTime, String
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class LocationData(Base):
    __tablename__ = "location_data"
    
    id = Column(Integer, primary_key=True)
    device_id = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    speed = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
