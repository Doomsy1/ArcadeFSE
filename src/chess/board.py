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

PROMOTION_PIECES = 0b010, 0b011, 0b100, 0b101

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
    def __init__(self, start, end, start_piece, captured_piece=0b0000, promotion_piece=0b0000, castling=0b0000, previous_castling_rights=0b0000, capture=False, en_passant=False, previous_en_passant_target_square=127, halfmove_clock=0):
        self.start = start
        self.end = end
        self.start_piece = start_piece
        self.captured_piece = captured_piece
        self.promotion_piece = promotion_piece
        self.castling = castling
        self.previous_castling_rights = previous_castling_rights
        self.capture = capture
        self.en_passant = en_passant
        self.previous_en_passant_target_square = previous_en_passant_target_square
        self.halfmove_clock = halfmove_clock

class Board:
    def __init__(self, fen = STARTING_FEN):

        # bitboards for each piece type (0x88 representation)
        self.piece_bitboards = {
            0b0000: 0,

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

        self.empty_squares_bitboard = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF # all squares are empty (all bits are set to 1)

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


    # getters
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
    
    def get_piece(self, square):
        for piece in self.piece_bitboards:
            if self.piece_bitboards[piece] & (1 << square):
                return piece

    # setters
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
        self.empty_squares_bitboard |= 1 << square

    def move_piece(self, piece, start, end):
        colour = piece >> 3
        self.piece_bitboards[piece] &= ~(1 << start)
        self.piece_bitboards[piece] |= 1 << end

        self.zobrist_hash ^= self.zobrist_table[piece][start]
        self.zobrist_hash ^= self.zobrist_table[piece][end]

        self.colour_bitboards[colour] &= ~(1 << start)
        self.colour_bitboards[colour] |= 1 << end

        self.empty_squares_bitboard |= 1 << start
        self.empty_squares_bitboard &= ~(1 << end)


    def load_fen(self, fen):
        # example fen: 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

        # reset boards
        for piece in self.piece_bitboards:
            self.piece_bitboards[piece] = 0
        self.colour_bitboards[0b0] = 0
        self.colour_bitboards[0b1] = 0
        self.empty_squares_bitboard = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF

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

        # # update zobrist hash
        # self.zobrist_hash = self.compute_initial_zobrist_hash()
        # self.cached_boards = {}

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
                    for piece in self.piece_bitboards: 
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
        move_obj = Move(
            start = start,
            end = end,
            start_piece = start_piece,
            captured_piece = captured_piece,
            promotion_piece = promotion_piece,
            castling = castling,
            previous_castling_rights = self.castling_rights,
            capture = capture,
            en_passant = en_passant,
            previous_en_passant_target_square = self.en_passant_target_square,
            halfmove_clock = self.halfmove_clock
        )


        if castling: # move rook
            if castling & 0b1000: # white queenside
                self.move_piece(0b1100, 0, 3)
            elif castling & 0b0100: # white kingside
                self.move_piece(0b1100, 7, 5)
            elif castling & 0b0010: # black queenside
                self.move_piece(0b0100, 112, 115)
            elif castling & 0b0001: # black kingside
                self.move_piece(0b0100, 119, 117)

        # check for rook moves (to disable castling)
        if start_piece & 0b0111 == 0b100:
            if start == 0:
                self.castling_rights &= 0b0111
            elif start == 7:
                self.castling_rights &= 0b1011
            elif start == 112:
                self.castling_rights &= 0b1101
            elif start == 119:
                self.castling_rights &= 0b1110

        # check for rook captures (to disable castling)
        if captured_piece & 0b0111 == 0b100:
            if end == 0:
                self.castling_rights &= 0b0111
            elif end == 7:
                self.castling_rights &= 0b1011
            elif end == 112:
                self.castling_rights &= 0b1101
            elif end == 119:
                self.castling_rights &= 0b1110

        # check for king moves (to disable castling)
        # this also accounts for castling moves
        if start_piece & 0b1110:
            self.castling_rights &= 0b0011
        elif start_piece & 0b0110:
            self.castling_rights &= 0b1100

        # check for pawn moves (to reset halfmove clock)
        if start_piece & 0b111 == 0b001:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1

        # check for captures (to reset halfmove clock)
        if capture:
            self.halfmove_clock = 0

        # check for pawn moves (to set en passant target square)
        if start_piece & 0b111 == 0b001 and abs(start - end) == 32:
            self.en_passant_target_square = (start + end) // 2
        else:
            self.en_passant_target_square = 127

        # check for pawn promotions
        if promotion_piece:
            self.clear_square(start)
            self.clear_square(end)
            self.set_piece(promotion_piece, end)

        # check for en passant captures
        elif en_passant:
            if self.white_to_move:
                self.clear_square(end - 16)
            else:
                self.clear_square(end + 16)

            self.move_piece(start_piece, start, end)

        # check for regular captures
        elif capture:
            self.clear_square(end)
            self.move_piece(start_piece, start, end)

        # move the piece
        else:
            self.move_piece(start_piece, start, end)

        # update turn
        self.white_to_move = not self.white_to_move

        # update fullmove number
        self.fullmove_number += 1 if start_piece >> 3 else 0

        # zobrist hash is updated in the move_piece and clear_square methods so no need to update it here

        # add move to move stack
        self.move_stack.append(move_obj)


    def undo_move(self):
        move = self.move_stack.pop()
        start = move.start
        end = move.end
        start_piece = move.start_piece
        captured_piece = move.captured_piece
        promotion_piece = move.promotion_piece
        castling = move.castling
        castling_rights = move.previous_castling_rights
        capture = move.capture
        en_passant = move.en_passant
        previous_en_passant_target_square = move.previous_en_passant_target_square
        halfmove_clock = move.halfmove_clock


        # undo castling (move rook back) and update castling rights
        if castling:
            if castling & 0b1000: # white queenside
                self.move_piece(0b1100, 3, 0)
            elif castling & 0b0100: # white kingside
                self.move_piece(0b1100, 5, 7)
            elif castling & 0b0010: # black queenside
                self.move_piece(0b0100, 115, 112)
            elif castling & 0b0001: # black kingside
                self.move_piece(0b0100, 117, 119)

        # undo pawn promotions
        if promotion_piece:
            self.clear_square(end)
            self.set_piece(start_piece, start)

        # undo en passant captures
        elif en_passant:
            if start_piece & 0b1000:
                self.set_piece(0b0001, end - 16)
            else:
                self.set_piece(0b1001, end + 16)

            self.move_piece(start_piece, end, start)

        # undo regular captures
        elif capture:
            self.move_piece(start_piece, end, start)
            self.set_piece(captured_piece, end)

        # undo regular moves
        else:
            self.move_piece(start_piece, end, start)

        # update turn
        self.white_to_move = not self.white_to_move

        # update castling rights
        self.castling_rights = castling_rights

        # update en passant target square
        self.en_passant_target_square = previous_en_passant_target_square

        # update halfmove clock
        self.halfmove_clock = halfmove_clock

        # update fullmove number
        self.fullmove_number -= 1 if start_piece & 0b1000 else 0

        # update zobrist hash is updated in the move_piece and clear_square methods so no need to update it here

    def is_valid_square(self, square):
        # check if square is out of bounds
        return square & OUT_OF_BOUNDS_MASK == 0
    
    def generate_sliding_moves(self, start_piece_type, start_square, directions, max_moves=7):
        moves = []

        start_color = start_piece_type >> 3
        for direction in directions:
            for distance in range(1, max_moves + 1):
                end = start_square + direction * distance

                # check if square is out of bounds
                if not self.is_valid_square(end):
                    break

                if self.is_piece(end):
                    if self.is_white(end) != start_color:
                        moves.append(encode_move(
                            start = start_square,
                            end = end,
                            start_piece = start_piece_type,
                            captured_piece = self.get_piece(end),
                            capture = True
                        ))
                    break
                else:
                    moves.append(encode_move(
                        start = start_square,
                        end = end,
                        start_piece = start_piece_type,
                    ))

        return moves
    
    def generate_knight_moves(self, start_piece_type, start_square):
        moves = []

        start_color = start_piece_type >> 3
        for direction in KNIGHT_DIRECTIONS:
            end = start_square + direction

            if self.is_valid_square(end):
                if self.is_piece(end):
                    if self.is_white(end) != start_color:
                        moves.append(encode_move(
                            start = start_square,
                            end = end,
                            start_piece = start_piece_type,
                            captured_piece = self.get_piece(end),
                            capture = True
                        ))
                else:
                    moves.append(encode_move(
                        start = start_square,
                        end = end,
                        start_piece = start_piece_type,
                    ))

        return moves
    
    def generate_pawn_moves(self, start_piece_type, start_square):
        moves = []

        start_color = start_piece_type >> 3
        direction = 16 if start_color else -16
        end = start_square + direction

        # single push
        if self.is_empty(end):
            moves.append(encode_move(
                start = start_square,
                end = end,
                start_piece = start_piece_type
            ))

            # white double push
            if start_color and start_square // 16 == 1:
                end += direction
                if self.is_empty(end):
                    moves.append(encode_move(
                        start = start_square,
                        end = end,
                        start_piece = start_piece_type
                    ))

            # black double push
            elif not start_color and start_square // 16 == 6:
                end += direction
                if self.is_empty(end):
                    moves.append(encode_move(
                        start = start_square,
                        end = end,
                        start_piece = start_piece_type
                    ))

        # captures
        directions = [15, 17] if start_color else [-15, -17]
        
        for direction in directions:
            end = start_square + direction
            if self.is_valid_square(end) and self.is_piece(end) and self.is_white(end) != start_color:
                
                # white promotion captures
                if start_color and end // 16 == 7:
                    for promotion_piece_type in PROMOTION_PIECES:
                        promotion_piece = promotion_piece_type | 0b1000
                        moves.append(encode_move(
                            start = start_square,
                            end = end,
                            start_piece = start_piece_type,
                            captured_piece = self.get_piece(end),
                            promotion_piece = promotion_piece,
                            capture = True
                        ))

                # black promotion captures
                elif not start_color and end // 16 == 0:
                    for promotion_piece_type in PROMOTION_PIECES:
                        moves.append(encode_move(
                            start = start_square,
                            end = end,
                            start_piece = start_piece_type,
                            captured_piece = self.get_piece(end),
                            promotion_piece = promotion_piece_type, # black promotion pieces are already in the correct format
                            capture = True
                        ))

                # regular captures
                else:
                    moves.append(encode_move(
                        start = start_square,
                        end = end,
                        start_piece = start_piece_type,
                        captured_piece = self.get_piece(end),
                        capture = True
                    ))

            # en passant captures
            elif end == self.en_passant_target_square:
                moves.append(encode_move(
                    start = start_square,
                    end = end,
                    start_piece = start_piece_type,
                    captured_piece = self.get_piece(end - direction),
                    en_passant = True,
                    capture = True
                ))

        return moves
    
    def generate_king_moves(self, start_piece_type, start_square):
        moves = []

        start_color = start_piece_type >> 3
        moves += self.generate_sliding_moves(start_piece_type, start_square, KING_DIRECTIONS, max_moves=1)

        # castling
        if start_color:
            if self.castling_rights & 0b1000: # white queenside
                if not self.is_piece(1) and not self.is_piece(2) and not self.is_piece(3):
                    moves.append(encode_move(
                        start = start_square,
                        end = 2,
                        start_piece = start_piece_type,
                        castling = 0b1000
                    ))

            if self.castling_rights & 0b0100: # white kingside
                if not self.is_piece(5) and not self.is_piece(6):
                    moves.append(encode_move(
                        start = start_square,
                        end = 6,
                        start_piece = start_piece_type,
                        castling = 0b0100
                    ))

        else:
            if self.castling_rights & 0b0010: # black queenside
                if not self.is_piece(113) and not self.is_piece(114) and not self.is_piece(115):
                    moves.append(encode_move(
                        start = start_square,
                        end = 114,
                        start_piece = start_piece_type,
                        castling = 0b0010
                    ))

            if self.castling_rights & 0b0001: # black kingside
                if not self.is_piece(117) and not self.is_piece(118):
                    moves.append(encode_move(
                        start = start_square,
                        end = 118,
                        start_piece = start_piece_type,
                        castling = 0b0001
                    ))

        return moves
    
    def generate_moves(self, turn): # add caching to this with zobrist hash
        '''
        Generate all moves for the player.
        Turn is the color of the player that is making the move.'''
        moves = []

        for square in LEGAL_SQUARES:
            if self.is_empty(square):
                continue

            if self.is_white(square) != turn:
                continue

            piece = self.get_piece(square)
            piece_type = piece & 0b111

            if piece_type == 0b0001: # pawn
                moves += self.generate_pawn_moves(piece, square)

            elif piece_type == 0b0010: # knight
                moves += self.generate_knight_moves(piece, square)

            elif piece_type == 0b0011: # bishop
                moves += self.generate_sliding_moves(piece, square, BISHOP_DIRECTIONS)

            elif piece_type == 0b0100: # rook
                moves += self.generate_sliding_moves(piece, square, ROOK_DIRECTIONS)

            elif piece_type == 0b0101: # queen
                moves += self.generate_sliding_moves(piece, square, QUEEN_DIRECTIONS)

            elif piece_type == 0b0110: # king
                moves += self.generate_king_moves(piece, square)

        return moves
    
    def is_check(self, turn): # add caching to this with zobrist hash
        '''
        Check if the player is in check.
        Turn is the color of the king that is being checked.
        '''

        # find the king
        king_square = self.piece_bitboards[0b1110 if turn else 0b0110].bit_length() - 1

        # check if the king is being attacked by any of the opponent's pieces
        enemy_moves = self.generate_moves(not turn)
        for move in enemy_moves:
            _, end, _, _, _, _, _, _ = decode_move(move)
            if end == king_square:
                return True
            
        return False
    
    def is_checkmate(self, turn): # add caching to this with zobrist hash
        '''
        Check if the player is in checkmate.
        Turn is the color of the king that is being checkmated.
        '''
        if not self.is_check(turn):
            return False
        
        moves = self.generate_moves(turn)
        for move in moves:
            self.make_move(move)
            if not self.is_check(turn):
                self.undo_move()
                return False
            self.undo_move()

        return True
    
    def is_stalemate(self, turn): # add caching to this with zobrist hash
        '''
        Check if the player is in stalemate.
        Turn is the color of the player that is being stalemated.
        '''
        if self.is_check(turn):
            return False
        
        moves = self.generate_moves(turn)
        for move in moves:
            self.make_move(move)
            if not self.is_check(turn):
                self.undo_move()
                return False
            self.undo_move()

        return True
    
    def is_draw(self): # add caching to this with zobrist hash
        '''
        Check if the game is a draw.
        '''
        if self.halfmove_clock >= 100:
            return True
        
        if self.is_stalemate(True) or self.is_stalemate(False):
            return True
        
        return False
    
    def is_game_over(self): # add caching to this with zobrist hash
        '''
        Check if the game is over.
        '''
        return self.is_checkmate(True) or self.is_checkmate(False) or self.is_draw()
    
    def generate_legal_moves(self, turn):
        '''
        Generate all legal moves for the player.
        Turn is the color of the player that is making the move.'''
        moves = self.generate_moves(turn)
        legal_moves = []

        # check if ally king is in check after move
        for move in moves:
            self.make_move(move)
            if not self.is_check(turn):
                legal_moves.append(move)
            self.undo_move()

        return legal_moves

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
    b.load_fen('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
    b.generate_fen()