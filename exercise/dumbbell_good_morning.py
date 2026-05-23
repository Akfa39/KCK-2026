import math
from enum import Enum, auto
from typing import Any, Optional

import mediapipe as mp

from exercise.excerise import Exercise, Feedback, PoseFrame

mp_pose = mp.solutions.pose


class GoodMorningState(Enum):
    STANDING = auto()
    HINGED = auto()


def _angle(a: Any, b: Any, c: Any) -> float:
    ax, ay = a.x - b.x, a.y - b.y
    cx, cy = c.x - b.x, c.y - b.y
    dot = ax * cx + ay * cy
    cross = ax * cy - ay * cx
    return abs(math.degrees(math.atan2(abs(cross), dot)))


def _trunk_angle(shoulder: Any, hip: Any) -> float:
    """Angle of the trunk line from vertical (0° = upright, 90° = horizontal)."""
    dx = shoulder.x - hip.x
    dy = hip.y - shoulder.y  # positive when shoulder above hip (normal standing)
    if dy <= 0:
        return 90.0
    return abs(math.degrees(math.atan2(abs(dx), dy)))


class DumbbellGoodMorning(Exercise):

    TRUNK_STANDING = 25   # trunk within 25° of vertical = standing position
    TRUNK_HINGED = 40     # trunk at 40°+ = properly hinged forward
    KNEE_ANGLE_MIN = 130  # below this threshold → squatting instead of hinging
    FAST_TRUNK_DELTA = 20

    def __init__(self):
        super().__init__()
        self._last_trunk_angle: Optional[float] = None

    name = "Dzień dobry z hantlem w uchwycie goblet"
    description = ("Stojąc z hantlem przy klatce, skłon w przód z wypchaniem bioder do tyłu — "
                   "ćwiczenie tylnej taśmy mięśniowej. Kręgosłup neutralny przez cały ruch.")
    muscle_group = "Tylna taśma"
    video_file = "dumbbell_good_morning.mp4"

    def _initial_state(self) -> GoodMorningState:
        return GoodMorningState.STANDING

    def reset(self):
        super().reset()
        self._last_trunk_angle = None

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
        shoulder = lm[mp_pose.PoseLandmark.RIGHT_SHOULDER]
        hip = lm[mp_pose.PoseLandmark.RIGHT_HIP]
        knee = lm[mp_pose.PoseLandmark.RIGHT_KNEE]
        ankle = lm[mp_pose.PoseLandmark.RIGHT_ANKLE]

        trunk_angle = _trunk_angle(shoulder, hip)
        knee_angle = _angle(hip, knee, ankle)

        if knee_angle < self.KNEE_ANGLE_MIN:
            return Feedback(
                message="Pchaj biodra do tyłu zamiast zginać kolana — to nie jest przysiad.",
                audio_file="squat_pattern.mp3",
                correct=False,
                rep_counted=False,
            )

        if self._last_trunk_angle is not None and abs(trunk_angle - self._last_trunk_angle) > self.FAST_TRUNK_DELTA:
            self._last_trunk_angle = trunk_angle
            return Feedback(
                message="Wykonuj ruch kontrolowanie — nie opadaj zbyt gwałtownie.",
                audio_file="slow_down_dont_drop.mp3",
                correct=False,
                rep_counted=False,
            )
        self._last_trunk_angle = trunk_angle

        if self.state == GoodMorningState.STANDING and trunk_angle > self.TRUNK_HINGED:
            self.state = GoodMorningState.HINGED
            return Feedback(
                message="Dobry skłon — utrzymaj neutralny kręgosłup, wracaj powoli.",
                audio_file="good_hinge.mp3",
                correct=True,
                rep_counted=False,
            )

        if self.state == GoodMorningState.HINGED and trunk_angle < self.TRUNK_STANDING:
            self.state = GoodMorningState.STANDING
            self.reps += 1
            return Feedback(
                message=f"Powtórzenie {self.reps} zaliczone!",
                audio_file="rep_counted.mp3",
                correct=True,
                rep_counted=True,
            )

        return Feedback(
            message=f"Kąt tułowia: {trunk_angle:.0f}°",
            audio_file="",
            correct=True,
            rep_counted=False,
        )
