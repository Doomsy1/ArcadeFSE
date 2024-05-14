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

from board import Board, Piece, Move
from engine import Engine

# Constants
FPS = 144
EN_PASSANT_ROW = {0: 5, 1: 2}  # Row for en passant for white and black pawns


class ChessGame:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.board = Board()

        self.root = tk.Tk()
        self.root.withdraw()

        self.selected_piece = None

        self.cached_moves = {} # store the moves of the selected piece
        # key: fen, value: moves

        # self.board.parse_fen("2k5/Q7/2K5/8/8/8/8/8 w - - 0 1")

        self.load_images()

    def get_moves(self):
        # cache the moves of the board
        fen = self.board.generate_fen()
        if fen in self.cached_moves:
            return self.cached_moves[fen]
        else:
            moves = self.board.generate_legal_moves()
            self.cached_moves[fen] = moves
            return moves

    def is_over_board(self, x, y):
        return OFFSET_X <= x <= OFFSET_X + 8 * GRID_SIZE and OFFSET_Y <= y <= OFFSET_Y + 8 * GRID_SIZE
    
    def set_FEN(self):
        # make a popup window that gets the user to set the FEN of the board
        fen = simpledialog.askstring("Input", "Please enter the FEN:", parent=self.root)
        # the FEN is then set to the board
        self.board.parse_fen(fen)

    def piece_selected(self):
        # return True if a piece is selected
        return self.selected_piece is not None

    def draw_arrow(self, start, end):
        # start and end are tuples with the file and rank of the squares
        start_file, start_rank = start
        end_file, end_rank = end
        start_x = start_rank * GRID_SIZE + OFFSET_X + GRID_SIZE // 2
        start_y = (7 - start_file) * GRID_SIZE + OFFSET_Y + GRID_SIZE // 2
        end_x = end_rank * GRID_SIZE + OFFSET_X + GRID_SIZE // 2
        end_y = (7 - end_file) * GRID_SIZE + OFFSET_Y + GRID_SIZE // 2

        # draw the arrow
        tail_start_offset = GRID_SIZE // 4
        tail_width = GRID_SIZE // 4
        head_width = GRID_SIZE // 2
        head_height = GRID_SIZE // 2.5
        color = MOVE_SQUARE
        alpha = 160
        draw_arrow(self.screen, (start_x, start_y), (end_x, end_y), tail_start_offset, tail_width, head_width, head_height, color, alpha)

    def draw_circle(self, file, rank):
        # draw the circle
        x_pos = rank * GRID_SIZE + OFFSET_X + GRID_SIZE // 2
        y_pos = (7 - file) * GRID_SIZE + OFFSET_Y + GRID_SIZE // 2
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

    def get_file_rank(self, x, y):
        # get the file and rank of the square
        file = 7 - (y - OFFSET_Y) // GRID_SIZE
        rank = (x - OFFSET_X) // GRID_SIZE
        return file, rank

    def display_moves(self):
        # display the possible moves for the selected piece as squares on the board
        # the squares are displayed in orange if the move is a non-capture move
        # the squares are displayed in red if the move is a capture move
        moves = self.get_moves()
        for move in moves:
            start = move.start
            end = move.end
            # if the start is the selected piece, display the end square
            if start == self.selected_piece:
                file, rank = end
                x_pos = rank * GRID_SIZE + OFFSET_X
                y_pos = file * GRID_SIZE + OFFSET_Y

                # draw a transparent rect
                # if the move is a capture move (en passant as well), draw the square in red
                # if the move is a non-capture move, draw the square in orange
                alpha = 128
                capture = False
                if self.board.get_piece(end):
                    capture = True
                # if the move is an en passant move, draw the square in red
                if self.board.is_en_passant_move(move):
                    capture = True

                if capture:
                    draw_transparent_rect(self.screen, (x_pos, y_pos, GRID_SIZE, GRID_SIZE), CAPTURE_SQUARE, alpha)
                else:
                    draw_transparent_rect(self.screen, (x_pos, y_pos, GRID_SIZE, GRID_SIZE), MOVE_SQUARE, alpha)

    def draw_selected_piece(self):
        if self.selected_piece is None:
            return
        file, rank = self.selected_piece
        x_pos = rank * GRID_SIZE + OFFSET_X
        y_pos = (7 - file) * GRID_SIZE + OFFSET_Y
        alpha = 128
        # draw the transparent rect
        draw_transparent_rect(self.screen, (x_pos, y_pos, GRID_SIZE, GRID_SIZE), (196,196,196), alpha)

        piece = self.board.get_piece((file, rank))
        if self.mb[0]:
            # draw the piece on the curser (self.mx, self.my)
            if piece.is_white:
                self.screen.blit(self.piece_imgs[piece.type], (self.mx - GRID_SIZE // 2, self.my - GRID_SIZE // 2))
            else:
                self.screen.blit(self.piece_imgs[piece.type.upper()], (self.mx - GRID_SIZE // 2, self.my - GRID_SIZE // 2))
        else:
            # draw the piece on the board
            self.draw_piece(piece, file, rank)
        
    def draw_board(self):
        for rank in range(8):
            for file in range(8):
                x_pos = rank * GRID_SIZE + OFFSET_X
                y_pos = (7 - file) * GRID_SIZE + OFFSET_Y
                
                color = LIGHT_SQUARE if (rank + file) % 2 == 0 else DARK_SQUARE
                pygame.draw.rect(self.screen, color, (x_pos, y_pos, GRID_SIZE, GRID_SIZE))

    def draw_piece(self, piece: Piece, file, rank):
        if piece.type is None:
            return
        
        x_pos = rank * GRID_SIZE + OFFSET_X
        y_pos = (7 - file) * GRID_SIZE + OFFSET_Y
        if piece.is_white:
            self.screen.blit(self.piece_imgs[piece.type], (x_pos, y_pos))
        else:
            self.screen.blit(self.piece_imgs[piece.type.upper()], (x_pos, y_pos))

    def draw_pieces(self):
        for file in range(8):
            for rank in range(8):
                # selected piece is drawn in the draw_selected_piece method
                if (file, rank) != self.selected_piece:
                    piece = self.board.get_piece((file, rank))
                    self.draw_piece(piece, file, rank)

    def make_engine_suggestion(self):
        engine = Engine(self.board)
        move = engine.get_best_move()
        # draw an arrow from the start to the end of the move
        self.arrows.append((move.start, move.end))

    def draw_game(self):
        self.draw_board()
        if self.piece_selected():
            self.display_moves()
        self.draw_pieces()

        if self.board.is_checkmate():
            checkmate_rect = pygame.Rect(200, 200, 400, 400)
            write_centered_text(self.screen, "Checkmate!", checkmate_rect, (0, 0, 0))

        for arrow in self.arrows:
            self.draw_arrow(arrow[0], arrow[1])

        for circle in self.circles:
            self.draw_circle(circle[0], circle[1])

        self.draw_preview_arrow()

        if self.piece_selected():
            self.draw_selected_piece()

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

                
        self.mx, self.my = pygame.mouse.get_pos()
        self.mb = pygame.mouse.get_pressed()

    def handle_game_inputs(self):
        # select piece
        # deselect piece
        # move piece
        # draw arrow
        # draw circle

        if self.L_mouse_down: # select a piece
            self.circles = []
            self.arrows = []

            file, rank = self.get_file_rank(self.mx, self.my)
            # if file, rank is a valid piece, select the piece 
            # else, deselect the piece unless the piece you clicked is a valid move
            if self.board.get_piece((file, rank)):
                self.selected_piece = (file, rank)
            elif self.piece_selected():
                move = Move(self.selected_piece, (file, rank))
                if move in self.board.legal_moves:
                    self.board.make_move(move)
                self.selected_piece = None
            else:
                self.selected_piece = None

        elif self.L_mouse_up: # move the piece if the move is valid
            file, rank = self.get_file_rank(self.mx, self.my)
            move = Move(self.selected_piece, (file, rank))
            if self.piece_selected():
                if move in self.board.legal_moves:
                    self.board.make_move(move)

                # if the same piece is clicked again dont deselect the piece
                elif (file, rank) == self.selected_piece:
                    pass
                else:
                    self.selected_piece = None
        
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
        FEN_rect = pygame.Rect(0, 0, 800, 100)
        write_centered_text(self.screen, self.board.generate_fen(), FEN_rect, (0, 0, 0))

    def main_loop(self):
        running = True
        self.arrows = []
        self.circles = []
        self.preview_arrow = None
        self.rmx, self.rmy = 0, 0
        self.lmx, self.lmy = 0, 0
        self.screen.fill((0, 0, 0))

        while running:
            # handle events
            result = self.handle_events()
            if result: # if the result is not None, return the result
                return result
            
            if self.is_over_board(self.mx, self.my):
                self.handle_game_inputs()

            self.draw_game()

            # self.developer_display() # remove this line if you dont want to display the FEN of the board

            # set the caption to be the fps
            pygame.display.set_caption(str(int(self.clock.get_fps())))
            pygame.display.flip()
            self.clock.tick(FPS)