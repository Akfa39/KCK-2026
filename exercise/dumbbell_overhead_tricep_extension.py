from enum import Enum, auto

import mediapipe as mp

from exercise.excerise import Exercise, Feedback, PoseFrame

mp_pose = mp.solutions.pose


class OverheadTricepState(Enum):
    UP = auto()
    DOWN = auto()


class DumbbellOverheadTricepExtension(Exercise):

    ANGLE_UP = 155
    ANGLE_DOWN = 90
    ELBOW_FLARE_RATIO = 1.25

    name = "Siedzące prostowanie tricepsa hantlem zza głowy"
    description = ("Siedząc na ławce, trzymanie hantla oburącz nad głową "
                   "i opuszczanie go za głowę - ćwiczenie tricepsa.")
    muscle_group = "Biceps/Triceps"
    video_file = "dumbbell_overhead_tricep_extension.mp4"

    def _initial_state(self) -> OverheadTricepState:
        return OverheadTricepState.UP

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

            flare_ratio = elbow_width / shoulder_width if shoulder_width > 0.02 else 0.0
            self._debug(
                f"elbow_flare_ratio={flare_ratio:.2f} (limit={self.ELBOW_FLARE_RATIO}, shoulder_width={shoulder_width:.3f})",
            )
            if shoulder_width > 0.02 and elbow_width / shoulder_width > self.ELBOW_FLARE_RATIO:
                return Feedback(
                    message="Trzymaj łokcie blisko głowy - nie rozchylaj ich na boki.",
                    audio_file="elbow_flare.mp3",
                    correct=False,
                    rep_counted=False,
                )

        source = frame.side if frame.side is not None else frame.front
        lm = source.landmark

        shoulder = lm[mp_pose.PoseLandmark.RIGHT_SHOULDER]
        elbow = lm[mp_pose.PoseLandmark.RIGHT_ELBOW]
        wrist = lm[mp_pose.PoseLandmark.RIGHT_WRIST]

        angle = self.angle(shoulder, elbow, wrist)

        self._debug(
            f"angle={angle:.1f} (DOWN<{self.ANGLE_DOWN}, UP>{self.ANGLE_UP})",
        )

        if self.state == OverheadTricepState.UP and self._hold(angle < self.ANGLE_DOWN):
            self.state = OverheadTricepState.DOWN
            return Feedback(
                message="Dobrze - hantel za głową, wracaj kontrolowanie.",
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
