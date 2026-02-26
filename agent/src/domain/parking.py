from dataclasses import dataclass

from agent.src.domain.gps import Gps


@dataclass
class Parking:
    empty_count: int
    gps: Gps
