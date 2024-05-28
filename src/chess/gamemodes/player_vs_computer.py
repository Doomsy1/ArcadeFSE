from src.chess.board import Board, Piece
from src.chess.engine import Engine
from tkinter import simpledialog
from constants import *
from time import time
import tkinter as tk
from utils import *
import threading
import pygame
import json



FPS = 60

def file_rank_to_square(file, rank):
    return 8*rank + file

def square_to_file_rank(square):
    return square%8, square//8

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
        current_time = time()
        elapsed_time = current_time - self.start_time

        if self.white_turn:
            self.white_time -= elapsed_time
        else:
            self.black_time -= elapsed_time

        self.start_time = current_time

    def switch_turn(self):
        if self.white_turn:
            self.white_time += self.increment
        else:
            self.black_time += self.increment
        self.white_turn = not self.white_turn

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 255, 255), chess_clock_white_rect)
        pygame.draw.rect(screen, (0, 0, 0), chess_clock_black_rect)

        if self.white_time <= 0:
            white_time_text = '0:00'
        else:
            white_time_text = f'{int(self.white_time//60)}:{int(self.white_time%60):02}'

        if self.black_time <= 0:
            black_time_text = '0:00'
        else:
            black_time_text = f'{int(self.black_time//60)}:{int(self.black_time%60):02}'

        white_time_color = (0, 0, 0) if self.white_turn else (128, 128, 128)
        black_time_color = (255, 255, 255) if not self.white_turn else (128, 128, 128)

        write_centered_text(screen, white_time_text, chess_clock_white_rect, white_time_color)
        write_centered_text(screen, black_time_text, chess_clock_black_rect, black_time_color)


