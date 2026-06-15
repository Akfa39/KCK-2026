from enum import Enum, auto
from typing import Optional

import mediapipe as mp

from exercise.excerise import Exercise, Feedback, PoseFrame

mp_pose = mp.solutions.pose


class CrunchState(Enum):
    DOWN = auto()
    UP = auto()


class DumbbellWeightedCrunch(Exercise):

    ANGLE_DOWN = 165
    ANGLE_UP = 150
    BACK_LIFT_THRESHOLD = 0.04

    def __init__(self):
        super().__init__()
        self._hip_y_baseline: Optional[float] = None

    name = "Brzuszek z hantlem"
    description = ("Leżąc na plecach z hantlem przy klatce, „zwijanie\" tułowia - "
                   "unoszenie łopatek od podłogi. Ćwiczenie mięśni brzucha.")
    muscle_group = "Klatka piersiowa"
    video_file = "dumbbell_crunch.mp4"

    def _initial_state(self) -> CrunchState:
        return CrunchState.DOWN

    def reset(self):
        super().reset()
        self._hip_y_baseline = None

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

        torso_angle = self.angle(shoulder, hip, knee)

        if self.state == CrunchState.DOWN and torso_angle > self.ANGLE_DOWN:
            self._hip_y_baseline = hip.y

        if self._hip_y_baseline is not None:
            hip_shift = self._hip_y_baseline - hip.y
            self._debug(
                f"hip_shift={hip_shift:.3f} (limit={self.BACK_LIFT_THRESHOLD})",
            )
            if hip_shift > self.BACK_LIFT_THRESHOLD:
                return Feedback(
                    message="Dolne plecy odrywają się od podłoża - przyciśnij je do podłogi.",
                    audio_file="back_lifted.mp3",
                    correct=False,
                    rep_counted=False,
                )

        self._debug(
            f"torso_angle={torso_angle:.1f} (UP<{self.ANGLE_UP}, DOWN>{self.ANGLE_DOWN})",
        )

        if self.state == CrunchState.DOWN and self._hold(torso_angle < self.ANGLE_UP):
            self.state = CrunchState.UP
            return Feedback(
                message="Dobra robota - łopatki uniesione!",
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
