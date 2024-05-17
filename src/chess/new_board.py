from random import getrandbits

STARTING_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

# using the properties of the board, we can determine if a square is out of bounds
OUT_OF_BOUNDS_MASK = 0x88

KNIGHT_DIRECTIONS = [
    -33, # (-16 x 2) - 1    | 2 down, 1 left
    -31, # (-16 x 2) + 1    | 2 down, 1 right
    -18, # (-16 + 2) x 2    | 1 down, 2 left
    -14, # (-16 + 2) x 2    | 1 down, 2 right
    14,  # (16 - 2) x 2     | 1 up, 2 left
    18,  # (16 + 2) x 2     | 1 up, 2 right
    31,  # (16 x 2) + 1     | 2 up, 1 left
    33   # (16 x 2) - 1     | 2 up, 1 right
]

BISHOP_DIRECTIONS = [
    -17, # (-16 - 1)        | 1 down, 1 left
    -15, # (-16 + 1)        | 1 down, 1 right
    15,  # (16 - 1)         | 1 up, 1 left
    17   # (16 + 1)         | 1 up, 1 right
]

ROOK_DIRECTIONS = [
    -16, # 16 down
    -1,  # 1 left
    1,   # 1 right
    16   # 16 up
]

QUEEN_DIRECTIONS = BISHOP_DIRECTIONS + ROOK_DIRECTIONS

KING_DIRECTIONS = QUEEN_DIRECTIONS

# illegal squares are those that are out of bounds
LEGAL_SQUARES = [i for i in range(128) if not i & OUT_OF_BOUNDS_MASK]

# Pieces represented as 4 digit binary numbers (first bit for colour, rest for type)
            #  pawn   knight   bishop  rook    queen   king
WHITE_PIECES = 0b1001, 0b1010, 0b1011, 0b1100, 0b1101, 0b1110
BLACK_PIECES = 0b0001, 0b0010, 0b0011, 0b0100, 0b0101, 0b0110

piece_char_to_bin = {
    'P': 0b1001,
    'N': 0b1010,
    'B': 0b1011,
    'R': 0b1100,
    'Q': 0b1101,
    'K': 0b1110,

    'p': 0b0001,
    'n': 0b0010,
    'b': 0b0011,
    'r': 0b0100,
    'q': 0b0101,
    'k': 0b0110
}

piece_bin_to_char = {
    0b1001: 'P',
    0b1010: 'N',
    0b1011: 'B',
    0b1100: 'R',
    0b1101: 'Q',
    0b1110: 'K',

    0b0001: 'p',
    0b0010: 'n',
    0b0011: 'b',
    0b0100: 'r',
    0b0101: 'q',
    0b0110: 'k'
}

class Move:
    def __init__(self, start, end, start_piece, captured_piece=0b0000, promotion_piece=0b0000, castling=0b0000, capture=False, en_passant=False):
        self.start = start
        self.end = end
        self.start_piece = start_piece
        self.captured_piece = captured_piece
        self.promotion_piece = promotion_piece
        self.castling = castling
        self.capture = capture
        self.en_passant = en_passant

