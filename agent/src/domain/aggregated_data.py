from dataclasses import dataclass

from datetime import datetime

from agent.src.domain.accelerometer import Accelerometer
from agent.src.domain.gps import Gps
from agent.src.domain.parking import Parking


@dataclass
class AggregatedData:
    accelerometer: Accelerometer
    gps: Gps
    parking: Parking
    timestamp: datetime
    user_id: int
