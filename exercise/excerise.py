import math
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, ClassVar, Optional

@dataclass
class PoseFrame:
    front: Optional[Any] = None
    side: Optional[Any] = None

@dataclass
class Feedback:
    message: str
    audio_file: str
    correct: bool
    rep_counted: bool

class Exercise(ABC):
    name: ClassVar[str]
    description: ClassVar[str]
    muscle_group: ClassVar[str]
    video_file: ClassVar[str]

    HOLD_FRAMES: ClassVar[int] = 60

    def __init__(self):
        self.reps = 0
        self.state: Enum = self._initial_state()
        self._hold_counter = 0

    @abstractmethod
    def _initial_state(self) -> Enum:
        pass

    @abstractmethod
    def analyze(self, frame: PoseFrame) -> Feedback:
        pass

    def reset(self):
        self.reps = 0
        self.state = self._initial_state()
        self._hold_counter = 0

    def _hold(self, condition: bool) -> bool:
        if not condition:
            self._hold_counter = 0
            return False
        self._hold_counter += 1
        if self._hold_counter >= self.HOLD_FRAMES:
            self._hold_counter = 0
            return True
        return False

    @property
    def hold_progress(self) -> float:
        return min(self._hold_counter / self.HOLD_FRAMES, 1.0)

    @staticmethod
    def angle(a: Any, b: Any, c: Any) -> float:
        ax, ay = a.x - b.x, a.y - b.y
        cx, cy = c.x - b.x, c.y - b.y
        dot = ax * cx + ay * cy
        cross = ax * cy - ay * cx
        return abs(math.degrees(math.atan2(abs(cross), dot)))