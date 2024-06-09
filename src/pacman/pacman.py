import pygame
from src.pacman.ghost import Ghost
from src.pacman.map import PacmanMap
from src.pacman.player import PacmanPlayer

# Constants
FPS = 30

class PacmanGame:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()

        self.map = PacmanMap(screen)

        self.player = PacmanPlayer(screen, self.map)

        self.ghosts = []
        for ghost_type in ["blinky", "pinky", "inky", "clyde"]:
            self.ghosts.append(Ghost(screen, self.map, self.player, ghost_type))

        self.powerup_timer = 0

    def update_powerup_timer(self):
        self.powerup_timer -= 1
        self.powerup_timer = max(self.powerup_timer, 0)

    def handle_ghost_collision(self):
        for ghost in self.ghosts:
            if self.player.rect.colliderect(ghost.rect):
                if self.powerup_timer > 0:
                    ghost.reset()
                    self.powerup_timer = 0
                else:
                    self.player.reset()

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

            for ghost in self.ghosts:
                ghost.update()
                ghost.draw()

            self.handle_ghost_collision()

            self.update_powerup_timer()


            # set the caption as the fps
            pygame.display.set_caption(f"Pacman | FPS: {int(self.clock.get_fps())}")
            self.clock.tick(FPS)
            pygame.display.flip()
        return "exit"