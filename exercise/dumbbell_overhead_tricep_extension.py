import math
from enum import Enum, auto
from typing import Any, Optional

import mediapipe as mp

from exercise.excerise import Exercise, Feedback, PoseFrame

mp_pose = mp.solutions.pose


class OverheadTricepState(Enum):
    UP = auto()
    DOWN = auto()


def _angle(a: Any, b: Any, c: Any) -> float:
    ax, ay = a.x - b.x, a.y - b.y
    cx, cy = c.x - b.x, c.y - b.y
    dot = ax * cx + ay * cy
    cross = ax * cy - ay * cx
    return abs(math.degrees(math.atan2(abs(cross), dot)))


class DumbbellOverheadTricepExtension(Exercise):

    ANGLE_UP = 155
    ANGLE_DOWN = 90
    ELBOW_FLARE_RATIO = 1.25
    FAST_MOVEMENT_DELTA = 35
    TORSO_DRIFT_THRESHOLD = 0.05

    def __init__(self):
        super().__init__()
        self._last_angle: Optional[float] = None
        self._shoulder_y_baseline: Optional[float] = None

    name = "Siedzące prostowanie tricepsa hantlem zza głowy"
    description = ("Siedząc na ławce, trzymanie hantla oburącz nad głową "
                   "i opuszczanie go za głowę — ćwiczenie tricepsa.")
    muscle_group = "Triceps"
    video_file = "dumbbell_overhead_tricep_extension.mp4"

    def _initial_state(self) -> OverheadTricepState:
        return OverheadTricepState.UP

    def reset(self):
        super().reset()
        self._last_angle = None
        self._shoulder_y_baseline = None

    def analyze(self, frame: PoseFrame) -> Feedback:
        if frame.front is None and frame.side is None:
            return Feedback(
                message="Nie wykryto sylwetki.",
                audio_file="no_pose.mp3",
                correct=False,
                rep_counted=False,
            )

        if frame.front is not None:
            lm_f = frame.front.landmark
            l_shoulder_f = lm_f[mp_pose.PoseLandmark.LEFT_SHOULDER]
            r_shoulder_f = lm_f[mp_pose.PoseLandmark.RIGHT_SHOULDER]
            l_elbow_f = lm_f[mp_pose.PoseLandmark.LEFT_ELBOW]
            r_elbow_f = lm_f[mp_pose.PoseLandmark.RIGHT_ELBOW]

            shoulder_width = abs(l_shoulder_f.x - r_shoulder_f.x)
            elbow_width = abs(l_elbow_f.x - r_elbow_f.x)

            if shoulder_width > 0.02 and elbow_width / shoulder_width > self.ELBOW_FLARE_RATIO:
                return Feedback(
                    message="Trzymaj łokcie blisko głowy — nie rozchylaj ich na boki.",
                    audio_file="elbow_flare.mp3",
                    correct=False,
                    rep_counted=False,
                )

        source = frame.side if frame.side is not None else frame.front
        lm = source.landmark

        shoulder = lm[mp_pose.PoseLandmark.RIGHT_SHOULDER]
        elbow = lm[mp_pose.PoseLandmark.RIGHT_ELBOW]
        wrist = lm[mp_pose.PoseLandmark.RIGHT_WRIST]

        angle = _angle(shoulder, elbow, wrist)

        if self.state == OverheadTricepState.UP and angle >= self.ANGLE_UP:
            self._shoulder_y_baseline = shoulder.y

        if self._shoulder_y_baseline is not None:
            drift = abs(shoulder.y - self._shoulder_y_baseline)
            if drift > self.TORSO_DRIFT_THRESHOLD:
                return Feedback(
                    message="Ustabilizuj tułów — barki nie powinny się ruszać podczas ćwiczenia.",
                    audio_file="torso_movement.mp3",
                    correct=False,
                    rep_counted=False,
                )

        if self._last_angle is not None and abs(angle - self._last_angle) > self.FAST_MOVEMENT_DELTA:
            self._last_angle = angle
            return Feedback(
                message="Zwolnij — wykonuj ruch w pełni kontrolowany.",
                audio_file="slow_down_controlled.mp3",
                correct=False,
                rep_counted=False,
            )
        self._last_angle = angle

        if self.state == OverheadTricepState.UP and angle < self.ANGLE_DOWN:
            self.state = OverheadTricepState.DOWN
            return Feedback(
                message="Dobrze — hantel za głową, wracaj kontrolowanie.",
                audio_file="good_dumbbell_behind_head.mp3",
                correct=True,
                rep_counted=False,
            )

        if self.state == OverheadTricepState.DOWN and angle > self.ANGLE_UP:
            self.state = OverheadTricepState.UP
            self.reps += 1
            return Feedback(
                message=f"Powtórzenie {self.reps} zaliczone!",
                audio_file="rep_counted.mp3",
                correct=True,
                rep_counted=True,
            )

        return Feedback(
            message=f"Kąt łokcia: {angle:.0f}°",
            audio_file="",
            correct=True,
            rep_counted=False,
        )
