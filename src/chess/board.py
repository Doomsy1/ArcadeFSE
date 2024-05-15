STARTING_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

OUT_OF_BOARD_MASK = 0x88

KNIGHT_DIRECTIONS = [   -33,    # (-16 x 2) - 1  | down 2, left 1
                        -31,    # (-16 x 2) + 1  | down 2, right 1
                        -18,    # (-16 x 1) - 2  | down 1, left 2
                        -14,     # (-16 x 1) + 2  | down 1, right 2
                        14,      # (16 x 1) - 2   | up 1, left 2
                        18,     # (16 x 1) + 2   | up 1, right 2
                        31,     # (16 x 2) - 1   | up 2, left 1
                        33]     # (16 x 2) + 1   | up 2, right 1

BISHOP_DIRECTIONS = [   -17,     # (-16 x 1) - 1  | down 1, left 1
                        -15,     # (-16 x 1) + 1  | down 1, right 1
                        15,      # (16 x 1) - 1   | up 1, left 1
                        17]      # (16 x 1) + 1   | up 1, right 1

ROOK_DIRECTIONS = [     -16,     # down
                        -1,     # left
                        1,      # right
                        16]      # up

QUEEN_DIRECTIONS = BISHOP_DIRECTIONS + ROOK_DIRECTIONS

LEGAL_SQUARES = [i for i in range(127) if not i & 0x88]

