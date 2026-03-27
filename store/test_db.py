from fastapi.testclient import TestClient
from main import app, processed_agent_data
from database import SessionLocal
from sqlalchemy import select
from datetime import datetime

client = TestClient(app)


def test_create_processed_agent_data():
    db = SessionLocal()
    before = db.execute(select(processed_agent_data)).fetchall()
    before_count = len(before)
    payload = {
        "user_id": 123,
        "data": [
            {
                "road_state": "normal",
                "agent_data": {
                    "user_id": 999, 
                    "accelerometer": {
                        "x": 1.1,
                        "y": 2.2,
                        "z": 3.3
                    },
                    "gps": {
                        "latitude": 50.45,
                        "longitude": 30.52
                    },
                    "timestamp": datetime.now().isoformat()
                }
            }
        ]
    }
    
    response = client.post("/processed_agent_data/", json=payload)

    assert response.status_code == 200

    after = db.execute(select(processed_agent_data)).fetchall()
    after_count = len(after)

    assert after_count == before_count + 1

    db.close()
