import pygame

class AudioPlayer:
    def __init__(self):
        pygame.mixer.init()

    def play(self, file_path: str, wait: bool = False):
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()

        if wait:
            self.wait_until_done()

    def wait_until_done(self):
        clock = pygame.time.Clock()
        while pygame.mixer.music.get_busy():
            clock.tick(10)

    def stop(self):
        pygame.mixer.music.stop()

    def is_playing(self) -> bool:
        return pygame.mixer.music.get_busy()

    def close(self):
        pygame.mixer.quit()
