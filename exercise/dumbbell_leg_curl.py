from enum import Enum, auto

import mediapipe as mp

from exercise.excerise import Exercise, Feedback, PoseFrame

mp_pose = mp.solutions.pose


class LegCurlState(Enum):
    DOWN = auto()
    UP = auto()


class DumbbellLegCurl(Exercise):

    ANGLE_DOWN = 160
    ANGLE_UP = 90

    name = "Uginanie nóg z hantlem"
    description = ("Leżąc twarzą w dół na ławce, hantel trzymany stopami - "
                   "zginanie nóg w kolanach. Ćwiczenie tylnej części uda.")
    muscle_group = "Nogi"
    video_file = "dumbbell_leg_curl.mp4"

    def _initial_state(self) -> LegCurlState:
        return LegCurlState.DOWN

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
        hip = lm[mp_pose.PoseLandmark.RIGHT_HIP]
        knee = lm[mp_pose.PoseLandmark.RIGHT_KNEE]
        ankle = lm[mp_pose.PoseLandmark.RIGHT_ANKLE]

        angle = self.angle(hip, knee, ankle)

        if self.state == LegCurlState.DOWN and self._hold(angle < self.ANGLE_UP):
            self.state = LegCurlState.UP
            return Feedback(
                message="Dobry zakres ruchu - wracaj kontrolowanie.",
                audio_file="good_range_of_motion.mp3",
                correct=True,
                rep_counted=False,
            )

        if self.state == LegCurlState.UP and angle > self.ANGLE_DOWN:
            self.state = LegCurlState.DOWN
            self.reps += 1
            return Feedback(
                message=f"Powtórzenie {self.reps} zaliczone!",
                audio_file="rep_counted.mp3",
                correct=True,
                rep_counted=True,
            )

        if self.state == LegCurlState.DOWN and angle < 130:
            return Feedback(
                message="Wyprostuj nogi do końca przed kolejnym uginaniem.",
                audio_file="extend_legs.mp3",
                correct=False,
                rep_counted=False,
            )

        return Feedback(
            message=f"Kąt kolana: {angle:.0f}°",
            audio_file="",
            correct=True,
            rep_counted=False,
        )
