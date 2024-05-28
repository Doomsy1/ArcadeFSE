# this board structure is inspired by Sebastian Lague's video entitled "Coding Adventure: Chess"
# Link: https://www.youtube.com/watch?v=U4ogK0MIzqk


import random





class Piece:
    # last 3 bits are type
    pawn = 1
    knight = 2
    bishop = 3
    rook = 4
    queen = 5
    king = 6

    # first 2 bits are color
    white = 8
    black = 16

    @staticmethod
    def is_color(piece, color):
        return piece & color
    
    @staticmethod
    def is_type(piece, type):
        return piece & type

    @staticmethod
    def get_color(piece):
        return piece & 24 # 24 is 11000 in binary
    
    @staticmethod
    def get_type(piece):
        return piece & 7 # 7 is 111 in binary
    
    @staticmethod
    def make_piece(color, type):
        return color | type

    @staticmethod
    def get_piece(color, type):
        return color | type

    @staticmethod
    def get_piece_from_char(char):
        return piece_to_char_map[char]
    
    @staticmethod
    def get_char_from_piece(piece):
        return char_to_piece_map[piece]
        
    @staticmethod
    def directions_for_piece(piece_type):
        if piece_type == Piece.rook:
            return [8, 1, -8, -1]  # vertical and horizontal
        elif piece_type == Piece.bishop:
            return [9, 7, -7, -9]  # diagonal
        elif piece_type == Piece.queen:
            return [8, 1, -8, -1, 9, 7, -7, -9]  # combination of rook and bishop
        return []
    
    @staticmethod
    def moves_for_piece(piece_type, square):
        file = square % 8
        rank = square // 8

        if piece_type == Piece.pawn:
            # Assuming this is just for generating attack squares, not actual moves
            return [square + 8, square - 8] if file != 0 else []

        elif piece_type == Piece.knight:
            moves = []
            knight_moves = [(-2, -1), (-1, -2), (1, -2), (2, -1), (2, 1), (1, 2), (-1, 2), (-2, 1)]
            for dr, dc in knight_moves:
                r, c = rank + dr, file + dc
                if 0 <= r < 8 and 0 <= c < 8:
                    moves.append(r * 8 + c)
            return moves

        elif piece_type == Piece.king:
            moves = []
            king_moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
            for dr, dc in king_moves:
                r, c = rank + dr, file + dc
                if 0 <= r < 8 and 0 <= c < 8:
                    moves.append(r * 8 + c)
            return moves

        return []

piece_to_char_map = {
    'p': Piece.black | Piece.pawn,
    'n': Piece.black | Piece.knight,
    'b': Piece.black | Piece.bishop,
    'r': Piece.black | Piece.rook,
    'q': Piece.black | Piece.queen,
    'k': Piece.black | Piece.king,
    'P': Piece.white | Piece.pawn,
    'N': Piece.white | Piece.knight,
    'B': Piece.white | Piece.bishop,
    'R': Piece.white | Piece.rook,
    'Q': Piece.white | Piece.queen,
    'K': Piece.white | Piece.king,
}
char_to_piece_map = {
    Piece.black | Piece.pawn: 'p',
    Piece.black | Piece.knight: 'n',
    Piece.black | Piece.bishop: 'b',
    Piece.black | Piece.rook: 'r',
    Piece.black | Piece.queen: 'q',
    Piece.black | Piece.king: 'k',
    Piece.white | Piece.pawn: 'P',
    Piece.white | Piece.knight: 'N',
    Piece.white | Piece.bishop: 'B',
    Piece.white | Piece.rook: 'R',
    Piece.white | Piece.queen: 'Q',
    Piece.white | Piece.king: 'K',
}


knight_directions = [
    -17, # (-8 x 2) - 1    | 2 down, 1 left
    -15, # (-8 x 2) + 1    | 2 down, 1 right
    -10, # (-8 + 2) x 2    | 1 down, 2 left
    -6, # (-8 + 2) x 2    | 1 down, 2 right
    6,  # (8 - 2) x 2     | 1 up, 2 left
    10,  # (8 + 2) x 2     | 1 up, 2 right
    15,  # (8 x 2) + 1     | 2 up, 1 left
    17   # (8 x 2) - 1     | 2 up, 1 right
]

