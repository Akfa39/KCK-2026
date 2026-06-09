import threading
import time
from dataclasses import dataclass
from typing import Any, Callable, Optional, Type

import cv2
import numpy as np

from cv.pose_detector import PoseDetector
from exercise.excerise import Exercise, PoseFrame

CAMERA_INDICES = [0, 1]
_JPEG_PARAMS = [int(cv2.IMWRITE_JPEG_QUALITY), 70]


@dataclass
class SessionResult:
    exercise_name: str
    reps_done: int
    target_reps: int
    duration_seconds: float
    incorrect_feedbacks: int
    total_feedbacks: int


def _to_bytes(frame) -> bytes:
    _, buf = cv2.imencode('.jpg', frame, _JPEG_PARAMS)
    return bytes(buf)


def _no_camera_frame() -> np.ndarray:
    h, w = 360, 480
    frame = np.full((h, w, 3), 22, dtype=np.uint8)
    cx, cy, r = w // 2, h // 2, 60
    cv2.circle(frame, (cx, cy), r, (60, 60, 60), 3)
    cv2.line(frame, (cx - r + 10, cy - r + 10), (cx + r - 10, cy + r - 10), (60, 60, 60), 3)
    cv2.putText(frame, "Brak kamery", (cx - 80, cy + r + 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (80, 80, 80), 2)
    return frame


_NO_CAM = _no_camera_frame()
PLACEHOLDER_BYTES = _to_bytes(_NO_CAM)


def _vision_loop(detector: PoseDetector, frames: dict, landmarks: dict, stop: threading.Event):
    detector.start()
    while not stop.is_set():
        frame, lm = detector.read()
        if frame is not None:
            frames[detector.camera_index] = frame
            landmarks[detector.camera_index] = lm
    detector.stop()


class ExerciseSession:
    """
    on_update(front_bytes, side_bytes, feedback, reps, countdown_str | None)
    on_complete(SessionResult)
    """

    def __init__(
            self,
            exercise_class: Type[Exercise],
            target_reps: int,
            dialogues_player: Optional[Any] = None,
    ):
        self._exercise_class = exercise_class
        self._target_reps = target_reps
        self._dialogues_player = dialogues_player
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    def start(self, on_update: Callable, on_complete: Callable):
        threading.Thread(target=self._run, args=(on_update, on_complete), daemon=True).start()

    def _run(self, on_update: Callable, on_complete: Callable):
        frames: dict = {}
        landmarks: dict = {}
        front_idx, side_idx = CAMERA_INDICES[0], CAMERA_INDICES[1]

        detectors = [PoseDetector(i) for i in CAMERA_INDICES]
        for det in detectors:
            threading.Thread(
                target=_vision_loop,
                args=(det, frames, landmarks, self._stop),
                daemon=True,
            ).start()

        # wait for cameras — max 4 s, then continue regardless
        deadline = time.time() + 4.0
        while time.time() < deadline and not self._stop.is_set():
            if len(frames) >= len(CAMERA_INDICES):
                break
            time.sleep(0.05)

        def get_frame(idx) -> np.ndarray:
            return frames.get(idx, _NO_CAM)

        # ── countdown ──────────────────────────────────────────────
        for count in [3, 2, 1]:
            if self._stop.is_set():
                break
            on_update(_to_bytes(get_frame(front_idx)), _to_bytes(get_frame(side_idx)), None, 0, str(count))
            time.sleep(1.0)

        if not self._stop.is_set():
            on_update(_to_bytes(get_frame(front_idx)), _to_bytes(get_frame(side_idx)), None, 0, "START!")
            time.sleep(0.7)

        # ── exercise loop ──────────────────────────────────────────
        exercise = self._exercise_class()
        start_time = time.time()
        incorrect = 0
        total = 0
        last_audio = ""

        while exercise.reps < self._target_reps and not self._stop.is_set():
            f = get_frame(front_idx)
            s = get_frame(side_idx)
            lm_front = landmarks.get(front_idx)
            lm_side = landmarks.get(side_idx)

            pose_frame = PoseFrame(front=lm_front, side=lm_side)
            feedback = exercise.analyze(pose_frame)
            total += 1
            if not feedback.correct:
                incorrect += 1

            if self._dialogues_player and feedback.audio_file and feedback.audio_file != last_audio:
                try:
                    self._dialogues_player.play(f"assets/{feedback.audio_file}")
                    last_audio = feedback.audio_file
                except Exception:
                    pass

            on_update(_to_bytes(f), _to_bytes(s), feedback, exercise.reps, None)
            time.sleep(1 / 15)

        self._stop.set()

        on_complete(SessionResult(
            exercise_name=self._exercise_class.name,
            reps_done=exercise.reps,
            target_reps=self._target_reps,
            duration_seconds=time.time() - start_time,
            incorrect_feedbacks=incorrect,
            total_feedbacks=total,
        ))
