import pygame

class AudioPlayer:
    _init = False

    def __init__(self, channel_id: int):
        if not AudioPlayer._init:
            pygame.init()
            pygame.mixer.init()
            _init = True

        self.channel = pygame.mixer.Channel(channel_id)

    def play(self, file_path: str):
        sound = pygame.mixer.Sound(file_path)
        self.channel.play(sound)

    def stop(self):
        self.channel.stop()

    def is_playing(self) -> bool:
        return self.channel.get_busy()

    def set_volume(self, volume: float):
        volume = max(0.0, min(1.0, volume))
        self.channel.set_volume(volume)

    def get_volume(self) -> float:
        return self.channel.get_volume()
