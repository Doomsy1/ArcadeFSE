from src.chess.board import Board, Piece
from tkinter import simpledialog
from constants import *
from time import time
import tkinter as tk
from utils import *
import pygame
import json

back_button = {
    'text': 'Back',
    'rect': pygame.Rect(300, 880, 200, 100),
    'action': 'chess main menu',
    'base_color': (0, 206, 209),
    'hover_color': (64, 224, 208),
    'clicked_color': (0, 139, 139),
    'text_color': (255, 255, 255),
    'description': 'Return to the main menu'
}

FPS = 60

def file_rank_to_square(file, rank):
    '''Convert a file and rank to a square number'''
    return 8*rank + file

def square_to_file_rank(square):
    '''Convert a square number to a file and rank'''
    if square is None:
        return 0, 0
    return square % 8, square // 8

def square_to_pixel(square):
    '''Convert a square number to a pixel position on the screen'''
    file, rank = square_to_file_rank(square)
    return (file*CHESS_GRID_SIZE + BOARD_OFFSET_X, (7-rank)*CHESS_GRID_SIZE + BOARD_OFFSET_Y)

def pixel_to_square(x, y):
    '''Convert a pixel position on the screen to a square number'''
    file = (x - BOARD_OFFSET_X) // CHESS_GRID_SIZE
    rank = 7 - (y - BOARD_OFFSET_Y) // CHESS_GRID_SIZE
    return file_rank_to_square(file, rank)

def pixel_on_board(x, y):
    '''Check if a pixel position is on the board'''
    file_on_board = BOARD_OFFSET_X <= x <= BOARD_OFFSET_X + 8*CHESS_GRID_SIZE
    rank_on_board = BOARD_OFFSET_Y <= y <= BOARD_OFFSET_Y + 8*CHESS_GRID_SIZE
    return file_on_board and rank_on_board

# white on bottom, black on top
chess_clock_white_rect = pygame.Rect(BOARD_OFFSET_X - CHESS_GRID_SIZE - 15, BOARD_OFFSET_Y + 4*CHESS_GRID_SIZE, CHESS_GRID_SIZE, CHESS_GRID_SIZE)
chess_clock_black_rect = pygame.Rect(BOARD_OFFSET_X - CHESS_GRID_SIZE - 15, BOARD_OFFSET_Y + 3*CHESS_GRID_SIZE, CHESS_GRID_SIZE, CHESS_GRID_SIZE)

class ChessClock:
    def __init__(self, start_time_per_side, increment):
        self.white_time = start_time_per_side + 1
        self.black_time = start_time_per_side
        self.increment = increment

        self.white_turn = True

        self.start_time = time()

    def update(self):
        # update the time of the player whose turn it is
        current_time = time()
        elapsed_time = current_time - self.start_time

        if self.white_turn:
            self.white_time -= elapsed_time
        else:
            self.black_time -= elapsed_time

        # update the start time
        self.start_time = current_time

    def switch_turn(self):
        # switch the turn and add the increment to the time of the player whose turn it is
        if self.white_turn:
            self.white_time += self.increment
        else:
            self.black_time += self.increment
        self.white_turn = not self.white_turn

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 255, 255), chess_clock_white_rect)
        pygame.draw.rect(screen, (0, 0, 0), chess_clock_black_rect)

        # draw the time of the player whose turn it is
        if self.white_time <= 0:
            white_time_text = '0:00'
        else:
            white_time_text = f'{int(self.white_time//60)}:{int(self.white_time%60):02}'

        if self.black_time <= 0:
            black_time_text = '0:00'
        else:
            black_time_text = f'{int(self.black_time//60)}:{int(self.black_time%60):02}'

        # set the color of the time text depending on whose turn it is
        white_time_color = (0, 0, 0) if self.white_turn else (128, 128, 128)
        black_time_color = (255, 255, 255) if not self.white_turn else (128, 128, 128)

        # draw the time text
        write_centered_text(screen, white_time_text, chess_clock_white_rect, white_time_color)
        write_centered_text(screen, black_time_text, chess_clock_black_rect, black_time_color)


