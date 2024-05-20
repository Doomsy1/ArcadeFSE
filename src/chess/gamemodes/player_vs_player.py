import json
import pygame
from constants import *






class PlayerVsPlayer:
    def __init__(self, screen):
        self.screen = screen
        self.selected_square = None

        self.board_image = self.create_board_image()

    
    def create_board_image(self):
        '''
        Create a chess board image
        '''
        # open settings.json
        with open('src/chess/settings.json', 'r') as file:
            settings = json.load(file)

        dark_square_color = (settings['dark_square_color']['r'], settings['dark_square_color']['g'], settings['dark_square_color']['b'])
        light_square_color = (settings['light_square_color']['r'], settings['light_square_color']['g'], settings['light_square_color']['b'])

        # create a chess board image
        board_image = pygame.Surface((CHESS_GRID_SIZE*8, CHESS_GRID_SIZE*8))

        for i in range(8):
            for j in range(8):
                color = dark_square_color if (i+j)%2 == 0 else light_square_color
                
                pygame.draw.rect(board_image, color, pygame.Rect(i*CHESS_GRID_SIZE, j*CHESS_GRID_SIZE, CHESS_GRID_SIZE, CHESS_GRID_SIZE))

        return board_image

    def draw_board(self):
        '''
        Draw the chess board
        '''
        self.screen.blit(self.board_image, (BOARD_OFFSET_X, BOARD_OFFSET_Y))

    def draw_pieces(self):
        '''
        Draw the pieces on the board
        '''
        pass

    def draw_selected_square(self):
        '''
        Draw the selected square'''
        if self.selected_square is not None:
            pass

    def draw_move_squares(self):
        '''
        Draw the squares where the selected piece can move to
        '''
        pass





    def main_loop(self):
        running = True

        self.lmx, self.lmy = pygame.mouse.get_pos()
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 'chess main menu'
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return 'chess main menu'
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.lmx, self.lmy = pygame.mouse.get_pos()
                    
            self.mx, self.my = pygame.mouse.get_pos()

            self.screen.fill((255, 255, 255)) # replace this with a background image

            self.draw_board()






            pygame.display.flip()