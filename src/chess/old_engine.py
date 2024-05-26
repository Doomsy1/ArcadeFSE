from src.chess.board import Board, Piece
import chess.PSQT as PSQT
from random import uniform

import time

# import PSQT
# from board import Board, Piece

# a positive evaluation of a position means white is winning
# a negative evaluation of a position means black is winning

PIECE_VALUES = {
    Piece.white | Piece.pawn: 100,
    Piece.white | Piece.knight: 300,
    Piece.white | Piece.bishop: 300,
    Piece.white | Piece.rook: 500,
    Piece.white | Piece.queen: 900,
    Piece.white | Piece.king: 10000,

    Piece.black | Piece.pawn: -100,
    Piece.black | Piece.knight: -300,
    Piece.black | Piece.bishop: -300,
    Piece.black | Piece.rook: -500,
    Piece.black | Piece.queen: -900,
    Piece.black | Piece.king: -10000
}

# Evaluation factors
MOBILITY_FACTOR = 0.2
CHECK_SCORE = 0.75
DOUBLE_PAWNS_DISADVANTAGE = -0.75
ISOLATED_PAWNS_DISADVANTAGE = -0.6 # down from -0.75
BACKWARD_PAWNS_DISADVANTAGE = -0.5
PASSED_PAWNS_ADVANTAGE = 1.2
CENTER_CONTROL_ADVANTAGE = 0.3 # | down from 0.4
# DEFENDING_ALLY_PIECES_ADVANTAGE = 0.5 | my generate move function doesn't create moves that defend pieces TODO: implement this
ATTACKING_ENEMY_PIECES_ADVANTAGE = 0.35 # | down from 0.5
KING_SAFETY_ADVANTAGE = 0.5
DEVELOPMENT_ADVANTAGE = 0.5

POSITIVE_INFINITY = float('inf')
NEGATIVE_INFINITY = float('-inf')

PHASE_WEIGHTS = {
    Piece.pawn: 0,
    Piece.knight: 1,
    Piece.bishop: 1,
    Piece.rook: 2,
    Piece.queen: 4,
    Piece.king: 0 
}

TOTAL_PHASE = (8 * PHASE_WEIGHTS[Piece.pawn] +
               2 * PHASE_WEIGHTS[Piece.knight] +
               2 * PHASE_WEIGHTS[Piece.bishop] +
               2 * PHASE_WEIGHTS[Piece.rook] +
               1 * PHASE_WEIGHTS[Piece.queen])

