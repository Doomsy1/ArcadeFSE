from pieces import Piece

STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


class Board:
    def __init__(self):
        self.undo_list = [] # list of board states for undoing moves

        self.game_FEN = STARTING_FEN
        self.FEN_to_board(self.game_FEN)

        self.legal_moves = generate_moves(self, self.turn)

    def copy(self):
        '''
        Returns a copy of the board
        '''
        new_board = Board()
        fen = self.generate_FEN()
        new_board.FEN_to_board(fen)
        return new_board

    def set_board(self, board):
        '''
        Sets the game board to the given board
        '''
        self.game_board = board

    def get_piece(self, row, col):
        '''
        Returns the piece in the given row and column
        '''
        if 0 <= row < 8 and 0 <= col < 8:
            return self.game_board[row][col]
        return None

    def has_legal_moves(self, row, col):
        '''
        Returns True if the piece in the given row and column has legal moves, False otherwise
        '''
        return any(move.start == (row, col) for move in self.legal_moves)

    def is_game_over(self):
        '''
        Returns True if the game is over, False otherwise
        '''
        return self.is_checkmate() or self.is_stalemate()

    def is_stalemate(self):
        '''
        Returns True if the game is in stalemate, False otherwise
        '''
        # Check if the ally king is not in check
        ally_king_in_check = self.ally_king_in_check()

        # Check if there are no legal moves
        no_legal_moves = self.legal_moves == []

        return not ally_king_in_check and no_legal_moves
    
    def is_checkmate(self):
        '''
        Returns True if the game is in checkmate, False otherwise
        '''
        # Check if the ally king is in check
        ally_king_in_check = self.ally_king_in_check()

        # Check if there are no legal moves
        no_legal_moves = self.legal_moves == []
        
        return ally_king_in_check and no_legal_moves

    def ally_king_in_check(self):
        '''
        Returns True if the ally king is in check, False otherwise
        '''
        # Get the position of the ally king
        for row in range(8):
            for col in range(8):
                piece = self.get_piece(row, col)
                if piece and piece.type == 'k' and piece.color == self.turn:
                    king_position = (row, col)
                    break
        # Check if the ally king is in check
        return any(move.end == king_position for move in self.legal_moves)

    def temp_move(self, move):
        '''
        Simplified version of make_move that returns True if the king is in check after the move, False otherwise. Doesn't update any variables
        '''
        start_row, start_col = move.start
        end_row, end_col = move.end
        save = self.generate_FEN()
        
        # move the piece to the new position
        piece = self.get_piece(start_row, start_col)

        # if the piece is a pawn and it moved diagonally, check if it is an en passant move and remove the enemy pawn that just moved 2 squares forward
        if piece.type.lower() == 'p' and start_col != end_col and not self.get_piece(end_row, end_col):
            self.game_board[start_row][end_col] = None

        self.game_board[end_row][end_col] = piece
        self.game_board[start_row][start_col] = None

        # update the legal moves
        self.legal_moves = generate_temp_moves(self, self.turn)

        # check if the king is in check
        king_in_check = self.ally_king_in_check()

        # undo the move
        self.FEN_to_board(save)

        return king_in_check


    def make_move(self, move): # this is the function that will be called when a player makes a move
        '''
        Moves the selected piece to the given row and column if it is a valid move
        '''
        start_row, start_col = move.start
        end_row, end_col = move.end
        self.undo_list.append(self.generate_FEN())

        # move the piece to the new position
        piece = self.get_piece(start_row, start_col)
        # if the piece is a pawn and it moved 2 squares forward, set the en passant variable to the end_column of the en passant square
        if piece.type.lower() == 'p':
            if abs(start_row - end_row) == 2:
                self.en_passant = end_col
            else:
                self.en_passant = None
        else:
            self.en_passant = None

        # if the piece is a pawn and it moved diagonally, check if it is an en passant move and remove the enemy pawn that just moved 2 squares forward
        if piece.type.lower() == 'p' and start_col != end_col and not self.get_piece(end_row, end_col):
            self.game_board[start_row][end_col] = None


        # if the king moved, disable castling for that king
        if piece.type == 'k':
            self.castling[2] = False
            self.castling[3] = False
        elif piece.type == 'K':
            self.castling[0] = False
            self.castling[1] = False

        # if the piece is a king and it moved 2 squares to the right or left, move the rook to the new position
        if piece.type.lower() == 'k' and abs(end_col - start_col) == 2:
            if end_col == 6:
                self.game_board[end_row][5] = self.game_board[end_row][7]
                self.game_board[end_row][7] = None
            else:
                self.game_board[end_row][3] = self.game_board[end_row][0]
                self.game_board[end_row][0] = None

        # if a rook moved, disable castling for that rook
        if piece.type.lower() == 'r':
            if move.start == (0, 0):
                self.castling[1] = False
            elif move.start == (0, 7):
                self.castling[0] = False
            elif move.start == (7, 0):
                self.castling[3] = False
            elif move.start == (7, 7):
                self.castling[2] = False

        # if a rook is captured, disable castling for that rook
        if self.get_piece(end_row, end_col) and self.get_piece(end_row, end_col).type.lower() == 'r':
            if end_row == 0 and end_col == 0:
                self.castling[1] = False
            elif end_row == 0 and end_col == 7:
                self.castling[0] = False
            elif end_row == 7 and end_col == 0:
                self.castling[3] = False
            elif end_row == 7 and end_col == 7:
                self.castling[2] = False

        # if the move is a pawn promotion, promote the pawn to a queen
        if piece.type == 'p' and end_row == 0:
            piece = Piece('q')
        elif piece.type == 'P' and end_row == 7:
            piece = Piece('Q')

        # if the move is a pawn move or a capture, reset the half move count
        if piece.type.lower() == 'p' or self.get_piece(end_row, end_col):
            self.half_move_count = 0
        else:
            self.half_move_count += 1

        self.game_board[end_row][end_col] = piece
        self.game_board[start_row][start_col] = None
        self.turn = 'white' if self.turn == 'black' else 'black'

        # update the legal moves
        self.legal_moves = generate_moves(self, self.turn)

    def undo_move(self):
        '''
        Undoes the last move
        '''
        if self.undo_list:
            self.FEN_to_board(self.undo_list.pop())

            # update the legal moves
            self.legal_moves = generate_moves(self, self.turn)

    def FEN_to_board(self, FEN):
        '''
        Converts the FEN string to a 2D list representing the game board
        '''
        board = []
        # split the FEN string to get the board state and the turn and castling information
        FEN = FEN.split()
        board_state = FEN[0]
        turn = FEN[1]
        castling = FEN[2]
        en_passant = FEN[3]
        half_move_count = FEN[4]
        full_move_count = FEN[5]

        # split the board state to get the rows
        rows = board_state.split('/')
        for row_num, row in enumerate(rows):
            new_row = []
            col_num = 0
            for char in row:
                if char.isdigit():
                    for _ in range(int(char)):
                        new_row.append(Piece(None, (row_num, col_num)))
                        col_num += 1
                else:
                    new_row.append(Piece(char, (row_num, col_num)))
                    col_num += 1
            board.append(new_row)

        self.game_board = board
        self.turn = "white" if turn == "w" else "black"
        self.castling = [True if char in castling else False for char in "KQkq"]
        self.en_passant = None if en_passant == "-" else ord(en_passant[0]) - ord('a')

        self.half_move_count = half_move_count
        self.full_move_count = full_move_count

    def generate_FEN(self):
        ''''
        Generates the FEN string from the game board
        '''
        fen = ''
        for row in self.game_board[::-1]:
            empty = 0
            for piece in row[::-1]:
                if not piece:
                    empty += 1
                else:
                    if empty:
                        fen += str(empty)
                        empty = 0
                    if piece.color == 'white':
                        fen += piece.type.upper()
                    else:
                        fen += piece.type
            if empty:
                fen += str(empty)
            fen += '/'

        fen = fen[:-1] + ' '
        fen += 'w' if self.turn == 'white' else 'b'
        fen += ' '
        fen += ''.join(['K' if self.castling[0] else '', 'Q' if self.castling[1] else '', 'k' if self.castling[2] else '', 'q' if self.castling[3] else ''])
        if not any(self.castling):
            fen += '-'
        fen += ' '
        fen += chr(self.en_passant + ord('a')) if self.en_passant is not None else '-'
        fen += ' '
        fen += str(self.half_move_count) + ' ' + str(self.full_move_count)
        return fen


