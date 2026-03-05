import json
import logging
from typing import List

import pydantic_core
import requests

from app.entities.processed_agent_data import ProcessedAgentData
from app.interfaces.store_gateway import StoreGateway


class StoreApiAdapter(StoreGateway):
    def __init__(self, api_base_url):
        self.api_base_url = api_base_url

    def save_data(self, processed_agent_data_batch: List[ProcessedAgentData]):
        if not processed_agent_data_batch:
            return False

        # Extract user_id from the first element
        user_id = processed_agent_data_batch[0].agent_data.user_id

        payload = {
            "data": [item.model_dump(mode='json') for item in processed_agent_data_batch],
            "user_id": user_id
        }

        try:
            # Perform a POST request to the Store API with a 10-second timeout
            response = requests.post(
                f"{self.api_base_url}/processed_agent_data/",
                json=payload,
                timeout=10
            )
            if response.status_code == 200:
                logging.info(f"Batch of {len(processed_agent_data_batch)} items sent to Store.")
                return True
            else:
                logging.error(f"Store API error: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logging.error(f"Failed to send data to Store: {e}")
            return False
