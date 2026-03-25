import time
from app.entities.agent_data import AgentData
from app.entities.processed_agent_data import ProcessedAgentData

_last_processed_times = {}

def process_agent_data(
    agent_data: AgentData,
) -> ProcessedAgentData:
    """
    Process agent data and classify the state of the road surface.
    Parameters:
        agent_data (AgentData): Agent data that containing accelerometer, GPS, and timestamp.
    Returns:
        processed_data_batch (ProcessedAgentData): Processed data containing the classified state of the road surface and agent data.
    """
    user_id = agent_data.user_id

    curr_time = time.time()
    last_processed_time = _last_processed_times.get(user_id, 0)
    if curr_time - last_processed_time < 1.0: 
        return None
    _last_processed_times[user_id] = curr_time

    road_state = "normal"

    if agent_data.accelerometer.z < -1.0:
        road_state = "pothole"
    elif agent_data.accelerometer.z > 1.0:
        road_state = "bump"

    return ProcessedAgentData(
        road_state=road_state,
        agent_data=agent_data
    )
