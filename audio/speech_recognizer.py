import json
import vosk
import pyaudio

class SpeechRecognizer:
    SAMPLE_RATE = 16000
    CHUNK_SIZE = 4096

    def __init__(self, model_path: str):
        self.model = vosk.Model(model_path)
        self.recognizer = vosk.KaldiRecognizer(self.model, self.SAMPLE_RATE)
        self._audio = pyaudio.PyAudio()

    def listen(self) -> str:
        stream = self._audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.SAMPLE_RATE,
            input=True,
            frames_per_buffer=self.CHUNK_SIZE,
        )

        try:
            while True:
                data = stream.read(self.CHUNK_SIZE, exception_on_overflow=False)
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    return result.get("text", "")
        finally:
            stream.stop_stream()
            stream.close()

    def close(self):
        self._audio.terminate()