class Move:
    def __init__(self, start, end):
        self.start = start
        self.end = end

def generate_temp_moves(board: Board, turn):
    moves = []
    for row in range(8):
        for col in range(8):
            piece = board.get_piece(row, col)
            # if there is a piece in the current square and it is the current player's turn
            if piece and piece.color == turn:
                match piece.type:
                    case "p":
                        moves += list_pawn_moves(board, piece)
                    case "n":
                        moves += list_knight_moves(board, piece)
                    case "b":
                        moves += list_bishop_moves(board, piece)
                    case "r":
                        moves += list_rook_moves(board, piece)
                    case "q":
                        moves += list_queen_moves(board, piece)
                    case "k":
                        moves += list_king_moves(board, piece)
    return moves

def generate_moves(board: Board, turn):
    moves = []
    for row in range(8):
        for col in range(8):
            piece = board.get_piece(row, col)
            # if there is a piece in the current square and it is the current player's turn
            if piece and piece.color == turn:
                match piece.type:
                    case "p":
                        print("p")
                        moves += list_pawn_moves(board, piece)
                    case "n":
                        moves += list_knight_moves(board, piece)
                    case "b":
                        moves += list_bishop_moves(board, piece)
                    case "r":
                        moves += list_rook_moves(board, piece)
                    case "q":
                        moves += list_queen_moves(board, piece)
                    case "k":
                        moves += list_king_moves(board, piece)
    legal_moves = filter_moves(board, moves)
    return legal_moves
                
