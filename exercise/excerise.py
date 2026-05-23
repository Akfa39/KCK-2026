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

    def __init__(self):
        self.reps = 0
        self.state: Enum = self._initial_state()

    @abstractmethod
    def _initial_state(self) -> Enum:
        pass

    @abstractmethod
    def analyze(self, frame: PoseFrame) -> Feedback:
        pass

    def reset(self):
        self.reps = 0
        self.state = self._initial_state()