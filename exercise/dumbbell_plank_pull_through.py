from enum import Enum, auto

import mediapipe as mp

from exercise.excerise import Exercise, Feedback, PoseFrame

mp_pose = mp.solutions.pose


class PlankPullThroughState(Enum):
    NEUTRAL = auto()
    PULLING = auto()


class DumbbellPlankPullThrough(Exercise):

    BODY_LINE_MAX_DEVIATION = 20
    WRIST_CROSS_THRESHOLD = 0.07

    name = "Deska z przeciąganiem hantla"
    description = ("W pozycji wysokiej deski, przeciąganie hantla pod ciałem "
                   "z jednej strony na drugą - ćwiczenie antyrotacyjne mięśni tułowia.")
    muscle_group = "Klatka piersiowa"
    video_file = "dumbbell_plank_pull_through.mp4"

    def _initial_state(self) -> PlankPullThroughState:
        return PlankPullThroughState.NEUTRAL

    def analyze(self, frame: PoseFrame) -> Feedback:
        if frame.front is None and frame.side is None:
            return Feedback(
                message="Nie wykryto sylwetki.",
                audio_file="no_pose.mp3",
                correct=False,
                rep_counted=False,
            )

        if frame.side is not None:
            lm_s = frame.side.landmark
            shoulder_s = lm_s[mp_pose.PoseLandmark.RIGHT_SHOULDER]
            hip_s = lm_s[mp_pose.PoseLandmark.RIGHT_HIP]
            ankle_s = lm_s[mp_pose.PoseLandmark.RIGHT_ANKLE]

            body_angle = self.angle(shoulder_s, hip_s, ankle_s)
            deviation = abs(body_angle - 180)

            if deviation > self.BODY_LINE_MAX_DEVIATION:
                if body_angle > 180:
                    return Feedback(
                        message="Nie unoś bioder - utrzymaj prostą linię deski.",
                        audio_file="hips_up.mp3",
                        correct=False,
                        rep_counted=False,
                    )
                else:
                    return Feedback(
                        message="Biodra opadają - napnij brzuch i utrzymaj prostą linię.",
                        audio_file="hips_down.mp3",
                        correct=False,
                        rep_counted=False,
                    )

        source = frame.front if frame.front is not None else frame.side
        lm = source.landmark

        l_hip = lm[mp_pose.PoseLandmark.LEFT_HIP]
        r_hip = lm[mp_pose.PoseLandmark.RIGHT_HIP]
        l_wrist = lm[mp_pose.PoseLandmark.LEFT_WRIST]
        r_wrist = lm[mp_pose.PoseLandmark.RIGHT_WRIST]

        hip_center_x = (l_hip.x + r_hip.x) / 2
        left_crossed = l_wrist.x > hip_center_x + self.WRIST_CROSS_THRESHOLD
        right_crossed = r_wrist.x < hip_center_x - self.WRIST_CROSS_THRESHOLD

        if self.state == PlankPullThroughState.NEUTRAL and self._hold(left_crossed or right_crossed):
            self.state = PlankPullThroughState.PULLING

        if self.state == PlankPullThroughState.PULLING and not left_crossed and not right_crossed:
            self.state = PlankPullThroughState.NEUTRAL
            self.reps += 1
            return Feedback(
                message=f"Powtórzenie {self.reps} zaliczone!",
                audio_file="rep_counted.mp3",
                correct=True,
                rep_counted=True,
            )

        return Feedback(
            message="Utrzymaj deskę - przeciągaj powoli i kontrolowanie.",
            audio_file="",
            correct=True,
            rep_counted=False,
        )
