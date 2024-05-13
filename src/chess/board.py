from pieces import Piece

STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"



class Board:
    def __init__(self):
        self.selected_piece = None
        self.undo_list = [] # list of board states for undoing moves

    def init_board(self):
        '''
        Initializes the game board to the starting position
        '''
        self.game_FEN = STARTING_FEN
        self.FEN_to_board(self.game_FEN)

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
        return self.game_board[row][col]

    def is_piece(self, row, col):
        '''
        Returns True if there is a piece in the given row and column, False otherwise
        '''
        return self.get_piece(row, col) is not None

    def select_piece(self, row, col):
        '''
        Selects the piece in the given row and column
        '''
        self.selected_piece = [row, col]

    def piece_selected(self):
        '''
        Returns True if a piece is selected, False otherwise
        '''
        return self.selected_piece is not None
    
    def deselect_piece(self):
        '''
        Deselects the selected piece
        '''
        self.selected_piece = None
    
    def has_legal_moves(self, row, col):
        '''
        Returns True if the piece in the given row and column has legal moves, False otherwise
        '''
        moves = self.get_legal_moves(row, col)
        return bool(moves)

    def is_game_over(self):
        '''
        Returns True if the game is over, False otherwise
        '''
        return self.is_checkmate() or self.is_stalemate()

    def is_stalemate(self):
        '''
        Returns True if the game is in stalemate, False otherwise
        '''
        if self.ally_king_in_check():
            return False
        if any(self.has_legal_moves(row, col) for row in range(8) for col in range(8) if self.get_piece(row, col) and self.get_piece(row, col).team == self.turn):
            return False
        return True
    
    def is_checkmate(self):
        '''
        Returns True if the game is in checkmate, False otherwise
        '''
        # Check if the ally king is in check and it has no legal moves
        return self.ally_king_in_check() and all(not self.has_legal_moves(row, col) for row in range(8) for col in range(8) if self.get_piece(row, col) and self.get_piece(row, col).team == self.turn)

    def ally_king_in_check(self):
        '''
        Returns True if the ally king is in check, False otherwise
        '''
        for row in range(8):
            for col in range(8):
                piece = self.get_piece(row, col)
                if piece and piece.team != self.turn and self.piece_threatens_king(row, col):
                    return True
        return False

    def piece_threatens_king(self, row, col):
        '''
        Returns True if the piece in the given row and column threatens the enemy king, False otherwise
        '''
        moves = self.list_moves(row, col)
        for move in moves:
            new_row, new_col = move
            new_piece = self.get_piece(new_row, new_col)
            if new_piece and new_piece.type.lower() == 'k':
                return True
        return False



    def make_move(self, row, col): # this is the function that will be called when a player makes a move
        '''
        Moves the selected piece to the given row and column if it is a valid move
        '''
        # if a piece is already selected, move the piece to the new position if it is a valid move. if it is not a valid move, deselect the piece
        self.move_piece(row, col)
        self.deselect_piece()

    def move_piece(self, row, col):
        '''
        Moves the selected piece to the given row and column
        '''
        self.undo_list.append(self.generate_FEN())

        # move the piece to the new position
        piece = self.get_piece(self.selected_piece[0], self.selected_piece[1])
        # if the piece is a pawn and it moved 2 squares forward, set the en passant variable to the column of the en passant square
        if piece.type.lower() == 'p':
            if abs(self.selected_piece[0] - row) == 2:
                self.en_passant = col
            else:
                self.en_passant = None
        else:
            self.en_passant = None

        # if the piece is a pawn and it moved diagonally, check if it is an en passant move and remove the enemy pawn that just moved 2 squares forward
        if piece.type.lower() == 'p' and col != self.selected_piece[1] and not self.is_piece(row, col):
            self.game_board[self.selected_piece[0]][col] = None


        # if the king moved, disable castling for that king
        if piece.type == 'k':
            self.castling[2] = False
            self.castling[3] = False
        elif piece.type == 'K':
            self.castling[0] = False
            self.castling[1] = False

        # if the piece is a king and it moved 2 squares to the right or left, move the rook to the new position
        if piece.type.lower() == 'k' and abs(col - self.selected_piece[1]) == 2:
            if col == 6:
                self.game_board[row][5] = self.game_board[row][7]
                self.game_board[row][7] = None
            else:
                self.game_board[row][3] = self.game_board[row][0]
                self.game_board[row][0] = None

        # if a rook moved, disable castling for that rook
        if piece.type.lower() == 'r':
            if self.selected_piece == (0, 0):
                self.castling[1] = False
            elif self.selected_piece == (0, 7):
                self.castling[0] = False
            elif self.selected_piece == (7, 0):
                self.castling[3] = False
            elif self.selected_piece == (7, 7):
                self.castling[2] = False

        # if a rook is captured, disable castling for that rook
        if self.is_piece(row, col) and self.get_piece(row, col).type.lower() == 'r':
            if row == 0 and col == 0:
                self.castling[1] = False
            elif row == 0 and col == 7:
                self.castling[0] = False
            elif row == 7 and col == 0:
                self.castling[3] = False
            elif row == 7 and col == 7:
                self.castling[2] = False

        # if the move is a pawn promotion, promote the pawn to a queen
        if piece.type == 'p' and row == 0:
            piece = Piece('q')
        elif piece.type == 'P' and row == 7:
            piece = Piece('Q')

        self.game_board[row][col] = piece
        self.game_board[self.selected_piece[0]][self.selected_piece[1]] = None
        self.turn = 'white' if self.turn == 'black' else 'black'

    def undo_move(self):
        '''
        Undoes the last move
        '''
        if self.undo_list:
            self.FEN_to_board(self.undo_list.pop())

    def full_move(self, start, end):
        '''
        Moves the piece from the start position to the end position
        '''
        start_row, start_col = start
        end_row, end_col = end
        self.select_piece(start_row, start_col)
        self.make_move(end_row, end_col)


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
        for row in rows:
            new_row = []
            for char in row:
                if char.isdigit():
                    new_row += [None for _ in range(int(char))]
                else:
                    new_row.append(Piece(char))
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

    def list_rook_moves(self, row, col):
        '''
        Returns a list of moves for the rook in the given row and column
        '''
        moves = []
        team = self.get_piece(row, col).team

        # check the moves in the same row to the right (stop if there is a piece)
        # if there is a piece, check if it is an enemy piece
        # if it is an enemy piece, add the move and stop
        # if it is a friendly piece, stop
        for i in range(col + 1, 8):
            if self.is_piece(row, i):
                if self.get_piece(row, i).team == team:
                    break
                moves.append((row, i))
                break
            moves.append((row, i))

        # same row to the left
        for i in range(col - 1, -1, -1):
            if self.is_piece(row, i):
                if self.get_piece(row, i).team == team:
                    break
                moves.append((row, i))
                break
            moves.append((row, i))

        # same column to the top
        for i in range(row - 1, -1, -1):
            if self.is_piece(i, col):
                if self.get_piece(i, col).team == team:
                    break
                moves.append((i, col))
                break
            moves.append((i, col))

        # same column to the bottom
        for i in range(row + 1, 8):
            if self.is_piece(i, col):
                if self.get_piece(i, col).team == team:
                    break
                moves.append((i, col))
                break
            moves.append((i, col))

        return moves

    def list_knight_moves(self, row, col):
        ''''
        Returns a list of moves for the knight in the given row and column
        '''
        # the knight moves in an L shape
        moves = []
        team = self.get_piece(row, col).team

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

            elif self.get_piece(new_row, new_col).team != team:
                moves.append((new_row, new_col))
        return moves

    def list_bishop_moves(self, row, col):
        '''
        Returns a list of moves for the bishop in the given row and column
        '''
        moves = []
        team = self.get_piece(row, col).team
        
        # check the moves in the diagonal to the top right
        for i in range(1, 8):
            if row - i < 0 or col + i > 7:
                break
            if self.is_piece(row - i, col + i):
                if self.get_piece(row - i, col + i).team == team:
                    break
                moves.append((row - i, col + i))
                break
            moves.append((row - i, col + i))

        # check the moves in the diagonal to the top left
        for i in range(1, 8):
            if row - i < 0 or col - i < 0:
                break
            if self.is_piece(row - i, col - i):
                if self.get_piece(row - i, col - i).team == team:
                    break
                moves.append((row - i, col - i))
                break
            moves.append((row - i, col - i))

        # check the moves in the diagonal to the bottom right
        for i in range(1, 8):
            if row + i > 7 or col + i > 7:
                break
            if self.is_piece(row + i, col + i):
                if self.get_piece(row + i, col + i).team == team:
                    break
                moves.append((row + i, col + i))
                break
            moves.append((row + i, col + i))

        # check the moves in the diagonal to the bottom left
        for i in range(1, 8):
            if row + i > 7 or col - i < 0:
                break
            if self.is_piece(row + i, col - i):
                if self.get_piece(row + i, col - i).team == team:
                    break
                moves.append((row + i, col - i))
                break
            moves.append((row + i, col - i))

        return moves

    def list_queen_moves(self, row, col):
        '''
        Returns a list of moves for the queen in the given row and column
        '''
        # the queen moves are the same as the rook and bishop moves
        return self.list_rook_moves(row, col) + self.list_bishop_moves(row, col)

    def list_king_moves(self, row, col):
        '''
        Returns a list of moves for the king in the given row and column
        '''
        # the king moves in all directions by 1 square
        moves = []
        team = self.get_piece(row, col).team

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

            elif self.get_piece(new_row, new_col).team != team:
                moves.append((new_row, new_col))

        # Check for castling moves KQkq
        if team == "white":
            if self.castling[0] and not self.is_piece(7, 5) and not self.is_piece(7, 6):
                moves.append((7, 6))
            if self.castling[1] and not self.is_piece(7, 1) and not self.is_piece(7, 2) and not self.is_piece(7, 3):
                moves.append((7, 2))
        else:
            if self.castling[2] and not self.is_piece(0, 5) and not self.is_piece(0, 6):
                moves.append((0, 6))
            if self.castling[3] and not self.is_piece(0, 1) and not self.is_piece(0, 2) and not self.is_piece(0, 3):
                moves.append((0, 2))

        return moves

    def list_white_pawn_moves(self, row, col):
        '''
        Returns a list of moves for the white pawn in the given row and column
        '''
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

        # check the diagonal to the top right and top left for enemy pieces or en passant
        if col < 7 and self.is_piece(row - 1, col + 1):
            if self.get_piece(row - 1, col + 1).team == "black":
                moves.append((row - 1, col + 1))
        if col > 0 and self.is_piece(row - 1, col - 1):
            if self.get_piece(row - 1, col - 1).team == "black":
                moves.append((row - 1, col - 1))

        # check en passant
        if self.en_passant is not None:
            if row == 3 and (col == self.en_passant + 1 or col == self.en_passant - 1):
                moves.append((row - 1, self.en_passant))

        return moves
    
    def list_black_pawn_moves(self, row, col):
        '''
        Returns a list of moves for the black pawn in the given row and column
        '''
        moves = []
        # the black pawn moves forward if the square in front is empty
        # the black pawn can move 2 squares forward if it is in the starting position and the 2 squares in front are empty (row 1)
        # the black pawn can move diagonally to the right or left if there is an enemy piece
        # the black pawn can move diagonally to the right or left if there is an enemy pawn that just moved 2 squares forward (en passant) (use the en passant variable)

        # check the square in front
        if not self.is_piece(row + 1, col):
            moves.append((row + 1, col))
            # check if the pawn is in the starting position
            if row == 1 and not self.is_piece(row + 2, col):
                moves.append((row + 2, col))

        # check the diagonal to the bottom right and bottom left for enemy pieces or en passant
        if col < 7 and self.is_piece(row + 1, col + 1):
            if self.get_piece(row + 1, col + 1).team == "white":
                moves.append((row + 1, col + 1))
        if col > 0 and self.is_piece(row + 1, col - 1):
            if self.get_piece(row + 1, col - 1).team == "white":
                moves.append((row + 1, col - 1))

        # check en passant
        if self.en_passant is not None:
            if row == 4 and (col == self.en_passant + 1 or col == self.en_passant - 1):
                moves.append((row + 1, self.en_passant))

        return moves