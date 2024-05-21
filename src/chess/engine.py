from src.chess.board import Board, decode_move
import time
# from board import Board, decode_move, encode_move

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
# CENTER_CONTROL_ADVANTAGE = 0.4
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
        if self.board.is_checkmate(True):
            return NEGATIVE_INFINITY
        if self.board.is_checkmate(False):
            return POSITIVE_INFINITY
        
        evaluation = 0
        evaluation += self.evaluate_piece_values()
        evaluation += self.evaluate_mobility()
        return evaluation 
    

    def minimax(self, depth):
        if depth == 0 or self.board.is_game_over():
            return self.evaluate_board()
        
        if self.board.white_to_move:
            best_eval = NEGATIVE_INFINITY
            for move in self.board.generate_legal_moves(True):
                self.board.make_move(move)
                eval = self.minimax(depth - 1)
                self.board.undo_move()
                best_eval = max(best_eval, eval)

        else:
            best_eval = POSITIVE_INFINITY
            for move in self.board.generate_legal_moves(False):
                self.board.make_move(move)
                eval = self.minimax(depth - 1)
                self.board.undo_move()
                best_eval = min(best_eval, eval)


    def find_best_move(self):
        start_time = time.time()
        starting_player = self.board.white_to_move
        best_move = None

        if starting_player: # white 
            best_eval = NEGATIVE_INFINITY
            for move in self.board.generate_legal_moves(True):
                self.board.make_move(move)
                eval = self.minimax(self.depth - 1)
                self.board.undo_move()
                if eval > best_eval:
                    best_eval = eval
                    best_move = move
        else: # black
            best_eval = POSITIVE_INFINITY
            for move in self.board.generate_legal_moves(False):
                self.board.make_move(move)
                eval = self.minimax(self.depth - 1)
                self.board.undo_move()
                if eval < best_eval:
                    best_eval = eval
                    best_move = move

        print(f"Best move: {decode_move(best_move)}")
        print(f"Time taken: {time.time() - start_time} seconds")
        return best_move, best_eval


if __name__ == '__main__':
    import cProfile
    import pstats
    import csv

    board = Board()
    board.load_fen('rnbqkbnr/ppppp2p/5p2/6p1/4PP2/8/PPPP2PP/RNBQKBNR w - - 0 1')
    # board.make_move(encode_move(3, 71, 0b1101))
    # board.load_fen('rnbqkbnr/ppppp2p/5p2/6pQ/4PP2/8/PPPP2PP/RNB1KBNR b - - 0 1')
    engine = Engine(board, depth=3)

    profiler = cProfile.Profile()
    profiler.enable()
    engine.find_best_move()
    # print(engine.evaluate_board())
    # print(board.is_game_over())
    profiler.disable()

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