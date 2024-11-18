
import pytest
import json
from httpx import AsyncClient
import socket
from datetime import datetime, timedelta
import asyncio

async def test_location_flow():
    # Test data
    location_data = {
        "device_id": "test_device_1",
        "latitude": 41.0082,
        "longitude": 28.9784,
        "speed": 20.5
    }
    
    # Test TCP Server input
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('localhost', 5500))
    sock.send(json.dumps(location_data).encode())
    sock.close()
    
    # Allow some time for message processing
    await asyncio.sleep(1)
    
    # Test API endpoints
    async with AsyncClient(base_url="http://localhost:8000") as client:
        # Test latest location
        response = await client.get(f"/location/{location_data['device_id']}/latest")
        assert response.status_code == 200
        result = response.json()
        assert result["device_id"] == location_data["device_id"]
        assert result["latitude"] == location_data["latitude"]
        
        # Test date range query
        now = datetime.utcnow()
        start_date = (now - timedelta(hours=1)).isoformat()
        end_date = (now + timedelta(hours=1)).isoformat()
        
        response = await client.get(
            f"/location/{location_data['device_id']}/range",
            params={"start_date": start_date, "end_date": end_date}
        )
        assert response.status_code == 200
        results = response.json()
        assert len(results) > 0

@pytest.mark.asyncio
async def test_api_post_location():
    location_data = {
        "device_id": "test_device_2",
        "latitude": 41.0082,
        "longitude": 28.9784,
        "speed": 20.5
    }
    
    async with AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.post("/location/", json=location_data)
        assert response.status_code == 200
        assert response.json()["status"] == "queued"
        
        # Allow some time for message processing
        await asyncio.sleep(1)
        
        # Verify data was stored
        response = await client.get(f"/location/{location_data['device_id']}/latest")
        assert response.status_code == 200
        result = response.json()
        assert result["device_id"] == location_data["device_id"]