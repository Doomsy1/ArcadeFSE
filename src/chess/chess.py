import sys
import pygame

from constants import LIGHT_SQUARE, DARK_SQUARE
from constants import CHESS_OFFSET_X as OFFSET_X, CHESS_OFFSET_Y as OFFSET_Y, CHESS_GRID_SIZE as GRID_SIZE
from constants import SELECTED_SQUARE, MOVE_SQUARE, CAPTURE_SQUARE

from utils import draw_arrow, draw_transparent_circle, write_centered_text

# set directory to src/chess
sys.path.append("src/chess")

from board import Board

# Constants
FPS = 30
EN_PASSANT_ROW = {0: 2, 1: 5}  # Row for en passant for white and black pawns


class ChessGame:
    def __init__(self, screen):
        self.screen = screen
        pygame.display.set_caption("Chess Game")
        self.clock = pygame.time.Clock()
        self.board = Board()
        self.board.init_board()

        # self.board.FEN_to_board("4k3/Q6Q/8/8/8/8/PPPPP1PP/RNB1KBNq w KQkq - 0 1")

        self.load_images()

    def is_over_board(self, x, y):
        return OFFSET_X <= x <= OFFSET_X + 8 * GRID_SIZE and OFFSET_Y <= y <= OFFSET_Y + 8 * GRID_SIZE
    
    def draw_arrow(self, start, end):
        # start and end are tuples with the row and column of the start and end positions
        if self.flip:
            start = (7 - start[0], start[1])
            end = (7 - end[0], end[1])
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
        if self.flip:
            row = 7 - row
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
        if row < 0 or row > 7 or col < 0 or col > 7:
            return None
        if self.flip:
            row = 7 - row
        return row, col

    def display_moves(self, moves):
        # display the possible moves for the selected piece as squares on the board
        # the squares are displayed in orange if the move is a non-capture move
        # the squares are displayed in red if the move is a capture move
        for move in moves:
            row, col = move
            if self.flip:
                row = 7 - row

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
        if self.board.selected_piece is not None:
            row, col = self.board.selected_piece
            if self.flip:
                row = 7 - row
            x_pos = col * GRID_SIZE + OFFSET_X
            y_pos = row * GRID_SIZE + OFFSET_Y
            pygame.draw.rect(self.screen, SELECTED_SQUARE, (x_pos, y_pos, GRID_SIZE, GRID_SIZE), 3)

    def draw_board(self):
        for row in range(8):
            for col in range(8):
                if self.flip:
                    color = LIGHT_SQUARE if (row + col) % 2 == 0 else DARK_SQUARE
                else:
                    color = LIGHT_SQUARE if (row + col) % 2 == 1 else DARK_SQUARE
                x_pos = col * GRID_SIZE + OFFSET_X
                y_pos = row * GRID_SIZE + OFFSET_Y
                pygame.draw.rect(self.screen, color, (x_pos, y_pos, GRID_SIZE, GRID_SIZE))

    def draw_piece(self, piece, row, col):
        if self.flip:
            row = 7 - row
        x_pos = col * GRID_SIZE + OFFSET_X
        y_pos = row * GRID_SIZE + OFFSET_Y
        if piece != "":
            self.screen.blit(self.piece_imgs[piece.type], (x_pos, y_pos))

    def draw_pieces(self):
        for row in range(8):
            for col in range(8):
                piece = self.board.get_piece(row, col)
                if piece != " ":
                    self.draw_piece(piece, row, col)

    def draw_game(self):
        self.flip = self.board.turn == "white"
        self.draw_board()
        if self.board.selected_piece is not None:
            self.display_moves(self.board.get_legal_moves(self.board.selected_piece[0], self.board.selected_piece[1]))
            self.draw_selected_piece()
        self.draw_pieces()

        if self.board.is_checkmate():
            checkmate_rect = pygame.Rect(200, 200, 400, 400)
            write_centered_text(self.screen, "Checkmate!", checkmate_rect, (0, 0, 0))

        for arrow in self.arrows:
            self.draw_arrow(arrow[0], arrow[1])

        for circle in self.circles:
            self.draw_circle(circle[0], circle[1])

    def main_loop(self):


        running = True
        self.arrows = []
        self.circles = []
        rmx, rmy = 0, 0
        self.screen.fill((0, 0, 0))
        while running:
            L_mouse_up = False
            R_mouse_up = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "exit"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "main menu"
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        L_mouse_up = True
                    elif event.button == 3:
                        R_mouse_up = True
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 3:
                        rmx, rmy = pygame.mouse.get_pos()
            
            mx, my = pygame.mouse.get_pos()
            mb = pygame.mouse.get_pressed()

            if self.is_over_board(mx, my):
                if L_mouse_up:
                    row, col = self.get_row_col(mx, my)
                    self.board.make_move(row, col)
                    self.arrows = []
                    self.circles = []
                if R_mouse_up and self.is_over_board(rmx, rmy):
                    start = self.get_row_col(rmx, rmy)
                    end = self.get_row_col(mx, my)
                    if start == end:
                        if start not in self.circles:
                            self.circles.append(start)
                        else:
                            self.circles.remove(start)
                    else:
                        if (start, end) not in self.arrows:
                            self.arrows.append((start, end))
                        else:
                            self.arrows.remove((start, end))

            self.draw_game()

            

            pygame.display.flip()
            self.clock.tick(FPS)