class Engine:
    def __init__(self, board: Board, depth: int = 20, time_limit_ms: int = 5000):
        self.board = board.__copy__()
        self.depth = depth
        self.time_limit_ms = time_limit_ms

        self.evaluated_boards = {}
        self.start_time = 0

    def update_board(self, board: Board):
        self.board.board = board.board.copy()

        self.board.white_king_square = board.white_king_square
        self.board.black_king_square = board.black_king_square

        self.board.white_pieces = board.white_pieces.copy()
        self.board.black_pieces = board.black_pieces.copy()

        self.board.white_attacked_squares = board.white_attacked_squares.copy()
        self.board.black_attacked_squares = board.black_attacked_squares.copy()

        self.board.white_to_move = board.white_to_move
        self.board.castling_rights =  board.castling_rights
        self.board.en_passant_target_square = board.en_passant_target_square
        self.board.halfmove_clock = board.halfmove_clock
        self.board.fullmove_number = board.fullmove_number
        self.board.undo_list = board.undo_list.copy()

    def evaluate_piece_values(self):
        piece_value_evaluation = 0
        for square in self.board.white_pieces + self.board.black_pieces:
            piece_value_evaluation += PIECE_VALUES[self.board.get_piece(square)]

        return piece_value_evaluation
    
    def calculate_phase(self):
        current_phase = TOTAL_PHASE

        # subtract the weights of pieces on the board
        for square in self.board.white_pieces + self.board.black_pieces:
            piece = self.board.get_piece(square)
            piece_type = piece & 7
            current_phase -= PHASE_WEIGHTS[piece_type]

        phase = current_phase / TOTAL_PHASE
        return phase
    
    def get_piece_square_table_value(self, piece, square, phase):
        rank = square // 8
        file = square % 8
        opening_value = PSQT.PST_OPENING[piece][rank][file]
        endgame_value = PSQT.PST_ENDGAME[piece][rank][file]
        return (opening_value * (1 - phase)) + (endgame_value * phase)
    
    def evaluate_piece_square_tables(self):
        phase = self.calculate_phase()

        psqt_evaluation = 0
        for square in self.board.white_pieces + self.board.black_pieces:
            piece = self.board.get_piece(square)
            psqt_evaluation += self.get_piece_square_table_value(piece, square, phase)

        return psqt_evaluation


        
        

        
    def evaluate_board(self):
        key = self.board.hash_board(self.board.white_to_move)
        if key in self.evaluated_boards:
            return self.evaluated_boards[key]

        if self.board.is_checkmate(True):
            self.evaluated_boards[key] = NEGATIVE_INFINITY
            return NEGATIVE_INFINITY
        
        if self.board.is_checkmate(False):
            self.evaluated_boards[key] = POSITIVE_INFINITY
            return POSITIVE_INFINITY
        
        evaluation = 0
        evaluation += self.evaluate_piece_values()
        # evaluation += self.evaluate_mobility() # | VERY SLOW
        # evaluation += self.evaluate_check()
        # evaluation += self.evaluate_center_control()
        # evaluation += self.evaluate_attack() # | VERY SLOW
        evaluation += self.evaluate_piece_square_tables()
        # evaluation += self.evaluate_development()

        # add some randomness to the evaluation
        evaluation += uniform(-0.01, 0.01) 

        self.evaluated_boards[key] = evaluation
        return evaluation










    def time_exceeded(self):
        return (time.time() - self.start_time) * 1000 >= self.time_limit_ms
    
    def quiescence_search(self, alpha, beta):
        # TOFIX: the engine is not returning the best move
        stand_pat = self.evaluate_board()
        if stand_pat >= beta:
            return beta
        if alpha < stand_pat:
            alpha = stand_pat

        for move in self.board.generate_legal_moves(self.board.white_to_move):
            if move[3]:
                self.board.make_move(move)
                score = -self.quiescence_search(-beta, -alpha)
                self.board.undo_move()

                if score >= beta:
                    return beta
                if score > alpha:
                    alpha = score

        return alpha

    def minimax(self, depth, alpha, beta):
        # TOFIX: the engine is not returning the best move
        if depth == 0 or self.board.is_game_over() or self.time_exceeded():
            return self.quiescence_search(alpha, beta)
        
        if self.board.white_to_move:
            best_eval = NEGATIVE_INFINITY
            for move in self.board.generate_legal_moves(True):
                self.board.make_move(move)
                eval = self.minimax(depth - 1, alpha, beta)
                self.board.undo_move()
                best_eval = max(best_eval, eval)
                alpha = max(alpha, best_eval)
                if beta <= alpha or self.time_exceeded():
                    break

        else:
            best_eval = POSITIVE_INFINITY
            for move in self.board.generate_legal_moves(False):
                self.board.make_move(move)
                eval = self.minimax(depth - 1, alpha, beta)
                self.board.undo_move()
                best_eval = min(best_eval, eval)
                beta = min(beta, best_eval)
                if beta <= alpha or self.time_exceeded():
                    break

        return best_eval

    def find_best_move(self, result_container):
        # TOFIX: the engine is not returning the best move

        self.start_time = time.time()
        starting_player = self.board.white_to_move
        best_move = None
        best_eval = NEGATIVE_INFINITY if starting_player else POSITIVE_INFINITY

        alpha = NEGATIVE_INFINITY
        beta = POSITIVE_INFINITY

        for current_depth in range(1, self.depth + 1):
            if self.time_exceeded():
                break
            
            current_best_move = None
            current_best_eval = NEGATIVE_INFINITY if starting_player else POSITIVE_INFINITY

            if starting_player: # white 
                for move in self.board.generate_legal_moves(True):
                    self.board.make_move(move)
                    eval = self.minimax(current_depth - 1, alpha, beta)
                    self.board.undo_move()
                    if eval > current_best_eval:
                        current_best_eval = eval
                        current_best_move = move
                    alpha = max(alpha, current_best_eval)

            else: # black
                for move in self.board.generate_legal_moves(False):
                    self.board.make_move(move)
                    eval = self.minimax(current_depth - 1, alpha, beta)
                    self.board.undo_move()
                    if eval < current_best_eval:
                        current_best_eval = eval
                        current_best_move = move
                    beta = min(beta, current_best_eval)
            
            if not self.time_exceeded():
                best_move = current_best_move
                best_eval = current_best_eval
                print(f'Best move at depth {current_depth}: {best_move} with evaluation {best_eval}')
                result_container.append((best_move, best_eval, False)) # false means the search was not completed and the move should not be made

        print(f'Best move: {best_move} with evaluation {best_eval}')
        result_container.append((best_move, best_eval, True)) # true means the search was completed and the move can be made


if __name__ == '__main__':
    import cProfile
    import pstats
    import csv

    board = Board()
    # board.load_fen('rnbqkbnr/ppppp2p/5p2/6p1/4PP2/8/PPPP2PP/RNBQKBNR w - - 0 1')
    # board.make_move(encode_move(3, 71, 0b1101))
    # board.load_fen('rnbqkbnr/ppppp2p/5p2/6pQ/4PP2/8/PPPP2PP/RNB1KBNR b - - 0 1')
    engine = Engine(board, depth=4)

    # engine.find_best_move()
    container = []

    profiler = cProfile.Profile()
    profiler.enable()
    engine.find_best_move(container)
    # print(engine.evaluate_board())
    # print(board.is_game_over())
    profiler.disable()
    print(container)

    stats = pstats.Stats(profiler)

    stats.sort_stats(pstats.SortKey.CUMULATIVE)

    profiling_data = []
    stats_data = stats.stats
    for func, (cc, nc, tt, ct, callers) in stats_data.items():
        filename, lineno, funcname = func
        profiling_data.append({
            'filename': filename,
            'line_number': lineno,
            'function_name': funcname,
            'call_count': cc,
            'recursive_call_count': nc,
            'total_time': tt,
            'cumulative_time': ct
        })

    csv_filename = 'profiling_results.csv'

    with open(csv_filename, mode='w', newline='') as csv_file:
        fieldnames = ['filename', 'line_number', 'function_name', 'call_count', 'recursive_call_count', 'total_time', 'cumulative_time']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()
        for data in profiling_data:
            writer.writerow(data)