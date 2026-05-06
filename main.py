import threading
import cv2

from audio.speech_recognizer import SpeechRecognizer
from audio.player import AudioPlayer
from cv.pose_detector import PoseDetector
from ui.app import run as run_ui, AppActions

MODEL_PATH = "assets/vosk-model-small-pl-0.22"
AUDIO_FILE = "assets/test.mp3"

CAMERA_INDICES = [0, 1]

_pose_running = False
_pose_lock = threading.Lock()


def _speech_loop(recognizer: SpeechRecognizer):
    while True:
        text = recognizer.listen()
        if text:
            print(f"Rozpoznano: {text}")


def _vision_loop(detector: PoseDetector, frames: dict, stop_event: threading.Event):
    detector.start()
    while not stop_event.is_set():
        frame = detector.read()
        if frame is not None:
            frames[detector.camera_index] = frame
    detector.stop()


def _pose_session():
    global _pose_running

    frames: dict = {}
    stop_event = threading.Event()

    detectors = [PoseDetector(i) for i in CAMERA_INDICES]
    for detector in detectors:
        threading.Thread(target=_vision_loop, args=(detector, frames, stop_event), daemon=True).start()

    shown_windows: set = set()

    while True:
        for camera_index, frame in dict(frames).items():
            win_name = f"Kamera {camera_index}"
            cv2.imshow(win_name, frame)
            shown_windows.add(win_name)

        if cv2.waitKey(10) & 0xFF in (ord("q"), ord("Q")):
            break

        if shown_windows and any(cv2.getWindowProperty(w, cv2.WND_PROP_VISIBLE) < 1 for w in shown_windows):
            break

    stop_event.set()
    cv2.destroyAllWindows()

    with _pose_lock:
        _pose_running = False


def start_pose_detection():
    global _pose_running
    with _pose_lock:
        if _pose_running:
            return
        _pose_running = True
    threading.Thread(target=_pose_session, daemon=True).start()


if __name__ == "__main__":
    player = AudioPlayer()
    player.play(AUDIO_FILE)

    recognizer = SpeechRecognizer(MODEL_PATH)
    threading.Thread(target=_speech_loop, args=(recognizer,), daemon=True).start()

    run_ui(AppActions(on_settings=start_pose_detection))

    player.close()
