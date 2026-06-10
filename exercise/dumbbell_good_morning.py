import math
from enum import Enum, auto
from typing import Any

import mediapipe as mp

from exercise.excerise import Exercise, Feedback, PoseFrame

mp_pose = mp.solutions.pose


class GoodMorningState(Enum):
    STANDING = auto()
    HINGED = auto()


def _trunk_angle(shoulder: Any, hip: Any) -> float:
    dx = shoulder.x - hip.x
    dy = hip.y - shoulder.y
    if dy <= 0:
        return 90.0
    return abs(math.degrees(math.atan2(abs(dx), dy)))


class DumbbellGoodMorning(Exercise):

    TRUNK_STANDING = 25
    TRUNK_HINGED = 40
    KNEE_ANGLE_MIN = 130

    name = "Dzień dobry z hantlem w uchwycie goblet"
    description = ("Stojąc z hantlem przy klatce, skłon w przód z wypchaniem bioder do tyłu - "
                   "ćwiczenie tylnej taśmy mięśniowej. Kręgosłup neutralny przez cały ruch.")
    muscle_group = "Nogi"
    video_file = "dumbbell_good_morning.mp4"

    def _initial_state(self) -> GoodMorningState:
        return GoodMorningState.STANDING

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
        knee_angle = self.angle(hip, knee, ankle)

        if knee_angle < self.KNEE_ANGLE_MIN:
            return Feedback(
                message="Pchaj biodra do tyłu zamiast zginać kolana - to nie jest przysiad.",
                audio_file="squat_pattern.mp3",
                correct=False,
                rep_counted=False,
            )

        if self.state == GoodMorningState.STANDING and self._hold(trunk_angle > self.TRUNK_HINGED):
            self.state = GoodMorningState.HINGED
            return Feedback(
                message="Dobry skłon - utrzymaj neutralny kręgosłup, wracaj powoli.",
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
