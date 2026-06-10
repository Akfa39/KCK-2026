from enum import Enum, auto

import mediapipe as mp

from exercise.excerise import Exercise, Feedback, PoseFrame

mp_pose = mp.solutions.pose


class FrenchPressState(Enum):
    UP = auto()
    DOWN = auto()


class DumbbellFrenchPress(Exercise):

    ANGLE_DOWN = 80
    ANGLE_UP = 150
    ELBOW_FLARE_RATIO = 1.20

    name = "Francuskie wyciskanie hantlami"
    description = ("Leżąc na ławce, opuszczanie hantli za głowę przez zginanie łokci - "
                   "ćwiczenie tricepsa. Łokcie blisko głowy, ramiona lekko odchylone od pionu.")
    muscle_group = "Biceps/Triceps"
    video_file = "dumbbell_french_press.mp4"

    def _initial_state(self) -> FrenchPressState:
        return FrenchPressState.UP

    def analyze(self, frame: PoseFrame) -> Feedback:
        if frame.front is None:
            return Feedback(
                message="Nie wykryto sylwetki.",
                audio_file="no_pose.mp3",
                correct=False,
                rep_counted=False,
            )

        lm_front = frame.front.landmark
        l_shoulder_f = lm_front[mp_pose.PoseLandmark.LEFT_SHOULDER]
        r_shoulder_f = lm_front[mp_pose.PoseLandmark.RIGHT_SHOULDER]
        l_elbow_f = lm_front[mp_pose.PoseLandmark.LEFT_ELBOW]
        r_elbow_f = lm_front[mp_pose.PoseLandmark.RIGHT_ELBOW]
        l_wrist_f = lm_front[mp_pose.PoseLandmark.LEFT_WRIST]
        r_wrist_f = lm_front[mp_pose.PoseLandmark.RIGHT_WRIST]

        shoulder_width = abs(l_shoulder_f.x - r_shoulder_f.x)
        elbow_width = abs(l_elbow_f.x - r_elbow_f.x)

        if shoulder_width > 0.02 and elbow_width / shoulder_width > self.ELBOW_FLARE_RATIO:
            return Feedback(
                message="Trzymaj łokcie blisko głowy - nie rozchylaj ich na boki.",
                audio_file="elbow_flare.mp3",
                correct=False,
                rep_counted=False,
            )

        r_angle_f = self.angle(r_shoulder_f, r_elbow_f, r_wrist_f)
        l_angle_f = self.angle(l_shoulder_f, l_elbow_f, l_wrist_f)
        angle = (r_angle_f + l_angle_f) / 2

        if frame.side is not None:
            lm_side = frame.side.landmark
            shoulder_s = lm_side[mp_pose.PoseLandmark.RIGHT_SHOULDER]
            elbow_s = lm_side[mp_pose.PoseLandmark.RIGHT_ELBOW]
            wrist_s = lm_side[mp_pose.PoseLandmark.RIGHT_WRIST]

            angle = self.angle(shoulder_s, elbow_s, wrist_s)

        if self.state == FrenchPressState.UP and self._hold(angle < self.ANGLE_DOWN):
            self.state = FrenchPressState.DOWN
            return Feedback(
                message="Dobrze - hantle przy uszach, wracaj kontrolowanie.",
                audio_file="good_dumbbells_at_ears.mp3",
                correct=True,
                rep_counted=False,
            )

        if self.state == FrenchPressState.DOWN and angle > self.ANGLE_UP:
            self.state = FrenchPressState.UP
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
