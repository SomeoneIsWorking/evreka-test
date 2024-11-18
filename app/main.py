from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, LocationData
from pydantic import BaseModel

app = FastAPI()

# Database setup
SQLALCHEMY_DATABASE_URL = "postgresql://user:password@db:5432/locationdb"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)

