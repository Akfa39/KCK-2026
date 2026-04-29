import threading
import cv2

from audio.speech_recognizer import SpeechRecognizer
from audio.player import AudioPlayer
from cv.pose_detector import PoseDetector

MODEL_PATH = "assets/vosk-model-small-pl-0.22"
AUDIO_FILE = "assets/test.mp3"

CAMERA_INDICES = [0, 1]

def _speech_loop(recognizer: SpeechRecognizer):
    while True:
        text = recognizer.listen()
        if text:
            print(f"Rozpoznano:  {text}")

def _vision_loop(detector: PoseDetector, frames: dict):
    detector.start()
    while True:
        frame = detector.read()
        if frame is not None:
            frames[detector.camera_index] = frame

if __name__ == "__main__":
    player = AudioPlayer()
    player.play(AUDIO_FILE)

    recognizer = SpeechRecognizer(MODEL_PATH)
    stt_thread = threading.Thread(target=_speech_loop, args=(recognizer,), daemon=True)
    stt_thread.start()

    frames: dict = {}

    detectors = [PoseDetector(i) for i in CAMERA_INDICES]
    for detector in detectors:
        pose_detector_thread = threading.Thread(target=_vision_loop, args=(detector, frames), daemon=True)
        pose_detector_thread.start()

    try:
        while True:
            for camera_index, frame in dict(frames).items():
                cv2.imshow(f"Kamera {camera_index}", frame)

            if cv2.waitKey(10) & 0xFF in (ord("q"), ord("Q")):
                break
    finally:
        cv2.destroyAllWindows()
        player.close()
