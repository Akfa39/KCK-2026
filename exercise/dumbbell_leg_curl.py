import math
from enum import Enum, auto
from typing import Any, Optional

import mediapipe as mp

from exercise.excerise import Exercise, Feedback, PoseFrame

mp_pose = mp.solutions.pose


class LegCurlState(Enum):
    DOWN = auto()
    UP = auto()


def _angle(a: Any, b: Any, c: Any) -> float:
    ax, ay = a.x - b.x, a.y - b.y
    cx, cy = c.x - b.x, c.y - b.y
    dot = ax * cx + ay * cy
    cross = ax * cy - ay * cx
    return abs(math.degrees(math.atan2(abs(cross), dot)))


class DumbbellLegCurl(Exercise):

    ANGLE_DOWN = 160
    ANGLE_UP = 90
    HIP_LIFT_THRESHOLD = 0.05
    FAST_MOVEMENT_DELTA = 35

    def __init__(self):
        super().__init__()
        self._hip_y_baseline: Optional[float] = None
        self._last_angle: Optional[float] = None

    @property
    def name(self) -> str:
        return "Uginanie nóg z hantlem"

    @property
    def description(self) -> str:
        return ("Leżąc twarzą w dół na ławce, hantel trzymany stopami — "
                "zginanie nóg w kolanach. Ćwiczenie tylnej części uda.")

    @property
    def muscle_group(self) -> str:
        return "Tylna część uda"

    def _initial_state(self) -> LegCurlState:
        return LegCurlState.DOWN

    def reset(self):
        super().reset()
        self._hip_y_baseline = None
        self._last_angle = None

    def analyze(self, frame: PoseFrame) -> Feedback:
        source = frame.side if frame.side is not None else frame.front
        if source is None:
            return Feedback(
                message="Nie wykryto sylwetki.",
                audio_file="no_pose.mp3",
                correct=False,
                rep_counted=False,
            )

        lm = source.landmark
        hip = lm[mp_pose.PoseLandmark.RIGHT_HIP]
        knee = lm[mp_pose.PoseLandmark.RIGHT_KNEE]
        ankle = lm[mp_pose.PoseLandmark.RIGHT_ANKLE]

        angle = _angle(hip, knee, ankle)

        if self.state == LegCurlState.DOWN and angle >= self.ANGLE_DOWN:
            self._hip_y_baseline = hip.y

        if self._hip_y_baseline is not None:
            hip_lift = abs(hip.y - self._hip_y_baseline)
            if hip_lift > self.HIP_LIFT_THRESHOLD:
                return Feedback(
                    message="Biodra odrywają się od ławki — dociśnij je i napnij brzuch.",
                    audio_file="hip_lift.mp3",
                    correct=False,
                    rep_counted=False,
                )

        if self._last_angle is not None and abs(angle - self._last_angle) > self.FAST_MOVEMENT_DELTA:
            self._last_angle = angle
            return Feedback(
                message="Zwolnij — wykonuj ruch powoli i kontrolowanie.",
                audio_file="too_fast.mp3",
                correct=False,
                rep_counted=False,
            )
        self._last_angle = angle

        if self.state == LegCurlState.DOWN and angle < self.ANGLE_UP:
            self.state = LegCurlState.UP
            return Feedback(
                message="Dobry zakres ruchu — wracaj kontrolowanie.",
                audio_file="good_up.mp3",
                correct=True,
                rep_counted=False,
            )

        if self.state == LegCurlState.UP and angle > self.ANGLE_DOWN:
            self.state = LegCurlState.DOWN
            self.reps += 1
            return Feedback(
                message=f"Powtórzenie {self.reps} zaliczone!",
                audio_file="rep_counted.mp3",
                correct=True,
                rep_counted=True,
            )

        if self.state == LegCurlState.DOWN and angle < 130:
            return Feedback(
                message="Wyprostuj nogi do końca przed kolejnym uginaniem.",
                audio_file="extend_legs.mp3",
                correct=False,
                rep_counted=False,
            )

        return Feedback(
            message=f"Kąt kolana: {angle:.0f}°",
            audio_file="",
            correct=True,
            rep_counted=False,
        )
