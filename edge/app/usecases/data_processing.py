from app.entities.agent_data import AgentData
from app.entities.processed_agent_data import ProcessedAgentData

_last_detection_state = {}

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
    road_state = "normal"

    last_detection_state = _last_detection_state.get(user_id, False)

    if (agent_data.accelerometer.z < 0.6):
        road_state = "pothole"
    elif (agent_data.accelerometer.z > 1.2):
        road_state = "bump"

    detection_happened = road_state != "normal"

    if not (not last_detection_state and detection_happened):
        road_state = "normal"

    _last_detection_state[user_id] = detection_happened

    return ProcessedAgentData(
        road_state=road_state,
        agent_data=agent_data
    )
