from board import Board, decode_move
import time

PIECE_VALUES = {
    "P": 1,
    "N": 3,
    "B": 3,
    "R": 5,
    "Q": 9,
    "K": 1000,

    "p": -1,
    "n": -3,
    "b": -3,
    "r": -5,
    "q": -9,
    "k": -1000,

    " ": 0
}

LEGAL_SQUARES = [i for i in range(127) if not i & 0x88]

class Engine:
    def __init__(self, board: Board, depth: int = 2):
        print(f"Engine initialized with depth {depth}")
        self.board = board
        self.max_depth = depth

        self.get_color_legal_moves_count = 0
        self.evaluate_board_count = 0
        self.negamax_count = 0

        self.cached_legal_moves = {}

    def get_piece_value(self, piece):
        """
        Get the value of a piece
        """
        return PIECE_VALUES[piece]

    def get_piece_type(self, square):
        """
        Get the type of the piece on a given square
        """
        bitboards = self.board.bitboards
        for piece_type in bitboards:
            if bitboards[piece_type] & (1 << square):
                return piece_type
        return " "

    def get_color_legal_moves(self, color: bool):
        """
        Get all legal moves for a given color
        """
        self.get_color_legal_moves_count += 1
        fen = self.board.board_to_fen() + str(color)
        if fen in self.cached_legal_moves:
            return self.cached_legal_moves[fen]
        
        moves = self.board.generate_legal_moves(color)
        self.cached_legal_moves[fen] = moves
        return moves

    def evaluate_piece_values(self):
        """
        Evaluate the board position based on piece values
        """
        evaluation = 0
        for square in LEGAL_SQUARES:
            piece = self.get_piece_type(square)
            value = self.get_piece_value(piece)
            evaluation += value

        return evaluation

    def evaluate_piece_mobility(self):
        """
        Evaluate the board position based on piece mobility
        """
        white_mobility = len(self.get_color_legal_moves(True))
        black_mobility = len(self.get_color_legal_moves(False))

        factor = 0.1
        evaluation = factor * (white_mobility - black_mobility)
        return evaluation

    def evaluate_check(self):
        """
        Evaluate the board position based on check
        """
        if self.board.is_check(self.board.white_to_move):
            if self.board.white_to_move:
                return -0.5
            else:
                return 0.5
        return 0
    
    def evaluate_pawn_structure(self):
        """
        Evaluate the board position based on pawn structure
        Double pawns, isolated pawns, backward pawns, passed pawns
        """
        evaluation = 0

        double_pawns_disadvantage = -0.5
        isolated_pawns_disadvantage = -0.5
        backward_pawns_disadvantage = -0.5
        passed_pawns_advantage = 0.5

        # double pawns

        # isolated pawns

        # backward pawns

        # passed pawns

    def evaluate_center_control(self):
        """
        Evaluate the board position based on control of the center
        """
        evaluation = 0
        center = [51, 52, 67, 68]
        center_control_advantage = 0.1
        for square in center:
            if self.board.is_white(square):
                evaluation += center_control_advantage
            elif self.board.is_black(square):
                evaluation -= center_control_advantage

        return evaluation

    def evaluate_defending_ally_pieces(self):
        """
        Evaluate the board position based on defending ally pieces
        """
        evaluation = 0
        defending_ally_pieces_advantage = 0.1
        
        white_moves = self.get_color_legal_moves(True)
        black_moves = self.get_color_legal_moves(False)

        for move in white_moves:
            _, end, _, _, _, _ = decode_move(move)
            if self.board.is_white(end):
                evaluation += defending_ally_pieces_advantage

        for move in black_moves:
            _, end, _, _, _, _ = decode_move(move)
            if self.board.is_black(end):
                evaluation -= defending_ally_pieces_advantage
            
        return evaluation

    def evaluate_attacking_enemy_pieces(self):
        """
        Evaluate the board position based on attacking enemy pieces
        """
        evaluation = 0
        attacking_enemy_pieces_advantage = 0.1
        
        white_moves = self.get_color_legal_moves(True)
        black_moves = self.get_color_legal_moves(False)

        for move in white_moves:
            _, _, _, _, _, capture = decode_move(move)
            if capture:
                evaluation += attacking_enemy_pieces_advantage

        for move in black_moves:
            _, _, _, _, _, capture = decode_move(move)
            if capture:
                evaluation -= attacking_enemy_pieces_advantage
            
        return evaluation

    def evaluate_board(self):
        """
        Evaluate the board position
        Negative score means black is winning
        Positive score means white is winning
        """
        self.evaluate_board_count += 1
        # checkmate

        if self.board.is_checkmate(True):
            return -10000
        elif self.board.is_checkmate(False):
            return 10000
            
        # draw
        if self.board.is_draw():
            return 0

        evaluation = 0

        # material evaluation
        evaluation += self.evaluate_piece_values()

        # mobility evaluation
        evaluation += self.evaluate_piece_mobility()

        # check evaluation
        evaluation += self.evaluate_check()

        # pawn structure evaluation TODO: implement
        # evaluation += self.evaluate_pawn_structure()

        # defending the center evaluation
        evaluation += self.evaluate_center_control()

        # defending ally pieces evaluation
        evaluation += self.evaluate_defending_ally_pieces()

        # attacking enemy pieces evaluation
        evaluation += self.evaluate_attacking_enemy_pieces()

        return evaluation
    
    def negamax(self, depth, alpha, beta):
        """
        Negamax algorithm with alpha-beta pruning
        """
        self.negamax_count += 1
        if depth == 0:
            return self.evaluate_board()

        max_score = -10000
        for move in self.get_color_legal_moves(self.board.white_to_move):
            self.board.make_move(move)
            score = -self.negamax(depth - 1, -beta, -alpha)
            self.board.undo_move()

            if score >= beta:
                return score
            if score > max_score:
                max_score = score
            if score > alpha:
                alpha = score
        return max_score
        
    
    def get_best_move(self):
        """
        Get the best move for the current position
        """
        start = time.time()
        best_move = None
        max_score = -10000
        for move in self.get_color_legal_moves(self.board.white_to_move):
            self.board.make_move(move)
            score = -self.negamax(self.max_depth - 1, -10000, 10000)
            self.board.undo_move()

            if score > max_score:
                max_score = score
                best_move = move
        
        print(f"get_color_legal_moves_count: {self.get_color_legal_moves_count}\nevaluate_board_count: {self.evaluate_board_count}\nnegamax_count: {self.negamax_count}")
        print(f"Time taken: {time.time() - start}")
        return best_move