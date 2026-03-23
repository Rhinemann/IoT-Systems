from app.entities.agent_data import AgentData
from app.entities.processed_agent_data import ProcessedAgentData


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
    # Implement it

    if not hasattr(agent_data, 'user_id') or agent_data.user_id is None:
        agent_data.user_id = 1

    return ProcessedAgentData(
        road_state="normal",
        agent_data=agent_data
    )