class Board:
    def __init__(self, fen = STARTING_FEN):
        self.bitboards = {
            'P': 0,'N': 0, 'B': 0, 'R': 0, 'Q': 0, 'K': 0, # specific white pieces
            'p': 0,'n': 0, 'b': 0, 'r': 0, 'q': 0, 'k': 0, # specific black pieces
            'occupied': 0, # all occupied squares
            'white': 0, # all white pieces
            'black': 0, # all black pieces
        }
        self.fen_to_board(fen)
        self.undo_list = [fen]

    # getters
    def is_piece(self, square):
        return bool(self.bitboards['occupied'] & (1 << square))
    def is_empty(self, square):
        return not self.is_piece(square)    
    def is_white(self, square):
        return bool(self.bitboards['white'] & (1 << square))
    def is_black(self, square):
        return bool(self.bitboards['black'] & (1 << square))
    def is_pawn(self, square):
        return bool(self.bitboards['P'] & (1 << square) or self.bitboards['p'] & (1 << square))
    def is_knight(self, square):
        return bool(self.bitboards['N'] & (1 << square) or self.bitboards['n'] & (1 << square))
    def is_bishop(self, square):
        return bool(self.bitboards['B'] & (1 << square) or self.bitboards['b'] & (1 << square))
    def is_rook(self, square):
        return bool(self.bitboards['R'] & (1 << square) or self.bitboards['r'] & (1 << square))
    def is_queen(self, square):
        return bool(self.bitboards['Q'] & (1 << square) or self.bitboards['q'] & (1 << square))
    def is_king(self, square):
        return bool(self.bitboards['K'] & (1 << square) or self.bitboards['k'] & (1 << square))
    
    def set_piece(self, piece, square):
        self.bitboards[piece] |= 1 << square
        self.bitboards['occupied'] |= 1 << square
        if piece.isupper():
            self.bitboards['white'] |= 1 << square
        else:
            self.bitboards['black'] |= 1 << square

    def clear_piece(self, square):
        for piece in self.bitboards:
            self.bitboards[piece] &= ~(1 << square)
        self.bitboards['occupied'] &= ~(1 << square)
        self.bitboards['white'] &= ~(1 << square)
        self.bitboards['black'] &= ~(1 << square)

    def move_piece(self, start, end):
        for piece in self.bitboards:
            if self.bitboards[piece] & (1 << start):
                self.clear_piece(start)
                self.set_piece(piece, end)
                break

    def fen_to_board(self, fen):
        # example fen: 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

        fen_data = fen.split(" ")
        piece_placement = fen_data[0]
        turn = fen_data[1]
        castling_availability = fen_data[2]
        en_passant_square = fen_data[3]
        halfmove_clock = fen_data[4]
        fullmove_number = fen_data[5]

        # clear the board
        self.bitboards = {
            'P': 0,'N': 0, 'B': 0, 'R': 0, 'Q': 0, 'K': 0, # specific white pieces
            'p': 0,'n': 0, 'b': 0, 'r': 0, 'q': 0, 'k': 0, # specific black pieces
            'occupied': 0, # all occupied squares
            'white': 0, # all white pieces
            'black': 0, # all black pieces
        }

        # set up the board (0x88 board representation)
        file = 0
        rank = 7
        for char in piece_placement:
            if char == '/':
                file = 0
                rank -= 1
                continue
            if char.isdigit():
                file += int(char)
            else:
                square = rank * 16 + file
                self.set_piece(char, square)
                file += 1

        # set the state of the game
        self.white_to_move = turn == 'w'
        self.castling_availability = castling_availability
        self.halfmove_clock = int(halfmove_clock)
        self.fullmove_number = int(fullmove_number)
        
        # calculate en passant square
        if en_passant_square != '-':
            self.en_passant_square = ord(en_passant_square[0]) - ord('a') + (int(en_passant_square[1]) - 1) * 16
        else:
            self.en_passant_square = None

    def board_to_fen(self):
        # piece placement
        fen = ''
        empty = 0
        for rank in range(7, -1, -1): # top to bottom
            for file in range(0, 8): # left to right
                square = rank * 16 + file
                if self.is_empty(square):
                    empty += 1
                else:
                    if empty > 0:
                        fen += str(empty)
                        empty = 0
                    piece = ''
                    for key in self.bitboards:
                        if self.bitboards[key] & (1 << square):
                            piece = key
                            break
                    fen += piece
            if empty > 0:
                fen += str(empty)
                empty = 0
            if rank > 0:
                fen += '/'
        fen += ' '

        # active color
        fen += 'w' if self.white_to_move else 'b'
        fen += ' '

        # castling availability
        fen += self.castling_availability
        fen += ' '

        # en passant square
        if self.en_passant_square is not None:
            rank = self.en_passant_square // 16
            file = self.en_passant_square % 16
            fen += chr(file + ord('a')) + str(rank + 1)
        else:
            fen += '-'
        fen += ' '

        # halfmove clock
        fen += str(self.halfmove_clock)
        fen += ' '

        # fullmove number
        fen += str(self.fullmove_number)

        return fen

    def make_move(self, move):
        start, end, promotion, piece_type, castle_flag, capture = decode_move(move)

        # add the move to the undo list
        self.undo_list.append(self.board_to_fen())
        
        # check for castling
        if castle_flag:
            if castle_flag & 0b1000: # white kingside
                self.move_piece(7, 5)

            elif castle_flag & 0b0100: # white queenside
                self.move_piece(0, 3)

            elif castle_flag & 0b0010: # black kingside
                self.move_piece(119, 117)

            elif castle_flag & 0b0001: # black queenside
                self.move_piece(112, 115)

        # check for rook move
        if self.is_rook(start):
            if self.is_white(start):
                if start == 0:
                    self.castling_availability = self.castling_availability.replace('Q', '')
                elif start == 7:
                    self.castling_availability = self.castling_availability.replace('K', '')
            else:
                if start == 112:
                    self.castling_availability = self.castling_availability.replace('q', '')
                elif start == 119:
                    self.castling_availability = self.castling_availability.replace('k', '')

        # check for king move
        if self.is_king(start):
            if self.is_white(start):
                self.castling_availability = self.castling_availability.replace('K', '')
                self.castling_availability = self.castling_availability.replace('Q', '')
            else:
                self.castling_availability = self.castling_availability.replace('k', '')
                self.castling_availability = self.castling_availability.replace('q', '')

        if self.castling_availability == '':
            self.castling_availability = '-'

        # check for promotion
        elif promotion:
            if piece_type == 0:
                piece = 'n'
            elif piece_type == 1:
                piece = 'b'
            elif piece_type == 2:
                piece = 'r'
            elif piece_type == 3:
                piece = 'q'
            self.clear_piece(start)
            piece = piece.upper() if self.is_white(start) else piece
            self.set_piece(piece, end)            

        # check for en passant capture
        if self.en_passant_square is not None and end == self.en_passant_square:
            if self.is_white(start):
                self.clear_piece(end - 16)
            else:
                self.clear_piece(end + 16)
                
        # check for capture
        if capture:
            self.clear_piece(end)

        # capture or normal move
        if not promotion:
            self.move_piece(start, end)

        # update halfmove clock
        if self.is_piece(end) or self.is_pawn(start):
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1

        # update fullmove number
        if not self.white_to_move:
            self.fullmove_number += 1

        # update turn
        self.white_to_move = not self.white_to_move

    def undo_move(self):
        if len(self.undo_list) >= 1:
            fen = self.undo_list[-1]
            self.fen_to_board(self.undo_list.pop())

    def is_valid_square(self, square):
        # check if the move is on the board
        if square & OUT_OF_BOARD_MASK:
            return False
        return True
        
    def generate_sliding_moves(self, square, directions, max_distance = 7):
        moves = []
        for direction in directions:
            for distance in range(1, max_distance + 1):
                end = square + direction * distance

                # check if the end square is valid
                if not self.is_valid_square(end):
                    break

                if self.is_piece(end):
                        # check for capture
                        if self.is_white(end) != self.is_white(square):
                            moves.append(encode_move(square, end, capture=True))
                        break # stop sliding after capturing a piece or hitting a piece of the same color
                else:
                    moves.append(encode_move(square, end))

        return moves
    
    def generate_knight_moves(self, square):
        moves = []
        for direction in KNIGHT_DIRECTIONS:

            end = square + direction

            # check if the end square is valid
            if not self.is_valid_square(end):
                continue

            if self.is_piece(end):
                # check for capture
                if self.is_white(end) != self.is_white(square):
                    moves.append(encode_move(square, end, capture=True))
            else:
                moves.append(encode_move(square, end))


        return moves

    def generate_pawn_moves(self, square):
        moves = []
        direction = 16 if self.is_white(square) else -16

        # en passant
        if self.en_passant_square is not None:
            if square + 1 == self.en_passant_square or square - 1 == self.en_passant_square:
                moves.append(encode_move(square, self.en_passant_square - direction, capture=True))

        # single move forward
        end = square + direction
        if self.is_empty(end):

            # white promotion to any piece
            if self.is_white(square) and end >= 112:
                for piece in range(0, 4):
                    moves.append(encode_move(square, end, promotion=True, piece_type=piece))

            # black promotion to any piece
            elif not self.is_white(square) and end <= 7:
                for piece in range(0, 4):
                    moves.append(encode_move(square, end, promotion=True, piece_type=piece))

            # normal move forward
            else:
                moves.append(encode_move(square, end))

                # white double move
                if self.is_white(square) and square // 16 == 1:
                    end = square + 2 * direction
                    if self.is_empty(end):
                        moves.append(encode_move(square, end))

                # black double move
                elif not self.is_white(square) and square // 16 == 6:
                    end = square + 2 * direction
                    if self.is_empty(end):
                        moves.append(encode_move(square, end))

        directions = [15, 17] if self.is_white(square) else [-15, -17]
        # capture moves
        for direction in directions:
            end = square + direction
            if self.is_valid_square(end) and self.is_piece(end) and self.is_white(end) != self.is_white(square):

                # white promotion to any piece with capture
                if self.is_white(square) and end >= 112:
                    for piece in range(0, 4):
                        moves.append(encode_move(square, end, promotion=True, piece_type=piece, capture=True))

                # black promotion to any piece with capture
                elif not self.is_white(square) and end <= 7:
                    for piece in range(0, 4):
                        moves.append(encode_move(square, end, promotion=True, piece_type=piece, capture=True))

                # normal capture
                else:
                    moves.append(encode_move(square, end, capture=True))

            # en passant capture
            if end == self.en_passant_square:
                moves.append(encode_move(square, end, capture=True))       

        return moves
    
    def generate_king_moves(self, square):
        moves = []
        directions = QUEEN_DIRECTIONS

        moves += self.generate_sliding_moves(square, directions, 1)

        # castling
        if self.is_white(square):
            if 'K' in self.castling_availability:
                if not self.is_piece(5) and not self.is_piece(6):
                    moves.append(encode_move(square, 6, castle_flag=0b1000))
            if 'Q' in self.castling_availability:
                if not self.is_piece(1) and not self.is_piece(2) and not self.is_piece(3):
                    moves.append(encode_move(square, 2, castle_flag=0b0100))
        else:
            if 'k' in self.castling_availability:
                if not self.is_piece(117) and not self.is_piece(118):
                    moves.append(encode_move(square, 118, castle_flag=0b0010))
            if 'q' in self.castling_availability:
                if not self.is_piece(113) and not self.is_piece(114) and not self.is_piece(115):
                    moves.append(encode_move(square, 114, castle_flag=0b0001))

        return moves

    def generate_moves(self, turn):
        moves = []
        for square in LEGAL_SQUARES:
            # skip empty squares and squares with the wrong color
            if self.is_empty(square) or turn != self.is_white(square):
                continue

            if self.is_pawn(square):
                moves += self.generate_pawn_moves(square)

            elif self.is_knight(square):
                moves += self.generate_knight_moves(square)

            elif self.is_bishop(square):
                moves += self.generate_sliding_moves(square, BISHOP_DIRECTIONS)

            elif self.is_rook(square):
                moves += self.generate_sliding_moves(square, ROOK_DIRECTIONS)

            elif self.is_queen(square):
                moves += self.generate_sliding_moves(square, QUEEN_DIRECTIONS)

            elif self.is_king(square):
                moves += self.generate_king_moves(square)

        return moves
    
    def is_check(self, turn):
        # check if the king is attacked by any of the opponent's pieces
        # turn is the color of the king
        
        # find the king square
        king_bitboard = self.bitboards['K'] if turn else self.bitboards['k']
        king_square = king_bitboard.bit_length() - 1

        # check if the king is attacked by any of the opponent's pieces
        moves = self.generate_moves(not turn)
        for move in moves:
            _, end, _, _, _, _ = decode_move(move)
            if end == king_square:
                return True
            
        return False

    def is_checkmate(self, turn):
        # check if the king is in check and there are no legal moves
        return self.is_check(turn) and self.generate_legal_moves(turn) == []

    def is_stalemate(self, turn):
        # check if the king is not in check and there are no legal moves
        return not self.is_check(turn) and not self.generate_legal_moves(turn)

    def in_threefold_repetition(self):
        # check if the position has occurred three times
        return self.undo_list.count(self.undo_list[-1]) >= 3

    def is_draw(self):
        # check if the game is a draw
        return self.halfmove_clock >= 50 or self.is_stalemate(True) or self.is_stalemate(False) or self.in_threefold_repetition()

    def generate_legal_moves(self, turn):
        moves = self.generate_moves(turn)
        legal_moves = []
        for move in moves:
            # check if the ally king will be in check after the move
            self.make_move(move)
            if not self.is_check(turn):
               legal_moves.append(move)
            self.undo_move()

        return legal_moves

