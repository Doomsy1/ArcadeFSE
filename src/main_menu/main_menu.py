import pygame

from utils import write_centered_text

# Constants
FPS = 30
game_rects = {
    "chess": pygame.Rect(300, 300, 200, 100),
    "pacman": pygame.Rect(300, 500, 200, 100)
}

class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        pygame.display.set_caption("Main Menu")
        self.clock = pygame.time.Clock()

    def main_loop(self):
        running = True
        L_mouse_up = False
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "exit"
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        L_mouse_up = True
            self.screen.fill((0, 0, 0))

            # Draw the game buttons
            for game, rect in game_rects.items():
                pygame.draw.rect(self.screen, (255, 255, 255), rect)
                # Draw the text using write_centered_text
                write_centered_text(self.screen, game.title(), rect, (0, 0, 0))

            # check if the left mouse button is released
            if L_mouse_up:
                mx, my = pygame.mouse.get_pos()
                for game, rect in game_rects.items():
                    if rect.collidepoint(mx, my):
                        return game

            pygame.display.flip()
            self.clock.tick(FPS)
        return "exit"