from src.pacman.gamemodes.pacman import Pacman
from src.pacman.menus.leaderboard import Leaderboard
from src.pacman.menus.pacman_menu import PacmanMenu

class PacmanGame:
    def __init__(self, screen):
        self.screen = screen

    def main_loop(self):
        running = True
        game_screen = 'pacman main menu'

        while running:
            match game_screen:
                case 'pacman main menu':
                    game_screen = self.pacman_main_menu()

                case 'pacman':
                    game_screen = self.pacman()

                case 'pacman leaderboard':
                    game_screen = self.leaderboard()
                    
                case 'exit':
                    running = False
                    break
                
        return 'main menu'
    
    def pacman_main_menu(self):
        pacman_main_menu = PacmanMenu(self.screen)
        return pacman_main_menu.main_loop()
    
    def pacman(self):
        pacman = Pacman(self.screen)
        return pacman.main_loop()
    
    def leaderboard(self):
        leaderboard = Leaderboard(self.screen)
        return leaderboard.main_loop()
    