def encode_move(start, end, promotion=False, piece_type=0, castle_flag=0, capture=False):
    """
    Encode a move into a 32-bit integer.
    
    Parameters:
        start (int): start square (0x88 index)
        end (int): end square (0x88 index)
        piece_type (int): Type of piece for promotion (default 0 for no promotion)
        flags (int): Special move flags (default 0)
        capture (bool): Whether the move is a capture (default False)
        
    Returns:
        int: Encoded move
    """
    # 7 bits for start, 7 bits for end, 1 bit for promotion, 2 bits for piece type, 4 bits for castle flag, 1 bit for capture
    # 7 + 7 + 1 + 2 + 4 + 1 = 22 bits
    move = start | (end << 7) | (promotion << 14) | (piece_type << 15) | (castle_flag << 18) | (capture << 22)
    return move

def decode_move(move):
    """
    Decode a 32-bit integer move into its components.
    
    Parameters:
        move (int): Encoded move
        
    Returns:
        tuple: (start, end, promotion, piece_type, castle_flag, capture)
    """
    start = move & 0x7F
    end = (move >> 7) & 0x7F
    promotion = (move >> 14) & 1
    piece_type = (move >> 15) & 3 # 0 for knight, 1 for bishop, 2 for rook, 3 for queen
    castle_flag = (move >> 18) & 15 # 4 bits each for white kingside, white queenside, black kingside, black queenside
    capture = (move >> 22) & 1
    return start, end, promotion, piece_type, castle_flag, capture



if __name__ == "__main__":
    b = Board()
    fen = '1q2K3/8/8/8/8/8/8/4k3 w - - 0 1'
    b.fen_to_board(fen)
    print(b.undo_list)
    print(fen)
    b.generate_legal_moves(True)
    print(b.undo_list)
    print(b.board_to_fen())
    
    print(b.is_check(True))

    