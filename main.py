import threading
import cv2

from audio.speech_recognizer import SpeechRecognizer
from audio.player import AudioPlayer
from cv.pose_detector import PoseDetector
from exercise.dumbbell_crunch import DumbbellWeightedCrunch
from exercise.dumbbell_curl import DumbbellCurl
from exercise.dumbbell_french_press import DumbbellFrenchPress
from exercise.dumbbell_good_morning import DumbbellGoodMorning
from exercise.dumbbell_hip_thrust import DumbbellHipThrust
from exercise.dumbbell_leg_curl import DumbbellLegCurl
from exercise.dumbbell_overhead_tricep_extension import DumbbellOverheadTricepExtension
from exercise.dumbbell_plank_pull_through import DumbbellPlankPullThrough
from exercise.dumbbell_woodchop import DumbbellWoodchop
from exercise.excerise import Exercise, PoseFrame

ALL_EXERCISES: list[type[Exercise]] = [
    DumbbellCurl,
    DumbbellFrenchPress,
    DumbbellOverheadTricepExtension,
    DumbbellHipThrust,
    DumbbellGoodMorning,
    DumbbellLegCurl,
    DumbbellWeightedCrunch,
    DumbbellWoodchop,
    DumbbellPlankPullThrough,
]
from ui.app import run as run_ui, AppActions
from database.connector import DatabaseConnector

MODEL_PATH = "assets/vosk-model-small-pl-0.22"
MUSIC_FILE = "assets/music.mp3"
DIALOGUE_FILE = "assets/oh_no.mp3"



CAMERA_INDICES = [0, 1]

_pose_running = False
_pose_lock = threading.Lock()


def _speech_loop(recognizer: SpeechRecognizer):
    while True:
        text = recognizer.listen()
        if text:
            print(f"Rozpoznano: {text}")


def _vision_loop(detector: PoseDetector, frames: dict, landmarks: dict, stop_event: threading.Event):
    detector.start()
    while not stop_event.is_set():
        frame, lm = detector.read()
        if frame is not None:
            frames[detector.camera_index] = frame
            landmarks[detector.camera_index] = lm
    detector.stop()


def _pose_session():
    global _pose_running

    frames: dict = {}
    landmarks: dict = {}
    stop_event = threading.Event()

    exercise = ALL_EXERCISES[5]()

    detectors = [PoseDetector(i) for i in CAMERA_INDICES]
    for detector in detectors:
        threading.Thread(target=_vision_loop, args=(detector, frames, landmarks, stop_event), daemon=True).start()

    shown_windows: set = set()
    front_idx, side_idx = CAMERA_INDICES[0], CAMERA_INDICES[1]

    while True:
        current_frames = dict(frames)
        current_landmarks = dict(landmarks)

        pose_frame = PoseFrame(
            front=current_landmarks.get(front_idx),
            side=current_landmarks.get(side_idx),
        )
        feedback = exercise.analyze(pose_frame)
        feedback_color = (0, 200, 0) if feedback.correct else (0, 0, 220)

        for camera_index, frame in current_frames.items():
            win_name = "Przednia" if camera_index == front_idx else "Boczna"
            display = frame.copy()

            if camera_index == front_idx:
                cv2.putText(display, feedback.message, (10, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, feedback_color, 2)
                cv2.putText(display, f"Powtorzenia: {exercise.reps}", (10, 75),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

            cv2.imshow(win_name, display)
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
    database = DatabaseConnector("app.db")

    background = AudioPlayer(0)
    background.play(MUSIC_FILE)

    dialogues = AudioPlayer(1)
    dialogues.play(DIALOGUE_FILE)

    recognizer = SpeechRecognizer(MODEL_PATH)
    threading.Thread(target=_speech_loop, args=(recognizer,), daemon=True).start()

    run_ui(AppActions(
        on_settings=start_pose_detection,
        music_player=background,
        dialogues_player=dialogues,
    ))

    database.close()
