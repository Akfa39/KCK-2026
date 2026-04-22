from audio.speech_recognizer import SpeechRecognizer
from audio.player import AudioPlayer

if __name__ == '__main__':
    # Model could be downloaded from: https://alphacephei.com/vosk/models
    MODEL_PATH = "assets/vosk-model-small-pl-0.22"
    AUDIO_FILE = "assets/test.mp3"

    recognizer = SpeechRecognizer(MODEL_PATH)
    player = AudioPlayer()

    player.play(AUDIO_FILE, wait=True)

    text = recognizer.listen()
    print(f"Rozpoznano: {text}")

    recognizer.close()
    player.close()
