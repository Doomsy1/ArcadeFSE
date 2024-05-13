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

from board import Board
from engine import Engine

# Constants
FPS = 144
EN_PASSANT_ROW = {0: 5, 1: 2}  # Row for en passant for white and black pawns


class ChessGame:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.board = Board()
        self.board.init_board()

        self.root = tk.Tk()
        self.root.withdraw()

        # self.board.FEN_to_board("2k5/Q7/2K5/8/8/8/8/8 w - - 0 1")

        self.load_images()

    def is_over_board(self, x, y):
        return OFFSET_X <= x <= OFFSET_X + 8 * GRID_SIZE and OFFSET_Y <= y <= OFFSET_Y + 8 * GRID_SIZE
    
    def set_FEN(self):
        # make a popup window that gets the user to set the FEN of the board
        fen = simpledialog.askstring("Input", "Please enter the FEN:", parent=self.root)
        # the FEN is then set to the board
        self.board.FEN_to_board(fen)


    def draw_arrow(self, start, end):
        # start and end are tuples with the row and column of the start and end positions
        start_x = start[1] * GRID_SIZE + OFFSET_X + GRID_SIZE // 2
        start_y = start[0] * GRID_SIZE + OFFSET_Y + GRID_SIZE // 2
        end_x = end[1] * GRID_SIZE + OFFSET_X + GRID_SIZE // 2
        end_y = end[0] * GRID_SIZE + OFFSET_Y + GRID_SIZE // 2

        # draw the arrow
        tail_start_offset = GRID_SIZE // 4
        tail_width = GRID_SIZE // 4
        head_width = GRID_SIZE // 2
        head_height = GRID_SIZE // 2.5
        colour = MOVE_SQUARE
        alpha = 160
        draw_arrow(self.screen, (start_x, start_y), (end_x, end_y), tail_start_offset, tail_width, head_width, head_height, colour, alpha)

    def draw_circle(self, row, col):
        # draw the circle
        x_pos = col * GRID_SIZE + OFFSET_X + GRID_SIZE // 2
        y_pos = row * GRID_SIZE + OFFSET_Y + GRID_SIZE // 2
        center = (x_pos, y_pos)
        radius = GRID_SIZE // 2
        colour = MOVE_SQUARE
        thickness = 3
        pygame.draw.circle(self.screen, colour, center, radius, thickness)
        
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

    def get_row_col(self, x, y):
        row = (y - OFFSET_Y) // GRID_SIZE
        col = (x - OFFSET_X) // GRID_SIZE
        return row, col

    def display_moves(self, moves):
        # display the possible moves for the selected piece as squares on the board
        # the squares are displayed in orange if the move is a non-capture move
        # the squares are displayed in red if the move is a capture move
        for move in moves:
            row, col = move
            color = CAPTURE_SQUARE if self.board.is_piece(move[0], move[1]) else MOVE_SQUARE

            # Check if the move is an en passant move
            if self.board.en_passant is not None and row == EN_PASSANT_ROW[self.board.turn == "white"] and col == self.board.en_passant:
                color = CAPTURE_SQUARE

            # draw the rectangle on the board
            x_pos = col * GRID_SIZE + OFFSET_X
            y_pos = row * GRID_SIZE + OFFSET_Y
            pygame.draw.rect(self.screen, color, (x_pos, y_pos, GRID_SIZE, GRID_SIZE), 3)

            # draw the circle on the board
            center = (x_pos + GRID_SIZE // 2, y_pos + GRID_SIZE // 2)
            radius = GRID_SIZE // 6
            alpha = 128
            draw_transparent_circle(self.screen, center, radius, color, alpha)

    def draw_selected_piece(self):
        if self.board.selected_piece is None:
            return   
        row, col = self.board.selected_piece
        x_pos = col * GRID_SIZE + OFFSET_X
        y_pos = row * GRID_SIZE + OFFSET_Y
        alpha = 128
        # draw the transparent rect
        draw_transparent_rect(self.screen, (x_pos, y_pos, GRID_SIZE, GRID_SIZE), (196,196,196), alpha)

        piece = self.board.get_piece(row, col)
        if self.mb[0]:
            # draw the piece on the curser (self.mx, self.my)
            self.screen.blit(self.piece_imgs[piece.type], (self.mx - GRID_SIZE // 2, self.my - GRID_SIZE // 2))
        else:
            # draw the piece on the board
            self.draw_piece(piece, row, col)
        
    def draw_board(self):
        for row in range(8):
            for col in range(8):
                color = LIGHT_SQUARE if (row + col) % 2 == 0 else DARK_SQUARE
                x_pos = col * GRID_SIZE + OFFSET_X
                y_pos = row * GRID_SIZE + OFFSET_Y
                pygame.draw.rect(self.screen, color, (x_pos, y_pos, GRID_SIZE, GRID_SIZE))

    def draw_piece(self, piece, row, col):
        x_pos = col * GRID_SIZE + OFFSET_X
        y_pos = row * GRID_SIZE + OFFSET_Y
        if piece:
            self.screen.blit(self.piece_imgs[piece.type], (x_pos, y_pos))

    def draw_pieces(self):
        for row in range(8):
            for col in range(8):
                piece = self.board.get_piece(row, col)
                # dont draw the piece if it is the selected piece
                if (row, col) == self.board.selected_piece:
                    continue
                self.draw_piece(piece, row, col)

    def make_engine_suggestion(self):
        engine = Engine(self.board)
        move = engine.get_best_move()
        # draw an arrow from the start to the end of the move
        self.arrows.append(((move[0][0], move[0][1]), (move[1][0], move[1][1])))

    def flip_board(self):# unused
        # rotate the board 180 degrees
        # this is done by flipping the board array in the vertical and horizontal direction
        temp_board = []
        for row in range(8):
            temp_board.append(self.board.game_board[7 - row][::-1])
        self.board.game_board = temp_board


    def draw_game(self):
        self.draw_board()
        if self.board.piece_selected():
            self.display_moves(self.board.get_legal_moves(self.board.selected_piece[0], self.board.selected_piece[1]))
        self.draw_pieces()

        if self.board.is_checkmate():
            checkmate_rect = pygame.Rect(200, 200, 400, 400)
            write_centered_text(self.screen, "Checkmate!", checkmate_rect, (0, 0, 0))

        for arrow in self.arrows:
            self.draw_arrow(arrow[0], arrow[1])

        for circle in self.circles:
            self.draw_circle(circle[0], circle[1])

        self.draw_preview_arrow()

        if self.board.piece_selected():
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

            row, col = self.get_row_col(self.mx, self.my)
            # if row, col is a valid piece, select the piece
            if self.board.is_piece(row, col):
                self.board.selected_piece = (row, col)
            
            #
            

        elif self.L_mouse_up: # move the piece if the move is valid
            row, col = self.get_row_col(self.mx, self.my)
            if self.board.piece_selected():
                if (row, col) in self.board.get_legal_moves(self.board.selected_piece[0], self.board.selected_piece[1]):
                    self.board.make_move(row, col)
                
                # if the same piece is clicked again dont deselect the piece
                elif (row, col) == self.board.selected_piece:
                    pass
                else:
                    self.board.deselect_piece()
        
        self.preview_arrow = None
        # if right mouse button is down draw the preview of a circle or arrow
        if self.mb[2]:
            start_row, start_col = self.get_row_col(self.rmx, self.rmy)
            end_row, end_col = self.get_row_col(self.mx, self.my)
            self.preview_arrow = ((start_row, start_col), (end_row, end_col))

        if self.R_mouse_up: # draw an arrow or circle
            start_row, start_col = self.get_row_col(self.rmx, self.rmy)
            end_row, end_col = self.get_row_col(self.mx, self.my)

            if start_row == end_row and start_col == end_col:
                # if the circle already exists, remove it
                if (start_row, start_col) in self.circles:
                    self.circles.remove((start_row, start_col))
                else:
                    self.circles.append((start_row, start_col))
            else:
                # if the arrow already exists, remove it
                if ((start_row, start_col), (end_row, end_col)) in self.arrows:
                    self.arrows.remove(((start_row, start_col), (end_row, end_col)))
                else:
                    self.arrows.append(((start_row, start_col), (end_row, end_col)))

    def draw_preview_arrow(self):
        if not self.preview_arrow:
            return
        if self.preview_arrow[0] == self.preview_arrow[1]:
            self.draw_circle(self.preview_arrow[0][0], self.preview_arrow[0][1])
        else:
            self.draw_arrow(self.preview_arrow[0], self.preview_arrow[1])


    def developer_display(self):
        # write the FEN of the board to the screen
        FEN_rect = pygame.Rect(0, 0, 800, 100)
        write_centered_text(self.screen, self.board.generate_FEN(), FEN_rect, (0, 0, 0))

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