# board.py

from pprint import pprint
import pygame
from constants import LIGHT_SQUARE, DARK_SQUARE, OFFSET_X, OFFSET_Y, GRID_SIZE
from pieces import Piece

starting_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"

class Board:
    def __init__(self, grid_size, screen):
        self.screen = screen
        self.grid_size = grid_size
        self.white_color = LIGHT_SQUARE
        self.black_color = DARK_SQUARE
        self.selected_piece = [None, None]
        self.turn = "white"
        self.en_passant = None # col of the en passant square (the square behind the pawn that just moved 2 squares forward)

        self.game_FEN = starting_FEN
        self.game_board = self.FEN_to_board(self.game_FEN)

        self.piece_imgs = {}
        self.load_images()

    def piece_selected(self):
        return self.selected_piece[0] is not None and self.selected_piece[1] is not None
    
    def deselect_piece(self):
        self.selected_piece = [None, None]

    def load_images(self):
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
            self.piece_imgs[img] = pygame.transform.scale(self.piece_imgs[img], (self.grid_size, self.grid_size))
                    
    def update(self):
        self.draw_board()
        if self.selected_piece[0] is not None and self.selected_piece[1] is not None:
            moves = self.list_moves(self.selected_piece[0], self.selected_piece[1])
            self.display_moves(moves)
        self.draw_selected_piece()
        self.draw_pieces()

    def get_row_col(self, x, y):
        row = (y - OFFSET_Y) // self.grid_size
        col = (x - OFFSET_X) // self.grid_size

        # if the click is outside the board
        if row < 0 or row > 7 or col < 0 or col > 7:
            return None, None
        return row, col
    
    def display_moves(self, moves):
        for move in moves:
            x_pos = move[1] * self.grid_size + OFFSET_X
            y_pos = move[0] * self.grid_size + OFFSET_Y
            pygame.draw.circle(self.screen, (0, 255, 0), (x_pos + self.grid_size // 2, y_pos + self.grid_size // 2), 10)

    def make_move(self, row, col):
        # if a piece is already selected, move the piece to the new position if it is a valid move
        if self.piece_selected():
            moves = self.list_moves(self.selected_piece[0], self.selected_piece[1])
            if (row, col) in moves:
                self.move_piece(row, col)
                self.deselect_piece()
                return
        # if no piece is selected, select the piece in the new position if it is a valid piece
        else:
            if self.is_piece(row, col):
                piece = self.get_piece(row, col)
                if piece.get_team() == self.turn:
                    self.select_piece(row, col)
                    return


    def move_piece(self, row, col):
        # move the piece to the new position
        piece = self.get_piece(self.selected_piece[0], self.selected_piece[1])
        self.game_board[row][col] = piece
        self.game_board[self.selected_piece[0]][self.selected_piece[1]] = ''
        self.turn = 'white' if self.turn == 'black' else 'black'

    def FEN_to_board(self, FEN):
        board = []
        for row_str in FEN.split("/"):
            row = []
            for piece in row_str:
                if piece.isdigit():
                    row += ['' for _ in range(int(piece))]
                else:
                    row.append(Piece(piece))
            board.append(row)

        pprint(board)
        return board

    def list_moves(self, row, col):
        piece = self.get_piece(row, col)
        moves = []
        match piece.get_type():
            case "r":
                moves = self.list_rook_moves(row, col)
            case "n":
                moves = self.list_knight_moves(row, col)
            case "b":
                moves = self.list_bishop_moves(row, col)
            case "q":
                moves = self.list_queen_moves(row, col)
            case "k":
                moves = self.list_king_moves(row, col)
            case "p":
                moves = self.list_black_pawn_moves(row, col)
            
            case "R":
                moves = self.list_rook_moves(row, col)
            case "N":
                moves = self.list_knight_moves(row, col)
            case "B":
                moves = self.list_bishop_moves(row, col)
            case "Q":
                moves = self.list_queen_moves(row, col)
            case "K":
                moves = self.list_king_moves(row, col)
            case "P":
                moves = self.list_white_pawn_moves(row, col)
        print(moves)
        return moves

    def get_piece(self, row, col):
        return self.game_board[row][col]

    def is_piece(self, row, col):
        return self.get_piece(row, col) != ''

    def select_piece(self, x, y):
        row, col = self.get_row_col(x, y)
        self.selected_piece = [row, col]

    def draw_selected_piece(self):
        if self.selected_piece[0] is not None and self.selected_piece[1] is not None:
            row, col = self.selected_piece
            x_pos = col * self.grid_size + OFFSET_X
            y_pos = row * self.grid_size + OFFSET_Y
            pygame.draw.rect(self.screen, (0, 255, 0), (x_pos, y_pos, self.grid_size, self.grid_size), 3)

    def draw_board(self):
        for row in range(8):
            for col in range(8):
                color = self.white_color if (row + col) % 2 == 0 else self.black_color

                x_pos = col * self.grid_size + OFFSET_X
                y_pos = row * self.grid_size + OFFSET_Y
                pygame.draw.rect(self.screen, color, (x_pos, y_pos, self.grid_size, self.grid_size))
    
    def draw_piece(self, piece, row, col):
        x_pos = col * self.grid_size + OFFSET_X
        y_pos = row * self.grid_size + OFFSET_Y
        self.screen.blit(self.piece_imgs[piece], (x_pos, y_pos))

    def draw_pieces(self):
        for row in range(8):
            for col in range(8):
                piece = self.get_piece(row, col)
                if piece != '':
                    self.draw_piece(piece.get_type(), row, col)

    def list_rook_moves(self, row, col):
        moves = []
        team = self.get_piece(row, col).get_team()

        # check the moves in the same row to the right (stop if there is a piece)
        # if there is a piece, check if it is an enemy piece
        # if it is an enemy piece, add the move and stop
        # if it is a friendly piece, stop
        for i in range(col + 1, 8):
            if self.is_piece(row, i):
                if self.get_piece(row, i).get_team() == team:
                    break
                moves.append((row, i))
                break
            moves.append((row, i))

        # same row to the left
        for i in range(col - 1, -1, -1):
            if self.is_piece(row, i):
                if self.get_piece(row, i).get_team() == team:
                    break
                moves.append((row, i))
                break
            moves.append((row, i))

        # same column to the top
        for i in range(row - 1, -1, -1):
            if self.is_piece(i, col):
                if self.get_piece(i, col).get_team() == team:
                    break
                moves.append((i, col))
                break
            moves.append((i, col))

        # same column to the bottom
        for i in range(row + 1, 8):
            if self.is_piece(i, col):
                if self.get_piece(i, col).get_team() == team:
                    break
                moves.append((i, col))
                break
            moves.append((i, col))

        return moves

    def list_knight_moves(self, row, col):
        # the knight moves in an L shape
        moves = []
        team = self.get_piece(row, col).get_team()

        # Define the possible knight moves
        knight_moves = [
            (-2, 1), (-1, 2), (1, 2), (2, 1),
            (-2, -1), (-1, -2), (1, -2), (2, -1)
        ]

        # Iterate over each possible move
        for move in knight_moves:
            new_row = row + move[0]
            new_col = col + move[1]

            # Check if the new position is within the board boundaries
            if 0 > new_row or new_row > 7 or 0 > new_col or new_col > 7:
                continue
            # Check if the new position is empty or contains an enemy piece
            if not self.is_piece(new_row, new_col):
                moves.append((new_row, new_col))

            elif self.get_piece(new_row, new_col).get_team() != team:
                moves.append((new_row, new_col))
        return moves

    def list_bishop_moves(self, row, col):
        moves = []
        team = self.get_piece(row, col).get_team()
        
        # check the moves in the diagonal to the top right
        for i in range(1, 8):
            if row - i < 0 or col + i > 7:
                break
            if self.is_piece(row - i, col + i):
                if self.get_piece(row - i, col + i).get_team() == team:
                    break
                moves.append((row - i, col + i))
                break
            moves.append((row - i, col + i))

        # check the moves in the diagonal to the top left
        for i in range(1, 8):
            if row - i < 0 or col - i < 0:
                break
            if self.is_piece(row - i, col - i):
                if self.get_piece(row - i, col - i).get_team() == team:
                    break
                moves.append((row - i, col - i))
                break
            moves.append((row - i, col - i))

        # check the moves in the diagonal to the bottom right
        for i in range(1, 8):
            if row + i > 7 or col + i > 7:
                break
            if self.is_piece(row + i, col + i):
                if self.get_piece(row + i, col + i).get_team() == team:
                    break
                moves.append((row + i, col + i))
                break
            moves.append((row + i, col + i))

        # check the moves in the diagonal to the bottom left
        for i in range(1, 8):
            if row + i > 7 or col - i < 0:
                break
            if self.is_piece(row + i, col - i):
                if self.get_piece(row + i, col - i).get_team() == team:
                    break
                moves.append((row + i, col - i))
                break
            moves.append((row + i, col - i))

        return moves

    def list_queen_moves(self, row, col):
        # the queen moves are the same as the rook and bishop moves
        return self.list_rook_moves(row, col) + self.list_bishop_moves(row, col)

    def list_king_moves(self, row, col):
        # the king moves in all directions by 1 square
        moves = []
        team = self.get_piece(row, col).get_team()

        # Define the possible directions for the king to move
        directions = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]
        
        # Iterate over each direction
        for direction in directions:
            new_row = row + direction[0]
            new_col = col + direction[1]
            
            # Check if the new position is within the board boundaries
            if 0 > new_row or new_row > 7 or 0 > new_col or new_col > 7:
                continue
            
            # Check if the new position is empty or contains an enemy piece
            if not self.is_piece(new_row, new_col):
                moves.append((new_row, new_col))

            elif self.get_piece(new_row, new_col).get_team() != team:
                moves.append((new_row, new_col))

        return moves

    def list_white_pawn_moves(self, row, col):
        moves = []
        # the white pawn moves forward if the square in front is empty
        # the white pawn can move 2 squares forward if it is in the starting position and the 2 squares in front are empty (row 6)
        # the white pawn can move diagonally to the right or left if there is an enemy piece
        # the white pawn can move diagonally to the right or left if there is an enemy pawn that just moved 2 squares forward (en passant) (use the en passant variable)

        # check the square in front
        if not self.is_piece(row - 1, col):
            moves.append((row - 1, col))
            # check if the pawn is in the starting position
            if row == 6 and not self.is_piece(row - 2, col):
                moves.append((row - 2, col))

        # check the diagonal to the top right and top left
        if col < 7 and self.is_piece(row - 1, col + 1) and self.get_piece(row - 1, col + 1).get_team():
            moves.append((row - 1, col + 1))
        if col > 0 and self.is_piece(row - 1, col - 1) and self.get_piece(row - 1, col - 1).get_team():
            moves.append((row - 1, col - 1))

        # check the en passant move
        if self.en_passant is not None:
            self.en_passant # the col of the en passant square (the square behind the pawn)
            if row == 3 and (col == self.en_passant + 1 or col == self.en_passant - 1):
                moves.append((row - 1, self.en_passant))

        return moves

    def list_black_pawn_moves(self, row, col):
        # the black pawn moves forward if the square in front is empty
        # the black pawn can move 2 squares forward if it is in the starting position and the 2 squares in front are empty (row 1)
        # the black pawn can move diagonally to the right or left if there is an enemy piece
        # the black pawn can move diagonally to the right or left if there is an enemy pawn that just moved 2 squares forward (en passant) (use the en passant variable)
        moves = []

        # check the square in front
        if not self.is_piece(row + 1, col):
            moves.append((row + 1, col))
            # check if the pawn is in the starting position
            if row == 1 and not self.is_piece(row + 2, col):
                moves.append((row + 2, col))

        # check the diagonal to the bottom right and bottom left
        if col < 7 and self.is_piece(row + 1, col + 1) and self.get_piece(row + 1, col + 1).isupper():
            moves.append((row + 1, col + 1))
        if col > 0 and self.is_piece(row + 1, col - 1) and self.get_piece(row + 1, col - 1).isupper():
            moves.append((row + 1, col - 1))

        # check the en passant move
        if self.en_passant is not None:
            if row == 4 and (col == self.en_passant + 1 or col == self.en_passant - 1):
                moves.append((row + 1, self.en_passant))

        return moves