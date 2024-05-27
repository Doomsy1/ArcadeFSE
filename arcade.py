import pygame
from src.chess.chess import ChessGame
from src.pacman.pacman import PacmanGame
from src.main_menu.main_menu import MainMenu

class Arcade:
    def __init__(self, menu):
        pygame.init()
        WIDTH, HEIGHT = 800, 800
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.menu = menu

    def run(self):
        running = True
        while running:
            match self.menu:
                case "main menu":
                    game = MainMenu(self.screen)
                case "chess":
                    game = ChessGame(self.screen)
                case "pacman":
                    game = PacmanGame(self.screen)
                case "exit":
                    pygame.quit()
                    return
            self.menu = game.main_loop()

# Run the gameu
if __name__ == "__main__":
    
    menu = "main menu"

    arcade = Arcade(menu)
    arcade.run()