class PlayerVsPlayer:
    def __init__(self, screen):
        self.screen = screen

        self.board = Board()
        
        self.selected_square = None

        self.board_image = self.create_board_image()
        self.piece_images = self.load_piece_images()
        self.sfx = self.load_sfx()
        self.turn = True
        self.start_time_per_side = self.load_start_time_per_side()
        self.increment = self.load_increment()

        self.chess_clock = ChessClock(self.start_time_per_side, self.increment)

        self.annotation_circles = [] # list of squares to draw a circle on
        self.annotation_arrows = [] # list of tuples of squares to draw an arrow from
        self.preview_annotation_start_square = None
        self.preview_annotation_end_square = None

        self.move_list = []

        self.clock = pygame.time.Clock()

        self.root = tk.Tk()
        self.root.withdraw()

        self.sfx['game_start'].play()

        self.back_button = Button(
            screen = self.screen,
            text = back_button['text'],
            rect = back_button['rect'],
            action = back_button['action'],
            base_color = back_button['base_color'],
            hover_color = back_button['hover_color'],
            clicked_color = back_button['clicked_color'],
            text_color = back_button['text_color'],
            descriptive_text = back_button['description']
        )

    def load_start_time_per_side(self):
        '''Load the start time per side'''
        with open('src/chess/settings.json', 'r') as file:
            settings = json.load(file)
        
        return settings['time_per_side']
    
    def load_increment(self):
        '''Load the increment'''
        with open('src/chess/settings.json', 'r') as file:
            settings = json.load(file)
        
        return settings['time_increment']

    def load_piece_images(self):
        '''
        Load the piece images
        '''
        file_path = 'src/chess/assets/pieces/'
        piece_images = {
            Piece.white | Piece.pawn: pygame.image.load(f'{file_path}white_pawn.png'),
            Piece.white | Piece.knight: pygame.image.load(f'{file_path}white_knight.png'),
            Piece.white | Piece.bishop: pygame.image.load(f'{file_path}white_bishop.png'),
            Piece.white | Piece.rook: pygame.image.load(f'{file_path}white_rook.png'),
            Piece.white | Piece.queen: pygame.image.load(f'{file_path}white_queen.png'),
            Piece.white | Piece.king: pygame.image.load(f'{file_path}white_king.png'),

            Piece.black | Piece.pawn: pygame.image.load(f'{file_path}black_pawn.png'),
            Piece.black | Piece.knight: pygame.image.load(f'{file_path}black_knight.png'),
            Piece.black | Piece.bishop: pygame.image.load(f'{file_path}black_bishop.png'),
            Piece.black | Piece.rook: pygame.image.load(f'{file_path}black_rook.png'),
            Piece.black | Piece.queen: pygame.image.load(f'{file_path}black_queen.png'),
            Piece.black | Piece.king: pygame.image.load(f'{file_path}black_king.png')
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

        volume = settings['volume']/100
        for sound in sfx:
            sfx[sound].set_volume(volume)

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

        for square in range(64):
            file, rank = square_to_file_rank(square)
            color = dark_square_color if (rank + file) % 2 == 1 else light_square_color
            pygame.draw.rect(board_image, color, (rank*CHESS_GRID_SIZE, file*CHESS_GRID_SIZE, CHESS_GRID_SIZE, CHESS_GRID_SIZE))

        return board_image
    
    def draw_board(self):
        '''Draw the chess board'''
        self.screen.blit(self.board_image, (BOARD_OFFSET_X, BOARD_OFFSET_Y))

    def draw_pieces(self):
        '''Draw the chess pieces'''
        for square, piece in enumerate(self.board.board):
            if piece == 0:
                continue
            
            if square == self.selected_square and self.mb[0]:
                continue

            # draw the piece on the square
            piece_image = self.piece_images[piece]
            x, y = square_to_pixel(square)
            self.screen.blit(piece_image, (x, y))

    def draw_selected_square(self):
        '''Draw the selected square'''
        if self.selected_square is not None:
            x, y = square_to_pixel(self.selected_square)

            # draw a transparent square on the selected square
            draw_transparent_rect(self.screen, (x, y, CHESS_GRID_SIZE, CHESS_GRID_SIZE), SELECTED_SQUARE_COLOR, SELECTED_SQUARE_ALPHA)

    def get_square_legal_moves(self, square):
        '''Get the legal moves of a piece on a square'''
        moves = self.board.generate_legal_moves()
        piece_moves = []
        for move in moves:
            start = move[0]
            if start == square:
                piece_moves.append(move)

        return piece_moves
    
    def draw_move_squares(self):
        '''Draw the squares where the selected piece can move to'''
        # if no piece is selected, return
        if self.selected_square is None:
            return
        
        if (Piece.get_color(self.board.get_piece(self.selected_square)) == Piece.white) != self.turn:
                return
        
        moves = self.get_square_legal_moves(self.selected_square)
        for move in moves:
            end = move[1]
            capture = move[3]
            en_passant = move[6]

            # draw a transparent square on the end square
            if capture or en_passant:
                color = CAPTURE_SQUARE_COLOR
                alpha = CAPTURE_SQUARE_ALPHA
            else:
                color = MOVE_SQUARE_COLOR
                alpha = MOVE_SQUARE_ALPHA

            x, y = square_to_pixel(end)
            draw_transparent_rect(self.screen, (x, y, CHESS_GRID_SIZE, CHESS_GRID_SIZE), color, alpha)

    def handle_piece_selection(self):
        '''Handle the selection of a piece'''
        if self.selected_square == None: # no piece is selected
            if self.left_mouse_down and pixel_on_board(self.mx, self.my): # if the left mouse button is down and the mouse is on the board
                if not self.board.is_empty(pixel_to_square(self.mx, self.my)): # if there is a piece on the square
                    self.selected_square = pixel_to_square(self.mx, self.my)

        else: # a piece is already selected
            if self.left_mouse_down and pixel_on_board(self.mx, self.my): # if the left mouse button is down and the mouse is on the board
                square = pixel_to_square(self.mx, self.my)
                # if the selected square is the same as the square the mouse is on, deselect the piece
                if self.board.is_empty(square):
                    self.selected_square = None
                else:
                    self.selected_square = square

    def draw_selected_piece(self):
        '''Draw the selected piece on the cursor'''
        # if a piece is selected, draw the piece on the cursor
        if self.selected_square != None:
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
                'white': Piece.white | Piece.knight,
                'black': Piece.black | Piece.knight,
                'rect': pygame.Rect(200, 200, 100, 100)
            },
            'bishop': {
                'white': Piece.white | Piece.bishop,
                'black': Piece.black | Piece.bishop,
                'rect': pygame.Rect(200, 300, 100, 100)
            },
            'rook': {
                'white': Piece.white | Piece.rook,
                'black': Piece.black | Piece.rook,
                'rect': pygame.Rect(300, 200, 100, 100)
            },
            'queen': {
                'white': Piece.white | Piece.queen,
                'black': Piece.black | Piece.queen,
                'rect': pygame.Rect(300, 300, 100, 100)
            }
        }

        promotion_box_rect = pygame.Rect(200, 200, 200, 200)

        promotion_piece = 0b0000 # the piece to promote to
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

                    # if the left mouse button is clicked, return the promotion piece
                    if mb[0]:
                        promotion_piece = promotion_choices[choice]['white'] if self.turn else promotion_choices[choice]['black']
                        return promotion_piece
                    
                # draw the piece on the promotion choice
                if self.turn:
                    piece = promotion_choices[choice]['white']
                else:
                    piece = promotion_choices[choice]['black']
                piece_image = self.piece_images[piece]
                self.screen.blit(piece_image, promotion_choices[choice]['rect'].topleft)

            pygame.display.flip()

    def draw_game_over(self):
        '''Draw the game over screen'''
        full_game_over_rect = pygame.Rect(CHESS_GRID_SIZE*2+BOARD_OFFSET_X, CHESS_GRID_SIZE*3+BOARD_OFFSET_Y, CHESS_GRID_SIZE*4, CHESS_GRID_SIZE*2)

        # draw a white rectangle on the full game over rect
        game_over_rect = pygame.Rect(CHESS_GRID_SIZE*2+BOARD_OFFSET_X, CHESS_GRID_SIZE*3+BOARD_OFFSET_Y, CHESS_GRID_SIZE*4, CHESS_GRID_SIZE)
        game_over_rect_color = (255, 255, 255)
        pygame.draw.rect(self.screen, game_over_rect_color, game_over_rect)

        # draw the game over text
        game_over_text_color = (255, 128, 128)
        write_centered_text(self.screen, "Game Over", game_over_rect, game_over_text_color)

        # draw the description rect
        description_rect = pygame.Rect(CHESS_GRID_SIZE*2+BOARD_OFFSET_X, CHESS_GRID_SIZE*4+BOARD_OFFSET_Y, CHESS_GRID_SIZE*4, CHESS_GRID_SIZE)
        description_rect_color = (255, 255, 255)
        pygame.draw.rect(self.screen, description_rect_color, description_rect)

        # draw the description text
        description_color = (128, 128, 128)
        if self.board.is_checkmate():
            if self.turn:
                write_centered_text(self.screen, "Checkmate! Black wins", description_rect, description_color)
            else:
                write_centered_text(self.screen, "Checkmate! White wins", description_rect, description_color)
        
        elif self.board.is_stalemate():
            write_centered_text(self.screen, "Stalemate! It's a draw\nClick to return to the main menu", description_rect, description_color)

        elif self.board.is_insufficient_material():
            write_centered_text(self.screen, "Insufficient material! It's a draw\nClick to return to the main menu", description_rect, description_color)

        elif self.board.is_threefold_repetition():
            write_centered_text(self.screen, "Draw by repetition! It's a draw\nClick to return to the main menu", description_rect, description_color)
        
        elif self.chess_clock.white_time <= 0:
            write_centered_text(self.screen, "Time's up! Black wins\nClick to return to the main menu", description_rect, description_color)
        elif self.chess_clock.black_time <= 0:
            write_centered_text(self.screen, "Time's up! White wins\nClick to return to the main menu", description_rect, description_color)

        # draw a border around the full game over rect
        border_color = (0, 0, 0)
        border_width = 4
        pygame.draw.rect(self.screen, border_color, full_game_over_rect, border_width)

        pygame.display.flip()

        # save the game to a json file
        # self.export_move_list()

        # wait for the user to click
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 'chess main menu'
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return 'chess main menu'
                if event.type == pygame.MOUSEBUTTONDOWN:
                    return 'chess main menu'
                
    def handle_move(self):
        '''Handle the move of a piece'''
        # if the left mouse button is up or down and the mouse is on the board
        if (self.left_mouse_up or self.left_mouse_down) and pixel_on_board(self.mx, self.my):
            square = pixel_to_square(self.mx, self.my)
            if self.selected_square == None:
                return

            if (Piece.get_color(self.board.get_piece(self.selected_square)) == Piece.white) != self.turn:
                return
            
            # if the selected square is the same as the square the mouse is on, return
            moves = self.get_square_legal_moves(self.selected_square)
            for move in moves:
                start, end, start_piece, captured_piece, promotion_piece, castling, en_passant = move
                if end != square:
                    continue

                # if the move is a promotion, show a popup to choose the promotion piece
                if promotion_piece == 0b0000:
                    if castling != 0b0000:
                        self.sfx['castle'].play()
                    elif captured_piece:
                        self.sfx['capture'].play()
                    else:
                        self.sfx['move'].play()

                # if the move is a promotion, show a popup to choose the promotion piece
                else:
                    chosen_promotion_piece = self.promotion_popup()
                    move = (start, end, start_piece, captured_piece, chosen_promotion_piece, castling, en_passant)
                    self.sfx['promotion'].play()

                # make the move
                self.board.make_move(move)
                self.move_list.append(move)

                # switch the turn
                self.selected_square = None
                self.turn = not self.turn
                self.chess_clock.switch_turn()
                return
                
    def handle_annotations(self):
        '''Handle the annotations of the game (circles, arrows)'''
        # if the left mouse button is down, clear the annotations
        if self.left_mouse_down:
            self.annotation_circles = []
            self.annotation_arrows = []

        # if the right mouse button is down, set the start square of the preview annotation
        if self.mb[2]:
            if pixel_on_board(self.rmx, self.rmy):
                start_square = pixel_to_square(self.rmx, self.rmy)
                self.preview_annotation_start_square = start_square

            if pixel_on_board(self.mx, self.my):
                end_square = pixel_to_square(self.mx, self.my)
                self.preview_annotation_end_square = end_square

        # if the right mouse button is up, add the preview annotation to the annotations
        if self.right_mouse_up:
            if pixel_on_board(self.rmx, self.rmy) and pixel_on_board(self.mx, self.my):
                start_square = self.preview_annotation_start_square
                end_square = self.preview_annotation_end_square

                if start_square == end_square:
                    circle = start_square
                    if start_square in self.annotation_circles:
                        self.annotation_circles.remove(circle)
                    else:
                        self.annotation_circles.append(start_square)

                else:
                    arrow = (start_square, end_square)
                    if (start_square, end_square) in self.annotation_arrows:
                        self.annotation_arrows.remove(arrow)
                    else:
                        self.annotation_arrows.append((start_square, end_square))
                
            self.preview_annotation_start_square = None
            self.preview_annotation_end_square = None

    def draw_arrow(self, start, end, color, alpha):
        '''Draw an arrow from the start square to the end square'''
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
        '''Draw a circle on a square'''
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
        '''Draw the annotations of the game (circles, arrows)'''
        # draw the circles
        for square in self.annotation_circles:
            self.draw_circle(square, CIRCLE_COLOR, CIRCLE_ALPHA)

        # draw the arrows
        for start, end in self.annotation_arrows:
            self.draw_arrow(start, end, ARROW_COLOR, ARROW_ALPHA)  

        # draw the preview annotation
        if self.preview_annotation_start_square is not None:
            if self.preview_annotation_start_square == self.preview_annotation_end_square:
                self.draw_circle(self.preview_annotation_start_square, CIRCLE_COLOR, CIRCLE_ALPHA)
            else:
                self.draw_arrow(self.preview_annotation_start_square, self.preview_annotation_end_square, ARROW_COLOR, ARROW_ALPHA)

    def draw_previous_move(self):
        '''Draw the previous move of the game'''

        if len(self.move_list) == 0:
            return
        move = self.move_list[-1]
        start = move[0]
        end = move[1]
        # draw a transparent square on the end square
        x, y = square_to_pixel(end)
        draw_transparent_rect(self.screen, (x, y, CHESS_GRID_SIZE, CHESS_GRID_SIZE), PREVIOUS_MOVE_COLOR, PREVIOUS_MOVE_ALPHA)

        # draw a transparent rect on the start square
        x, y = square_to_pixel(start)
        draw_transparent_rect(self.screen, (x, y, CHESS_GRID_SIZE, CHESS_GRID_SIZE), PREVIOUS_MOVE_COLOR, PREVIOUS_MOVE_ALPHA)

    def export_move_list(self):
        '''Export the move list to a json file'''

        # create a folder to store the move lists if it does not exist
        file_name = f'src/chess/debug_data/move_lists/{len(self.move_list)}_ID{self.board.hash_board()}.json'
        with open(file_name, 'w') as file:
            json.dump(self.move_list, file)

    def draw_algebraic_notation(self):
        '''
        Draw the algebraic notation of the board
        '''
        p, q = 7, 24
        # draw files
        for file in range(8):
            letter = chr(ord('a') + file)
            x, y = square_to_pixel(file)

            # draw the file letter on the bottom left of the square
            text_x = x + (q - p)*CHESS_GRID_SIZE/q
            text_y = y + (q - p)*CHESS_GRID_SIZE/q
            
            text_rect = pygame.Rect(text_x, text_y, p*CHESS_GRID_SIZE/q, p*CHESS_GRID_SIZE/q)
            # draw a black rectangle behind the text
            pygame.draw.rect(self.screen, (0, 0, 0), text_rect)

            # draw the text
            write_centered_text(self.screen, letter, text_rect, (255, 255, 255))

        for rank in range(8):
            number = str(rank + 1)
            x, y = square_to_pixel(rank*8)

            # draw the rank number on the top right of the square
            text_x = x
            text_y = y

            text_rect = pygame.Rect(text_x, text_y, p*CHESS_GRID_SIZE/q, p*CHESS_GRID_SIZE/q)
            # draw a black rectangle behind the text
            pygame.draw.rect(self.screen, (0, 0, 0), text_rect)

            # draw the text
            write_centered_text(self.screen, number, text_rect, (255, 255, 255))


    def draw_game(self):
        '''
        Draw the chess game
        '''
        self.draw_board()
        
        self.draw_previous_move()

        self.draw_selected_square()

        self.draw_move_squares()

        self.draw_pieces()

        self.draw_annotations()

        self.draw_algebraic_notation()

        self.chess_clock.draw(self.screen)

    def edit_fen(self):
        '''Edit the fen string of the board'''

        current_fen = self.board.create_fen()
        # make a popup window that gets the user to set the FEN of the board
        fen = simpledialog.askstring("Input", "Please enter the FEN:", parent=self.root, initialvalue=current_fen)

        if fen is None:
            return
        
        try:
            # the FEN is then set to the board
            self.board.load_fen(fen)
        except:
            pass

    def handle_events(self):
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
                if event.button == 1: # left click
                    self.lmx, self.lmy = pygame.mouse.get_pos()
                    self.left_mouse_down = True
                if event.button == 3: # right click
                    self.rmx, self.rmy = pygame.mouse.get_pos()
                    self.right_mouse_down = True

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1: # left up
                    self.left_mouse_up = True
                if event.button == 3: #right up
                    self.right_mouse_up = True

            if event.type == pygame.KEYDOWN:
                # if u is pressed, undo the last move and play the move sound effect
                if event.key == pygame.K_u:
                        self.sfx['move'].play()
                        self.board.undo_move()
                        self.board.undo_move()
                        if len(self.move_list) > 1:
                            self.move_list.pop()
                            self.move_list.pop()
                        self.selected_square = None

                # if the s key is pressed, export the move list to a json file
                if event.key == pygame.K_s:
                    self.export_move_list()
                # if the f key is pressed, create a popup to edit the fen string
                if event.key == pygame.K_f:
                    self.edit_fen()
                # if the t key is pressed, give 30 seconds to each player
                if event.key == pygame.K_t:
                    self.chess_clock.white_time += 30
                    self.chess_clock.black_time += 30
        return False
    
    def is_game_over(self):
        '''Check if the game is over from the board or the chess clock'''
        # if the game is over, return True
        if self.board.is_game_over():
            return True
        
        # if the time of a player is less than or equal to 0, return True
        if self.chess_clock.white_time <= 0 or self.chess_clock.black_time <= 0:
            return True

    def main_loop(self):
        running = True

        self.lmx, self.lmy = pygame.mouse.get_pos()
        self.rmx, self.rmy = pygame.mouse.get_pos()
        self.previous_depth = 0 # the depth of the engine in the previous frame
        while running:
            menu_change = self.handle_events()
            if menu_change:
                return menu_change
            
            self.mx, self.my = pygame.mouse.get_pos()
            self.mb = pygame.mouse.get_pressed()

            self.screen.fill((96, 96, 96))

            self.chess_clock.update()

            # handle the events
            self.handle_annotations()
            self.handle_move()
            self.handle_piece_selection()

            self.draw_game()

            # draw the back button
            self.back_button.draw(self.mx, self.my, self.mb)

            # check if the back button is clicked
            action = self.back_button.check_click(self.mx, self.my, self.left_mouse_up)
            if action:
                return action

            # if the game is over, draw the game over screen
            if self.is_game_over():
                self.sfx['game_over'].play()
                return self.draw_game_over()

            if self.mb[0]:
                self.draw_selected_piece()

            # set the title of the window to the fps
            pygame.display.set_caption(f'Chess | FPS: {int(self.clock.get_fps())}')
            self.clock.tick(FPS)
            
            pygame.display.flip()