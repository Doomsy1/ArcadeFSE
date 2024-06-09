from src.chess.gamemodes.player_vs_computer import PlayerVsComputer
from src.chess.menus.main_chess_menu import ChessMainMenu
from src.chess.menus.chess_settings_menu import ChessSettingsMenu
from src.chess.gamemodes.player_vs_player import PlayerVsPlayer

class ChessGame:
    def __init__(self, screen):
        self.screen = screen

    def main_loop(self):
        running = True
        game_screen = 'chess main menu'

        while running:
            match game_screen:
                case 'chess main menu':
                    game_screen = self.main_chess_menu()

                case 'chess settings menu':
                    game_screen = self.chess_settings_menu()

                case 'player vs player':
                    game_screen = self.player_vs_player()

                case 'player vs computer':
                    game_screen = self.player_vs_computer()
                    
                case 'exit':
                    running = False
                    break

        return 'main menu'
    
    def main_chess_menu(self):
        main_chess_menu = ChessMainMenu(self.screen)
        return main_chess_menu.main_loop()
    
    def chess_settings_menu(self):
        chess_settings_menu = ChessSettingsMenu(self.screen)
        return chess_settings_menu.main_loop()

    def player_vs_player(self):
        player_vs_player = PlayerVsPlayer(self.screen)
        return player_vs_player.main_loop()

    def player_vs_computer(self):
        player_vs_computer = PlayerVsComputer(self.screen)
        return player_vs_computer.main_loop()