def list_rook_moves(board: Board, piece: Piece):
    moves = []
    team = piece.color

    piece_row, piece_col = piece.position

    # check the moves in the same row to the right (stop if there is a piece)
    # if there is a piece, check if it is an enemy piece
    # if it is an enemy piece, add the move and stop
    # if it is a friendly piece, stop

    # same row to the right
    for i in range(piece_col + 1, 8):
        new_piece = board.get_piece(piece_row, i)
        if new_piece:
            if new_piece.color == team:
                break
            moves.append(Move(piece.position, (piece_row, i)))
            break
        moves.append(Move(piece.position, (piece_row, i)))

    # same row to the left
    for i in range(piece_col - 1, -1, -1):
        new_piece = board.get_piece(piece_row, i)
        if new_piece:
            if new_piece.color == team:
                break
            moves.append(Move(piece.position, (piece_row, i)))
            break
        moves.append(Move(piece.position, (piece_row, i)))

    # same column to the top
    for i in range(piece_row - 1, -1, -1):
        new_piece = board.get_piece(i, piece_col)
        if new_piece:
            if new_piece.color == team:
                break
            moves.append(Move(piece.position, (i, piece_col)))
            break
        moves.append(Move(piece.position, (i, piece_col)))

    # same column to the bottom
    for i in range(piece_row + 1, 8):
        new_piece = board.get_piece(i, piece_col)
        if new_piece:
            if new_piece.color == team:
                break
            moves.append(Move(piece.position, (i, piece_col)))
            break
        moves.append(Move(piece.position, (i, piece_col)))

    return moves

def list_knight_moves(board: Board, piece: Piece):
    moves = []
    team = piece.color

    piece_row, piece_col = piece.position

    # Define the possible knight moves
    knight_moves = [
        (-2, 1), (-1, 2), (1, 2), (2, 1), # top right, right top, right bottom, bottom right
        (-2, -1), (-1, -2), (1, -2), (2, -1) # top left, left top, left bottom, bottom left
    ]

    # Iterate over each possible move
    for move in knight_moves:
        new_row = piece_row + move[0]
        new_col = piece_col + move[1]

        new_piece = board.get_piece(new_row, new_col)

        # Check if the new position is within the board boundaries
        if 0 > new_row or new_row > 7 or 0 > new_col or new_col > 7:
            continue
        # Check if the new position is empty or contains an enemy piece
        if not new_piece:
            moves.append(Move(piece.position, (new_row, new_col)))

        elif new_piece.color != team:
            moves.append(Move(piece.position, (new_row, new_col)))
    return moves

