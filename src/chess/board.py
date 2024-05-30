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

# moves will be represented as a tuple
# (start, end, start_piece, captured_piece, promotion_piece, castling, en_passant)

STARTING_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

class Board:
    def __init__(self, fen=STARTING_FEN):
        self.board = [0] * 64                   # 64 squares

        self.white_king_square = 0              # square of white king
        self.black_king_square = 0              # square of black king

        self.white_pieces = set()               # set of white piece squares
        self.black_pieces = set()               # set of black piece squares

        self.white_to_move = True               # True if it's white's turn
        self.castling_rights = 0                # 4 bits for each side (KQkq)
        self.en_passant_target_square = 0       # square where en passant is possible (0 if not possible)
        self.halfmove_clock = 0                 # number of halfmoves since last capture or pawn move
        self.fullmove_number = 0                # starts at 1 and is incremented after b's move

        self.undo_stack = []                    # stack of moves (used for undo_move)

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

        new_board.white_to_move = self.white_to_move
        new_board.castling_rights = self.castling_rights
        new_board.en_passant_target_square = self.en_passant_target_square
        new_board.halfmove_clock = self.halfmove_clock
        new_board.fullmove_number = self.fullmove_number
        new_board.undo_stack = self.undo_stack

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
        piece_color = Piece.get_color(piece)
        piece_type = Piece.get_type(piece)

        if piece_color == Piece.white:
            self.white_pieces.add(square)
            if piece_type == Piece.king:
                self.white_king_square = square
        else:
            self.black_pieces.add(square)
            if piece_type == Piece.king:
                self.black_king_square = square

    def clear_piece(self, square, piece):
        '''Clears the piece on the square'''
        self.board[square] = 0
        piece_color = Piece.get_color(piece)

        if piece_color == Piece.white:
            self.white_pieces.discard(square)
        else:
            self.black_pieces.discard(square)

    def move_piece(self, start_square, end_square, piece):
        '''Moves the piece from start_square to end_square'''
        self.clear_piece(start_square, piece)
        self.set_piece(end_square, piece)

    def load_fen(self, fen):
        '''Sets the state of the board to the given FEN string'''

        # example fen: 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

        # reset board
        self.board = [0] * 64

        self.white_king_square = 0
        self.black_king_square = 0
        
        self.white_pieces = set()
        self.black_pieces = set()
        
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
    
    def generate_moves(self):
        '''Generates all possible moves for the given turn'''
        # key = self.hash_board(turn)
        # if key in self.generated_moves:
        #     return self.generated_moves[key]

        moves = []

        for square in (self.white_pieces if self.white_to_move else self.black_pieces):
            piece = self.board[square]
            piece_type = Piece.get_type(piece)

            match piece_type:
                case Piece.pawn:
                    generate_pawn_moves(self, piece, square, moves)
                case Piece.knight:
                    generate_knight_moves(self, piece, square, moves)
                case Piece.bishop | Piece.rook | Piece.queen:
                    generate_sliding_moves(self, piece, square, moves)
                case Piece.king:
                    generate_king_moves(self, piece, square, moves)

        # self.generated_moves[key] = moves
        return moves

    def make_move(self, move):
        '''Makes the given move on the board'''
        start_square, end_square, start_piece, captured_piece, promotion_piece, castling, en_passant = move

        # save the board for undoing the move
        self.add_to_stack(move)

        # special moves
        if castling:
            self.handle_castling(end_square)
        elif en_passant:
            self.handle_en_passant(end_square, captured_piece)
        # capture (+ promotion capture)
        elif captured_piece:
            self.handle_capture(start_square, end_square, start_piece, captured_piece, promotion_piece)

        # promotion (w/o capture)
        if promotion_piece and not captured_piece:
            self.promote_pawn(start_square, end_square, start_piece, promotion_piece)            

        # normal move
        elif not promotion_piece:
            self.move_piece(start_square, end_square, start_piece)


        # update states
        self.update_castling_rights(start_square, end_square, start_piece, captured_piece)
        self.update_en_passant_target(start_square, end_square, start_piece)
        self.update_halfmove_clock(start_piece, captured_piece)
        self.update_fullmove_number()

        # update turn
        self.white_to_move = not self.white_to_move

    def add_to_stack(self, move):
        '''Adds info needed to undo the move to the undo stack'''
        self.undo_stack.append((
            move,
            self.castling_rights,
            self.en_passant_target_square,
            self.halfmove_clock
        ))

    def handle_castling(self, end_square):
        '''Handles castling moves'''
        if self.white_to_move:
            if end_square == 6:
                self.move_piece(7, 5, Piece.white | Piece.rook)
            elif end_square == 2:
                self.move_piece(0, 3, Piece.white | Piece.rook)
        else:
            if end_square == 62:
                self.move_piece(63, 61, Piece.black | Piece.rook)
            elif end_square == 58:
                self.move_piece(56, 59, Piece.black | Piece.rook)

    def handle_en_passant(self, end_square, captured_piece):
        '''Handles en passant moves'''
        if self.white_to_move:
            self.clear_piece(end_square-8, captured_piece)
        else:
            self.clear_piece(end_square+8, captured_piece)

    def handle_capture(self, start_square, end_square, start_piece, captured_piece, promotion_piece):
        if promotion_piece:
            self.promote_pawn(start_square, end_square, start_piece, promotion_piece)
        else:
            self.clear_piece(end_square, captured_piece)

    def promote_pawn(self, start_square, end_square, start_piece, promotion_piece):
        self.clear_piece(start_square, start_piece)
        self.set_piece(end_square, promotion_piece)

    def update_castling_rights(self, start_square, end_square, start_piece, captured_piece):
        # king move
        if start_piece == Piece.white | Piece.king:
            self.castling_rights &= 0b0011
        elif start_piece == Piece.black | Piece.king:
            self.castling_rights &= 0b1100

        # rook move
        match start_piece:
            case 0:
                self.castling_rights &= 0b1011
            case 7:
                self.castling_rights &= 0b0111

            case 63:
                self.castling_rights &= 0b1101
            case 56:
                self.castling_rights &= 0b1110

        # rook capture
        match captured_piece:
            case 0:
                self.castling_rights &= 0b1011
            case 7:
                self.castling_rights &= 0b0111
        
            case 63:
                self.castling_rights &= 0b1101
            case 56:
                self.castling_rights &= 0b1110
        
    def update_en_passant_target(self, start_square, end_square, start_piece):
        if Piece.get_type(start_piece) == Piece.pawn and abs(start_square - end_square) == 16:
            self.en_passant_target_square = (start_square + end_square) // 2
        else:
            self.en_passant_target_square = 0

    def update_halfmove_clock(self, start_piece, captured_piece):
        if Piece.get_type(start_piece) == Piece.pawn or captured_piece:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1

    def update_fullmove_number(self):
        if not self.white_to_move:
            self.fullmove_number += 1

    def undo_move(self):
        '''Undoes the last move made on the board'''
        # TODO: check if this is faster than copying the board

        move, castling_rights, en_passant_target_square, halfmove_clock = self.undo_stack.pop()

        start_square, end_square, start_piece, captured_piece, promotion_piece, castling, en_passant = move

        self.white_to_move = not self.white_to_move

        if not promotion_piece:
            self.move_piece(end_square, start_square, start_piece)

        # undo special moves
        if castling:
            self.undo_castling(end_square)
        elif en_passant:
            self.undo_en_passant(end_square, captured_piece)
        # capture (+ promotion capture)
        elif captured_piece:
            self.undo_capture(start_square, end_square, start_piece, captured_piece, promotion_piece)

        # promotion (w/o capture)
        elif promotion_piece:
            self.undo_promotion(start_square, end_square, start_piece, promotion_piece)

        # restore board state
        self.castling_rights = castling_rights
        self.en_passant_target_square = en_passant_target_square
        self.halfmove_clock = halfmove_clock
        self.fullmove_number -= 1 if self.white_to_move else 0

    def undo_castling(self, end_square):
        match end_square:
            case 6:
                self.move_piece(5, 7, Piece.white | Piece.rook)
            case 2:
                self.move_piece(3, 0, Piece.white | Piece.rook)

            case 62:
                self.move_piece(61, 63, Piece.black | Piece.rook)
            case 58:
                self.move_piece(59, 56, Piece.black | Piece.rook)

    def undo_en_passant(self, end_square, captured_piece):
        if self.white_to_move:
            self.set_piece(end_square-8, Piece.black | Piece.pawn)
        else:
            self.set_piece(end_square+8, Piece.white | Piece.pawn)

    def undo_capture(self, start_square, end_square, start_piece, captured_piece, promotion_piece):
        if promotion_piece:
            self.undo_promotion(start_square, end_square, start_piece, promotion_piece)
        else:
            self.set_piece(end_square, captured_piece)

    def undo_promotion(self, start_square, end_square, start_piece, promotion_piece):
        self.clear_piece(end_square, promotion_piece)
        self.set_piece(start_square, start_piece)



    def is_check(self, color):
        '''Returns True if the given color is in check, False otherwise'''
        ally_king_square = self.white_king_square if color else self.black_king_square
        ally_king_rank, ally_king_file = divmod(ally_king_square, 8)

        enemy_color = Piece.black if color else Piece.white

        # look at potential knight attacks
        for rank_change, file_change in knight_offsets:
            target_rank = ally_king_rank + rank_change
            target_file = ally_king_file + file_change
            if not is_within_board(target_rank, target_file):
                continue
            if self.get_piece(target_rank * 8 + target_file) == (enemy_color | Piece.knight):
                return True
            
        # look at potential king attacks
        for rank_change, file_change in king_offsets:
            target_rank = ally_king_rank + rank_change
            target_file = ally_king_file + file_change
            if not is_within_board(target_rank, target_file):
                continue
            if self.get_piece(target_rank * 8 + target_file) == (enemy_color | Piece.king):
                return True
            
        # look at potential pawn attacks
        pawn_direction = 1 if color else -1
        for offset in [-1, 1]:
            target_rank = ally_king_rank + pawn_direction
            target_file = ally_king_file + offset
            if not is_within_board(target_rank, target_file):
                continue
            if self.get_piece(target_rank * 8 + target_file) == (enemy_color | Piece.pawn):
                return True
            
        # look at potential rook attacks
        for rank_change, file_change in sliding_offsets[Piece.rook]:
            new_rank, new_file = ally_king_rank + rank_change, ally_king_file + file_change
            while is_within_board(new_rank, new_file):
                target_square = new_rank * 8 + new_file
                target_piece = self.get_piece(target_square)
                if target_piece:
                    if target_piece in [enemy_color | Piece.rook, enemy_color | Piece.queen]:
                        return True
                    break
                new_rank += rank_change
                new_file += file_change

        # look at potential bishop attacks
        for rank_change, file_change in sliding_offsets[Piece.bishop]:
            new_rank, new_file = ally_king_rank + rank_change, ally_king_file + file_change
            while is_within_board(new_rank, new_file):
                target_square = new_rank * 8 + new_file
                target_piece = self.get_piece(target_square)
                if target_piece:
                    if target_piece in [enemy_color | Piece.bishop, enemy_color | Piece.queen]:
                        return True
                    break
                new_rank += rank_change
                new_file += file_change

        return False

    def generate_pawn_attacks(self, piece, square, attack_map):
        color = Piece.get_color(piece)
        move_direction = 1 if color == Piece.white else -1
        start_rank = 1 if color == Piece.white else 6
        promotion_rank = 7 if color == Piece.white else 0

        for offset in [-1, 1]:
            attack_rank = square // 8 + move_direction
            attack_file = square % 8 + offset
            if 0 <= attack_rank < 8 and 0 <= attack_file < 8:
                attack_square = attack_rank * 8 + attack_file
                attack_map[attack_square] += 1

    def generate_knight_attacks(self, square, attack_map):
        knight_offsets = [(2, 1), (1, 2), (-1, 2), (-2, 1), (-2, -1), (-1, -2), (1, -2), (2, -1)]
        self.generate_piece_attacks(square, knight_offsets, attack_map)

    def generate_sliding_attacks(self, piece, square, attack_map):
        directions = {
            Piece.bishop: [(1, 1), (1, -1), (-1, -1), (-1, 1)],
            Piece.rook: [(1, 0), (0, 1), (-1, 0), (0, -1)],
            Piece.queen: [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, -1), (-1, 1)]
        }
        piece_type = Piece.get_type(piece)
        self.generate_piece_attacks(square, directions[piece_type], attack_map, True)

    def generate_king_attacks(self, square, attack_map):
        king_offsets = [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, -1), (-1, 1)]
        self.generate_piece_attacks(square, king_offsets, attack_map)

    def generate_piece_attacks(self, square, offsets, attack_map, is_sliding=False):
        rank, file = divmod(square, 8)
        for rank_change, file_change in offsets:
            new_rank, new_file = rank + rank_change, file + file_change
            while 0 <= new_rank < 8 and 0 <= new_file < 8:
                attack_square = new_rank * 8 + new_file
                attack_map[attack_square] += 1
                if not is_sliding or self.board[attack_square]:
                    break
                new_rank += rank_change
                new_file += file_change

    def generate_attack_map(self, color):
        '''Generates a map of attacked squares for the given color'''
        attack_map = [0] * 64

        for square in (self.white_pieces if color else self.black_pieces):
            piece = self.board[square]
            piece_type = Piece.get_type(piece)

            match piece_type:
                case Piece.pawn:
                    self.generate_pawn_attacks(piece, square, attack_map)
                case Piece.knight:
                    self.generate_knight_attacks(square, attack_map)
                case Piece.bishop | Piece.rook | Piece.queen:
                    self.generate_sliding_attacks(piece, square, attack_map)
                case Piece.king:
                    self.generate_king_attacks(square, attack_map)

        return attack_map
            

    def generate_legal_moves(self):
        '''Optimized legal move generation'''
        pseuo_legal_moves = self.generate_moves()
        # TODO: en passant pinning

        king_square = self.white_king_square if self.white_to_move else self.black_king_square
        king_rank, king_file = divmod(king_square, 8)
        king_color = Piece.white if self.white_to_move else Piece.black
        enem_color = Piece.black if self.white_to_move else Piece.white

        # generate enemy attack map
        enemy_attack_map = self.generate_attack_map(not self.white_to_move)

        # identify pinned pieces and which squares they can move to (between the king and the attacker, including the attacker)
        # [square of pinned piece, square of attacker, [list of squares between the king and the attacker]]
        pins = [] # TODO: pin[1] doesn't seem to be used

        # identify pieces that are attacking the king and squares that will stop the attack
        # sliding pieces -> squares between the king and the attacker
        # knight -> square of the attacker
        # pawn -> square of the attacker
        # [list of squares to stop the attack]
        checks = [] # only used for single check

        # move away from the king and add to the list of pins if you come across an ally piece followed by an enemy piece
        for rank_change, file_change in sliding_offsets[Piece.rook]:
            num_allies = 0
            new_rank, new_file = king_rank + rank_change, king_file + file_change
            while is_within_board(new_rank, new_file):
                target_square = new_rank * 8 + new_file
                target_piece = self.get_piece(target_square)
                if target_piece:
                    target_color = Piece.get_color(target_piece)
                    if target_color == king_color:

                        # if there has already been an ally piece in the path, it is not a pin
                        if num_allies == 1:
                            break

                        num_allies += 1
                        pinned_piece_square = target_square

                    # if the piece is an enemy rook or queen and there is only one ally piece in the path, it is a pin
                    elif Piece.get_type(target_piece) in [Piece.rook, Piece.queen]:
                        enemy_attacker_square = target_square

                        # find the squares between the king and the attacker (including the attacker)
                        blocking_squares = []
                        while target_square != king_square:
                            blocking_squares.append(target_square)
                            # move target_square towards the king
                            target_square -= rank_change * 8 + file_change

                        if num_allies == 1:
                            pins.append((pinned_piece_square, enemy_attacker_square, blocking_squares))
                        elif num_allies == 0:
                            checks = blocking_squares
                        break
                new_rank += rank_change
                new_file += file_change

        for rank_change, file_change in sliding_offsets[Piece.bishop]:
            num_allies = 0
            new_rank, new_file = king_rank + rank_change, king_file + file_change
            while is_within_board(new_rank, new_file):
                target_square = new_rank * 8 + new_file
                target_piece = self.get_piece(target_square)
                if target_piece:
                    target_color = Piece.get_color(target_piece)
                    if target_color == king_color:

                        # if there has already been an ally piece in the path, it is not a pin
                        if num_allies == 1:
                            break

                        num_allies += 1
                        pinned_piece_square = target_square

                    # if the piece is an enemy bishop or queen and there is only one ally piece in the path, it is a pin
                    elif Piece.get_type(target_piece) in [Piece.bishop, Piece.queen]:
                        enemy_attacker_square = target_square

                        # find the squares between the king and the attacker (including the attacker)
                        blocking_squares = []
                        while target_square != king_square:
                            blocking_squares.append(target_square)
                            # move target_square towards the king
                            target_square -= rank_change * 8 + file_change

                        if num_allies == 1:
                            pins.append((pinned_piece_square, enemy_attacker_square, blocking_squares))
                        elif num_allies == 0:
                            checks = blocking_squares
                        break
                new_rank += rank_change
                new_file += file_change

        for rank_change, file_change in knight_offsets:
            new_rank, new_file = king_rank + rank_change, king_file + file_change
            if is_within_board(new_rank, new_file):
                target_square = new_rank * 8 + new_file
                target_piece = self.get_piece(target_square)
                if target_piece == (enem_color | Piece.knight):
                    checks = [target_square]

        pawn_direction = 1 if self.white_to_move else -1
        for offset in [-1, 1]:
            target_square = king_square + pawn_direction * 8 + offset
            if is_within_board(target_square // 8, target_square % 8):
                target_piece = self.get_piece(target_square)
                if target_piece == (enem_color | Piece.pawn):
                    checks = [target_square]
                    break
        

        # if the king is double checked, the only legal moves will be moves that move the king somewhere it is not attacked
        if enemy_attack_map[king_square] > 1:
            legal_moves = []
            for move in pseuo_legal_moves:
                if enemy_attack_map[move[1]] == 0:
                    legal_moves.append(move)
            return legal_moves
        
        # if the king is single checked
        elif enemy_attack_map[king_square] == 1:
            legal_moves = []
            for move in pseuo_legal_moves:
                # move king to a square that is not attacked (king can't castle out of check)
                if move[0] == king_square and enemy_attack_map[move[1]] == 0 and not move[5]:
                    # perform the move and check if the king is still in check
                    # TODO: see if there is a cleaner way to do this
                    self.make_move(move)
                    if not self.is_check(not self.white_to_move):
                        legal_moves.append(move)
                    self.undo_move()
                
                # capture the attacking piece or block the attack
                if move[0] != king_square and move[1] in checks:
                    # if the piece is pinned, it can only move along the pin
                    for pin in pins:
                        if move[0] == pin[0]:
                            if move[1] in pin[2]:
                                legal_moves.append(move)
                            break

                    # if the piece is not pinned, it can block the attack or capture the attacker freely
                    else:
                        legal_moves.append(move)
            return legal_moves


        # if the king is not checked
        legal_moves = []
        for move in pseuo_legal_moves:
            start_square, end_square, start_piece, captured_piece, promotion_piece, castling, en_passant = move

            # if the piece is pinned, it can only move along the pin
            for pin in pins:
                if start_square == pin[0]:
                    if end_square in pin[2]:
                        legal_moves.append(move)
                    break

            # if the piece is not pinned, it can move freely
            else:
                if start_square == king_square:
                    if enemy_attack_map[end_square] == 0:
                        legal_moves.append(move)
                else:
                    legal_moves.append(move)

        return legal_moves
    
    def known_generate_legal_moves(self):
        '''Generates all legal moves for the given turn'''
        pseuo_legal_moves = self.generate_moves()

        legal_moves = []
        for move in pseuo_legal_moves:
            self.make_move(move)
            if not self.is_check(not self.white_to_move):
                legal_moves.append(move)
            self.undo_move()

        return legal_moves
    
    def is_checkmate(self):
        '''Returns True if the current player is in checkmate, False otherwise'''
        return self.is_check(self.white_to_move) and not self.generate_legal_moves()
    
    def is_stalemate(self):
        '''Returns True if the current player is in stalemate, False otherwise'''
        return not self.is_check(self.white_to_move) and not self.generate_legal_moves()
    
    def is_insufficient_material(self):
        '''Returns True if the game is a draw due to insufficient material, False otherwise'''
        if len(self.white_pieces) == 1 and len(self.black_pieces) == 1:
            return True
        
        if len(self.white_pieces) == 2 and len(self.black_pieces) == 1:
            if any(Piece.get_type(piece) in [Piece.bishop, Piece.knight] for piece in self.white_pieces):
                return True
            
        if len(self.white_pieces) == 1 and len(self.black_pieces) == 2:
            if any(Piece.get_type(piece) in [Piece.bishop, Piece.knight] for piece in self.black_pieces):
                return True
            
        return False


    def is_draw(self):
        '''Returns True if the game is a draw, False otherwise'''
        return self.is_stalemate() or self.halfmove_clock >= 50 or self.is_insufficient_material()
    
    def is_game_over(self):
        '''Returns True if the game is over, False otherwise'''
        return self.is_checkmate() or self.is_draw()



def is_within_board(rank, file):
    return 0 <= rank < 8 and 0 <= file < 8






sliding_offsets = {
    Piece.rook: [(0, 1), (1, 0), (0, -1), (-1, 0)],
    Piece.bishop: [(1, 1), (1, -1), (-1, -1), (-1, 1)],
    Piece.queen: [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (1, -1), (-1, -1), (-1, 1)]
    }

def generate_sliding_moves(board: Board, piece, square, moves):
        rank, file = divmod(square, 8)
        color = Piece.get_color(piece)

        for rank_change, file_change in sliding_offsets[Piece.get_type(piece)]:
            new_rank, new_file = rank + rank_change, file + file_change
            while is_within_board(new_rank, new_file):
                target_square = new_rank * 8 + new_file
                target_piece = board.get_piece(target_square)

                # capture or stop if there is a piece on the target square
                if target_piece:
                    if Piece.get_color(target_piece) != color:
                        moves.append((
                            square,             # start
                            target_square,      # end
                            piece,              # start piece
                            target_piece,       # captured piece
                            0, 0, 0))
                    break

                else:
                    moves.append((square, target_square, piece, 0, 0, 0, 0))
                new_rank += rank_change
                new_file += file_change

knight_offsets =   [(-2, -1), (-1, -2), (1, -2), (2, -1), 
                    (2, 1), (1, 2), (-1, 2), (-2, 1)]
def generate_knight_moves(board: Board, piece, square, moves):
        rank, file = divmod(square, 8)
        color = Piece.get_color(piece)

        for rank_change, file_change in knight_offsets:
            new_rank, new_file = rank + rank_change, file + file_change
            if is_within_board(new_rank, new_file):
                target_square = new_rank * 8 + new_file
                target_piece = board.get_piece(target_square)
                if target_piece == 0 or Piece.get_color(target_piece) != color:
                    moves.append((
                        square,         # start
                        target_square,  # end
                        piece,          # start piece
                        target_piece,   # captured piece (0 if empty)
                        0, 0, 0))
        
king_offsets = [(-1, -1), (-1, 0), (-1, 1), (0, -1),
                (0, 1), (1, -1), (1, 0), (1, 1)]
def generate_king_moves(board: Board, piece, square, moves):
        rank, file = divmod(square, 8)
        color = Piece.get_color(piece)

        for offset in king_offsets:
            target_rank = rank + offset[0]
            target_file = file + offset[1]
            if is_within_board(target_rank, target_file):
                target_square = target_rank * 8 + target_file
                if not is_within_board(target_rank, target_file):
                    continue
                target_piece = board.board[target_square]
                if target_piece == 0 or Piece.get_color(target_piece) != color:
                    moves.append((
                        square,         # start
                        target_square,  # end
                        piece,          # start piece
                        target_piece,   # captured piece (0 if empty)
                        0, 0, 0))

        handle_castling_moves(board, piece, moves, color)

def handle_castling_moves(board: Board, piece, moves, color):
    if color == Piece.white:
        check_castling(board, 4, (5, 6), moves, piece, 8)
        check_castling(board, 4, (3, 2, 1), moves, piece, 4)
    else:
        check_castling(board, 60, (61, 62), moves, piece, 2)
        check_castling(board, 60, (59, 58, 57), moves, piece, 1)

def check_castling(board: Board, king_initial, squares, moves, piece, rights_bit):
    if board.castling_rights & rights_bit:
        if all(board.is_empty(sq) for sq in squares):
            end_square = squares[1] # king moves 2 squares
            moves.append((
                king_initial,   # start
                end_square,     # end
                piece,          # start piece
                0,              # captured piece
                0,              # promotion piece
                1,              # castling
                0               # en passant
            ))



pawn_ranks = {
    # (move_direction, start_rank, promotion_rank)
    Piece.white: ( 1, 1, 7),
    Piece.black: (-1, 6, 0)
}

def generate_pawn_moves(board: Board, piece, square, moves):
    color = Piece.get_color(piece)
    move_direction, start_rank, promotion_rank = pawn_ranks[color]
    single_step = square + move_direction * 8
    
    if board.is_empty(single_step):
        handle_pawn_promotion(piece, square, single_step, moves, promotion_rank)
        handle_pawn_double_move(board, piece, square, single_step, move_direction, start_rank, moves)

    handle_pawn_captures(board, piece, square, move_direction, moves, promotion_rank)

def handle_pawn_promotion(piece, start_square, end_square, moves, promotion_rank):
        if end_square // 8 == promotion_rank:
            for promotion_piece in [Piece.knight, Piece.bishop, Piece.rook, Piece.queen]:
                moves.append((
                    start_square,   # start
                    end_square,     # end
                    piece,          # start piece
                    0,              # captured piece
                    promotion_piece | Piece.get_color(piece),   # promotion piece
                    0,0))
        else:
            moves.append((
                start_square,       # start
                end_square,         # end
                piece,              # start piece
                0, 0, 0, 0))
        
def handle_pawn_double_move(board: Board, piece, start_square, single_step, move_direction, start_rank, moves):
    if start_square // 8 == start_rank and board.is_empty(single_step + move_direction * 8):
        moves.append((
            start_square,           # start
            single_step + move_direction * 8,   # end
            piece,                  # start piece
            0, 0, 0, 0))
        
def handle_pawn_captures(board: Board, piece, square, move_direction, moves, promotion_rank):
    for offset in [-1, 1]:
        capture_rank = square // 8 + move_direction
        capture_file = square % 8 + offset
        if not is_within_board(capture_rank, capture_file):
            continue

        capture_square = capture_rank * 8 + capture_file
        if board.get_piece(capture_square) and Piece.get_color(board.get_piece(capture_square)) != Piece.get_color(piece):
            process_capture_or_promotion(board, piece, square, capture_square, moves, promotion_rank)
        elif capture_square == board.en_passant_target_square:
            process_en_passant(board, piece, square, capture_square, moves)

def process_capture_or_promotion(board: Board, piece, start_square, capture_square, moves, promotion_rank):
    captured_piece = board.get_piece(capture_square)
    if capture_square // 8 == promotion_rank:
        for promotion_piece in [Piece.knight, Piece.bishop, Piece.rook, Piece.queen]:
            moves.append((
                start_square,       # start
                capture_square,     # end
                piece,              # start piece
                captured_piece,     # captured piece
                promotion_piece | Piece.get_color(piece),   # promotion piece
                0, 0))
    else:
        moves.append((start_square, capture_square, piece, captured_piece, 0, 0, 0))

def process_en_passant(board: Board, piece, start_square, capture_square, moves):
        moves.append((
            start_square,           # start
            capture_square,         # end
            piece,                  # start piece
            board.get_piece(capture_square),    # captured piece
            0,                      # promotion piece
            0,                      # castling
            1                       # en passant
            ))