class Board:
    def __init__(self, fen = STARTING_FEN):

        # bitboards for each piece type (0x88 representation)
        self.piece_bitboards = {
            # white
            0b1001: 0, # pawn
            0b1010: 0, # knight
            0b1011: 0, # bishop
            0b1100: 0, # rook
            0b1101: 0, # queen
            0b1110: 0, # king

            # black
            0b0001: 0, # pawn
            0b0010: 0, # knight
            0b0011: 0, # bishop
            0b0100: 0, # rook
            0b0101: 0, # queen
            0b0110: 0  # king
        }


        self.colour_bitboards = {
            0b1: 0, # white
            0b0: 0  # black
        }

        self.empty_squares_bitboard = 0

        self.castling_rights = 0 # 0b0000
        self.en_passant_target_square = 127 # 127 is an invalid square
        self.halfmove_clock = 0
        self.fullmove_number = 0
        self.white_to_move = True # True = white, False = black

        self.zobrist_table = self.initialize_zobrist_table()
        self.zobrist_hash = self.compute_initial_zobrist_hash()
        self.cached_boards = {}

        self.load_fen(fen)
        self.move_stack = []

    def initialize_zobrist_table(self):
        table = {}
        for piece in self.piece_bitboards:
            for square in LEGAL_SQUARES:
                table[piece] = [getrandbits(64) for _ in range(128)] 
        return table
    
    def compute_initial_zobrist_hash(self):
        hash_value = 0
        for piece, bitboard in self.piece_bitboards.items():
            for square in range(128):
                if bitboard & (1 << square):
                    hash_value ^= self.zobrist_table[piece][square]
            
        return hash_value


    # getters/setters
    def is_piece(self, square):
        return self.empty_squares_bitboard & (1 << square) == 0
    
    def is_empty(self, square):
        return self.empty_squares_bitboard & (1 << square) != 0
    
    def is_white(self, square):
        return self.colour_bitboards[0b1] & (1 << square) != 0
    
    def is_black(self, square):
        return self.colour_bitboards[0b0] & (1 << square) != 0
    
    def is_pawn(self, square):
        return self.piece_bitboards[0b1001] & (1 << square) != 0
    
    def is_knight(self, square):
        return self.piece_bitboards[0b1010] & (1 << square) != 0
    
    def is_bishop(self, square):
        return self.piece_bitboards[0b1011] & (1 << square) != 0
    
    def is_rook(self, square):
        return self.piece_bitboards[0b1100] & (1 << square) != 0
    
    def is_queen(self, square):
        return self.piece_bitboards[0b1101] & (1 << square) != 0
    
    def is_king(self, square):
        return self.piece_bitboards[0b1110] & (1 << square) != 0
    
    def set_piece(self, piece, square):
        self.piece_bitboards[piece] |= 1 << square
        self.empty_squares_bitboard &= ~(1 << square)
        self.colour_bitboards[piece >> 3] |= 1 << square

        self.zobrist_hash ^= self.zobrist_table[piece][square]

    def clear_square(self, square):
        for piece in self.piece_bitboards:
            if self.piece_bitboards[piece] & (1 << square):
                self.piece_bitboards[piece] &= ~(1 << square)

                self.zobrist_hash ^= self.zobrist_table[piece][square]
                
        self.colour_bitboards[0b0] &= ~(1 << square)
        self.colour_bitboards[0b1] &= ~(1 << square)
        self.empty_squares_bitboard &= ~(1 << square)

    def move_piece(self, piece, start, end):
        colour = piece >> 3
        self.piece_bitboards[piece] &= ~(1 << start)
        self.piece_bitboards[piece] |= 1 << end

        self.zobrist_hash ^= self.zobrist_table[piece][start]
        self.zobrist_hash ^= self.zobrist_table[piece][end]

        self.colour_bitboards[colour] &= ~(1 << start)
        self.colour_bitboards[colour] |= 1 << end

        self.empty_squares_bitboard &= ~(1 << start)
        self.empty_squares_bitboard |= 1 << end


    def load_fen(self, fen):
        # example fen: 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

        # reset boards
        for piece in self.piece_bitboards:
            self.piece_bitboards[piece] = 0
        self.colour_bitboards[0b0] = 0
        self.colour_bitboards[0b1] = 0
        self.empty_squares_bitboard = 0

        piece_placements, turn, castling_availibility, en_passant_target_square, halfmove_clock, fullmove_number = fen.split(' ')

        # set up the board (0x88 representation)
        rank = 7
        file = 0
        for char in piece_placements:
            # new rank
            if char == '/':
                file = 0 # back to 'a' file
                rank -= 1
            
            # empty squares
            elif char.isdigit():
                file += int(char)

            # piece
            else:
                square = rank * 16 + file
                piece = piece_char_to_bin[char]
                self.set_piece(piece, square)
                file += 1

        # set turn
        self.white_to_move = turn == 'w'

        # set castling rights
        self.castling_rights = 0b0000
        for char in castling_availibility:
            if char == 'K':
                self.castling_rights |= 0b1000
            elif char == 'Q':
                self.castling_rights |= 0b0100
            elif char == 'k':
                self.castling_rights |= 0b0010
            elif char == 'q':
                self.castling_rights |= 0b0001

        # set en passant target square
        self.en_passant_target_square = 127 # 127 is an invalid square
        if en_passant_target_square != '-':
            rank, file = en_passant_target_square
            self.en_passant_target_square = (ord(rank) - ord('a')) + (int(file) - 1) * 16

        # set halfmove clock and fullmove number
        self.halfmove_clock = int(halfmove_clock)
        self.fullmove_number = int(fullmove_number)

        # update zobrist hash
        self.zobrist_hash = self.compute_initial_zobrist_hash()
        self.cached_boards = {}

    def generate_fen(self):
        
        # piece placements
        fen = ''
        empty = 0
        for rank in range(7, -1, -1): # top to bottom
            for file in range(8): # left to right
                square = rank * 16 + file

                # empy square are represented by a number
                if self.is_empty(square):
                    empty += 1

                # piece
                else:
                    # add empty squares
                    if empty > 0:
                        fen += str(empty)
                        empty = 0
                    
                    # add piece
                    for piece in self.piece_bitboards: # iterate through all pieces to find which piece is on the square
                        if self.piece_bitboards[piece] & (1 << square):
                            fen += piece_bin_to_char[piece]
                            break
            
            # add empty squares at the end of the rank
            if empty > 0:
                fen += str(empty)
                empty = 0
            if rank > 0:
                fen += '/'
        fen += ' '

        # turn
        fen += 'w' if self.white_to_move else 'b'
        fen += ' '

        # castling rights
        castling_rights = ''
        if self.castling_rights & 0b1000:
            castling_rights += 'K'
        if self.castling_rights & 0b0100:
            castling_rights += 'Q'
        if self.castling_rights & 0b0010:
            castling_rights += 'k'
        if self.castling_rights & 0b0001:
            castling_rights += 'q'

        fen += castling_rights if castling_rights else '-'
        fen += ' '

        # en passant target square
        en_passant_target_square = '-'
        if self.en_passant_target_square != 127:
            file = chr(self.en_passant_target_square % 16 + ord('a'))
            rank = str(self.en_passant_target_square // 16 + 1)
            en_passant_target_square = file + rank

        fen += en_passant_target_square

        # halfmove clock and fullmove number
        fen += f' {self.halfmove_clock} {self.fullmove_number}'

        return fen
    
    def make_move(self, move):
        start, end, start_piece, captured_piece, promotion_piece, castling, capture, en_passant = decode_move(move)


def encode_move(start, end, start_piece, captured_piece=0b0000, promotion_piece=0b0000, castling=0b0000, capture=False, en_passant=False):
    '''
    Encode a move into a 32-bit integer.
    
    Args:
        start: (int), start square (0x88 index)
        end: (int), end square (0x88 index)
        start_piece: (int), piece on the start square
        captured_piece: (int), piece on the end square
        promotion_piece: (int), piece to promote to
        castling: (int), castling rights
        capture: (bool), whether the move is a capture
        en_passant: (bool), whether the move is an en passant move
        
    Returns:
        int, encoded move'''
    # 16 bits
    # 0-6: start square         (7 bits)
    # 7-13: end square          (7 bits)
    # 14-17: start piece        (4 bits)
    # 18-21: captured piece     (4 bits)
    # 22-25: promotion piece    (4 bits)
    # 28-31: castling           (4 bits)
    # 26: capture               (1 bit)
    # 27: en passant            (1 bit)
    
    move = 0

    move |= start
    move |= end << 7
    move |= start_piece << 14
    move |= captured_piece << 18
    move |= promotion_piece << 22
    move |= castling << 28
    move |= capture << 26
    move |= en_passant << 27

    return move

def decode_move(move):
    '''
    Decode a move from a 32-bit integer.
    
    Args:
        move: (int), encoded move
        
    Returns:
        tuple, (start, end, start_piece, captured_piece, promotion_piece, castling, capture, en_passant)'''
    
    start = move & 0x7F
    end = (move >> 7) & 0x7F
    start_piece = (move >> 14) & 0xF
    captured_piece = (move >> 18) & 0xF
    promotion_piece = (move >> 22) & 0xF
    castling = (move >> 28) & 0xF
    capture = (move >> 26) & 0x1
    en_passant = (move >> 27) & 0x1

    return start, end, start_piece, captured_piece, promotion_piece, castling, capture, en_passant

if __name__ == "__main__":
    b = Board()
    print(b.generate_fen())
    print(b.zobrist_hash)
    b.move_piece(0b1001, 16, 32)
    print(b.generate_fen())
    print(b.zobrist_hash)
    b.move_piece(0b1001, 32, 16)
    print(b.generate_fen())
    print(b.zobrist_hash)