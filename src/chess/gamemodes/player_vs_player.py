import json
import pygame
from constants import *
from src.chess.board import Board, decode_move, LEGAL_SQUARES, encode_move
from utils import *





class PlayerVsPlayer:
    def __init__(self, screen):
        self.screen = screen
        self.selected_square = 127

        self.board_image = self.create_board_image()
        self.piece_images = self.load_piece_images()
        self.sfx = self.load_sfx()

        self.circles = [] # (square)
        self.arrows = [] # (start_square, end_square)
        self.preview_annotation_start = 127
        self.preview_annotation_end = 127

        self.turn = True # True for white, False for black

        self.board = Board()

        # play the game start sound effect
        self.sfx['game_start'].play()

    def load_piece_images(self):
        '''
        Load the piece images
        '''
        file_path = 'src/chess/assets/pieces/'
        piece_images = {
            0b1001: pygame.image.load(f'{file_path}white_pawn.png'),
            0b1010: pygame.image.load(f'{file_path}white_knight.png'),
            0b1011: pygame.image.load(f'{file_path}white_bishop.png'),
            0b1100: pygame.image.load(f'{file_path}white_rook.png'),
            0b1101: pygame.image.load(f'{file_path}white_queen.png'),
            0b1110: pygame.image.load(f'{file_path}white_king.png'),

            0b0001: pygame.image.load(f'{file_path}black_pawn.png'),
            0b0010: pygame.image.load(f'{file_path}black_knight.png'),
            0b0011: pygame.image.load(f'{file_path}black_bishop.png'),
            0b0100: pygame.image.load(f'{file_path}black_rook.png'),
            0b0101: pygame.image.load(f'{file_path}black_queen.png'),
            0b0110: pygame.image.load(f'{file_path}black_king.png')
        }

        for piece in piece_images:
            piece_images[piece] = pygame.transform.scale(piece_images[piece], (CHESS_GRID_SIZE, CHESS_GRID_SIZE))

        return piece_images
    
    def load_sfx(self):
        '''
        Load the sound effects
        '''
        # initialize the mixer
        pygame.mixer.init()

        # open settings.json to get the volume of the sound effects
        with open('src/chess/settings.json', 'r') as file:
            settings = json.load(file)

        # set the volume of the sound effects
        pygame.mixer.music.set_volume(settings['volume'])

        file_path = 'src/chess/assets/sfx/'
        sfx = {
            'move': pygame.mixer.Sound(f'{file_path}move.mp3'),
            'capture': pygame.mixer.Sound(f'{file_path}capture.mp3'),
            'castle': pygame.mixer.Sound(f'{file_path}castle.mp3'),
            'check': pygame.mixer.Sound(f'{file_path}check.mp3'),
            'game_over': pygame.mixer.Sound(f'{file_path}game_over.mp3'),
            'game_start': pygame.mixer.Sound(f'{file_path}game_start.mp3'),
            'promotion': pygame.mixer.Sound(f'{file_path}promotion.mp3')
        }

        return sfx

    def create_board_image(self):
        '''
        Create a chess board image
        '''
        # open settings.json
        with open('src/chess/settings.json', 'r') as file:
            settings = json.load(file)

        dark_square_color = tuple(settings['dark_square_color'].values())
        light_square_color = tuple(settings['light_square_color'].values())

        # create a chess board image
        board_image = pygame.Surface((CHESS_GRID_SIZE*8, CHESS_GRID_SIZE*8))

        for square in LEGAL_SQUARES:
            rank, file = square_to_file_rank(square)
            color = dark_square_color if (rank + file) % 2 == 1 else light_square_color
            pygame.draw.rect(board_image, color, (rank*CHESS_GRID_SIZE, file*CHESS_GRID_SIZE, CHESS_GRID_SIZE, CHESS_GRID_SIZE))

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
        # piece bitboard are 0x88 board representation
        for square in LEGAL_SQUARES:
            if self.board.is_empty(square):
                continue
            
            if square == self.selected_square and self.mb[0]:
                continue

            piece = self.board.get_piece(square)
            piece_image = self.piece_images[piece]
            x, y = square_to_pixel(square)
            self.screen.blit(piece_image, (x, y))

    def draw_selected_square(self):
        '''
        Draw the selected square'''
        if self.selected_square != 127:
            x, y = square_to_pixel(self.selected_square)

            # draw a transparent square on the selected square
            draw_transparent_rect(self.screen, (x, y, CHESS_GRID_SIZE, CHESS_GRID_SIZE), SELECTED_SQUARE_COLOR, SELECTED_SQUARE_ALPHA)

    def get_square_legal_moves(self, square):
        '''
        Get the legal moves of a piece
        '''
        moves = self.board.generate_legal_moves(self.turn)
        piece_moves = []
        for move in moves:
            start, _, _, _, _, _, _, _ = decode_move(move)
            if start == square:
                piece_moves.append(move)

        return piece_moves

    def draw_move_squares(self):
        '''
        Draw the squares where the selected piece can move to
        '''
        if self.selected_square != 127:
            moves = self.get_square_legal_moves(self.selected_square)
            for move in moves:
                _, end, _, _, _, _, capture, _ = decode_move(move)
                if capture:
                    color = CAPTURE_SQUARE_COLOR
                    alpha = CAPTURE_SQUARE_ALPHA
                else:
                    color = MOVE_SQUARE_COLOR
                    alpha = MOVE_SQUARE_ALPHA

                x, y = square_to_pixel(end)
                draw_transparent_rect(self.screen, (x, y, CHESS_GRID_SIZE, CHESS_GRID_SIZE), color, alpha)

    def handle_piece_selection(self):
        '''
        Handle the selection of a piece
        '''
        if self.selected_square == 127:
            if self.left_mouse_down and pixel_on_board(self.mx, self.my):
                if not self.board.is_empty(pixel_to_square(self.mx, self.my)):
                    self.selected_square = pixel_to_square(self.mx, self.my)

        else: # a piece is already selected
            if self.left_mouse_down and pixel_on_board(self.mx, self.my):
                square = pixel_to_square(self.mx, self.my)
                if self.board.is_empty(square):
                    self.selected_square = 127
                else:
                    self.selected_square = square

    def draw_selected_piece(self):
        '''
        Draw the selected piece on the cursor
        '''
        if self.selected_square != 127:
            piece = self.board.get_piece(self.selected_square)
            piece_image = self.piece_images[piece]
            x, y = pygame.mouse.get_pos()
            x -= CHESS_GRID_SIZE//2
            y -= CHESS_GRID_SIZE//2
            self.screen.blit(piece_image, (x, y))

    def promotion_popup(self):
        '''
        Display a promotion popup
        '''
        promotion_choices = {
            'knight': {
                'white': 0b1010,
                'black': 0b0010,
                'rect': pygame.Rect(200, 200, 100, 100)
            },
            'bishop': {
                'white': 0b1011,
                'black': 0b0011,
                'rect': pygame.Rect(200, 300, 100, 100)
            },
            'rook': {
                'white': 0b1100,
                'black': 0b0100,
                'rect': pygame.Rect(300, 200, 100, 100)
            },
            'queen': {
                'white': 0b1101,
                'black': 0b0101,
                'rect': pygame.Rect(300, 300, 100, 100)
            }
        }

        promotion_box_rect = pygame.Rect(200, 200, 200, 200)

        promotion_piece = 0b0000
        while promotion_piece == 0b0000:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 'chess main menu'
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return 'chess main menu'

            mx, my = pygame.mouse.get_pos()
            mb = pygame.mouse.get_pressed()
            # draw the promotion popup background
            pygame.draw.rect(self.screen, (128, 128, 128), promotion_box_rect)

            # draw the promotion choices
            for choice in promotion_choices:
                pygame.draw.rect(self.screen, (255, 255, 255), promotion_choices[choice]['rect'])
                if promotion_choices[choice]['rect'].collidepoint(mx, my):
                    pygame.draw.rect(self.screen, (255, 0, 0), promotion_choices[choice]['rect'], 5)

                    if mb[0]:
                        promotion_piece = promotion_choices[choice]['white'] if self.turn else promotion_choices[choice]['black']
                        return promotion_piece
                    
                if self.turn:
                    piece = promotion_choices[choice]['white']
                else:
                    piece = promotion_choices[choice]['black']
                piece_image = self.piece_images[piece]
                self.screen.blit(piece_image, promotion_choices[choice]['rect'].topleft)

            pygame.display.flip()

    def handle_move(self):
        '''
        Handle the move of a piece
        '''
        if (self.left_mouse_up or self.left_mouse_down) and pixel_on_board(self.mx, self.my):
            square = pixel_to_square(self.mx, self.my)
            if self.selected_square != 127:
                moves = self.get_square_legal_moves(self.selected_square)
                for move in moves:
                    start, end, start_piece, captured_piece, promotion_piece, castling, capture, en_passant = decode_move(move)
                    if end == square:
                        if promotion_piece == 0b0000:
                            self.board.make_move(move)

                            if castling != 0b0000:
                                self.sfx['castle'].play()
                            elif capture:
                                self.sfx['capture'].play()
                            else:
                                self.sfx['move'].play()

                            self.selected_square = 127
                            self.turn = not self.turn
                            return
                        else:
                            chosen_promotion_piece = self.promotion_popup()
                            move = encode_move(start, end, start_piece, captured_piece, chosen_promotion_piece, castling, capture, en_passant)
                            self.board.make_move(move)
                            
                            self.sfx['promotion'].play()

                            self.selected_square = 127
                            self.turn = not self.turn
                            return
          
    def handle_annotations(self):
        '''
        Handle the annotations of the game (circles, arrows)
        '''
        if self.left_mouse_down:
            self.circles = []
            self.arrows = []

        if self.mb[2]:
            if pixel_on_board(self.rmx, self.rmy):
                start_square = pixel_to_square(self.rmx, self.rmy)
                self.preview_annotation_start = start_square

            if pixel_on_board(self.mx, self.my):
                end_square = pixel_to_square(self.mx, self.my)
                self.preview_annotation_end = end_square

        if self.right_mouse_up:
            if pixel_on_board(self.rmx, self.rmy) and pixel_on_board(self.mx, self.my):
                start_square = self.preview_annotation_start
                end_square = self.preview_annotation_end

                if start_square == end_square:
                    circle = start_square
                    if start_square in self.circles:
                        self.circles.remove(circle)
                    else:
                        self.circles.append(start_square)

                else:
                    arrow = (start_square, end_square)
                    if (start_square, end_square) in self.arrows:
                        self.arrows.remove(arrow)
                    else:
                        self.arrows.append((start_square, end_square))
                
            self.preview_annotation_start = 127
            self.preview_annotation_end = 127
            
    def draw_arrow(self, start, end, color, alpha):
        start_x, start_y = square_to_pixel(start)
        end_x, end_y = square_to_pixel(end)
        draw_arrow(
            screen=self.screen,
            start=(start_x + CHESS_GRID_SIZE//2, start_y + CHESS_GRID_SIZE//2),
            end=(end_x + CHESS_GRID_SIZE//2, end_y + CHESS_GRID_SIZE//2),
            tail_start_offset=ARROW_TAIL_START_OFFSET,
            tail_width=TAIL_WIDTH,
            head_width=HEAD_WIDTH,
            head_height=HEAD_HEIGHT,
            color=color,
            alpha=alpha
        )

    def draw_circle(self, square, color, alpha):
        x, y = square_to_pixel(square)
        draw_transparent_circle(
            screen=self.screen,
            center=(x + CHESS_GRID_SIZE//2, y + CHESS_GRID_SIZE//2),
            radius=CHESS_GRID_SIZE//2,
            color=color,
            alpha=alpha,
            thickness=CIRCLE_THICKNESS
        )

    def draw_annotations(self):
        '''
        Draw the annotations of the game (circles, arrows)
        '''
        # draw the preview annotation
        if self.preview_annotation_start != 127:
            if self.preview_annotation_start == self.preview_annotation_end:
                self.draw_circle(self.preview_annotation_start, CIRCLE_COLOR, CIRCLE_ALPHA)
            else:
                self.draw_arrow(self.preview_annotation_start, self.preview_annotation_end, ARROW_COLOR, ARROW_ALPHA)

        for square in self.circles:
            self.draw_circle(square, CIRCLE_COLOR, CIRCLE_ALPHA)

        for start, end in self.arrows:
            self.draw_arrow(start, end, ARROW_COLOR, ARROW_ALPHA)        

    def draw_game(self):
        '''
        Draw the chess game
        '''
        self.draw_board()

        self.draw_selected_square()

        self.draw_move_squares()

        self.draw_pieces()

        self.draw_annotations()

    def main_loop(self):
        running = True

        self.lmx, self.lmy = pygame.mouse.get_pos()
        self.rmx, self.rmy = pygame.mouse.get_pos()
        while running:
            self.left_mouse_down = False
            self.left_mouse_up = False
            self.right_mouse_down = False
            self.right_mouse_up = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 'chess main menu'
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return 'chess main menu'
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.lmx, self.lmy = pygame.mouse.get_pos()
                        self.left_mouse_down = True
                    if event.button == 3:
                        self.rmx, self.rmy = pygame.mouse.get_pos()
                        self.right_mouse_down = True
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.left_mouse_up = True
                    if event.button == 3:
                        self.right_mouse_up = True
                # if u is pressed, undo the last move and play the move sound effect
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_u:
                        self.sfx['move'].play()
                        self.board.undo_move()
                        self.turn = not self.turn
                        self.selected_square = 127
                
                    
            self.mx, self.my = pygame.mouse.get_pos()
            self.mb = pygame.mouse.get_pressed()

            self.screen.fill((255, 255, 255)) # replace this with a background image

            self.handle_annotations()
            self.handle_move()
            self.handle_piece_selection()

            self.draw_game()
            

            if self.mb[0]:
                self.draw_selected_piece()



            pygame.display.flip()


def file_rank_to_square(file, rank):

    return 16*rank + file

def square_to_file_rank(square):
    return square%16, square//16

def square_to_pixel(square):
    file, rank = square_to_file_rank(square)
    return (file*CHESS_GRID_SIZE + BOARD_OFFSET_X, (7-rank)*CHESS_GRID_SIZE + BOARD_OFFSET_Y)

def pixel_to_square(x, y):
    file = (x - BOARD_OFFSET_X) // CHESS_GRID_SIZE
    rank = 7 - (y - BOARD_OFFSET_Y) // CHESS_GRID_SIZE
    return file_rank_to_square(file, rank)

def pixel_on_board(x, y):
    file_on_board = BOARD_OFFSET_X <= x <= BOARD_OFFSET_X + 8*CHESS_GRID_SIZE
    rank_on_board = BOARD_OFFSET_Y <= y <= BOARD_OFFSET_Y + 8*CHESS_GRID_SIZE
    return file_on_board and rank_on_board