eval_bar_rect = pygame.Rect(BOARD_OFFSET_X + 8*CHESS_GRID_SIZE + 15, BOARD_OFFSET_Y, CHESS_GRID_SIZE//2, 8*CHESS_GRID_SIZE)

class EvalBar:
    def __init__(self):
        self.eval = 0

    def update_eval(self, eval):
        self.eval = eval

    def draw(self, screen):
        # draw a white rectangle on the eval bar
        pygame.draw.rect(screen, (255, 255, 255), eval_bar_rect)

        # draw a black rectangle from the top depending on the eval
        rect_height = int(4*CHESS_GRID_SIZE - 4*CHESS_GRID_SIZE*self.eval/5000)
        rect_height = max(0, rect_height)
        rect_height = min(8*CHESS_GRID_SIZE, rect_height)

        eval_rect = pygame.Rect(eval_bar_rect.x, eval_bar_rect.y, eval_bar_rect.width, rect_height)
        pygame.draw.rect(screen, (32, 32, 32), eval_rect)

        # draw a border around the eval bar
        # pygame.draw.rect(screen, (64, 128, 64), eval_bar_rect, 5)


class PlayerVsComputer:
    def __init__(self, screen):
        self.screen = screen

        self.board = Board()
        
        self.board.load_fen('2b3N1/8/1r2pN1b/1p2kp2/1P1R4/8/4K3/6Q1 w - - 0 1')

        self.selected_square = None

        self.board_image = self.create_board_image()
        self.piece_images = self.load_piece_images()
        self.engine_depth = self.load_engine_depth()
        self.sfx = self.load_sfx()
        self.human_player = self.load_human_player()
        self.start_time_per_side = self.load_start_time_per_side()
        self.increment = self.load_increment()

        self.chess_clock = ChessClock(self.start_time_per_side, self.increment)

        self.annotation_circles = [] # list of squares to draw a circle on
        self.annotation_arrows = [] # list of tuples of squares to draw an arrow from
        self.preview_annotation_start_square = None
        self.preview_annotation_end_square = None

        self.allocated_engine_time = self.start_time_per_side*1000//50 + self.increment*900
        self.engine = Engine(
            self.board, 
            self.engine_depth, 
            time_limit_ms=self.allocated_engine_time)
        self.engine_move_container = []
        self.engine_status = 'idle'

        self.eval_bar = EvalBar()
        
        self.move_list = []

        self.turn = True

        self.clock = pygame.time.Clock()

        self.root = tk.Tk()
        self.root.withdraw()

        self.sfx['game_start'].play()

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

    def load_human_player(self):
        '''Load the human player'''
        with open('src/chess/settings.json', 'r') as file:
            settings = json.load(file)
        
        return settings['human_player']

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
    
    def load_engine_depth(self):
        '''
        Load the engine depth
        '''
        with open('src/chess/settings.json', 'r') as file:
            settings = json.load(file)
        
        return settings['difficulty']
    
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
            rank, file = square_to_file_rank(square)
            color = dark_square_color if (rank + file) % 2 == 1 else light_square_color
            pygame.draw.rect(board_image, color, (rank*CHESS_GRID_SIZE, file*CHESS_GRID_SIZE, CHESS_GRID_SIZE, CHESS_GRID_SIZE))

        return board_image
    
    def draw_board(self):
        '''Draw the chess board'''
        self.screen.blit(self.board_image, (BOARD_OFFSET_X, BOARD_OFFSET_Y))

    def draw_pieces(self):
        '''Draw the chess pieces'''
        # TODO: check if there is a better way to draw the pieces
        for square, piece in enumerate(self.board.board):
            if piece == 0:
                continue
            
            if square == self.selected_square and self.mb[0]:
                continue

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
        '''Draw the legal moves of the selected piece'''
        moves = self.board.generate_legal_moves(self.turn)
        piece_moves = []
        for move in moves:
            start = move[0]
            if start == square:
                piece_moves.append(move)

        return piece_moves
    
    def draw_move_squares(self):
        '''Draw the squares where the selected piece can move to'''
        if self.turn != self.human_player:
            return
        
        if self.selected_square is None:
            return
        
        moves = self.get_square_legal_moves(self.selected_square)
        for move in moves:
            end = move[1]
            capture = move[3]
            if capture:
                color = CAPTURE_SQUARE_COLOR
                alpha = CAPTURE_SQUARE_ALPHA
            else:
                color = MOVE_SQUARE_COLOR
                alpha = MOVE_SQUARE_ALPHA

            x, y = square_to_pixel(end)
            draw_transparent_rect(self.screen, (x, y, CHESS_GRID_SIZE, CHESS_GRID_SIZE), color, alpha)

    def handle_piece_selection(self):
        '''Handle the selection of a piece'''
        if self.selected_square == None:
            if self.left_mouse_down and pixel_on_board(self.mx, self.my):
                if not self.board.is_empty(pixel_to_square(self.mx, self.my)):
                    self.selected_square = pixel_to_square(self.mx, self.my)

        else: # a piece is already selected
            if self.left_mouse_down and pixel_on_board(self.mx, self.my):
                square = pixel_to_square(self.mx, self.my)
                if self.board.is_empty(square):
                    self.selected_square = None
                else:
                    self.selected_square = square

    def draw_selected_piece(self):
        '''Draw the selected piece on the cursor'''
        if self.selected_square != None:
            piece = self.board.get_piece(self.selected_square)
            piece_image = self.piece_images[piece]
            x, y = pygame.mouse.get_pos()
            x -= CHESS_GRID_SIZE//2
            y -= CHESS_GRID_SIZE//2
            self.screen.blit(piece_image, (x, y))

    def promotion_popup(self):
        '''Show a promotion popup'''
        # TODO: add a promotion popup
        pass

    def draw_game_over(self):
        '''Draw the game over screen'''
        full_game_over_rect = pygame.Rect(CHESS_GRID_SIZE*2+BOARD_OFFSET_X, CHESS_GRID_SIZE*3+BOARD_OFFSET_Y, CHESS_GRID_SIZE*4, CHESS_GRID_SIZE*2)

        game_over_rect = pygame.Rect(CHESS_GRID_SIZE*2+BOARD_OFFSET_X, CHESS_GRID_SIZE*3+BOARD_OFFSET_Y, CHESS_GRID_SIZE*4, CHESS_GRID_SIZE)
        game_over_rect_color = (255, 255, 255)
        pygame.draw.rect(self.screen, game_over_rect_color, game_over_rect)

        game_over_text_color = (255, 128, 128)
        write_centered_text(self.screen, "Game Over", game_over_rect, game_over_text_color)

        description_rect = pygame.Rect(CHESS_GRID_SIZE*2+BOARD_OFFSET_X, CHESS_GRID_SIZE*4+BOARD_OFFSET_Y, CHESS_GRID_SIZE*4, CHESS_GRID_SIZE)
        description_rect_color = (255, 255, 255)
        pygame.draw.rect(self.screen, description_rect_color, description_rect)

        description_color = (128, 128, 128)
        if self.board.is_checkmate():
            if self.turn:
                write_centered_text(self.screen, "Checkmate! Black wins", description_rect, description_color)
            else:
                write_centered_text(self.screen, "Checkmate! White wins", description_rect, description_color)
        
        elif self.board.is_stalemate():
            write_centered_text(self.screen, "Stalemate! It's a draw\nClick to return to the main menu", description_rect, description_color)
        
        elif self.chess_clock.white_time <= 0:
            write_centered_text(self.screen, "Time's up! Black wins\nClick to return to the main menu", description_rect, description_color)
        elif self.chess_clock.black_time <= 0:
            write_centered_text(self.screen, "Time's up! White wins\nClick to return to the main menu", description_rect, description_color)

        # draw a border around the full game over rect
        border_color = (0, 0, 0)
        border_width = 4
        pygame.draw.rect(self.screen, border_color, full_game_over_rect, border_width)

        pygame.display.flip()

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
        if self.turn != self.human_player:
            return
        
        if (self.left_mouse_up or self.left_mouse_down) and pixel_on_board(self.mx, self.my):
            square = pixel_to_square(self.mx, self.my)
            if self.selected_square == None:
                return
            
            moves = self.get_square_legal_moves(self.selected_square)
            for move in moves:
                start, end, start_piece, captured_piece, promotion_piece, castling, en_passant = move
                if end != square:
                    continue

                if promotion_piece == 0b0000:
                    if castling != 0b0000:
                        self.sfx['castle'].play()
                    elif captured_piece:
                        self.sfx['capture'].play()
                    else:
                        self.sfx['move'].play()

                else:
                    chosen_promotion_piece = self.promotion_popup()
                    move = (start, end, start_piece, captured_piece, chosen_promotion_piece, castling, en_passant)
                    self.sfx['promotion'].play()

                self.board.make_move(move)
                self.engine.update_board(self.board)
                self.move_list.append(move)

                self.selected_square = None
                self.turn = not self.turn
                self.chess_clock.switch_turn()
                return
                
    def handle_annotations(self):
        '''Handle the annotations of the game (circles, arrows)'''
        if self.left_mouse_down:
            self.annotation_circles = []
            self.annotation_arrows = []

        if self.mb[2]:
            if pixel_on_board(self.rmx, self.rmy):
                start_square = pixel_to_square(self.rmx, self.rmy)
                self.preview_annotation_start_square = start_square

            if pixel_on_board(self.mx, self.my):
                end_square = pixel_to_square(self.mx, self.my)
                self.preview_annotation_end_square = end_square

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
        '''Draw the annotations of the game (circles, arrows)'''

        # draw the circles
        for square in self.annotation_circles:
            self.draw_circle(square, CIRCLE_COLOR, CIRCLE_ALPHA)

        # draw the arrows
        for start, end in self.annotation_arrows:
            self.draw_arrow(start, end, ARROW_COLOR, ARROW_ALPHA)  

        # draw the preview annotation
        if self.preview_annotation_start_square != None:
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

        file_name = f'src/chess/debug_data/move_lists/{len(self.move_list)}_ID{self.board.hash_board(self.turn)}.json'
        with open(file_name, 'w') as file:
            json.dump(self.move_list, file)
    
    def request_engine_move(self):
        '''Request a move from the engine'''

        if self.human_player:
            self.engine.set_time_limit(min(self.chess_clock.black_time*1000//4, self.allocated_engine_time))
        else:
            self.engine.set_time_limit(min(self.chess_clock.white_time*1000//4, self.allocated_engine_time))

        self.engine_move_container = []
        threading.Thread(target=self.engine.find_best_move, args=(self.engine_move_container,)).start()
        # self.engine.find_best_move(self.engine_move_container) # for debugging purposes

    def draw_latest_engine_move(self):
        '''Draw the latest move of the engine'''

        if self.turn == self.human_player:
            return

        if len(self.engine_move_container) == 0:
            return
        
        move = self.engine_move_container[-1][0]
        if move is None:
            return
        
        start = move[0]
        end = move[1]

        # draw an arrow from the start square to the end square
        self.draw_arrow(start, end, ENGINE_SUGGESTION_COLOR, ENGINE_SUGGESTION_ALPHA)

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

        self.draw_latest_engine_move()

        self.chess_clock.draw(self.screen)

        self.eval_bar.draw(self.screen)

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
            self.engine.update_board(self.board)
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
                    if self.turn == self.human_player and len(self.move_list) > 1:
                        self.sfx['move'].play()
                        self.board.undo_move()
                        self.board.undo_move()
                        self.engine.update_board(self.board)
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
        return False
    
    def handle_engine(self):
        # TODO: add a feature to have the engine think on the human player's turn
        if self.engine_status == 'idle':
            if self.turn != self.human_player: # if it is the engine's turn
                self.engine_status = 'thinking'
                self.request_engine_move()

        elif self.engine_status == 'thinking':
            if len(self.engine_move_container) > self.previous_depth:
                self.previous_depth = len(self.engine_move_container)
                move_confirmation = self.engine_move_container[-1][2]
                if move_confirmation:
                    move = self.engine_move_container[-1][0]
                    self.board.make_move(move)
                    self.engine.update_board(self.board)
                    self.move_list.append(move)
                    self.sfx['move'].play()
                    self.turn = not self.turn
                    self.chess_clock.switch_turn()
                    self.engine_status = 'idle'
                    self.previous_depth = 0

    def update_eval_bar(self):
        '''Update the eval bar'''
        # print(self.engine_move_container)
        if self.turn == self.human_player:
            return
        
        if len(self.engine_move_container) == 0:
            return
        
        eval = self.engine_move_container[-1][1]
        if eval is None:
            return

        self.eval_bar.update_eval(eval)

    def is_game_over(self):
        '''Check if the game is over from the board or the chess clock'''
        if self.board.is_game_over():
            return True
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

            self.handle_annotations()
            self.handle_move()
            self.handle_piece_selection()


            self.update_eval_bar()
            self.handle_engine()

            self.draw_game()

            if self.is_game_over():
                self.sfx['game_over'].play()
                return self.draw_game_over()

            if self.mb[0]:
                self.draw_selected_piece()

            # set the title of the window to the fps
            pygame.display.set_caption(f'Chess | FPS: {int(self.clock.get_fps())}')
            self.clock.tick(FPS)
            
            pygame.display.flip()