from enum import Enum, auto

import mediapipe as mp

from exercise.excerise import Exercise, Feedback, PoseFrame

mp_pose = mp.solutions.pose


class CurlState(Enum):
    DOWN = auto()
    UP = auto()


class DumbbellCurl(Exercise):

    ANGLE_DOWN = 160
    ANGLE_UP = 10
    ELBOW_DRIFT_THRESHOLD = 0.07

    name = "Dumbbell Curl"
    description = "Uginanie przedramienia z hantlem - ćwiczenie bicepsa."
    muscle_group = "Biceps/Triceps"
    video_file = "dumbbell_curl.mp4"

    def _initial_state(self) -> CurlState:
        return CurlState.DOWN

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
        elbow_f = lm_front[mp_pose.PoseLandmark.RIGHT_ELBOW]
        wrist_f = lm_front[mp_pose.PoseLandmark.RIGHT_WRIST]
        angle = self.angle(shoulder_f, elbow_f, wrist_f)

        if frame.side is not None:
            lm_side = frame.side.landmark
            shoulder_s = lm_side[mp_pose.PoseLandmark.RIGHT_SHOULDER]
            elbow_s = lm_side[mp_pose.PoseLandmark.RIGHT_ELBOW]

            elbow_drift = shoulder_s.x - elbow_s.x
            self._debug(
                f"elbow_drift={elbow_drift:.3f} (limit={self.ELBOW_DRIFT_THRESHOLD})",
            )
            if abs(elbow_drift) > self.ELBOW_DRIFT_THRESHOLD:
                return Feedback(
                    message="Trzymaj łokieć przy tułowiu - nie wysuwaj go do przodu.",
                    audio_file="elbow_drift.mp3",
                    correct=False,
                    rep_counted=False,
                )

        self._debug(
            f"angle={angle:.1f} (UP<{self.ANGLE_UP}, DOWN>{self.ANGLE_DOWN})",
        )

        if self.state == CurlState.DOWN and self._hold(angle < self.ANGLE_UP):
            self.state = CurlState.UP
            return Feedback(
                message="Dobra robota - pełne uniesienie!",
                audio_file="good_full_lift.mp3",
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

        return Feedback(
            message=f"Kąt łokcia: {angle:.0f}°",
            audio_file="",
            correct=True,
            rep_counted=False,
        )
