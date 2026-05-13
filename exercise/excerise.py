from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

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
    def __init__(self):
        self.reps = 0
        self.state: Enum = self._initial_state()

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    @property
    @abstractmethod
    def muscle_group(self) -> str:
        pass

    @abstractmethod
    def _initial_state(self) -> Enum:
        pass

    @abstractmethod
    def analyze(self, frame: PoseFrame) -> Feedback:
        pass

    def reset(self):
        self.reps = 0
        self.state = self._initial_state()