directions = [8, 1, -8, -1, 9, 7, -7, -9]
distance_to_edge = []

for square in range(64):
    file = square % 8
    rank = square // 8

    # horizontal and vertical distances
    distance_to_north = 7 - rank
    distance_to_east = 7 - file
    distance_to_south = rank
    distance_to_west = file

    # diagonal distances
    distance_to_north_east = min(distance_to_north, distance_to_east)
    distance_to_north_west = min(distance_to_north, distance_to_west)
    distance_to_south_east = min(distance_to_south, distance_to_east)
    distance_to_south_west = min(distance_to_south, distance_to_west)

    distance_to_edge.append((
        distance_to_north,      # 0
        distance_to_east,       # 1
        distance_to_south,      # 2
        distance_to_west,       # 3

        distance_to_north_east, # 4
        distance_to_north_west, # 5

        distance_to_south_east, # 6
        distance_to_south_west  # 7
    ))

# moves will be represented as a tuple
# (start, end, start_piece, captured_piece, promotion_piece, castling, en_passant)

STARTING_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

class Board:
    def __init__(self, fen=STARTING_FEN):
        self.board = [0] * 64                   # 64 squares

        self.white_king_square = 0              # square of white king
        self.black_king_square = 0              # square of black king

        self.white_pieces = []                  # list of white piece squares
        self.black_pieces = []                  # list of black piece squares

        self.white_attacked_squares = [0] * 64  # list of squares attacked by white (used by is_check)
        self.black_attacked_squares = [0] * 64  # list of squares attacked by black (used by is check)

        self.white_to_move = True               # True if it's white's turn
        self.castling_rights = 0                # 4 bits for each side (KQkq)
        self.en_passant_target_square = 0       # square where en passant is possible (0 if not possible)
        self.halfmove_clock = 0                 # number of halfmoves since last capture or pawn move
        self.fullmove_number = 0                # starts at 1 and is incremented after b's move

        self.undo_list = []                     # list of previous board states

        self.generated_moves = {}               # dictionary of generated moves for each board state

        self.load_fen(fen)

    def hash_board(self, turn):
        '''Returns a hash of the board state'''
        # TODO: implement Zobrist hashing
        # for now, use python's built-in hash function
        return hash((tuple(self.board), self.white_to_move, turn, self.castling_rights, self.en_passant_target_square))

    def __copy__(self):
        new_board = Board()
        new_board.board = self.board

        new_board.white_king_square = self.white_king_square
        new_board.black_king_square = self.black_king_square

        new_board.white_pieces = self.white_pieces
        new_board.black_pieces = self.black_pieces

        new_board.white_attacked_squares = self.white_attacked_squares
        new_board.black_attacked_squares = self.black_attacked_squares

        new_board.white_to_move = self.white_to_move
        new_board.castling_rights = self.castling_rights
        new_board.en_passant_target_square = self.en_passant_target_square
        new_board.halfmove_clock = self.halfmove_clock
        new_board.fullmove_number = self.fullmove_number
        new_board.undo_list = self.undo_list

        return new_board

    def is_piece(self, square):
        '''Returns True if there is a piece on the square, False otherwise'''
        return self.board[square] != 0 # bool?
    
    def is_empty(self, square):
        '''Returns True if the square is empty, False otherwise'''
        return self.board[square] == 0
    
    def get_piece(self, square):
        '''Returns the piece on the square'''
        return self.board[square]
    
    def set_piece(self, square, piece):
        '''Sets the piece on the square'''
        self.board[square] = piece

        if Piece.get_color(piece) == Piece.white:
            self.white_pieces.append(square)
            if Piece.get_type(piece) == Piece.king:
                self.white_king_square = square

        else:
            self.black_pieces.append(square)
            if Piece.get_type(piece) == Piece.king:
                self.black_king_square = square

        self.update_attacks(square, piece, add=True)

    def clear_piece(self, square, piece):
        '''Clears the piece on the square'''
        self.board[square] = 0

        if Piece.get_color(piece) == Piece.white:
            self.white_pieces.remove(square)

        else:
            self.black_pieces.remove(square)

        self.update_attacks(square, piece, add=False)

    def move_piece(self, start_square, end_square, piece):
        '''Moves the piece from start_square to end_square'''
        self.clear_piece(start_square, piece)
        self.set_piece(end_square, piece)

        self.update_attacks(start_square, piece, add=False)
        self.update_attacks(end_square, piece, add=True)

    def load_fen(self, fen):
        '''Sets the state of the board to the given FEN string'''

        # example fen: 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

        # reset board
        self.board = [0] * 64

        self.white_king_square = 0
        self.black_king_square = 0
        
        self.white_pieces = []
        self.black_pieces = []
        
        fen_data = fen.split(' ')
        piece_placement = fen_data[0]
        turn = fen_data[1]
        castling_rights = fen_data[2]
        en_passant_square = fen_data[3]
        halfmove_clock = fen_data[4]
        fullmove_number = fen_data[5]

        # set up the board
        rank = 7
        file = 0
        for char in piece_placement:
            # new rank
            if char == '/':
                rank -= 1
                file = 0

            # empty square
            elif char.isdigit():
                file += int(char)

            # piece
            else:
                square = rank * 8 + file
                piece = Piece.get_piece_from_char(char)
                self.set_piece(square, piece)
                file += 1

        # set the turn
        self.white_to_move = turn == 'w'

        # set the castling rights
        self.castling_rights = 0
        for char in castling_rights:
            if char == 'K':
                self.castling_rights |= 8 # 1000
            elif char == 'Q':
                self.castling_rights |= 4 # 0100
            elif char == 'k':
                self.castling_rights |= 2 # 0010
            elif char == 'q':
                self.castling_rights |= 1 # 0001

        # set the en passant square
        self.en_passant_target_square = 0
        if en_passant_square != '-':
            file = ord(en_passant_square[0]) - ord('a')
            rank = int(en_passant_square[1]) - 1
            self.en_passant_target_square = rank * 8 + file

        # set the halfmove clock and fullmove number
        self.halfmove_clock = int(halfmove_clock)
        self.fullmove_number = int(fullmove_number)

    def create_fen(self):
        '''Returns the FEN string representing the state of the board'''

        # piece placement
        fen = ''
        empty_counter = 0
        for rank in range(7, -1, -1):
            for file in range(8):
                square = rank * 8 + file
                piece = self.board[square]

                if self.is_piece(square):
                    if empty_counter:
                        fen += str(empty_counter)
                        empty_counter = 0
                    fen += Piece.get_char_from_piece(piece)

                # empty square
                else:
                    empty_counter += 1

            # end of rank
            if empty_counter:
                fen += str(empty_counter)
                empty_counter = 0

            if rank != 0:
                fen += '/'
        fen += ' '

        # turn
        fen += 'w' if self.white_to_move else 'b'
        fen += ' '

        # castling rights
        castling = ''
        if self.castling_rights & 8: # 1000
            castling += 'K'
        if self.castling_rights & 4: # 0100
            castling += 'Q'
        if self.castling_rights & 2: # 0010
            castling += 'k'
        if self.castling_rights & 1: # 0001
            castling += 'q'

        fen += castling if castling else '-'
        fen += ' '

        # en passant target square
        if self.en_passant_target_square:
            file = chr(self.en_passant_target_square % 8 + ord('a'))
            rank = str(self.en_passant_target_square // 8 + 1)
            fen += file + rank
        else:
            fen += '-'
        fen += ' '

        # halfmove clock and fullmove number
        fen += str(self.halfmove_clock) + ' ' + str(self.fullmove_number)

        return fen
    
    def generate_moves(self, turn):
        '''Generates all possible moves for the given turn'''
        # key = self.hash_board(turn)
        # if key in self.generated_moves:
        #     return self.generated_moves[key]

        moves = []

        for square in (self.white_pieces if turn else self.black_pieces):
            piece = self.board[square]
            piece_type = Piece.get_type(piece)

            match piece_type:
                case Piece.pawn:
                    self.generate_pawn_moves(piece, square, moves)
                case Piece.knight:
                    self.generate_knight_moves(piece, square, moves)
                case Piece.bishop:
                    self.generate_bishop_moves(piece, square, moves)
                case Piece.rook:
                    self.generate_rook_moves(piece, square, moves)
                case Piece.queen:
                    self.generate_queen_moves(piece, square, moves)
                case Piece.king:
                    self.generate_king_moves(piece, square, moves)

        # self.generated_moves[key] = moves
        return moves
    
    def generate_sliding_moves(self, piece, square, moves, direction_indexes):
        '''Generates all possible sliding moves for the piece on the given square'''
        color = Piece.get_color(piece)

        for direction_index in direction_indexes:
            for distance in range(1, distance_to_edge[square][direction_index] + 1):
                target_square = square + directions[direction_index] * distance
                target_square_piece = self.board[target_square]

                if target_square_piece:
                    # capture if the target square has an enemy piece
                    if Piece.get_color(target_square_piece) != color:
                        moves.append((
                            square,                 # start
                            target_square,          # end
                            piece,                  # start_piece
                            target_square_piece,    # captured_piece
                            0,                      # promotion_piece
                            0,                      # castling
                            0                       # en_passant
                            ))
                    break

                moves.append((
                    square,         # start
                    target_square,  # end
                    piece,          # start_piece
                    0,              # captured_piece
                    0,              # promotion_piece
                    0,              # castling
                    0               # en_passant
                    ))


    def generate_pawn_moves(self, piece, square, moves):
        '''Generates all possible moves for the pawn on the given square'''
        color = Piece.get_color(piece)

        if color == Piece.white:
            direction = 8
            start_rank = 1
            promotion_rank = 7
        else:
            direction = -8
            start_rank = 6
            promotion_rank = 0
        
        piece_rank = square // 8

        # single move
        single_move = square + direction
        if self.is_empty(single_move):
            if (single_move//8) == promotion_rank:
                for promotion_piece in [Piece.knight, Piece.bishop, Piece.rook, Piece.queen]:
                    moves.append((
                        square,                 # start
                        single_move,            # end
                        piece,                  # start_piece
                        0,                      # captured_piece
                        promotion_piece | color,# promotion_piece
                        0,                      # castling
                        0                       # en_passant
                        ))
                
            else:
                moves.append((
                    square,         # start
                    single_move,    # end
                    piece,          # start_piece
                    0,              # captured_piece
                    0,              # promotion_piece
                    0,              # castling
                    0               # en_passant
                    ))

                # double move
                if piece_rank == start_rank and self.is_empty(single_move + direction):
                    moves.append((
                        square,                     # start
                        single_move + direction,    # end
                        piece,                      # start_piece
                        0,                          # captured_piece
                        0,                          # promotion_piece
                        0,                          # castling
                        0                           # en_passant
                        ))
                
        # captures
        for capture_direction in [direction - 1, direction + 1]:
            capture_square = square + capture_direction
            capture_rank = capture_square // 8

            # off the board
            if abs(capture_rank - piece_rank) != 1:
                continue

            # capture
            if self.is_piece(capture_square) and Piece.get_color(self.board[capture_square]) != color:

                # promotion capture
                if capture_rank == promotion_rank:
                    captured_piece = self.board[capture_square]
                    for promotion_piece in [Piece.knight, Piece.bishop, Piece.rook, Piece.queen]:
                        moves.append((
                            square,                     # start
                            capture_square,             # end
                            piece,                      # start_piece
                            captured_piece,             # captured_piece
                            color | promotion_piece,    # promotion_piece
                            0,                          # castling
                            0                           # en_passant
                            ))
                        
                # regular capture
                else:
                    moves.append((
                        square,                     # start
                        capture_square,             # end
                        piece,                      # start_piece
                        self.board[capture_square], # captured_piece
                        0,                          # promotion_piece
                        0,                          # castling
                        0                           # en_passant
                        ))
                    
            # en passant
            elif capture_square == self.en_passant_target_square:
                moves.append((
                    square,                     # start
                    capture_square,             # end
                    piece,                      # start_piece
                    (piece ^ 24),               # captured_piece
                    0,                          # promotion_piece
                    0,                          # castling
                    1                           # en_passant
                    ))
        
    def generate_knight_moves(self, piece, square, moves):
        '''Generates all possible moves for the knight on the given square'''
        color = Piece.get_color(piece)
        # distance_to_north,      # 0
        # distance_to_east,       # 1
        # distance_to_south,      # 2
        # distance_to_west,       # 3

        # distance_to_north_east, # 4
        # distance_to_north_west, # 5

        # distance_to_south_east, # 6
        # distance_to_south_west  # 7


        # -17,  # (-8 x 2) - 1    | 2 down, 1 left
        # -15,  # (-8 x 2) + 1    | 2 down, 1 right
        # -10,  # (-8 x 2) - 2    | 1 down, 2 left
        # -6,   # (-8 x 2) + 2    | 1 down, 2 right
        # 6,    # ( 8 x 2) - 2    | 1 up,   2 left
        # 10,   # ( 8 x 2) + 2    | 1 up,   2 right
        # 15,   # ( 8 x 2) - 1    | 2 up,   1 left
        # 17    # ( 8 x 2) + 1    | 2 up,   1 right
        distance_data = distance_to_edge[square]

        invalid_list = []

        if distance_data[0] == 0:       # remove all up moves
            invalid_list.append(6)
            invalid_list.append(10)
            invalid_list.append(15)
            invalid_list.append(17)
        elif distance_data[0] == 1:     # remove 2 up moves
            invalid_list.append(15)
            invalid_list.append(17)

        if distance_data[1] == 0:       # remove all right moves
            invalid_list.append(-15)
            invalid_list.append(-6)
            invalid_list.append(10)
            invalid_list.append(17)
        elif distance_data[1] == 1:     # remove 2 right moves
            invalid_list.append(-6)
            invalid_list.append(10)

        if distance_data[2] == 0:       # remove all down moves
            invalid_list.append(-17)
            invalid_list.append(-15)
            invalid_list.append(-10)
            invalid_list.append(-6)
        elif distance_data[2] == 1:     # remove 2 down moves
            invalid_list.append(-17)
            invalid_list.append(-15)

        if distance_data[3] == 0:       # remove all left moves
            invalid_list.append(-17)
            invalid_list.append(-10)
            invalid_list.append(6)
            invalid_list.append(15)
        elif distance_data[3] == 1:     # remove 2 left moves
            invalid_list.append(-10)
            invalid_list.append(6)

        for move in knight_directions:
            if move in invalid_list:
                continue

            target_square = square + move
            target_square_piece = self.board[target_square]

            if target_square_piece:
                if Piece.get_color(target_square_piece) != color:
                    moves.append((
                        square,                 # start
                        target_square,          # end
                        piece,                  # start_piece
                        target_square_piece,    # captured_piece
                        0,                      # promotion_piece
                        0,                      # castling
                        0                       # en_passant
                        ))
            else:
                moves.append((
                    square,         # start
                    target_square,  # end
                    piece,          # start_piece
                    0,              # captured_piece
                    0,              # promotion_piece
                    0,              # castling
                    0               # en_passant
                    ))

    def generate_bishop_moves(self, piece, square, moves):
        '''Generates all possible moves for the bishop on the given square'''
        self.generate_sliding_moves(piece, square, moves, [4, 5, 6, 7])

    def generate_rook_moves(self, piece, square, moves):
        '''Generates all possible moves for the rook on the given square'''
        self.generate_sliding_moves(piece, square, moves, [0, 1, 2, 3])

    def generate_queen_moves(self, piece, square, moves):
        '''Generates all possible moves for the queen on the given square'''
        self.generate_sliding_moves(piece, square, moves, [0, 1, 2, 3, 4, 5, 6, 7])

    def generate_king_moves(self, piece, square, moves):
        '''Generates all possible moves for the king on the given square'''
        color = Piece.get_color(piece)

        for direction_index in range(8):
            if distance_to_edge[square][direction_index] == 0:
                continue

            target_square = square + directions[direction_index]
            target_square_piece = self.board[target_square]


            # normal move
            if target_square_piece:
                if Piece.get_color(target_square_piece) != color:
                    moves.append((
                        square,                 # start
                        target_square,          # end
                        piece,                  # start_piece
                        target_square_piece,    # captured_piece
                        0,                      # promotion_piece
                        0,                      # castling
                        0                       # en_passant
                        ))
            else:
                moves.append((
                    square,         # start
                    target_square,  # end
                    piece,          # start_piece
                    0,              # captured_piece
                    0,              # promotion_piece
                    0,              # castling
                    0               # en_passant
                    ))
                
            # castling
            if color == Piece.white:
                if self.castling_rights & 8: # white kingside
                    if self.is_empty(5) and self.is_empty(6):
                        moves.append((
                            square,         # start
                            6,              # end
                            piece,          # start_piece
                            0,              # captured_piece
                            0,              # promotion_piece
                            1,              # castling
                            0               # en_passant
                            ))
                if self.castling_rights & 4: # white queenside
                    if self.is_empty(3) and self.is_empty(2) and self.is_empty(1):
                        moves.append((
                            square,         # start
                            2,              # end
                            piece,          # start_piece
                            0,              # captured_piece
                            0,              # promotion_piece
                            1,              # castling
                            0               # en_passant
                            ))
            else:
                if self.castling_rights & 2: # black kingside
                    if self.is_empty(61) and self.is_empty(62):
                        moves.append((
                            square,         # start
                            62,             # end
                            piece,          # start_piece
                            0,              # captured_piece
                            0,              # promotion_piece
                            1,              # castling
                            0               # en_passant
                            ))
                if self.castling_rights & 1: # black queenside
                    if self.is_empty(59) and self.is_empty(58) and self.is_empty(57):
                        moves.append((
                            square,         # start
                            58,             # end
                            piece,          # start_piece
                            0,              # captured_piece
                            0,              # promotion_piece
                            1,              # castling
                            0               # en_passant
                            ))
                        
    def make_move(self, move):
        '''Makes the given move on the board'''
        start_square, end_square, start_piece, captured_piece, promotion_piece, castling, en_passant = move

        # save board state to the undo list 
        # TODO: save the move and undo the move manually (for now with works)
        self.undo_list.append((
            self.board.copy(),
            self.white_king_square,
            self.black_king_square,
            self.white_pieces.copy(),
            self.black_pieces.copy(),
            self.white_attacked_squares.copy(),
            self.black_attacked_squares.copy(),
            self.castling_rights,
            self.en_passant_target_square,
            self.halfmove_clock
        ))

        # castling - move the rook (castling rights removed when the king moves)
        if castling:
            # white kingside
            if end_square == 6:
                self.move_piece(7, 5, Piece.white | Piece.rook)

            # white queenside
            elif end_square == 2:
                self.move_piece(0, 3, Piece.white | Piece.rook)

            # black kingside
            elif end_square == 62:
                self.move_piece(63, 61, Piece.black | Piece.rook)

            # black queenside
            elif end_square == 58:
                self.move_piece(56, 59, Piece.black | Piece.rook)

        # en passant - remove the captured pawn
        if en_passant:
            if self.white_to_move:
                self.clear_piece(end_square-8, captured_piece)
            else:
                self.clear_piece(end_square+8, captured_piece)

        # capture
        elif captured_piece: # TODO: promotion capture
            self.clear_piece(end_square, captured_piece)

        # promotion
        if promotion_piece:
            self.clear_piece(start_square, start_piece)
            self.set_piece(end_square, promotion_piece)

        # normal move
        else:
            self.move_piece(start_square, end_square, start_piece)


        # update castling rights
        if start_piece == Piece.white | Piece.king:
            self.castling_rights &= 0b0011
        elif start_piece == Piece.black | Piece.king:
            self.castling_rights &= 0b1100

        # rook move
        if start_piece == Piece.white | Piece.rook:
            if start_square == 0:
                self.castling_rights &= 0b1011
            elif start_square == 7:
                self.castling_rights &= 0b0111
        elif start_piece == Piece.black | Piece.rook:
            if start_square == 63:
                self.castling_rights &= 0b1101
            elif start_square == 56:
                self.castling_rights &= 0b1110

        # rook capture
        if captured_piece == Piece.white | Piece.rook:
            if end_square == 0:
                self.castling_rights &= 0b1011
            elif end_square == 7:
                self.castling_rights &= 0b0111
        elif captured_piece == Piece.black | Piece.rook:
            if end_square == 63:
                self.castling_rights &= 0b1101
            elif end_square == 56:
                self.castling_rights &= 0b1110

        # update en passant target square
        if en_passant:
            if self.white_to_move:
                self.en_passant_target_square = end_square - 8
            else:
                self.en_passant_target_square = end_square + 8
        else:
            self.en_passant_target_square = 0

        # update halfmove clock (reset if pawn move or capture)
        if Piece.get_type(start_piece) == Piece.pawn or captured_piece:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1

        # update fullmove number
        if not self.white_to_move:
            self.fullmove_number += 1

        # update turn
        self.white_to_move = not self.white_to_move

    def undo_move(self):
        '''Undoes the last move made on the board'''
        # TODO: implement undoing the move manually (for now this works)
        # restore board state
        board, white_king_square, black_king_square, white_pieces, black_pieces, white_attacked_squares, black_attacked_squares, castling_rights, en_passant_target_square, halfmove_clock = self.undo_list.pop()

        self.board = board

        self.white_king_square = white_king_square
        self.black_king_square = black_king_square

        self.white_pieces = white_pieces
        self.black_pieces = black_pieces

        self.white_attacked_squares = white_attacked_squares
        self.black_attacked_squares = black_attacked_squares

        self.castling_rights = castling_rights
        self.en_passant_target_square = en_passant_target_square
        self.halfmove_clock = halfmove_clock
        self.fullmove_number -= 1 if self.white_to_move else 0
        self.white_to_move = not self.white_to_move

    def update_attacks(self, square, piece, add=True):
        increment = 1 if add else -1
        piece_type = Piece.get_type(piece)
        color = Piece.get_color(piece)
        attack_map = self.white_attacked_squares if color == Piece.white else self.black_attacked_squares

        if piece_type in [Piece.rook, Piece.bishop, Piece.queen]:
            # Update for sliding pieces
            directions = Piece.directions_for_piece(piece_type)
            for direction in directions:
                next_square = square
                while True:
                    next_square += direction
                    if not (0 <= next_square < 64) or not self.is_on_same_line(next_square - direction, next_square):
                        break
                    attack_map[next_square] += increment
                    if self.board[next_square] != 0:  # Stop if there's another piece
                        break
        else:
            # Update for non-sliding pieces (knights, king, pawns)
            moves = Piece.moves_for_piece(piece_type, square)
            for move in moves:
                attack_map[move] += increment

    @staticmethod
    def is_on_same_line(sq1, sq2):
        return sq1 // 8 == sq2 // 8 or sq1 % 8 == sq2 % 8 or (sq1 // 8 - sq2 // 8 == sq1 % 8 - sq2 % 8)




    def is_check(self, turn):
        king_square = self.white_king_square if turn == Piece.white else self.black_king_square
        attack_map = self.black_attacked_squares if turn == Piece.white else self.white_attacked_squares
        return attack_map[king_square] > 0
    
    def generate_legal_moves(self, turn):
        '''Generates all legal moves for the given turn'''
        potential_moves = self.generate_moves(turn)
        legal_moves = []

        for move in potential_moves:
            self.make_move(move)
            if not self.is_check(turn):  # Check if the current player is not in check
                legal_moves.append(move)
            self.undo_move()
        return legal_moves
    
    def is_checkmate(self, turn):
        '''Returns True if the given turn is in checkmate, False otherwise'''
        return self.is_check(turn) and not self.generate_legal_moves(turn)
    
    def is_stalemate(self, turn):
        '''Returns True if the given turn is in stalemate, False otherwise'''
        return not self.is_check(turn) and not self.generate_legal_moves(turn)
    
    def is_threefold_repetition(self):
        '''Returns True if the current board state has occurred three times, False otherwise'''
        # count the number of occurrences of the current board state in the undo list
        # TODO: optimize?
        # count = 0
        # for board, _, _, _ in self.undo_list:
        #     if board == self.board:
        #         count += 1
        #         if count == 3:
        #             return True
        return False
    
    def is_fifty_move_rule(self):
        '''Returns True if the halfmove clock is greater than or equal to 100, False otherwise'''
        return self.halfmove_clock >= 100
    
    def is_insufficient_material(self):
        '''Returns True if there is insufficient material for checkmate, False otherwise'''
        return False # TODO: implement

    def is_draw(self):
        '''Returns True if the game is a draw, False otherwise'''
        return self.is_threefold_repetition() or self.is_fifty_move_rule() or self.is_insufficient_material()
    
    def is_game_over(self):
        '''Returns True if the game is over, False otherwise'''
        return self.is_checkmate(True) or self.is_checkmate(False) or self.is_stalemate(True) or self.is_stalemate(False) or self.is_draw()
    

if __name__ == "__main__":
    b = Board()
    print(STARTING_FEN)
    print(b.create_fen())

    print(b.generate_legal_moves(True))

    print(b.create_fen())