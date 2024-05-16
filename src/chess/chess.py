import sys
import pygame

from constants import LIGHT_SQUARE, DARK_SQUARE
from constants import CHESS_OFFSET_X as OFFSET_X, CHESS_OFFSET_Y as OFFSET_Y, CHESS_GRID_SIZE as GRID_SIZE
from constants import SELECTED_SQUARE, MOVE_SQUARE, CAPTURE_SQUARE

from utils import draw_arrow, draw_transparent_circle, draw_transparent_rect, write_centered_text

import tkinter as tk
from tkinter import simpledialog

# set directory to src/chess
sys.path.append("src/chess")

from board import Board, decode_move
from engine import Engine

# Constants
FPS = 9999
EN_PASSANT_ROW = {0: 5, 1: 2}  # Row for en passant for white and black pawns


class ChessGame:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.board = Board()

        self.root = tk.Tk()
        self.root.withdraw()

        self.selected_square = None

        self.cached_legal_moves = {} # stores the legal moves of the board
        self.cached_checkmate_checks = {} # stores calculated checkmate checks

        self.bitboard_display_toggle = False
        self.bitboard_display_index = 0
        
        self.developer_display_toggle = False

        self.engine_suggestion = None

        # self.board.fen_to_board("2k5/Q7/2K5/8/8/8/8/8 w - - 0 1")

        self.load_images()

    def get_moves(self):
        # cache the moves of the board
        fen = self.board.board_to_fen()
        if fen in self.cached_legal_moves:
            return self.cached_legal_moves[fen]
        
        moves = self.board.generate_legal_moves(turn=self.board.white_to_move)
        self.cached_legal_moves[fen] = moves
        return moves

    def is_over_board(self, x, y):
        return OFFSET_X <= x <= OFFSET_X + 8 * GRID_SIZE and OFFSET_Y <= y <= OFFSET_Y + 8 * GRID_SIZE
    
    def set_FEN(self):
        current_fen = self.board.board_to_fen()
        # make a popup window that gets the user to set the FEN of the board
        fen = simpledialog.askstring("Input", "Please enter the FEN:", parent=self.root, initialvalue=current_fen)
        # the FEN is then set to the board
        self.board.fen_to_board(fen)

    def piece_selected(self):
        # return True if a piece is selected
        return self.selected_square is not None

    def draw_arrow(self, start, end, color=MOVE_SQUARE):
        # start and end are tuples with the file and rank of the squares
        start_file, start_rank = start
        end_file, end_rank = end
        start_x = start_file * GRID_SIZE + OFFSET_X + GRID_SIZE // 2
        start_y = (7 - start_rank) * GRID_SIZE + OFFSET_Y + GRID_SIZE // 2
        end_x = end_file * GRID_SIZE + OFFSET_X + GRID_SIZE // 2
        end_y = (7 - end_rank) * GRID_SIZE + OFFSET_Y + GRID_SIZE // 2

        # draw the arrow
        tail_start_offset = GRID_SIZE // 4
        tail_width = GRID_SIZE // 4
        head_width = GRID_SIZE // 2
        head_height = GRID_SIZE // 2.5
        alpha = 160
        draw_arrow(self.screen, (start_x, start_y), (end_x, end_y), tail_start_offset, tail_width, head_width, head_height, color, alpha)

    def draw_circle(self, file, rank):
        # draw the circle
        x_pos = file * GRID_SIZE + OFFSET_X + GRID_SIZE // 2
        y_pos = (7 - rank) * GRID_SIZE + OFFSET_Y + GRID_SIZE // 2
        center = (x_pos, y_pos)
        radius = GRID_SIZE // 2
        color = MOVE_SQUARE
        thickness = 3
        pygame.draw.circle(self.screen, color, center, radius, thickness)
        
    def load_images(self):
        self.piece_imgs = {}

        self.piece_imgs["r"] = pygame.image.load("src/chess/pieces/black_rook.png")
        self.piece_imgs["n"] = pygame.image.load("src/chess/pieces/black_knight.png")
        self.piece_imgs["b"] = pygame.image.load("src/chess/pieces/black_bishop.png")
        self.piece_imgs["q"] = pygame.image.load("src/chess/pieces/black_queen.png")
        self.piece_imgs["k"] = pygame.image.load("src/chess/pieces/black_king.png")
        self.piece_imgs["p"] = pygame.image.load("src/chess/pieces/black_pawn.png")

        self.piece_imgs["R"] = pygame.image.load("src/chess/pieces/white_rook.png")
        self.piece_imgs["N"] = pygame.image.load("src/chess/pieces/white_knight.png")
        self.piece_imgs["B"] = pygame.image.load("src/chess/pieces/white_bishop.png")
        self.piece_imgs["Q"] = pygame.image.load("src/chess/pieces/white_queen.png")
        self.piece_imgs["K"] = pygame.image.load("src/chess/pieces/white_king.png")
        self.piece_imgs["P"] = pygame.image.load("src/chess/pieces/white_pawn.png")

        # scale the images to the grid size
        for img in self.piece_imgs:
            self.piece_imgs[img] = pygame.transform.scale(self.piece_imgs[img], (GRID_SIZE, GRID_SIZE))

    def get_square(self, x, y):
        # get the file and rank of the square
        file = (x - OFFSET_X) // GRID_SIZE
        rank = 7 - (y - OFFSET_Y) // GRID_SIZE
        return rank * 16 + file

    def get_piece_type(self, file, rank):
        bitboards = self.board.bitboards
        square = 1 << (rank * 16 + file)
        for piece in bitboards:
            if bitboards[piece] & square:
                return piece
        return None
        
    def get_file_rank(self, x, y):
        # get the file and rank of the square
        file = (x - OFFSET_X) // GRID_SIZE
        rank = 7 - (y - OFFSET_Y) // GRID_SIZE
        return file, rank

    def square_to_file_rank(self, square):
        # get the file and rank of the square
        file = square % 16
        rank = square // 16
        return file, rank

    def display_moves(self):
        # display the possible moves for the selected piece as squares on the board
        # the squares are displayed in orange if the move is a non-capture move
        # the squares are displayed in red if the move is a capture move
        moves = self.get_moves()
        for move in moves:
            start_square, end_square, _, _, _, capture = decode_move(move)
            # if the start is the selected piece, display the end square
            if start_square == self.selected_square:
                file, rank = self.square_to_file_rank(end_square)
                x_pos = file * GRID_SIZE + OFFSET_X
                y_pos = (7 - rank) * GRID_SIZE + OFFSET_Y

                # draw a transparent rect
                # if the move is a capture move (en passant as well), draw the square in red
                # if the move is a non-capture move, draw the square in orange
                alpha = 128

                color = CAPTURE_SQUARE if capture else MOVE_SQUARE
                draw_transparent_rect(self.screen, (x_pos, y_pos, GRID_SIZE, GRID_SIZE), color, alpha)

    def select_square(self):
        if self.selected_square is None:
            return
        file, rank = self.square_to_file_rank(self.selected_square)
        x_pos = file * GRID_SIZE + OFFSET_X
        y_pos = (7 - rank) * GRID_SIZE + OFFSET_Y
        alpha = 128
        # draw the transparent rect
        draw_transparent_rect(self.screen, (x_pos, y_pos, GRID_SIZE, GRID_SIZE), (196,196,196), alpha)

        piece_type = self.get_piece_type(file, rank)
        if self.mb[0]:
            # draw the piece on the curser (self.mx, self.my)
            self.screen.blit(self.piece_imgs[piece_type], (self.mx - GRID_SIZE // 2, self.my - GRID_SIZE // 2))
        else:
            # draw the piece on the board
            self.draw_piece(piece_type, file, rank)
        
    def draw_board(self):
        for rank in range(8):
            for file in range(8):
                x_pos = file * GRID_SIZE + OFFSET_X
                y_pos = (7 - rank) * GRID_SIZE + OFFSET_Y
                
                color = LIGHT_SQUARE if (file + rank) % 2 == 0 else DARK_SQUARE
                pygame.draw.rect(self.screen, color, (x_pos, y_pos, GRID_SIZE, GRID_SIZE))

    def draw_piece(self, piece_type, file, rank):
        if piece_type is None:
            return
        
        x_pos = file * GRID_SIZE + OFFSET_X
        y_pos = (7 - rank) * GRID_SIZE + OFFSET_Y
        self.screen.blit(self.piece_imgs[piece_type], (x_pos, y_pos))

    def draw_pieces(self):
        for file in range(8):
            for rank in range(8):
                # selected piece is drawn in the selected_square method
                if (file, rank) != self.selected_square:
                    piece_type = self.get_piece_type(file, rank)
                    self.draw_piece(piece_type, file, rank)

    def make_engine_suggestion(self):
        "Get the best move from the engine and store it in self.engine_suggestion"
        # write "thinking..." on the screen
        thinking_rect = pygame.Rect(200, 200, 400, 400)
        write_centered_text(self.screen, "Thinking...", thinking_rect, (0, 0, 0))
        pygame.display.flip()

        # calculate the depth based on the numer of pieces on the board
        occupied_bitboard = self.board.bitboards["occupied"]
        num_pieces = bin(occupied_bitboard).count("1")
        if num_pieces <= 10:
            depth = 5
        elif num_pieces <= 20:
            depth = 4
        else:
            depth = 3

        engine = Engine(self.board, depth=depth, time_limit=6)
        move = engine.get_best_move()
        # draw an arrow from the start to the end of the move
        start, end, _, _, _, _ = decode_move(move)
        start_file, start_rank = self.square_to_file_rank(start)
        end_file, end_rank = self.square_to_file_rank(end)
        self.engine_suggestion = ((start_file, start_rank), (end_file, end_rank))

    def check_checkmate(self):
        # checks checkmate and stores what it finds
        fen = self.board.board_to_fen()
        if fen in self.cached_checkmate_checks:
            return self.cached_checkmate_checks[fen]
        else:
            checkmate = self.board.is_checkmate(turn=self.board.white_to_move)
            self.cached_checkmate_checks[fen] = checkmate
            return checkmate

    def draw_game(self):
        self.draw_board()
        if self.piece_selected():
            self.display_moves()
        self.draw_pieces()

        if self.check_checkmate():
            checkmate_rect = pygame.Rect(200, 200, 400, 400)
            write_centered_text(self.screen, "Checkmate!", checkmate_rect, (0, 0, 0))

        if self.engine_suggestion is not None:
            self.draw_arrow(self.engine_suggestion[0], self.engine_suggestion[1], (0, 255, 0))

        for arrow in self.arrows:
            self.draw_arrow(arrow[0], arrow[1])

        for circle in self.circles:
            self.draw_circle(circle[0], circle[1])

        self.draw_preview_arrow()

        if self.piece_selected():
            self.select_square()

    def handle_events(self):
        self.L_mouse_up = False
        self.L_mouse_down = False
        self.R_mouse_up = False
        self.R_mouse_down = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "main menu"
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.L_mouse_up = True
                elif event.button == 3:
                    self.R_mouse_up = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:
                    self.rmx, self.rmy = pygame.mouse.get_pos()
                    self.R_mouse_down = True
                elif event.button == 1:
                    self.lmx, self.lmy = pygame.mouse.get_pos()
                    self.L_mouse_down = True
            # if the user presses the space key, request a move from the engine
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.make_engine_suggestion()
                # if the user presses the u key, undo the last move
                elif event.key == pygame.K_u:
                    self.board.undo_move()
                # if the user presses the f key, set the FEN of the board
                elif event.key == pygame.K_f:
                    self.set_FEN()
                # if the user presses the d key, toggle the developer display
                elif event.key == pygame.K_d:
                    self.developer_display_toggle = not self.developer_display_toggle
                # if the user presses the b key, toggle the bitboard display
                elif event.key == pygame.K_b:
                    self.bitboard_display_toggle = not self.bitboard_display_toggle
                # if the user presses the p key, cycle through the bitboards forward
                elif event.key == pygame.K_p:
                    self.bitboard_display_index += 1
                    self.bitboard_display_index %= 15
                # if the user presses the o key, cycle through the bitboards backward
                elif event.key == pygame.K_o:
                    self.bitboard_display_index -= 1
                    self.bitboard_display_index %= 15

                
        self.mx, self.my = pygame.mouse.get_pos()
        self.mb = pygame.mouse.get_pressed()

    def handle_game_inputs(self):
        # select piece
        # deselect piece
        # move piece
        # draw arrow
        # draw circle

        moves = self.get_moves()

        # if left mouse pressed, select piece, move piece, or deselect piece
        if self.L_mouse_down:
            self.circles = []
            self.arrows = []
            self.engine_suggestion = None
            # select piece if no piece is selected or if the new square that is clicked is one of the legal moves of the selected piece
            no_piece_selected = self.selected_square is None
            file, rank = self.get_file_rank(self.lmx, self.lmy)
            if no_piece_selected:
                self.select_piece(file, rank)
            else:
                # check if the new square is a legal move of the selected piece
                start_square = self.selected_square
                end_square = rank * 16 + file

                for move in moves:
                    start, end, _, _, _, _ = decode_move(move)
                    if start == start_square and end == end_square:
                        self.board.make_move(move)
                        break
                # if the new square is another piece, select the new piece
                if rank * 16 + file != self.selected_square:
                    self.select_piece(file, rank)

            
        # if the left mouse button is released and there is a piece selected, move the piece if the new square is a legal move
        if self.L_mouse_up:
            file, rank = self.get_file_rank(self.mx, self.my)
            if self.selected_square is not None:
                start_square = self.selected_square
                end_square = rank * 16 + file
                for move in moves:
                    start, end, _, _, _, _ = decode_move(move)
                    if start == start_square and end == end_square:
                        self.board.make_move(move)
                        break
                # if the new square is not a legal move, deselect the piece
                if rank * 16 + file != self.selected_square:
                    self.selected_square = None


        
        self.preview_arrow = None
        # if right mouse button is down draw the preview of a circle or arrow
        if self.mb[2]:
            start_file, start_rank = self.get_file_rank(self.rmx, self.rmy)
            end_file, end_rank = self.get_file_rank(self.mx, self.my)
            self.preview_arrow = ((start_file, start_rank), (end_file, end_rank))

        if self.R_mouse_up: # draw an arrow or circle
            start_file, start_rank = self.get_file_rank(self.rmx, self.rmy)
            end_file, end_rank = self.get_file_rank(self.mx, self.my)

            # if the start and end are the same, draw a circle
            if (start_file, start_rank) == (end_file, end_rank):
                # if the circle already exists, remove it
                if (start_file, start_rank) in self.circles:
                    self.circles.remove((start_file, start_rank))
                else:
                    self.circles.append((start_file, start_rank))
            else:
                # if the arrow already exists, remove it
                if ((start_file, start_rank), (end_file, end_rank)) in self.arrows:
                    self.arrows.remove(((start_file, start_rank), (end_file, end_rank)))
                else:
                    self.arrows.append(((start_file, start_rank), (end_file, end_rank)))

    def select_piece(self, file, rank):
        # if the square is a piece, select the piece
        piece = self.get_piece_type(file, rank)
        if piece is not None:
            self.selected_square = rank * 16 + file
        else:
            self.selected_square = None

    def draw_preview_arrow(self):
        if not self.preview_arrow:
            return
        # draw the preview arrow or circle
        start, end = self.preview_arrow
        if start == end:
            self.draw_circle(start[0], start[1])
        else:
            self.draw_arrow(start, end)

    def developer_display(self):
        # write the FEN of the board to the screen
        FEN_rect = pygame.Rect(0, 0, 800, 800)
        write_centered_text(self.screen, self.board.board_to_fen(), FEN_rect, (0, 0, 0))

        # draw all legal moves
        moves = self.get_moves()
        for move in moves:
            start, end, _, _, _, _ = decode_move(move)
            start_file, start_rank = self.square_to_file_rank(start)
            end_file, end_rank = self.square_to_file_rank(end)
            self.draw_arrow((start_file, start_rank), (end_file, end_rank), (0, 0, 128))

        # write whose turn it is
        turn_rect = pygame.Rect(0, 300, 100, 100)
        write_centered_text(self.screen, f"{self.board.white_to_move}'s turn", turn_rect, (0, 0, 0))

        # if there is a piece selected, write the info of the piece
        if self.selected_square is not None:
            piece_type = self.get_piece_type(*self.square_to_file_rank(self.selected_square))
            piece_rect = pygame.Rect(0, 500, 100, 100)
            piece_data = f"Selected piece: {piece_type}"
            write_centered_text(self.screen, piece_data, piece_rect, (0, 0, 0))

        # write the square numbers on the board
        for rank in range(8):
            for file in range(8):
                x_pos = file * GRID_SIZE + OFFSET_X
                y_pos = (7 - rank) * GRID_SIZE + OFFSET_Y
                write_centered_text(self.screen, str(rank * 16 + file), pygame.Rect(x_pos, y_pos, GRID_SIZE//2, GRID_SIZE//2), (0, 128, 128))

    def draw_bitboard(self, bitboard):
        for rank in range(8):
            for file in range(8):
                square = rank * 16 + file
                if bitboard & (1 << square):
                    x_pos = file * GRID_SIZE + OFFSET_X
                    y_pos = (7 - rank) * GRID_SIZE + OFFSET_Y
                    # draw a transparent rect
                    draw_transparent_rect(self.screen, (x_pos, y_pos, GRID_SIZE, GRID_SIZE), (0, 0, 128), 128)

    def main_loop(self):
        running = True
        self.arrows = []
        self.circles = []
        self.preview_arrow = None
        self.rmx, self.rmy = 0, 0
        self.lmx, self.lmy = 0, 0
        self.screen.fill((0, 0, 0))

        while running:
            self.get_moves()
            # handle events
            result = self.handle_events()
            if result: # if the result is not None, return the result
                return result

            if self.is_over_board(self.mx, self.my):
                self.handle_game_inputs()

            self.draw_game()
            
            if self.developer_display_toggle:
                self.developer_display()

            if self.bitboard_display_toggle:
                bitboard = list(self.board.bitboards.values())[self.bitboard_display_index]
                self.draw_bitboard(bitboard)

            # set the caption to be the fps
            pygame.display.set_caption(str(int(self.clock.get_fps())))
            pygame.display.flip()
            self.clock.tick(FPS)