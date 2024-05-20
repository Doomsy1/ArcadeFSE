from src.chess.board import Board, decode_move
import time

# a positive evaluation of a position means white is winning
# a negative evaluation of a position means black is winning

PIECE_VALUES = {
    0b1001: 1, # white pawn
    0b1010: 3, # white knight
    0b1011: 3, # white bishop
    0b1100: 5, # white rook
    0b1101: 9, # white queen
    0b1110: 100, # white king

    0b0001: -1, # black pawn
    0b0010: -3, # black knight
    0b0011: -3, # black bishop
    0b0100: -5, # black rook
    0b0101: -9, # black queen
    0b0110: -100, # black king
}

# Evaluation factors
MOBILITY_FACTOR = 0.2
CHECK_SCORE = 0.75
DOUBLE_PAWNS_DISADVANTAGE = -0.75
ISOLATED_PAWNS_DISADVANTAGE = -0.75
BACKWARD_PAWNS_DISADVANTAGE = -0.5
PASSED_PAWNS_ADVANTAGE = 1.2
CENTER_CONTROL_ADVANTAGE = 0.4
# DEFENDING_ALLY_PIECES_ADVANTAGE = 0.5 | my generate move function doesn't create moves that defend pieces TODO: implement this
ATTACKING_ENEMY_PIECES_ADVANTAGE = 0.5

LEGAL_SQUARES = [i for i in range(127) if not i & 0x88]

POSITIVE_INFINITY = float('inf')
NEGATIVE_INFINITY = float('-inf')

class Engine:
    def __init__(self, board: Board, depth: int = 2, time_limit_ms: int = 1000):
        self.board = board
        self.depth = depth
        self.time_limit_ms = time_limit_ms

    def evaluate_piece_values(self):
        piece_value_evaluation = 0
        for piece, bitboard in self.board.piece_bitboards.items():
            piece_value_evaluation += PIECE_VALUES[piece] * bin(bitboard).count("1")
        return piece_value_evaluation
    
    def evaluate_mobility(self):
        mobility_evaluation = 0
        white_moves = self.board.generate_legal_moves(True)
        black_moves = self.board.generate_legal_moves(False)

        mobility_evaluation += (len(white_moves) - len(black_moves)) * MOBILITY_FACTOR

        return mobility_evaluation
    
    def evaluate_board(self):
        evaluation = 0
        evaluation += self.evaluate_piece_values()
        evaluation += self.evaluate_mobility()
        return evaluation
    

    def minimax(self, depth, alpha, beta, maximizing_player):
        '''
        Minimax algorithm with alpha-beta pruning
        '''
        if depth == 0 or self.board.is_game_over():
            return self.evaluate_board()
        
        if maximizing_player:
            max_eval = NEGATIVE_INFINITY
            for move in self.board.generate_legal_moves(True):
                self.board.make_move(move)
                eval = self.minimax(depth - 1, alpha, beta, False)
                self.board.undo_move()
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        
        else:
            min_eval = POSITIVE_INFINITY
            for move in self.board.generate_legal_moves(False):
                self.board.make_move(move)
                eval = self.minimax(depth - 1, alpha, beta, True)
                self.board.undo_move()
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval
        
    def find_best_move(self):
        '''
        Find the best move using minimax
        '''
        best_move = 0
        best_score = NEGATIVE_INFINITY
        alpha = NEGATIVE_INFINITY
        beta = POSITIVE_INFINITY
        
        for move in self.board.generate_legal_moves(True):
            self.board.make_move(move)
            score = self.minimax(self.depth - 1, -beta, -alpha, False)
            self.board.undo_move()
            
            if score > best_score:
                best_score = score
                best_move = move
            
            alpha = max(alpha, score)
        
        return best_move, best_score
    