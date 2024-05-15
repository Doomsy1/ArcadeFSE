STARTING_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

class Board:
    def __init__(self):
        self.bitboards = {
            'P': 0,'N': 0, 'B': 0, 'R': 0, 'Q': 0, 'K': 0, # specific white pieces
            'p': 0,'n': 0, 'b': 0, 'r': 0, 'q': 0, 'k': 0, # specific black pieces
            'occupied': 0, # all occupied squares
            'white': 0, # all white pieces
            'black': 0, # all black pieces
        }




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
    
    