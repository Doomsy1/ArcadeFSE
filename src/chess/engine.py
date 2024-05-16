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

# Evaluation factors
MOBILITY_FACTOR = 0.2
CHECK_SCORE = 0.75
DOUBLE_PAWNS_DISADVANTAGE = -0.75
ISOLATED_PAWNS_DISADVANTAGE = -0.75
BACKWARD_PAWNS_DISADVANTAGE = -0.5
PASSED_PAWNS_ADVANTAGE = 1.2
CENTER_CONTROL_ADVANTAGE = 0.4
DEFENDING_ALLY_PIECES_ADVANTAGE = 0.5
ATTACKING_ENEMY_PIECES_ADVANTAGE = 0.5


LEGAL_SQUARES = [i for i in range(127) if not i & 0x88]

class Engine:
    def __init__(self, board: Board, depth: int = 2, time_limit: int = 5):
        print(f"Engine initialized with depth {depth}")
        self.board = board
        self.max_depth = depth
        self.time_limit = time_limit

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
        # fen = self.board.board_to_fen() + str(color)
        # if fen in self.cached_legal_moves:
        #     return self.cached_legal_moves[fen]
        
        self.get_color_legal_moves_count += 1
        moves = self.board.generate_legal_moves(color)
        # self.cached_legal_moves[fen] = moves
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

        evaluation = MOBILITY_FACTOR * (white_mobility - black_mobility)
        return evaluation

    def evaluate_check(self):
        """
        Evaluate the board position based on check
        """
        if self.board.is_check(self.board.white_to_move):
            if self.board.white_to_move:
                return -CHECK_SCORE
            else:
                return CHECK_SCORE
        return 0
    
    def evaluate_pawn_structure(self):
        """
        Evaluate the board position based on pawn structure
        Double pawns, isolated pawns, backward pawns, passed pawns
        """
        evaluation = 0

        # Double pawns
        evaluation += self.evaluate_double_pawns(DOUBLE_PAWNS_DISADVANTAGE)

        # Isolated pawns
        evaluation += self.evaluate_isolated_pawns(ISOLATED_PAWNS_DISADVANTAGE)

        # Backward pawns
        evaluation += self.evaluate_backward_pawns(BACKWARD_PAWNS_DISADVANTAGE)

        # Passed pawns
        evaluation += self.evaluate_passed_pawns(PASSED_PAWNS_ADVANTAGE)

        return evaluation

    def evaluate_double_pawns(self, penalty):
        """
        Evaluate double pawns on the board
        """
        evaluation = 0
        for file in range(8):
            white_pawns = sum(1 for rank in range(8) if self.get_piece_type(file + rank * 16) == 'P')
            black_pawns = sum(1 for rank in range(8) if self.get_piece_type(file + rank * 16) == 'p')
            if white_pawns > 1:
                evaluation += penalty
            if black_pawns > 1:
                evaluation -= penalty
        return evaluation

    def evaluate_isolated_pawns(self, penalty):
        """
        Evaluate isolated pawns on the board
        """
        evaluation = 0
        for file in range(8):
            for rank in range(8):
                square = file + rank * 16
                piece = self.get_piece_type(square)
                if piece == 'P':
                    if not any(self.get_piece_type(f + rank * 16) == 'P' for f in (file-1, file+1) if 0 <= f < 8):
                        evaluation += penalty
                elif piece == 'p':
                    if not any(self.get_piece_type(f + rank * 16) == 'p' for f in (file-1, file+1) if 0 <= f < 8):
                        evaluation -= penalty
        return evaluation

    def evaluate_backward_pawns(self, penalty):
        """
        Evaluate backward pawns on the board
        """
        evaluation = 0
        for file in range(8):
            for rank in range(8):
                square = file + rank * 16
                piece = self.get_piece_type(square)
                if piece == 'P':
                    if self.is_backward_pawn(square, 'P'):
                        evaluation += penalty
                elif piece == 'p':
                    if self.is_backward_pawn(square, 'p'):
                        evaluation -= penalty
        return evaluation

    def is_backward_pawn(self, square, pawn):
        """
        Determine if a pawn is backward
        """
        file = square % 16
        rank = square // 16
        if pawn == 'P':
            for r in range(rank + 1, 8):
                if self.get_piece_type(file + r * 16) == 'P':
                    return False
            for f in (file - 1, file + 1):
                if 0 <= f < 8:
                    for r in range(rank + 1, 8):
                        if self.get_piece_type(f + r * 16) == 'P':
                            return False
        else:
            for r in range(rank - 1, -1, -1):
                if self.get_piece_type(file + r * 16) == 'p':
                    return False
            for f in (file - 1, file + 1):
                if 0 <= f < 8:
                    for r in range(rank - 1, -1, -1):
                        if self.get_piece_type(f + r * 16) == 'p':
                            return False
        return True

    def evaluate_passed_pawns(self, advantage):
        """
        Evaluate passed pawns on the board
        """
        evaluation = 0
        for file in range(8):
            for rank in range(8):
                square = file + rank * 16
                piece = self.get_piece_type(square)
                if piece == 'P':
                    if self.is_passed_pawn(square, 'P'):
                        evaluation += advantage
                elif piece == 'p':
                    if self.is_passed_pawn(square, 'p'):
                        evaluation -= advantage
        return evaluation

    def is_passed_pawn(self, square, pawn):
        """
        Determine if a pawn is passed
        """
        file = square % 16
        rank = square // 16
        if pawn == 'P':
            for r in range(rank + 1, 8):
                if self.get_piece_type(file + r * 16) == 'p':
                    return False
            for f in (file - 1, file + 1):
                if 0 <= f < 8:
                    for r in range(rank + 1, 8):
                        if self.get_piece_type(f + r * 16) == 'p':
                            return False
        else:
            for r in range(rank - 1, -1, -1):
                if self.get_piece_type(file + r * 16) == 'P':
                    return False
            for f in (file - 1, file + 1):
                if 0 <= f < 8:
                    for r in range(rank - 1, -1, -1):
                        if self.get_piece_type(f + r * 16) == 'P':
                            return False
        return True

    def evaluate_center_control(self):
        """
        Evaluate the board position based on control of the center
        """
        evaluation = 0
        center = [51, 52, 67, 68]
        for square in center:
            if self.board.is_white(square):
                evaluation += CENTER_CONTROL_ADVANTAGE
            elif self.board.is_black(square):
                evaluation -= CENTER_CONTROL_ADVANTAGE

        return evaluation

    def evaluate_defending_ally_pieces(self):
        """
        Evaluate the board position based on defending ally pieces
        """
        evaluation = 0
        
        white_moves = self.get_color_legal_moves(True)
        black_moves = self.get_color_legal_moves(False)

        for move in white_moves:
            _, end, _, _, _, _ = decode_move(move)
            if self.board.is_white(end):
                evaluation += DEFENDING_ALLY_PIECES_ADVANTAGE

        for move in black_moves:
            _, end, _, _, _, _ = decode_move(move)
            if self.board.is_black(end):
                evaluation -= DEFENDING_ALLY_PIECES_ADVANTAGE
            
        return evaluation

    def evaluate_attacking_enemy_pieces(self):
        """
        Evaluate the board position based on attacking enemy pieces
        """
        evaluation = 0
        
        white_moves = self.get_color_legal_moves(True)
        black_moves = self.get_color_legal_moves(False)

        for move in white_moves:
            _, _, _, _, _, capture = decode_move(move)
            if capture:
                evaluation += ATTACKING_ENEMY_PIECES_ADVANTAGE

        for move in black_moves:
            _, _, _, _, _, capture = decode_move(move)
            if capture:
                evaluation -= ATTACKING_ENEMY_PIECES_ADVANTAGE
            
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
            return -100000
        elif self.board.is_checkmate(False):
            return 100000
            
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

        # pawn structure evaluation
        evaluation += self.evaluate_pawn_structure()

        # defending the center evaluation
        evaluation += self.evaluate_center_control()

        # defending ally pieces evaluation
        evaluation += self.evaluate_defending_ally_pieces()

        # attacking enemy pieces evaluation
        evaluation += self.evaluate_attacking_enemy_pieces()

        return evaluation
    

    def iterative_deepening(self, max_depth, time_limit=None):
        best_move = None
        start_time = time.time()

        depth_reached = 0
        for depth in range(1, max_depth + 1):
            if time_limit and (time.time() - start_time) > time_limit:
                depth_reached = depth - 1
                print(f"Depth reached: {depth_reached}")
                break
            best_move = self.negamax_root(depth)

        return best_move

    def negamax_root(self, depth):
        best_move = None
        max_score = -float('inf')

        for move in self.get_color_legal_moves(self.board.white_to_move):
            self.board.make_move(move)
            score = -self.negamax(depth - 1, -float('inf'), float('inf'))
            self.board.undo_move()

            if score > max_score:
                max_score = score
                best_move = move

        return best_move

    def null_move_pruning(self, depth, beta):
        """
        Perform null-move pruning.
        """
        self.board.make_null_move()
        score = -self.negamax(depth - 1 - 2, -beta, -beta + 1)
        self.board.undo_null_move()

        return score

    def negamax(self, depth, alpha, beta):
        """
        Negamax algorithm with alpha-beta pruning and null-move pruning.
        """
        self.negamax_count += 1
        if depth == 0:
            return self.evaluate_board()

        if depth > 2 and not self.board.is_check(True) and not self.board.is_check(False):
            score = self.null_move_pruning(depth, beta)
            if score >= beta:
                return beta

        max_score = -100000
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
        start_time = time.time()
        
        best_move = self.iterative_deepening(self.max_depth, self.time_limit)
        
        print(f"get_color_legal_moves_count: {self.get_color_legal_moves_count}\nevaluate_board_count: {self.evaluate_board_count}\nnegamax_count: {self.negamax_count}")
        print(f"Time taken: {time.time() - start_time}")
        return best_move
    


import cProfile
import pstats
import io

def profile_code():
    profiler = cProfile.Profile()
    profiler.enable()

    board = Board()
    
    # Run the part of the code you want to profile
    engine = Engine(board, depth=2)  # Assuming `board` is already defined
    best_move = engine.get_best_move()
    
    profiler.disable()
    
    # Print profiling results
    stream = io.StringIO()
    stats = pstats.Stats(profiler, stream=stream)
    stats.sort_stats(pstats.SortKey.CUMULATIVE)
    stats.print_stats()
    print(stream.getvalue())

if __name__ == "__main__":
    profile_code()