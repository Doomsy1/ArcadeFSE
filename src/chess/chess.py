import sys
import pygame

# set directory to src/chess
sys.path.append("src/chess")

from constants import GRID_SIZE
from board import Board

# Constants
FPS = 30


class ChessGame:
    def __init__(self, screen):
        self.screen = screen
        pygame.display.set_caption("Chess Game")
        self.clock = pygame.time.Clock()
        self.board = Board(GRID_SIZE, screen)
        self.turn = 'white'


    def main_loop(self):
        running = True
        while running:
            mouse_up = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "exit"
                if event.type == pygame.MOUSEBUTTONUP:
                    mouse_up = True
                
            
            mx, my = pygame.mouse.get_pos()
            mb = pygame.mouse.get_pressed()



            self.board.update()
            if mouse_up:
                self.board.make_move(mx, my)
            



            pygame.display.flip()
            self.clock.tick(FPS)



