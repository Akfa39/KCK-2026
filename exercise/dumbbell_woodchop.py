from enum import Enum, auto
from typing import Optional

import mediapipe as mp

from exercise.excerise import Exercise, Feedback, PoseFrame

mp_pose = mp.solutions.pose


class WoodchopState(Enum):
    DOWN = auto()
    UP = auto()


class DumbbellWoodchop(Exercise):

    FAST_WRIST_DELTA = 0.06

    def __init__(self):
        super().__init__()
        self._last_wrist_mid_y: Optional[float] = None

    name = "Skręt tułowia w półklęku z hantlem"
    description = ("W półklęku z hantlem, obrót tułowia prowadzący hantel diagonalnie "
                   "od biodra do przeciwnego ramienia - ćwiczenie mięśni tułowia.")
    muscle_group = "Klatka piersiowa"
    video_file = "dumbbell_woodchop.mp4"

    def _initial_state(self) -> WoodchopState:
        return WoodchopState.DOWN

    def reset(self):
        super().reset()
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
        l_wrist = lm[mp_pose.PoseLandmark.LEFT_WRIST]
        r_wrist = lm[mp_pose.PoseLandmark.RIGHT_WRIST]
        shoulder = lm[mp_pose.PoseLandmark.RIGHT_SHOULDER]
        hip = lm[mp_pose.PoseLandmark.RIGHT_HIP]

        wrist_mid_y = (l_wrist.y + r_wrist.y) / 2

        if self._last_wrist_mid_y is not None:
            wrist_delta = abs(wrist_mid_y - self._last_wrist_mid_y)
            self._debug(
                f"wrist_delta={wrist_delta:.3f} (limit={self.FAST_WRIST_DELTA})",
            )
            if wrist_delta > self.FAST_WRIST_DELTA:
                self._last_wrist_mid_y = wrist_mid_y
                return Feedback(
                    message="Zwolnij - wykonuj ruch kontrolowanie, utrzymując napięcie tułowia.",
                    audio_file="slow_down_core_tension.mp3",
                    correct=False,
                    rep_counted=False,
                )
        self._last_wrist_mid_y = wrist_mid_y

        self._debug(
            f"wrist_mid_y={wrist_mid_y:.3f} (UP<{shoulder.y + 0.05:.3f}, DOWN>{hip.y - 0.05:.3f})",
        )

        if self.state == WoodchopState.DOWN and self._hold(wrist_mid_y < shoulder.y + 0.05):
            self.state = WoodchopState.UP
            return Feedback(
                message="Dobra rotacja - hantel przy ramieniu, wracaj kontrolowanie.",
                audio_file="good_rotation.mp3",
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
