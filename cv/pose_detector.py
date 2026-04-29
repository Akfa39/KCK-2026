import cv2
import mediapipe as mp

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

class PoseDetector:
    def __init__(self, camera_index: int = 0):
        self.camera_index = camera_index
        self._cap = None
        self._pose = None

    def start(self):
        self._cap = cv2.VideoCapture(self.camera_index)
        self._pose = mp_pose.Pose()

    def stop(self):
        if self._cap:
            self._cap.release()
            self._cap = None
        if self._pose:
            self._pose.close()
            self._pose = None

    def read(self):
        if not self._cap or not self._cap.isOpened():
            return None
        ret, frame = self._cap.read()
        if not ret:
            return None

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = self._pose.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if results.pose_landmarks:
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        return image