def list_bishop_moves(board: Board, piece: Piece):
    moves = []
    team = piece.color

    piece_row, piece_col = piece.position

    # check the moves in the diagonal to the top right
    for i in range(1, 8):
        if piece_row - i < 0 or piece_col + i > 7:
            break

        new_piece = board.get_piece(piece_row - i, piece_col + i)
        if new_piece:
            if new_piece.color == team:
                break
            moves.append(Move(piece.position, (piece_row - i, piece_col + i)))
            break
        moves.append(Move(piece.position, (piece_row - i, piece_col + i)))

    # check the moves in the diagonal to the top left
    for i in range(1, 8):
        if piece_row - i < 0 or piece_col - i < 0:
            break

        new_piece = board.get_piece(piece_row - i, piece_col - i)
        if new_piece:
            if new_piece.color == team:
                break
            moves.append(Move(piece.position, (piece_row - i, piece_col - i)))
            break
        moves.append(Move(piece.position, (piece_row - i, piece_col - i)))

    # check the moves in the diagonal to the bottom right
    for i in range(1, 8):
        if piece_row + i > 7 or piece_col + i > 7:
            break

        new_piece = board.get_piece(piece_row + i, piece_col + i)
        if new_piece:
            if new_piece.color == team:
                break
            moves.append(Move(piece.position, (piece_row + i, piece_col + i)))
            break
        moves.append(Move(piece.position, (piece_row + i, piece_col + i)))

    # check the moves in the diagonal to the bottom left
    for i in range(1, 8):
        if piece_row + i > 7 or piece_col - i < 0:
            break

        new_piece = board.get_piece(piece_row + i, piece_col - i)
        if new_piece:
            if new_piece.color == team:
                break
            moves.append(Move(piece.position, (piece_row + i, piece_col - i)))
            break
        moves.append(Move(piece.position, (piece_row + i, piece_col - i)))

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
        new_position = board.get_piece(new_row, new_col)
        if not new_position:
            moves.append(Move(piece.position, (new_row, new_col)))

        elif new_position.color != team:
            moves.append(Move(piece.position, (new_row, new_col)))

    # Check for castling moves KQkq
    if team == "white":
        if board.castling[0] and not board.get_piece(7, 5) and not board.get_piece(7, 6):
            moves.append(Move(piece.position, (7, 6)))
        if board.castling[1] and not board.get_piece(7, 1) and not board.get_piece(7, 2) and not board.get_piece(7, 3):
            moves.append(Move(piece.position, (7, 2)))
    else:
        if board.castling[2] and not board.get_piece(0, 5) and not board.get_piece(0, 6):
            moves.append(Move(piece.position, (0, 6)))
        if board.castling[3] and not board.get_piece(0, 1) and not board.get_piece(0, 2) and not board.get_piece(0, 3):
            moves.append(Move(piece.position, (0, 2)))

    return moves

def list_pawn_moves(board, piece):
    moves = []
    team = piece.color

    piece_row, piece_col = piece.position

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
    if not board.get_piece(piece_row + direction, piece_col):
        moves.append(Move(piece.position, (piece_row + direction, piece_col)))

        # If the pawn is in the starting position, the pawn can move 2 squares forward
        if piece_row == starting_row and not board.get_piece(piece_row + 2 * direction, piece_col):
            moves.append(Move(piece.position, (piece_row + 2 * direction, piece_col)))

    # If there is an enemy piece in the diagonal to the right, the pawn can move there
    new_piece = board.get_piece(piece_row + direction, piece_col + 1)
    if new_piece and new_piece.color != team:
        moves.append(Move(piece.position, (piece_row + direction, piece_col + 1)))

    new_piece = board.get_piece(piece_row + direction, piece_col - 1)
    # If there is an enemy piece in the diagonal to the left, the pawn can move there
    if new_piece and new_piece.color != team:
        moves.append(Move(piece.position, (piece_row + direction, piece_col - 1)))

    # Check for en passant
    if board.en_passant is not None and piece_row == en_passant_row:
        if piece_col == board.en_passant + 1 or piece_col == board.en_passant - 1:
            moves.append(Move(piece.position, (piece_row + direction, board.en_passant)))

    return moves

def king_in_check(board, team):
    for row in range(8):
        for col in range(8):
            piece = board.get_piece(row, col)
            if piece and piece.color != team:
                moves = []
                match piece:
                    case "p":
                        moves = list_pawn_moves(board, piece)
                    case "n":
                        moves = list_knight_moves(board, piece)
                    case "b":
                        moves = list_bishop_moves(board, piece)
                    case "r":
                        moves = list_rook_moves(board, piece)
                    case "q":
                        moves = list_queen_moves(board, piece)
                    case "k":
                        moves = list_king_moves(board, piece)
                for move in moves:
                    new_row, new_col = move.end
                    if board.get_piece(new_row, new_col).type == "k":
                        return True
    return False

def filter_moves(board, moves):
    legal_moves = []
    for move in moves:
        start = move.start
        end = move.end
        # filter illegal castling moves (the king cannot move through check)
        start_piece = board.get_piece(start[0], start[1])
        if start_piece.type == "k" and start[1] - end[1] == 2:
            # simulate moving the king 1 square to the right (the king cannot move through check so if the king is in check after moving 1 square to the right, the move is illegal)
            if not board.temp_move(Move(start, (start[0], start[1] + 1))):
                legal_moves.append(move)

        elif start_piece.type == "k" and end[1] - start[1] == 2:
            # simulate moving the king 1 square to the left
            if not board.temp_move(Move(start, (start[0], start[1] - 1))):
                legal_moves.append(move)

        else: # if the move is not a castling move (it is a normal move)
            if not board.temp_move(move):
                legal_moves.append(move)


    return legal_moves