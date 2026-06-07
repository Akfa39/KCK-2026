from dataclasses import dataclass
from typing import Callable, Optional, Any


@dataclass
class AppActions:
    on_home: Optional[Callable] = None
    on_trainings: Optional[Callable] = None
    on_calendar: Optional[Callable] = None
    on_settings: Optional[Callable] = None
    on_exercise_select: Optional[Callable] = None
    music_player: Optional[Any] = None
    dialogues_player: Optional[Any] = None
    db: Optional[Any] = None
