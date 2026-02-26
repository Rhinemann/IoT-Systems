from dataclasses import dataclass

from domain.gps import Gps


@dataclass
class Parking:
    empty_count: int
    gps: Gps
