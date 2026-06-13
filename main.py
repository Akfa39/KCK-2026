import threading

from audio.player import AudioPlayer
from audio.speech_recognizer import SpeechRecognizer
from audio.voice_commands import VoiceCommandDispatcher
from database.connector import DatabaseConnector
from exercise.dumbbell_crunch import DumbbellWeightedCrunch
from exercise.dumbbell_curl import DumbbellCurl
from exercise.dumbbell_french_press import DumbbellFrenchPress
from exercise.dumbbell_good_morning import DumbbellGoodMorning
from exercise.dumbbell_hip_thrust import DumbbellHipThrust
from exercise.dumbbell_leg_curl import DumbbellLegCurl
from exercise.dumbbell_overhead_tricep_extension import DumbbellOverheadTricepExtension
from exercise.dumbbell_plank_pull_through import DumbbellPlankPullThrough
from exercise.dumbbell_woodchop import DumbbellWoodchop
from ui.app import run as run_ui, AppActions

MODEL_PATH = "assets/vosk-model-small-pl-0.22"
MUSIC_FILE = "assets/music.mp3"

_EXERCISE_CLASSES = [
    DumbbellCurl,
    DumbbellFrenchPress,
    DumbbellOverheadTricepExtension,
    DumbbellWeightedCrunch,
    DumbbellHipThrust,
    DumbbellLegCurl,
    DumbbellGoodMorning,
    DumbbellWoodchop,
    DumbbellPlankPullThrough,
]

def _speech_loop(recognizer: SpeechRecognizer, voice_commands: VoiceCommandDispatcher):
    while True:
        text = recognizer.listen()
        if text:
            print(f"Rozpoznano: {text}")
            voice_commands.handle_text(text)

if __name__ == "__main__":
    database = DatabaseConnector("app.db")
    database.seed_exercises(_EXERCISE_CLASSES)

    background = AudioPlayer(0)
    background.play(MUSIC_FILE)

    dialogues = AudioPlayer(1)

    recognizer = SpeechRecognizer(MODEL_PATH)
    voice_commands = VoiceCommandDispatcher()
    threading.Thread(target=_speech_loop, args=(recognizer, voice_commands), daemon=True).start()

    run_ui(AppActions(
        music_player=background,
        dialogues_player=dialogues,
        voice_commands=voice_commands,
        db=database,
    ))

    database.close()
