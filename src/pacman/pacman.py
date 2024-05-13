import pygame

from constants import VEL

# Constants
FPS = 30

class PacmanGame:
    def __init__(self, screen):
        self.screen = screen
        self.pacman_pos = [300, 300]  # Start position of Pac-Man
        pygame.display.set_caption("Pacman")
        self.clock = pygame.time.Clock()

    def handle_keys(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.pacman_pos[0] -= VEL
        if keys[pygame.K_RIGHT]:
            self.pacman_pos[0] += VEL
        if keys[pygame.K_UP]:
            self.pacman_pos[1] -= VEL
        if keys[pygame.K_DOWN]:
            self.pacman_pos[1] += VEL

    def main_loop(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "exit"
                # if escape is pressed, return to main menu
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "main menu"
            self.handle_keys()
            self.screen.fill((0, 0, 0))
            # Draw Pac-Man
            pygame.draw.circle(self.screen, (255, 255, 0), self.pacman_pos, 20)
            pygame.display.flip()
            self.clock.tick(FPS)
        return "exit"