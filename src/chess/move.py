from board import Board
from pieces import Piece

class Move:
    def __init__(self, start, end):
        self.start = start
        self.end = end

def GenerateMoves(board: Board, turn):
    moves = []
    for row in range(8):
        for col in range(8):
            piece = board.game_board[row][col]
            # if there is a piece in the current square and it is the current player's turn
            if piece and piece.color == turn:
                match piece:
                    case "p":
                        pass
                    case "n":
                        moves += list_knight_moves(board, piece)
                    case "b":
                        moves += list_bishop_moves(board, piece)
                    case "r":
                        moves += list_rook_moves(board, piece)
                    case "q":
                        moves += list_queen_moves(board, piece)
                    case "k":
                        pass
    return moves
                
def list_rook_moves(board: Board, piece: Piece):
    moves = []
    team = piece.color

    piece_row, piece_col = piece.position

    game_board = board.game_board

    # check the moves in the same row to the right (stop if there is a piece)
    # if there is a piece, check if it is an enemy piece
    # if it is an enemy piece, add the move and stop
    # if it is a friendly piece, stop

    # same row to the right
    for i in range(piece_col + 1, 8):
        if game_board[piece_row][i]:
            if game_board[piece_row][i].color == team:
                break
            moves.append(Move(piece.position, (piece_row, i)))
            break
        moves.append(Move(piece.position, (piece_row, i)))

    # same row to the left
    for i in range(piece_col - 1, -1, -1):
        if game_board[piece_row][i]:
            if game_board[piece_row][i].color == team:
                break
            moves.append(Move(piece.position, (piece_row, i)))
            break
        moves.append(Move(piece.position, (piece_row, i)))

    # same column to the top
    for i in range(piece_row - 1, -1, -1):
        if game_board[i][piece_col]:
            if game_board[i][piece_col].color == team:
                break
            moves.append(Move(piece.position, (i, piece_col)))
            break
        moves.append(Move(piece.position, (i, piece_col)))
                     
    # same column to the bottom
    for i in range(piece_row + 1, 8):
        if game_board[i][piece_col]:
            if game_board[i][piece_col].color == team:
                break
            moves.append(Move(piece.position, (i, piece_col)))
            break
        moves.append(Move(piece.position, (i, piece_col)))

    return moves

def list_knight_moves(board: Board, piece: Piece):
    moves = []
    team = piece.color

    piece_row, piece_col = piece.position

    game_board = board.game_board

    # Define the possible knight moves
    knight_moves = [
        (-2, 1), (-1, 2), (1, 2), (2, 1), # top right, right top, right bottom, bottom right
        (-2, -1), (-1, -2), (1, -2), (2, -1) # top left, left top, left bottom, bottom left
    ]

    # Iterate over each possible move
    for move in knight_moves:
        new_row = piece_row + move[0]
        new_col = piece_col + move[1]

        # Check if the new position is within the board boundaries
        if 0 > new_row or new_row > 7 or 0 > new_col or new_col > 7:
            continue
        # Check if the new position is empty or contains an enemy piece
        if not game_board[new_row][new_col]:
            moves.append(Move(piece.position, (new_row, new_col)))

        elif game_board[new_row][new_col].color != team:
            moves.append(Move(piece.position, (new_row, new_col)))
    return moves

def list_bishop_moves(board: Board, piece: Piece):
    moves = []
    team = piece.color

    piece_row, piece_col = piece.position

    game_board = board.game_board

    # check the moves in the diagonal to the top right
    for i in range(1, 8):
        if piece_row - i < 0 or piece_col + i > 7:
            break
        if game_board[piece_row - i][piece_col + i]:
            if game_board[piece_row - i][piece_col + i].color == team:
                break
            moves.append(Move(piece.position, (piece_row - i, piece_col + i)))
            break
        moves.append(Move(piece.position, (piece_row - i, piece_col + i)))

    # check the moves in the diagonal to the top left
    for i in range(1, 8):
        if piece_row - i < 0 or piece_col - i < 0:
            break
        if game_board[piece_row - i][piece_col - i]:
            if game_board[piece_row - i][piece_col - i].color == team:
                break
            moves.append(Move(piece.position, (piece_row - i, piece_col - i)))
            break
        moves.append(Move(piece.position, (piece_row - i, piece_col - i)))

    # check the moves in the diagonal to the bottom right
    for i in range(1, 8):
        if piece_row + i > 7 or piece_col + i > 7:
            break
        if board[piece_row + i][piece_col + i]:
            if board[piece_row + i][piece_col + i].color == team:
                break
            moves.append(Move(piece.position, (piece_row + i, piece_col + i)))
            break
        moves.append(Move(piece.position, (piece_row + i, piece_col + i)))

    # check the moves in the diagonal to the bottom left
    for i in range(1, 8):
        if piece_row + i > 7 or piece_col - i < 0:
            break
        if board[piece_row + i][piece_col - i]:
            if board[piece_row + i][piece_col - i].color == team:
                break
            moves.append(Move(piece.position, (piece_row + i, piece_col - i)))
            break
        moves.append(Move(piece.position, (piece_row + i,)))

    return moves

