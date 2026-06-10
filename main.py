import threading

from audio.player import AudioPlayer
from audio.speech_recognizer import SpeechRecognizer
from database.connector import DatabaseConnector
from ui.app import run as run_ui, AppActions

MODEL_PATH = "assets/vosk-model-small-pl-0.22"
MUSIC_FILE = "assets/music.mp3"

def _speech_loop(recognizer: SpeechRecognizer):
    while True:
        text = recognizer.listen()
        if text:
            print(f"Rozpoznano: {text}")

if __name__ == "__main__":
    database = DatabaseConnector("app.db")

    background = AudioPlayer(0)
    background.play(MUSIC_FILE)

    dialogues = AudioPlayer(1)

    recognizer = SpeechRecognizer(MODEL_PATH)
    threading.Thread(target=_speech_loop, args=(recognizer,), daemon=True).start()

    run_ui(AppActions(
        music_player=background,
        dialogues_player=dialogues,
        db=database,
    ))

    database.close()
