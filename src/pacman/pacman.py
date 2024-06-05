import pygame
from src.pacman.map import PacmanMap
from constants import PACMAN_VEL
from src.pacman.player import PacmanPlayer

# Constants
FPS = 30

class PacmanGame:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()

        self.map = PacmanMap(screen)

        self.player = PacmanPlayer(screen, self.map)


    def main_loop(self):
        running = True
        while running:
            # handle events
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    return "main menu"
                # escape key
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return "main menu"
            
            self.mx, self.my = pygame.mouse.get_pos()

            self.map.draw()
            self.player.handle_keys(events)
            self.player.update()
            self.player.draw()


            # set the caption as the fps
            pygame.display.set_caption(f"Pacman | FPS: {int(self.clock.get_fps())}")
            self.clock.tick(FPS)
            pygame.display.flip()
        return "exit"