def list_queen_moves(board, piece):
    return list_rook_moves(board, piece) + list_bishop_moves(board, piece) # the queen moves are the same as the rook and bishop moves

def list_king_moves(board, piece):
    moves = []
    team = piece.color

    piece_row, piece_col = piece.position

    # Define the possible directions for the king to move
    directions = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]

    # Iterate over each direction
    for direction in directions:
        new_row = piece_row + direction[0]
        new_col = piece_col + direction[1]

        # Check if the new position is within the board boundaries
        if 0 > new_row or new_row > 7 or 0 > new_col or new_col > 7:
            continue

        # Check if the new position is empty or contains an enemy piece
        if not board[new_row][new_col]:
            moves.append(Move(piece.position, (new_row, new_col)))

        elif board[new_row][new_col].color != team:
            moves.append(Move(piece.position, (new_row, new_col)))

    # Check for castling moves KQkq
    if team == "white":
        if board.castling[0] and not board[7][5] and not board[7][6]:
            moves.append(Move(piece.position, (7, 6)))
        if board.castling[1] and not board[7][1] and not board[7][2] and not board[7][3]:
            moves.append(Move(piece.position, (7, 2)))
    else:
        if board.castling[2] and not board[0][5] and not board[0][6]:
            moves.append(Move(piece.position, (0, 6)))
        if board.castling[3] and not board[0][1] and not board[0][2] and not board[0][3]:
            moves.append(Move(piece.position, (0, 2)))

    return moves

def list_pawn_moves(board, piece):
    moves = []
    team = piece.color

    piece_row, piece_col = piece.position

    game_board = board.game_board

    # Define the possible directions for the pawn to move
    if team == "white":
        direction = -1 # the direction the pawn moves
        starting_row = 6 # the row where the pawn can move 2 squares forward
        en_passant_row = 3 # the row where the ally pawn can capture the enemy pawn en passant
    else:
        direction = 1
        starting_row = 1
        en_passant_row = 4

    # If the square in front of the pawn is empty, the pawn can move forward
    if not game_board[piece_row + direction][piece_col]:
        moves.append(Move(piece.position, (piece_row + direction, piece_col)))

        # If the pawn is in the starting position, the pawn can move 2 squares forward
        if piece_row == starting_row and not game_board[piece_row + 2 * direction][piece_col]:
            moves.append(Move(piece.position, (piece_row + 2 * direction, piece_col)))

    # If there is an enemy piece in the diagonal to the right, the pawn can move there
    if game_board[piece_row + direction][piece_col + 1] and game_board[piece_row + direction][piece_col + 1].color != team:
        moves.append(Move(piece.position, (piece_row + direction, piece_col + 1)))

    # If there is an enemy piece in the diagonal to the left, the pawn can move there
    if game_board[piece_row + direction][piece_col - 1] and game_board[piece_row + direction][piece_col - 1].color != team:
        moves.append(Move(piece.position, (piece_row + direction, piece_col - 1)))

    # Check for en passant
    if board.en_passant is not None and piece_row == en_passant_row:
        if piece_col == board.en_passant + 1 or piece_col == board.en_passant - 1:
            moves.append(Move(piece.position, (piece_row + direction, board.en_passant)))

    return moves

def filter_moves(board, moves):
    legal_moves = []
    for move in moves:
        new_row, new_col = move.end
        piece = board.game_board[move.start[0]][move.start[1]]
        new_piece = board.game_board[new_row][new_col]
        board.game_board[new_row][new_col] = piece
        board.game_board[move.start[0]][move.start[1]] = None
        if not board.ally_king_in_check():
            legal_moves.append(move)
        board.game_board[new_row][new_col] = new_piece
        board.game_board[move.start[0]][move.start[1]] = piece

class brd:
    def list_moves(self, row, col):
        '''
        Returns a list of moves for the piece in the given row and column
        '''
        piece = self.get_piece(row, col)
        moves = []
        if not self.is_piece(row, col): # if there is no piece in the given row and column
            return moves
        
        match piece.type.lower():
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
                if piece.team == "white":
                    moves = self.list_white_pawn_moves(row, col)
                else:
                    moves = self.list_black_pawn_moves(row, col)

        return moves

    def list_all_moves(self):
        '''
        Returns a list of all possible moves for the current player
        '''
        moves = []
        for row in range(8):
            for col in range(8):
                piece = self.get_piece(row, col)
                if piece and piece.team == self.turn:
                    moves += [((row, col), move) for move in self.get_legal_moves(row, col)]
        return moves

    def get_legal_moves(self, row, col):
        '''
        Returns a list of legal moves for the piece in the given row and column
        '''
        # if it is not the current player's turn, return an empty list
        if self.get_piece(row, col).team != self.turn:
            return []

        piece = self.get_piece(row, col)
        legal_moves = []
        moves = self.list_moves(row, col)
        for move in moves:
            # check if the move is legal by moving the piece and checking if the ally king is in check
            new_row, new_col = move
            new_piece = self.get_piece(new_row, new_col)
            self.game_board[new_row][new_col] = piece
            self.game_board[row][col] = None
            if not self.ally_king_in_check():
                legal_moves.append(move)

            # undo the move
            self.game_board[new_row][new_col] = new_piece
            self.game_board[row][col] = piece

        return legal_moves