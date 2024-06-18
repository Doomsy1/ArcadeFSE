import pygame
from src.chess.chess import ChessGame
from src.pacman.pacman import PacmanGame
from src.main_menu.main_menu import MainMenu
from src.connect_four.connect_four import ConnectFourGame

class Arcade:
    def __init__(self, menu):
        pygame.init()
        WIDTH, HEIGHT = 760, 1000
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
                case "connect four":
                    game = ConnectFourGame(self.screen)
                case "exit":
                    pygame.quit()
                    return
            self.menu = game.main_loop()

# run the game
if __name__ == "__main__":
    
    menu = "main menu"

    arcade = Arcade(menu)
    arcade.run()