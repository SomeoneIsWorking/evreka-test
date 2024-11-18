
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import pika
import json
import logging
from models import Base, LocationData

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
SQLALCHEMY_DATABASE_URL = "postgresql://user:password@db:5432/locationdb"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)

def callback(ch, method, properties, body):
    data = json.loads(body)
    db = SessionLocal()
    location_data = LocationData(
        device_id=data['device_id'],
        latitude=data['latitude'],
        longitude=data['longitude'],
        speed=data['speed'],
        timestamp=datetime.now()
    )
    try:
        db.add(location_data)
        db.commit()
        logger.info(f"Stored location data for device {data['device_id']}")
    except Exception as e:
        logger.error(f"Error storing location data: {str(e)}")
    finally:
        db.close()

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()
    channel.queue_declare(queue='location_data')

    channel.basic_consume(
        queue='location_data',
        on_message_callback=callback,
        auto_ack=True
    )
    
    logger.info("Consumer started. Waiting for messages...")
    channel.start_consuming()

if __name__ == "__main__":
    main()