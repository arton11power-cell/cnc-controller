"""Machine state model"""

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class MachineState:
    """Represents the current state of CNC machine"""

    is_running: bool = False
    position: Dict[str, float] = field(default_factory=lambda: {'X': 0, 'Y': 0, 'Z': 0})
    feed_rate: float = 100.0
    spindle_speed: float = 0.0
    temperature: float = 0.0
    error_message: str = ""

    def to_dict(self):
        """Convert state to dictionary"""
        return {
            'is_running': self.is_running,
            'position': self.position,
            'feed_rate': self.feed_rate,
            'spindle_speed': self.spindle_speed,
            'temperature': self.temperature,
            'error_message': self.error_message,
        }
