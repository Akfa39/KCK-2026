from enum import Enum, auto
from typing import Optional

import mediapipe as mp

from exercise.excerise import Exercise, Feedback, PoseFrame

mp_pose = mp.solutions.pose


class HipThrustState(Enum):
    DOWN = auto()
    UP = auto()


class DumbbellHipThrust(Exercise):
    HIP_DOWN_THRESHOLD = 0.15
    HIP_UP_THRESHOLD = 0.08
    LORDOSIS_Y_MARGIN = 0.03

    def __init__(self):
        super().__init__()
        self._top_reached: bool = False

    name = "Unoszenie bioder z hantlem"
    description = ("Oparcie górnej części pleców o ławkę, hantel na biodrach, "
                   "wypychanie bioder w górę - ćwiczenie pośladków.")
    muscle_group = "Nogi"
    video_file = "dumbbell_hip_thrust.mp4"

    def _initial_state(self) -> HipThrustState:
        return HipThrustState.DOWN

    def reset(self):
        super().reset()
        self._top_reached = False

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

        hip_rel = hip.y - shoulder.y

        if hip.y < shoulder.y - self.LORDOSIS_Y_MARGIN:
            return Feedback(
                message="Nie wyginaj dolnych pleców - zatrzymaj ruch gdy ciało tworzy prostą linię.",
                audio_file="lordosis.mp3",
                correct=False,
                rep_counted=False,
            )

        if self.state == HipThrustState.DOWN and self._hold(hip_rel < self.HIP_UP_THRESHOLD):
            self.state = HipThrustState.UP
            return Feedback(
                message="Świetnie - biodra w górze, ściśnij pośladki!",
                audio_file="good_hips_squeezed.mp3",
                correct=True,
                rep_counted=False,
            )

        if self.state == HipThrustState.UP and hip_rel > self.HIP_DOWN_THRESHOLD:
            self.state = HipThrustState.DOWN
            self.reps += 1
            return Feedback(
                message=f"Powtórzenie {self.reps} zaliczone!",
                audio_file="rep_counted.mp3",
                correct=True,
                rep_counted=True,
            )

        return Feedback(
            message=f"Biodra: {'góra' if hip_rel < self.HIP_UP_THRESHOLD else 'dół'}",
            audio_file="",
            correct=True,
            rep_counted=False,
        )
