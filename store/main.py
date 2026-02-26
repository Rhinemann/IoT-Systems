import json
from typing import Set, Dict, List
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Body
from fastapi.encoders import jsonable_encoder
from sqlalchemy import (
    Table,
    Column,
    Integer,
    String,
    Float,
    DateTime,
)
from sqlalchemy.sql import select

from database import metadata, SessionLocal
from schemas import ProcessedAgentData, ProcessedAgentDataInDB

# FastAPI app setup
app = FastAPI()

processed_agent_data = Table(
    "processed_agent_data",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("road_state", String),
    Column("user_id", Integer),
    Column("x", Float),
    Column("y", Float),
    Column("z", Float),
    Column("latitude", Float),
    Column("longitude", Float),
    Column("timestamp", DateTime),
)

# WebSocket subscriptions
subscriptions: Dict[int, Set[WebSocket]] = {}


# FastAPI WebSocket endpoint
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await websocket.accept()
    if user_id not in subscriptions:
        subscriptions[user_id] = set()
    subscriptions[user_id].add(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        subscriptions[user_id].remove(websocket)


# Function to send data to subscribed users
async def send_data_to_subscribers(user_id: int, data):
    if user_id in subscriptions:
        for websocket in subscriptions[user_id]:
            await websocket.send_json(json.dumps(data))


# FastAPI CRUDL endpoints


@app.post("/processed_agent_data/")
async def create_processed_agent_data(data: List[ProcessedAgentData], user_id: int = Body(..., embed=True)):
    session = SessionLocal()
    try:
        created_data = [
            {
                "road_state": item.road_state,
                "user_id": user_id,
                "x": item.agent_data.accelerometer.x,
                "y": item.agent_data.accelerometer.y,
                "z": item.agent_data.accelerometer.z,
                "latitude": item.agent_data.gps.latitude,
                "longitude": item.agent_data.gps.longitude,
                "timestamp": item.agent_data.timestamp,
            }
            for item in data
        ]
        stmt = processed_agent_data.insert().values(created_data).returning(processed_agent_data)
        result = session.execute(stmt)
        created_records = [dict(row._mapping) for row in result.fetchall()]
        session.commit()

        for record in created_records:
            await send_data_to_subscribers(user_id, jsonable_encoder(record))
        return created_records
    except Exception as err:
        session.rollback()
        print(f"Database error: {err}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        session.close()


@app.get(
    "/processed_agent_data/{processed_agent_data_id}",
    response_model=ProcessedAgentDataInDB,
)
def read_processed_agent_data(processed_agent_data_id: int):
    session = SessionLocal()
    try:
        stmt = select(processed_agent_data).where(
            processed_agent_data.c.id == processed_agent_data_id
        )
        res = session.execute(stmt).fetchone()
        if not res:
            raise HTTPException(status_code=404, detail="Not found")

        return dict(res._mapping)

    finally:
        session.close()


@app.get("/processed_agent_data/", response_model=list[ProcessedAgentDataInDB])
def list_processed_agent_data():
    session = SessionLocal()
    try:
        stmt = select(processed_agent_data)
        res = session.execute(stmt).fetchall()
        if not res:
            raise HTTPException(status_code=404, detail="Not found")

        return [dict(r._mapping) for r in res]

    finally:
        session.close()


@app.put(
    "/processed_agent_data/{processed_agent_data_id}",
    response_model=ProcessedAgentDataInDB,
)
def update_processed_agent_data(processed_agent_data_id: int, data: ProcessedAgentData):
    # Update data
    pass


@app.delete(
    "/processed_agent_data/{processed_agent_data_id}",
    response_model=ProcessedAgentDataInDB,
)
def delete_processed_agent_data(processed_agent_data_id: int):
    # Delete by id
    pass


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
