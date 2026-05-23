import math
from enum import Enum, auto
from typing import Any, Optional

import mediapipe as mp

from exercise.excerise import Exercise, Feedback, PoseFrame

mp_pose = mp.solutions.pose


class CrunchState(Enum):
    DOWN = auto()
    UP = auto()


def _angle(a: Any, b: Any, c: Any) -> float:
    ax, ay = a.x - b.x, a.y - b.y
    cx, cy = c.x - b.x, c.y - b.y
    dot = ax * cx + ay * cy
    cross = ax * cy - ay * cx
    return abs(math.degrees(math.atan2(abs(cross), dot)))


class DumbbellWeightedCrunch(Exercise):

    ANGLE_DOWN = 165
    ANGLE_UP = 150
    ANGLE_TOO_HIGH = 115
    FAST_MOVEMENT_DELTA = 25
    BACK_LIFT_THRESHOLD = 0.04
    NECK_DROP_THRESHOLD = 25
    WRIST_DISTANCE_THRESHOLD = 0.12

    def __init__(self):
        super().__init__()
        self._last_angle: Optional[float] = None
        self._hip_y_baseline: Optional[float] = None
        self._neck_angle_baseline: Optional[float] = None

    name = "Brzuszek z hantlem"
    description = ("Leżąc na plecach z hantlem przy klatce, „zwijanie\" tułowia — "
                   "unoszenie łopatek od podłogi. Ćwiczenie mięśni brzucha.")
    muscle_group = "Brzuch"
    video_file = "dumbbell_crunch.mp4"

    def _initial_state(self) -> CrunchState:
        return CrunchState.DOWN

    def reset(self):
        super().reset()
        self._last_angle = None
        self._hip_y_baseline = None
        self._neck_angle_baseline = None

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
        ear = lm[mp_pose.PoseLandmark.RIGHT_EAR]
        wrist = lm[mp_pose.PoseLandmark.RIGHT_WRIST]

        torso_angle = _angle(shoulder, hip, knee)
        neck_angle = _angle(ear, shoulder, hip)

        if self.state == CrunchState.DOWN and torso_angle > self.ANGLE_DOWN:
            self._hip_y_baseline = hip.y
            self._neck_angle_baseline = neck_angle

        if self._hip_y_baseline is not None:
            hip_shift = self._hip_y_baseline - hip.y
            if hip_shift > self.BACK_LIFT_THRESHOLD:
                return Feedback(
                    message="Dolne plecy odrywają się od podłoża — przyciśnij je do podłogi.",
                    audio_file="back_lifted.mp3",
                    correct=False,
                    rep_counted=False,
                )

        if self._neck_angle_baseline is not None:
            neck_drop = self._neck_angle_baseline - neck_angle
            if neck_drop > self.NECK_DROP_THRESHOLD:
                return Feedback(
                    message="Nie naciągaj karku — broda lekko przyciągnięta, głowa razem z tułowiem.",
                    audio_file="neck_strain.mp3",
                    correct=False,
                    rep_counted=False,
                )

        wrist_dist = math.hypot(wrist.x - shoulder.x, wrist.y - shoulder.y)
        if wrist_dist > self.WRIST_DISTANCE_THRESHOLD:
            return Feedback(
                message="Trzymaj hantel blisko klatki piersiowej.",
                audio_file="dumbbell_far.mp3",
                correct=False,
                rep_counted=False,
            )

        if self._last_angle is not None and abs(torso_angle - self._last_angle) > self.FAST_MOVEMENT_DELTA:
            self._last_angle = torso_angle
            return Feedback(
                message="Wykonuj ruch kontrolowanie — bez rozpędu.",
                audio_file="no_momentum.mp3",
                correct=False,
                rep_counted=False,
            )
        self._last_angle = torso_angle

        if torso_angle < self.ANGLE_TOO_HIGH:
            if self.state == CrunchState.DOWN:
                self.state = CrunchState.UP
            return Feedback(
                message="Nie unoś tułowia tak wysoko — wystarczy oderwać łopatki od podłogi.",
                audio_file="crunch_too_high.mp3",
                correct=False,
                rep_counted=False,
            )

        if self.state == CrunchState.DOWN and torso_angle < self.ANGLE_UP:
            self.state = CrunchState.UP
            return Feedback(
                message="Dobra robota — łopatki uniesione!",
                audio_file="good_shoulder_blades_up.mp3",
                correct=True,
                rep_counted=False,
            )

        if self.state == CrunchState.UP and torso_angle > self.ANGLE_DOWN:
            self.state = CrunchState.DOWN
            self.reps += 1
            return Feedback(
                message=f"Powtórzenie {self.reps} zaliczone!",
                audio_file="rep_counted.mp3",
                correct=True,
                rep_counted=True,
            )

        return Feedback(
            message=f"Kąt tułowia: {torso_angle:.0f}°",
            audio_file="",
            correct=True,
            rep_counted=False,
        )
