import pygame
from constants import PACMAN_VEL

# Constants
FPS = 30

class PacmanGame:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()

    def main_loop(self):
        running = True
        while running:
            pygame.display.flip()

            # set the caption as the fps
            pygame.display.set_caption(f"Pacman | FPS: {int(self.clock.get_fps())}")
            self.clock.tick(FPS)
        return "exit"