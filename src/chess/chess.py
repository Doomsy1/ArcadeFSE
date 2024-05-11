import sys
import pygame

# set directory to src/chess
sys.path.append("src/chess")

from board import Board

# Constants
FPS = 30


class ChessGame:
    def __init__(self, screen):
        self.screen = screen
        pygame.display.set_caption("Chess Game")
        self.clock = pygame.time.Clock()
        self.board = Board()
        self.board.load_images(self.screen)


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
                row, col = self.board.get_row_col(mx, my)
                self.board.make_move(row, col)
            



            pygame.display.flip()
            self.clock.tick(FPS)



