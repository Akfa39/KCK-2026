import math
from enum import Enum, auto
from typing import Any, Optional

import mediapipe as mp

from exercise.excerise import Exercise, Feedback, PoseFrame

mp_pose = mp.solutions.pose


class CurlState(Enum):
    DOWN = auto()
    UP = auto()


def _angle(a: Any, b: Any, c: Any) -> float:
    ax, ay = a.x - b.x, a.y - b.y
    cx, cy = c.x - b.x, c.y - b.y
    dot = ax * cx + ay * cy
    cross = ax * cy - ay * cx
    return abs(math.degrees(math.atan2(abs(cross), dot)))


class DumbbellCurl(Exercise):

    ANGLE_DOWN = 160
    ANGLE_UP = 50
    ELBOW_DRIFT_THRESHOLD = 0.07
    BODY_SWING_THRESHOLD = 0.06

    def __init__(self):
        super().__init__()
        self._torso_x_baseline: Optional[float] = None

    @property
    def name(self) -> str:
        return "Dumbbell Curl"

    @property
    def description(self) -> str:
        return "Uginanie przedramienia z hantlem — ćwiczenie bicepsa."

    @property
    def muscle_group(self) -> str:
        return "Biceps"

    def _initial_state(self) -> CurlState:
        return CurlState.DOWN

    def reset(self):
        super().reset()
        self._torso_x_baseline = None

    def analyze(self, frame: PoseFrame) -> Feedback:
        if frame.front is None:
            return Feedback(
                message="Nie wykryto sylwetki.",
                audio_file="no_pose.mp3",
                correct=False,
                rep_counted=False,
            )

        lm_front = frame.front.landmark
        shoulder_f = lm_front[mp_pose.PoseLandmark.RIGHT_SHOULDER]
        elbow_f    = lm_front[mp_pose.PoseLandmark.RIGHT_ELBOW]
        wrist_f    = lm_front[mp_pose.PoseLandmark.RIGHT_WRIST]
        angle = _angle(shoulder_f, elbow_f, wrist_f)

        if frame.side is not None:
            lm_side   = frame.side.landmark
            shoulder_s = lm_side[mp_pose.PoseLandmark.RIGHT_SHOULDER]
            elbow_s    = lm_side[mp_pose.PoseLandmark.RIGHT_ELBOW]
            hip_s      = lm_side[mp_pose.PoseLandmark.RIGHT_HIP]

            if self.state == CurlState.DOWN and angle >= self.ANGLE_DOWN:
                self._torso_x_baseline = shoulder_s.x - hip_s.x

            if shoulder_s.x - elbow_s.x > self.ELBOW_DRIFT_THRESHOLD:
                return Feedback(
                    message="Trzymaj łokieć przy tułowiu — nie wysuwaj go do przodu.",
                    audio_file="elbow_drift.mp3",
                    correct=False,
                    rep_counted=False,
                )

            if self._torso_x_baseline is not None:
                torso_shift = abs((shoulder_s.x - hip_s.x) - self._torso_x_baseline)
                if torso_shift > self.BODY_SWING_THRESHOLD:
                    return Feedback(
                        message="Nie bujaj tułowiem — utrzymaj stabilną postawę.",
                        audio_file="body_swing.mp3",
                        correct=False,
                        rep_counted=False,
                    )

        if self.state == CurlState.DOWN and angle < self.ANGLE_UP:
            self.state = CurlState.UP
            return Feedback(
                message="Dobra robota — pełne uniesienie!",
                audio_file="good_up.mp3",
                correct=True,
                rep_counted=False,
            )

        if self.state == CurlState.UP and angle > self.ANGLE_DOWN:
            self.state = CurlState.DOWN
            self.reps += 1
            return Feedback(
                message=f"Powtórzenie {self.reps} zaliczone!",
                audio_file="rep_counted.mp3",
                correct=True,
                rep_counted=True,
            )

        if self.state == CurlState.DOWN and angle < 120:
            return Feedback(
                message="Wyprostuj ramię do końca przed następnym uniesieniem.",
                audio_file="extend_arm.mp3",
                correct=False,
                rep_counted=False,
            )

        return Feedback(
            message=f"Kąt łokcia: {angle:.0f}°",
            audio_file="",
            correct=True,
            rep_counted=False,
        )
