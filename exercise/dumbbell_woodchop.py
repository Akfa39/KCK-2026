import math
from enum import Enum, auto
from typing import Any, Optional

import mediapipe as mp

from exercise.excerise import Exercise, Feedback, PoseFrame

mp_pose = mp.solutions.pose


class WoodchopState(Enum):
    DOWN = auto()
    UP = auto()


class DumbbellWoodchop(Exercise):

    HIP_ROTATION_RATIO = 0.15   # relative change of hip width triggering error
    FAST_WRIST_DELTA = 0.12     # wrist midpoint y-change per frame

    def __init__(self):
        super().__init__()
        self._hip_width_baseline: Optional[float] = None
        self._last_wrist_mid_y: Optional[float] = None

    @property
    def name(self) -> str:
        return "Skręt tułowia w półklęku z hantlem"

    @property
    def description(self) -> str:
        return ("W półklęku z hantlem, obrót tułowia prowadzący hantel diagonalnie "
                "od biodra do przeciwnego ramienia — ćwiczenie mięśni tułowia.")

    @property
    def muscle_group(self) -> str:
        return "Mięśnie tułowia"

    def _initial_state(self) -> WoodchopState:
        return WoodchopState.DOWN

    def reset(self):
        super().reset()
        self._hip_width_baseline = None
        self._last_wrist_mid_y = None

    def analyze(self, frame: PoseFrame) -> Feedback:
        source = frame.front if frame.front is not None else frame.side
        if source is None:
            return Feedback(
                message="Nie wykryto sylwetki.",
                audio_file="no_pose.mp3",
                correct=False,
                rep_counted=False,
            )

        lm = source.landmark
        l_hip = lm[mp_pose.PoseLandmark.LEFT_HIP]
        r_hip = lm[mp_pose.PoseLandmark.RIGHT_HIP]
        l_wrist = lm[mp_pose.PoseLandmark.LEFT_WRIST]
        r_wrist = lm[mp_pose.PoseLandmark.RIGHT_WRIST]
        shoulder = lm[mp_pose.PoseLandmark.RIGHT_SHOULDER]
        hip = lm[mp_pose.PoseLandmark.RIGHT_HIP]

        hip_width = abs(l_hip.x - r_hip.x)

        if self._hip_width_baseline is None:
            self._hip_width_baseline = hip_width
        elif self._hip_width_baseline > 0.01:
            hip_rotation = abs(hip_width - self._hip_width_baseline) / self._hip_width_baseline
            if hip_rotation > self.HIP_ROTATION_RATIO:
                return Feedback(
                    message="Biodra nie rotują — ruch pochodzi z tułowia, nie z bioder.",
                    audio_file="hip_rotation.mp3",
                    correct=False,
                    rep_counted=False,
                )

        wrist_mid_y = (l_wrist.y + r_wrist.y) / 2

        if self._last_wrist_mid_y is not None and abs(wrist_mid_y - self._last_wrist_mid_y) > self.FAST_WRIST_DELTA:
            self._last_wrist_mid_y = wrist_mid_y
            return Feedback(
                message="Zwolnij — wykonuj ruch kontrolowanie, utrzymując napięcie tułowia.",
                audio_file="too_fast.mp3",
                correct=False,
                rep_counted=False,
            )
        self._last_wrist_mid_y = wrist_mid_y

        # DOWN: wrists near hip level (wrist_mid_y ≈ hip.y, larger y = lower in frame)
        # UP: wrists near shoulder level (wrist_mid_y ≈ shoulder.y, smaller y = higher)
        if self.state == WoodchopState.DOWN and wrist_mid_y < shoulder.y + 0.05:
            self.state = WoodchopState.UP
            return Feedback(
                message="Dobra rotacja — hantel przy ramieniu, wracaj kontrolowanie.",
                audio_file="good_up.mp3",
                correct=True,
                rep_counted=False,
            )

        if self.state == WoodchopState.UP and wrist_mid_y > hip.y - 0.05:
            self.state = WoodchopState.DOWN
            self.reps += 1
            return Feedback(
                message=f"Powtórzenie {self.reps} zaliczone!",
                audio_file="rep_counted.mp3",
                correct=True,
                rep_counted=True,
            )

        return Feedback(
            message="Ruch diagonalny w toku...",
            audio_file="",
            correct=True,
            rep_counted=False,
        )
