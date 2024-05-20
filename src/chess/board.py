from random import getrandbits
import mmh3 # this needs to be installed with pip | pip install mmh3


STARTING_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'


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

# using the properties of the board, we can determine if a square is out of bounds
OUT_OF_BOUNDS_MASK = 0x88

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

piece_bin_to_char = {v: k for k, v in piece_char_to_bin.items()}


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

class Board:
    def __init__(self, fen=STARTING_FEN):
        
        # 0x88 board representation
        self.piece_bitboards = {
            0b1001: 0, # white pawns
            0b1010: 0, # white knights
            0b1011: 0, # white bishops
            0b1100: 0, # white rooks
            0b1101: 0, # white queens
            0b1110: 0, # white king

            0b0001: 0, # black pawns
            0b0010: 0, # black knights
            0b0011: 0, # black bishops
            0b0100: 0, # black rooks
            0b0101: 0, # black queens
            0b0110: 0  # black king
        }

        self.color_bitboards = {
            0b1: 0, # white
            0b0: 0  # black
        }

        self.castling_rights = 0b1111 # KQkq
        self.en_passant_target_square = 127 # no en passant target square
        self.halfmove_clock = 0
        self.fullmove_number = 1
        self.white_to_move = True

        self.undo_list = []

        self.load_fen(fen)

    def hash_board(self):
        '''
        Hash the board using murmurhash3
        '''

        bitboards_binary = b''.join(
            bitboard.to_bytes(16, 'big') for bitboard in self.piece_bitboards.values()
        )

        en_passant_binary = self.en_passant_target_square.to_bytes(1, 'big')

        castling_rights_binary = self.castling_rights.to_bytes(1, 'big')

        concatenated_binary = bitboards_binary + en_passant_binary + castling_rights_binary

        hash1, hash2 = mmh3.hash128(concatenated_binary, seed=0)

        return f"{hash1:016x}{hash2:016x}"

    # getters
    def is_piece(self, square):
        return (self.color_bitboards[0b1] | self.color_bitboards[0b0]) & (1 << square) != 0

    def is_empty(self, square):
        return (self.color_bitboards[0b1] | self.color_bitboards[0b0]) & (1 << square) == 0
    
    def is_white(self, square):
        return self.color_bitboards[0b1] & (1 << square) != 0

    def is_black(self, square):
        return self.color_bitboards[0b0] & (1 << square) != 0

    def is_pawn(self, square):
        return (self.piece_bitboards[0b1001] | self.piece_bitboards[0b0001]) & (1 << square) != 0

    def is_knight(self, square):
        return (self.piece_bitboards[0b1010] | self.piece_bitboards[0b0010]) & (1 << square) != 0

    def is_bishop(self, square):
        return (self.piece_bitboards[0b1011] | self.piece_bitboards[0b0011]) & (1 << square) != 0

    def is_rook(self, square):
        return (self.piece_bitboards[0b1100] | self.piece_bitboards[0b0100]) & (1 << square) != 0

    def is_queen(self, square):
        return (self.piece_bitboards[0b1101] | self.piece_bitboards[0b0101]) & (1 << square) != 0

    def is_king(self, square):
        return (self.piece_bitboards[0b1110] | self.piece_bitboards[0b0110]) & (1 << square) != 0

    def get_piece(self, square):
        for piece in self.piece_bitboards:
            if self.piece_bitboards[piece] & (1 << square) != 0:
                return piece


    # setters
    def set_piece(self, square, piece):
        self.piece_bitboards[piece] |= 1 << square
        self.color_bitboards[piece >> 3] |= 1 << square

    def clear_piece(self, square, piece):
        self.piece_bitboards[piece] &= ~(1 << square)
        self.color_bitboards[piece >> 3] &= ~(1 << square)

    def move_piece(self, start, end, piece):
        self.clear_piece(start, piece)
        # self.clear_piece(end, piece) # TOTEST: this might be redundant
        self.set_piece(end, piece)


    def load_fen(self, fen):
        '''
        Load a FEN string into the board.
        '''
        # example fen: 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

        # reset the board
        for piece in self.piece_bitboards:
            self.piece_bitboards[piece] = 0
        for color in self.color_bitboards:
            self.color_bitboards[color] = 0

        fen_data = fen.split(' ')
        piece_placement = fen_data[0]
        turn = fen_data[1]
        castling_rights = fen_data[2]
        en_passant = fen_data[3]
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
                square = rank * 16 + file
                piece = piece_char_to_bin[char]
                self.set_piece(square, piece)
                file += 1

        # set the turn
        self.white_to_move = turn == 'w'

        # set the castling rights
        self.castling_rights = 0b0000
        for char in castling_rights:
            if char == 'K':
                self.castling_rights |= 0b1000
            elif char == 'Q':
                self.castling_rights |= 0b0100
            elif char == 'k':
                self.castling_rights |= 0b0010
            elif char == 'q':
                self.castling_rights |= 0b0001

        # set the en passant target square
        self.en_passant_target_square = 127
        if en_passant != '-':
            file = ord(en_passant[0]) - ord('a')
            rank = int(en_passant[1]) - 1
            self.en_passant_target_square = rank * 16 + file

        # set the halfmove clock and fullmove number
        self.halfmove_clock = int(halfmove_clock)
        self.fullmove_number = int(fullmove_number)


    def create_fen(self):
        '''
        Create a FEN string from the board.
        '''

        # piece placement
        fen = ''
        empty_counter = 0
        for rank in range(7, -1, -1):
            for file in range(8):
                square = rank * 16 + file
                
                if self.is_piece(square):
                    if empty_counter:
                        fen += str(empty_counter)
                        empty_counter = 0
                    fen += piece_bin_to_char[self.get_piece(square)]

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
        if self.castling_rights & 0b1000:
            castling += 'K'
        if self.castling_rights & 0b0100:
            castling += 'Q'
        if self.castling_rights & 0b0010:
            castling += 'k'
        if self.castling_rights & 0b0001:
            castling += 'q'

        fen += castling if castling else '-'
        fen += ' '

        # en passant target square
        if self.en_passant_target_square == 127:
            fen += '-'
        else:
            file = chr(ord('a') + self.en_passant_target_square % 16)
            rank = str(self.en_passant_target_square // 16 + 1)
            fen += file + rank
        fen += ' '

        # halfmove clock
        fen += str(self.halfmove_clock) + ' '

        # fullmove number
        fen += str(self.fullmove_number)

        return fen
    
    def make_move(self, move):
        '''
        Make a move on the board.
        
        Args:
            move: (int), encoded move
        '''
        start, end, start_piece, captured_piece, promotion_piece, castling, capture, en_passant = decode_move(move)

        # save the state for undo
        self.undo_list.append((
            self.piece_bitboards.copy(),
            self.color_bitboards.copy(), 
            self.castling_rights,
            self.en_passant_target_square, 
            self.halfmove_clock, 
            self.fullmove_number, 
            self.white_to_move))


        # castling - move the rook (castling rights removed when the king moves)
        if castling != 0b0000:
            if castling & 0b1000: # white kingside
                self.move_piece(7, 5, 0b1000)

            elif castling & 0b0100: # white queenside
                self.move_piece(0, 3, 0b0100)

            elif castling & 0b0010: # black kingside
                self.move_piece(119, 117, 0b0010)

            elif castling & 0b0001: # black queenside
                self.move_piece(112, 115, 0b0001)

        # en passant
        if en_passant:
            # clear the captured pawn
            if self.white_to_move:
                self.clear_piece(end - 16, 0b0001)
            else:
                self.clear_piece(end + 16, 0b1001)

        # promotion
        if promotion_piece != 0b0000:
            if capture:
                self.clear_piece(end, captured_piece)
            
            self.clear_piece(start, start_piece)
            self.set_piece(end, promotion_piece)

        # normal move
        else:
            if capture:
                self.clear_piece(end, captured_piece)
            self.move_piece(start, end, start_piece)

        # update castling rights
        if start_piece == 0b1110:
            self.castling_rights &= 0b0011
        if start_piece == 0b0110:
            self.castling_rights &= 0b1100
            
        # update castling rights if a rook is moved or captured
        if start == 0 or end == 0: # white queenside rook
            self.castling_rights &= 0b1011
        if start == 7 or end == 7: # white kingside rook
            self.castling_rights &= 0b0111
        if start == 112 or end == 112: # black queenside rook
            self.castling_rights &= 0b1101
        if start == 119 or end == 119: # black kingside rook
            self.castling_rights &= 0b1110 

        # update en passant target square
        if (start_piece & 0b0111 == 0b001) and abs(start - end) == 32:
            self.en_passant_target_square = (start + end) // 2
        else:
            self.en_passant_target_square = 127

        # update board state
        if not self.white_to_move:
            self.fullmove_number += 1
        self.white_to_move = not self.white_to_move
        self.halfmove_clock += 1
        if capture or self.is_pawn(start):
            self.halfmove_clock = 0

    def undo_move(self):
        '''
        Undo the last move.
        '''
        # restore the state from the undo list
        if self.undo_list:
            self.piece_bitboards, self.color_bitboards, self.castling_rights, self.en_passant_target_square, self.halfmove_clock, self.fullmove_number, self.white_to_move = self.undo_list.pop()

    def generate_moves(self, turn):
        '''
        Generate all moves for the current position. Does not check for legality.
        '''
        moves = []
        for square in LEGAL_SQUARES:
            if self.is_piece(square):
                piece = self.get_piece(square)
                piece_color = 0b1 if self.is_white(square) else 0b0
                if piece_color == turn:
                    if self.is_pawn(square):
                        moves += self.generate_pawn_moves(square, piece)
                    elif self.is_knight(square):
                        moves += self.generate_knight_moves(square, piece)
                    elif self.is_bishop(square):
                        moves += self.generate_bishop_moves(square, piece)
                    elif self.is_rook(square):
                        moves += self.generate_rook_moves(square, piece)
                    elif self.is_queen(square):
                        moves += self.generate_queen_moves(square, piece)
                    elif self.is_king(square):
                        moves += self.generate_king_moves(square, piece)

        return moves

    def generate_single_moves(self, square, piece, directions):
        '''
        Generate all single moves for a given square.
        '''
        piece_color = 0b1 if self.is_white(square) else 0b0
        moves = []
        for direction in directions:
            target_square = square + direction
            if target_square & OUT_OF_BOUNDS_MASK == 0:
                if self.is_empty(target_square):
                    moves.append(encode_move(
                        start=square, 
                        end=target_square, 
                        start_piece=piece, 
                        capture=False
                        ))
                elif self.is_white(target_square) != piece_color:
                    moves.append(encode_move(
                        start=square, 
                        end=target_square, 
                        start_piece=piece, 
                        captured_piece=self.get_piece(target_square), 
                        capture=True
                        ))
                    
        return moves

    def generate_sliding_moves(self, square, piece, directions):
        '''
        Generate all sliding moves for a given square.
        '''
        piece_color = 0b1 if self.is_white(square) else 0b0
        moves = []
        for direction in directions:
            target_square = square + direction

            while target_square & OUT_OF_BOUNDS_MASK == 0:
                if self.is_empty(target_square):
                    moves.append(encode_move(
                        start=square, 
                        end=target_square, 
                        start_piece=piece, 
                        capture=False
                        ))
                    
                elif self.is_white(target_square) != piece_color:
                    moves.append(encode_move(
                        start=square, 
                        end=target_square, 
                        start_piece=piece, 
                        captured_piece=self.get_piece(target_square), 
                        capture=True
                        ))
                    break

                else:
                    break

                target_square += direction

        return moves

    def generate_pawn_moves(self, square, piece):
        '''
        Generate all pawn moves for a given square.
        '''
        moves = []
        piece_color = 0b1 if self.is_white(square) else 0b0 # replace this with getting the color from the piece
        direction = 16 if piece_color else -16
        start_rank = 1 if piece_color else 6
        promotion_rank = 7 if piece_color else 0

        # single push
        single_push = square + direction
        if self.is_empty(single_push):
            moves.append(encode_move(square, single_push, piece))

            # double push
            if (square >> 4) == start_rank:
                if self.is_empty(square + 2 * direction):
                    moves.append(encode_move(square, square + 2 * direction, piece))

            # promotion
            elif ((single_push) >> 4) == promotion_rank:
                for promotion_piece in PROMOTION_PIECES:
                    moves.append(encode_move(square, single_push, piece, promotion_piece))

        # captures
        capture_directions = [15, 17] if piece_color else [-15, -17]
        for direction in capture_directions:
            capture_square = square + direction
            if self.is_piece(capture_square) and self.is_white(capture_square) != piece_color:

                # promotion
                if ((capture_square) >> 4) == promotion_rank:
                    for promotion_piece in PROMOTION_PIECES:
                        moves.append(encode_move(
                            start=square, 
                            end=capture_square, 
                            start_piece=piece, 
                            captured_piece=self.get_piece(capture_square), 
                            promotion_piece=promotion_piece, 
                            capture=True
                            ))

                # normal capture
                else:
                    moves.append(encode_move(
                        start=square, 
                        end=capture_square, 
                        start_piece=piece, 
                        captured_piece=self.get_piece(capture_square), 
                        capture=True
                        ))

            # en passant
            if capture_square == self.en_passant_target_square:
                moves.append(encode_move(
                    start=square, 
                    end=capture_square, 
                    start_piece=piece, 
                    captured_piece=0b0001 if piece_color else 0b1001, # maybe remove this
                    capture=True, 
                    en_passant=True
                    ))
                
        return moves

    def generate_knight_moves(self, square, piece):
        '''
        Generate all knight moves for a given square.
        '''
        return self.generate_single_moves(square, piece, KNIGHT_DIRECTIONS)

    def generate_bishop_moves(self, square, piece):
        '''
        Generate all bishop moves for a given square.
        '''
        return self.generate_sliding_moves(square, piece, BISHOP_DIRECTIONS)

    def generate_rook_moves(self, square, piece):
        '''
        Generate all rook moves for a given square.
        '''
        return self.generate_sliding_moves(square, piece, ROOK_DIRECTIONS)

    def generate_queen_moves(self, square, piece):
        '''
        Generate all queen moves for a given square.
        '''
        return self.generate_sliding_moves(square, piece, QUEEN_DIRECTIONS)

    def generate_king_moves(self, square, piece):
        '''
        Generate all king moves for a given square.
        '''
        moves = []
        piece_color = 0b1 if self.is_white(square) else 0b0
        for direction in KING_DIRECTIONS:
            target_square = square + direction
            if target_square & OUT_OF_BOUNDS_MASK == 0:
                if self.is_empty(target_square):
                    moves.append(encode_move(
                        start=square, 
                        end=target_square, 
                        start_piece=piece, 
                        capture=False
                        ))
                elif self.is_white(target_square) != piece_color:
                    moves.append(encode_move(
                        start=square, 
                        end=target_square, 
                        start_piece=piece, 
                        captured_piece=self.get_piece(target_square), 
                        capture=True
                        ))
                    
        return moves

    def is_check(self, turn):
        '''
        Check if the current position is in check.
        Turn is the color of the king to check.
        '''
        # find the ally king
        ally_king = 0b1110 if turn else 0b0110
        # ally_king_square = self.piece_bitboards[ally_king].bit_length() - 1

        enemy_moves = self.generate_moves(not turn)
        for move in enemy_moves:
            _, _, _, captured_piece, _, _, _, _ = decode_move(move)
            if captured_piece == ally_king:
                return True
            
        return False
    
    def generate_legal_moves(self, turn):
        '''
        Generate all legal moves for the current position.
        '''
        moves = self.generate_moves(turn)
        legal_moves = []
        for move in moves:
            self.make_move(move)
            if not self.is_check(turn):
                legal_moves.append(move)

            self.undo_move()
        return legal_moves
    
    def is_checkmate(self, turn):
        '''
        Check if the current position is in checkmate.
        '''
        return self.is_check(turn) and not self.generate_legal_moves(turn)
    
    def is_stalemate(self, turn):
        '''
        Check if the current position is in stalemate.
        '''
        return not self.is_check(turn) and not self.generate_legal_moves(turn)