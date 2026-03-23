import logging
import os
from app.adapters.agent_mqtt_adapter import AgentMQTTAdapter
from app.adapters.hub_http_adapter import HubHttpAdapter
from app.adapters.hub_mqtt_adapter import HubMqttAdapter
from threading import Event
from config import (
    MQTT_BROKER_HOST,
    MQTT_BROKER_PORT,
    MQTT_TOPIC,
    HUB_URL,
    HUB_MQTT_BROKER_HOST,
    HUB_MQTT_BROKER_PORT,
    HUB_MQTT_TOPIC,
    HUB_CONNECTION_TYPE,
)

if __name__ == "__main__":
    # Configure logging settings
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)s] [%(module)s] %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("app.log"),
        ],
    )

    # Initialize the stop event to prevent high CPU usage
    stop_event = Event()

    # Logic to select the adapter based on configuration (SCRUM-93 & SCRUM-94)
    # This allows easy switching between HTTP and MQTT protocols
    if HUB_CONNECTION_TYPE.lower() == "http":
        logging.info("Initializing HubHttpAdapter (SCRUM-93 integration)")
        hub_adapter = HubHttpAdapter(
            api_base_url=HUB_URL,
        )
    else:
        logging.info("Initializing HubMqttAdapter (SCRUM-94 integration)")
        hub_adapter = HubMqttAdapter(
            broker=HUB_MQTT_BROKER_HOST,
            port=HUB_MQTT_BROKER_PORT,
            topic=HUB_MQTT_TOPIC,
        )

    # Create an instance of the AgentMQTTAdapter using the selected hub adapter
    # This adapter acts as a bridge between the Agent and the Hub
    agent_adapter = AgentMQTTAdapter(
        broker_host=MQTT_BROKER_HOST,
        broker_port=MQTT_BROKER_PORT,
        topic=MQTT_TOPIC,
        hub_gateway=hub_adapter,
    )

    try:
        logging.info(f"Starting Edge module. Connecting to Agent Broker at {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}")
        # Connect to the MQTT broker and start listening for messages from Agent
        agent_adapter.connect()
        agent_adapter.start()

        logging.info("Edge module started successfully. Waiting for data...")

        # Block the main thread efficiently without consuming CPU cycles
        stop_event.wait()

    except KeyboardInterrupt:
        # Stop the MQTT adapter and exit gracefully if interrupted by the user
        logging.info("Stop signal received. Shutting down...")
        agent_adapter.stop()
        stop_event.set()  # Release the event
        logging.info("System stopped.")