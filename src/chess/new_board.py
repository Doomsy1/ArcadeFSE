STARTING_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

OUT_OF_BOUNDS_MASK = 0x88

KNIGHT_DIRECTIONS = [   -17,    # (-8 x 2) - 1  | down 2, left 1
                        -15,    # (-8 x 2) + 1  | down 2, right 1
                        -10,    # (-8 x 1) - 2  | down 1, left 2
                        -6,     # (-8 x 1) + 2  | down 1, right 2
                        6,      # (8 x 1) - 2   | up 1, left 2
                        10,     # (8 x 1) + 2   | up 1, right 2
                        15,     # (8 x 2) - 1   | up 2, left 1
                        17]     # (8 x 2) + 1   | up 2, right 1

BISHOP_DIRECTIONS = [   -9,     # (-8 x 1) - 1  | down 1, left 1
                        -7,     # (-8 x 1) + 1  | down 1, right 1
                        7,      # (8 x 1) - 1   | up 1, left 1
                        9]      # (8 x 1) + 1   | up 1, right 1

ROOK_DIRECTIONS = [     -8,     # down
                        -1,     # left
                        1,      # right
                        8]      # up

QUEEN_DIRECTIONS = BISHOP_DIRECTIONS + ROOK_DIRECTIONS

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

    def is_piece(self, square):
        return self.bitboards['occupied'] & (1 << square)
    
    def is_empty(self, square):
        return not self.is_piece(square)
    
    def is_white(self, square):
        return self.bitboards['white'] & (1 << square)
    
    def is_black(self, square):
        return self.bitboards['black'] & (1 << square)
    
    def is_pawn(self, square):
        return self.bitboards['P'] & (1 << square) or self.bitboards['p'] & (1 << square)
    
    def is_knight(self, square):
        return self.bitboards['N'] & (1 << square) or self.bitboards['n'] & (1 << square)
    
    def is_bishop(self, square):
        return self.bitboards['B'] & (1 << square) or self.bitboards['b'] & (1 << square)
    
    def is_rook(self, square):
        return self.bitboards['R'] & (1 << square) or self.bitboards['r'] & (1 << square)
    
    def is_queen(self, square):
        return self.bitboards['Q'] & (1 << square) or self.bitboards['q'] & (1 << square)
    
    def is_king(self, square):
        return self.bitboards['K'] & (1 << square) or self.bitboards['k'] & (1 << square)
    
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
            self.bitboards[piece] &= ~(1 << start)
            self.bitboards[piece] |= 1 << end
        self.bitboards['occupied'] &= ~(1 << start)
        self.bitboards['occupied'] |= 1 << end

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
        for square in range(64):
            self.clear_piece(square)

        # set up the board
        file, rank = 0, 7 # start at a8
        for char in piece_placement:
            if char == '/': # new rank (lower down the board)
                file = 0
                rank -= 1
            elif char.isdigit():
                file += int(char) # empty squares
            else:
                self.set_piece(char, 8 * rank + file)
                file += 1

        # set the state of the game
        self.white_to_move = turn == 'w'
        self.castling_availability = castling_availability
        self.halfmove_clock = int(halfmove_clock)
        self.fullmove_number = int(fullmove_number)
        
        # calculate en passant square
        if en_passant_square != '-':
            self.en_passant_square = ord(en_passant_square[0]) - ord('a') + (int(en_passant_square[1]) - 1) * 8
        else:
            self.en_passant_square = None

    def board_to_fen(self):
        # piece placement
        fen = ''
        empty = 0
        for rank in range(7, -1, -1):
            for file in range(8):
                square = 8 * rank + file
                if self.is_empty(square):
                    empty += 1
                else:
                    if empty:
                        fen += str(empty)
                        empty = 0
                    piece = None
                    if self.is_pawn(square):
                        piece = 'p' if self.is_black(square) else 'P'
                    elif self.is_knight(square):
                        piece = 'n' if self.is_black(square) else 'N'
                    elif self.is_bishop(square):
                        piece = 'b' if self.is_black(square) else 'B'
                    elif self.is_rook(square):
                        piece = 'r' if self.is_black(square) else 'R'
                    elif self.is_queen(square):
                        piece = 'q' if self.is_black(square) else 'Q'
                    elif self.is_king(square):
                        piece = 'k' if self.is_black(square) else 'K'
                    fen += piece
            if empty:
                fen += str(empty)
                empty = 0
            if rank:
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
            rank = self.en_passant_square // 8
            file = self.en_passant_square % 8
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
        start, end, flag = decode_move(move)
        match flag:
            case 0: # normal move
                self.move_piece(start, end)

            case 1: # promotion to knight
                self.clear_piece(start)
                self.set_piece('N' if self.is_white(start) else 'n', end)

            case 2: # promotion to bishop
                self.clear_piece(start)
                self.set_piece('B' if self.is_white(start) else 'b', end)

            case 3: # promotion to rook
                self.clear_piece(start)
                self.set_piece('R' if self.is_white(start) else 'r', end)

            case 4: # promotion to queen
                self.clear_piece(start)
                self.set_piece('Q' if self.is_white(start) else 'q', end)

            case 5: # en passant capture
                self.move_piece(start, end)
                self.clear_piece(end - 8 if self.is_white(start) else end + 8)

            case 6: # castling kingside
                self.move_piece(start, end) # move the king

                if end == 62: # white
                    self.move_piece(63, 61) # move the rook
                else: # black
                    self.move_piece(7, 5) # move the rook
            case 7:
                self.move_piece(start, end) # move the king
                if end == 58: # white
                    self.move_piece(56, 59) # move the rook
                else: # black
                    self.move_piece(0, 3) # move the rook



        self.white_to_move = not self.white_to_move

    def generate_sliding_moves(self, square, directions, max_distance = 7):
        moves = []
        for direction in directions:
            for distance in range(1, max_distance + 1):
                end = square + direction * distance

                # check if the end square is off the board
                if end & OUT_OF_BOUNDS_MASK:
                    break

                # check if the end square is occupied
                if self.is_piece(end):

                    # capture if the end square is occupied by an enemy piece
                    if self.is_white(end) != self.is_white(square):
                        moves.append(encode_move(square, end))
                    break
                    
                # add the move if the end square is empty
                moves.append(encode_move(square, end))

        return moves
    
    def generate_knight_moves(self, square):
        moves = []
        for direction in KNIGHT_DIRECTIONS:

            end = square + direction

            # check if the end square is off the board
            if end & OUT_OF_BOUNDS_MASK:
                continue

            if self.is_piece(end):

                # check for capture
                if self.is_white(end) != self.is_white(square):
                    moves.append(encode_move(square, end))
                    
            else:
                moves.append(encode_move(square, end))

        return moves

    def generate_pawn_moves(self, square):
        moves = []
        direction = -8 if self.is_white(square) else 8

        # single move
        end = square + direction
        if self.is_empty(end):
            moves.append(encode_move(square, end))

            # double move for white pawns
            if self.is_white(square) and square // 8 == 1 and self.is_empty(end + direction):
                moves.append(encode_move(square, end))

            # double move for black pawns
            if not self.is_white(square) and square // 8 == 6 and self.is_empty(end + direction):
                moves.append(encode_move(square, end))

        # captures
        for direction in [-9, -7] if self.is_white(square) else [7, 9]:
            end = square + direction
            if end & OUT_OF_BOUNDS_MASK:
                continue

            if self.is_piece(end) and self.is_white(end) != self.is_white(square):
                moves.append(encode_move(square, end))

        return moves
    
    def generate_king_moves(self, square):
        moves = []
        directions = QUEEN_DIRECTIONS

        moves += self.generate_sliding_moves(square, directions, 1)

        # castling
        if self.is_white(square):
            if 'K' in self.castling_availability and self.is_empty(5) and self.is_empty(6):
                moves.append(encode_move(square, 6, 6))
            if 'Q' in self.castling_availability and self.is_empty(1) and self.is_empty(2) and self.is_empty(3):
                moves.append(encode_move(square, 2, 7))
        elif self.is_black(square):
            if 'k' in self.castling_availability and self.is_empty(61) and self.is_empty(62):
                moves.append(encode_move(square, 62, 6))
            if 'q' in self.castling_availability and self.is_empty(57) and self.is_empty(58) and self.is_empty(59):
                moves.append(encode_move(square, 58, 7))

        return moves

    def generate_moves(self, turn):
        moves = []
        for square in range(64):
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
        
        # find the king
        king_square = self.bitboards['K'] if turn else self.bitboards['k']

        king_square = king_square.bit_length() - 1

        # check if the king is attacked by any of the opponent's pieces
        moves = self.generate_moves(not turn)
        for move in moves:
            start, end, flag = decode_move(move)
            if end == king_square:
                return True
            
        return False





def encode_move(start, end, flag = 0):
        # start is 0 - 63       | 6 bits
        # end is 0 - 63         | 6 bits

        # Special moves:        | 4 bits
        # 0000 - Normal move
        # 0001 - Promotion to knight
        # 0010 - Promotion to bishop
        # 0011 - Promotion to rook
        # 0100 - Promotion to queen

        # 0101 - En passant capture
        # 0110 - Castling kingside
        # 0111 - Castling queenside

        # Total: 16 bits

        move = start << 6 # first 6 bits encode the start
        move |= end # next 6 bits encode the end
        move <<= 4 # next 4 bits encode the special flags (last bit is unused)
        move |= flag
        return move

def decode_move(move):
    flag = move & 0b1111 # get the last 4 bits
    move >>= 4 # shift the move 4 bits to the right
    end = move & 0b111111 # get the last 6 bits
    move >>= 6 # shift the move 6 bits to the right
    start = move & 0b111111 # get the last 6 bits again
    return start, end, flag








if __name__ == "__main__":
    b = Board()
    fen = '4k3/8/2Q5/8/8/8/8/4K3 w - - 0 1'
    b.fen_to_board(fen)
    print(fen)
    print(b.board_to_fen())
    print(b.is_check(True))