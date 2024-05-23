# this board structure is inspired by Sebastian Lague's video entitled "Coding Adventure: Chess"
# Link: https://www.youtube.com/watch?v=U4ogK0MIzqk


STARTING_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

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

    piece_to_char_map = {
        'p': black | pawn,
        'n': black | knight,
        'b': black | bishop,
        'r': black | rook,
        'q': black | queen,
        'k': black | king,
        'P': white | pawn,
        'N': white | knight,
        'B': white | bishop,
        'R': white | rook,
        'Q': white | queen,
        'K': white | king,
    }

    char_to_piece_map = {
        black | pawn: 'p',
        black | knight: 'n',
        black | bishop: 'b',
        black | rook: 'r',
        black | queen: 'q',
        black | king: 'k',
        white | pawn: 'P',
        white | knight: 'N',
        white | bishop: 'B',
        white | rook: 'R',
        white | queen: 'Q',
        white | king: 'K',
    }

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
        return Piece.piece_to_char_map[char]
    
    @staticmethod
    def get_char_from_piece(piece):
        return Piece.char_to_piece_map[piece]

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
        distance_to_north,
        distance_to_east,
        distance_to_south,
        distance_to_west,

        distance_to_north_east,
        distance_to_north_west,

        distance_to_south_east,
        distance_to_south_west
    ))

# moves will be represented as a tuple
# (start, end, start_piece, captured_piece, promotion_piece, castling, en_passant)

class Board:
    def __init__(self, fen=STARTING_FEN):
        self.board = [0] * 64 # 64 squares

        self.white_king_square = 0 # square of white king
        self.black_king_square = 0 # square of black king

        self.white_pieces = [] # list of white piece squares
        self.black_pieces = [] # list of black piece squares

        self.white_to_move = True
        self.castling_rights = 0 # 4 bits for each side (KQkq)
        self.en_passant_target_square = 0 # square where en passant is possible (0 if not possible)
        self.halfmove_clock = 0 # number of halfmoves since last capture or pawn move
        self.fullmove_number = 0 # starts at 1 and is incremented after b's move

        # self.load_fen(fen)

    def is_piece(self, square):
        '''Returns True if there is a piece on the square, False otherwise.'''
        return self.board[square] != 0 # bool?
    
    def is_empty(self, square):
        '''Returns True if the square is empty, False otherwise.'''
        return self.board[square] == 0
    
    def get_piece(self, square):
        '''Returns the piece on the square.'''
        return self.board[square]
    
    def set_piece(self, square, piece):
        '''Sets the piece on the square.'''
        self.board[square] = piece

        if piece == Piece.white:
            self.white_pieces.append(square)
            if piece == Piece.king:
                self.white_king_square = square

        else:
            self.black_pieces.append(square)
            if piece == Piece.king:
                self.black_king_square = square

    def clear_piece(self, square, piece):
        '''Clears the piece on the square.'''
        self.board[square] = 0

        if piece == Piece.white:
            self.white_pieces.remove(square)
            if piece == Piece.king:
                self.white_king_square = 0

        else:
            self.black_pieces.remove(square)
            if piece == Piece.king:
                self.black_king_square = 0

    def move_piece(self, start_square, end_square, piece):
        '''Moves the piece from start_square to end_square.'''
        self.clear_piece(start_square, piece)
        self.set_piece(end_square, piece)

    def load_fen(self, fen):
        '''Sets the state of the board to the given FEN string.'''

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
        '''Returns the FEN string representing the state of the board.'''

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
        '''Generates all possible moves for the given turn.'''
        moves = []

        for square in (self.white_pieces if turn else self.black_pieces):
            piece = self.board[square]

            match piece:
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

        return moves
    
    def generate_sliding_moves(self, piece, square, moves, direction_indexes):
        '''Generates all possible sliding moves for the piece on the given square.'''
        color = Piece.get_color(piece)

        for direction_index in direction_indexes:
            for distance in range(1, distance_to_edge[square][direction_index]):
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

    def generate_single_moves(self, piece, square, moves, direction_indexes):
        '''Generates all possible single moves for the piece on the given square.'''
        color = Piece.get_color(piece)

        for direction_index in direction_indexes:
            if distance_to_edge[square][direction_index] == 0:
                continue

            target_square = square + directions[direction_index]
            target_square_piece = self.board[target_square]
            # TODO: Continue from here

    def generate_pawn_moves(self, piece, square, moves):
        '''Generates all possible moves for the pawn on the given square.'''
        color = Piece.get_color(piece)

        if color == Piece.white:
            direction = 8
            start_rank = 1
            promotion_rank = 7
            en_passant_rank = 4
        else:
            direction = -8
            start_rank = 6
            promotion_rank = 0
            en_passant_rank = 3
        
        piece_rank = square // 8

        # single move
        single_move = square + direction
        if self.is_empty(single_move):
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
                    single_move                 # en_passant
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
                            promotion_piece | color,    # promotion_piece
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
                    (piece ^ 24) | Piece.pawn,  # captured_piece
                    0,                          # promotion_piece
                    0,                          # castling
                    1                           # en_passant
                    ))
                
    