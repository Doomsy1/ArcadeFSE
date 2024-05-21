from src.chess.board import Board, decode_move
import src.chess.PSQT as PSQT

import time

# import PSQT
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
ISOLATED_PAWNS_DISADVANTAGE = -0.6 # down from -0.75
BACKWARD_PAWNS_DISADVANTAGE = -0.5
PASSED_PAWNS_ADVANTAGE = 1.2
CENTER_CONTROL_ADVANTAGE = 0.3 # | down from 0.4
# DEFENDING_ALLY_PIECES_ADVANTAGE = 0.5 | my generate move function doesn't create moves that defend pieces TODO: implement this
ATTACKING_ENEMY_PIECES_ADVANTAGE = 0.35 # | down from 0.5
KING_SAFETY_ADVANTAGE = 0.5
DEVELOPMENT_ADVANTAGE = 0.5


LEGAL_SQUARES = [i for i in range(127) if not i & 0x88]
CENTRAL_LEGAL_SQUARES = [i for i in LEGAL_SQUARES if 3 <= i // 16 <= 6]
CENTER_SQUARES = [51, 52, 67, 68]

POSITIVE_INFINITY = float('inf')
NEGATIVE_INFINITY = float('-inf')

FILE_MASKS = [0x0101010101010101 << i for i in range(8)]

piece_map = {
    'white': {
        'pawn': (0b1001, PSQT.white_pawn),
        'knight': (0b1010, PSQT.white_knight),
        'bishop': (0b1011, PSQT.white_bishop),
        'rook': (0b1100, PSQT.white_rook),
        'queen': (0b1101, PSQT.white_queen),
        'king': (0b1110, PSQT.white_king),
    },
    'black': {
        'pawn': (0b0001, PSQT.black_pawn),
        'knight': (0b0010, PSQT.black_knight),
        'bishop': (0b0011, PSQT.black_bishop),
        'rook': (0b0100, PSQT.black_rook),
        'queen': (0b0101, PSQT.black_queen),
        'king': (0b0110, PSQT.black_king),
    }
}

class Engine:
    def __init__(self, board: Board, depth: int = 2, time_limit_ms: int = 1000):
        self.board = board.__copy__()
        self.depth = depth
        self.time_limit_ms = time_limit_ms

        self.evaluated_boards = {}

    def update_board(self, board: Board):
        self.board = board.__copy__()

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
    
    def evaluate_double_pawns(self): # pawns on the same file
        '''If the player has double pawns, the position is worse'''
        evaluation = 0
        white_pawns = self.board.piece_bitboards[0b1001]
        black_pawns = self.board.piece_bitboards[0b0001]

        for i in range(8):
            if bin(white_pawns & FILE_MASKS[i]).count("1") > 1:
                evaluation += DOUBLE_PAWNS_DISADVANTAGE
            if bin(black_pawns & FILE_MASKS[i]).count("1") > 1:
                evaluation -= DOUBLE_PAWNS_DISADVANTAGE

        return evaluation

    def evaluate_isolated_pawns(self): # pawns with no pawns on adjacent files
        '''If the player has isolated pawns, the position is worse'''
        evaluation = 0
        white_pawns = self.board.piece_bitboards[0b1001]
        black_pawns = self.board.piece_bitboards[0b0001]

        for i in range(8):
            left_mask = FILE_MASKS[i-1] if i > 0 else 0
            right_mask = FILE_MASKS[i+1] if i < 7 else 0

            if bin(white_pawns & FILE_MASKS[i] & (left_mask | right_mask)).count("1") == 0:
                evaluation += ISOLATED_PAWNS_DISADVANTAGE

            if bin(black_pawns & FILE_MASKS[i] & (left_mask | right_mask)).count("1") == 0:
                evaluation -= ISOLATED_PAWNS_DISADVANTAGE

        return evaluation

    def evaluate_backward_pawns(self): # pawns that are behind all pawns on adjacent files
        pass

    def evaluate_passed_pawns(self): # pawns that have no enemy pawns on adjacent files and are not blocked by enemy pawns
        pass

    def evaluate_center_control(self): # control of the center of the board (pieces on the center squares + pieces that attack the center squares)
        '''If the player controls the center, the position is better'''
        white_center_control = 0
        black_center_control = 0

        for square in CENTER_SQUARES:
            if self.board.is_piece(square):
                if self.board.is_white(square):
                    white_center_control += 1
                else:
                    black_center_control += 1


        return (white_center_control - black_center_control) * CENTER_CONTROL_ADVANTAGE

    def evaluate_check(self): # checking the opponent
        '''If the opponent is in check, the position is better'''
        if self.board.is_check(True):
            return CHECK_SCORE
        if self.board.is_check(False):
            return -CHECK_SCORE
        return 0

    def evaluate_attack(self): # attacking the opponent's pieces
        '''If the player is attacking the opponent's pieces, the position is better'''
        white_moves = self.board.generate_legal_moves(True)
        black_moves = self.board.generate_legal_moves(False)

        white_attacks = 0
        for move in white_moves:
            _, _, _, attacked_piece, _, _, _, _ = decode_move(move)
            if attacked_piece:
                white_attacks += 1

        black_attacks = 0
        for move in black_moves:
            _, _, _, attacked_piece, _, _, _, _ = decode_move(move)
            if attacked_piece:
                black_attacks += 1

        return (white_attacks - black_attacks) * ATTACKING_ENEMY_PIECES_ADVANTAGE

    def evaluate_defense(self): # defending own pieces
        pass #

    def evaluate_king_safety(self): # how safe the king is
        pass #

    def evaluate_piece_square_tables(self):
        '''If the player's pieces are on good squares, the position is better'''
        evaluation = 0

        for color, pieces in piece_map.items():
            for piece, (bitboard_index, psqt) in pieces.items():
                bitboard = self.board.piece_bitboards[bitboard_index]
                for file in range(8):
                    for rank in range(8):
                        if bitboard & (1 << (file + rank * 16)):
                            if color == 'white':
                                evaluation += psqt[7 - rank][file]
                            else:
                                evaluation -= psqt[7 - rank][file]

        return evaluation / 100 # divide by 100 to make the evaluation less significant


    def evaluate_development(self): # how developed the pieces are (pieces on their starting squares are not developed) (more important in the opening)
        '''If the player has developed more pieces, the position is better''' # TODO: make this more accurate by checking if the pieces are on their starting squares and making it less important in the endgame
        white_developed = 0
        black_developed = 0

        for square in CENTRAL_LEGAL_SQUARES:
            if self.board.is_piece(square) and not self.board.is_pawn(square):
                if self.board.is_white(square):
                    white_developed += 1
                else:
                    black_developed += 1

        return (white_developed - black_developed) * DEVELOPMENT_ADVANTAGE
    
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
        evaluation += self.evaluate_double_pawns()
        evaluation += self.evaluate_isolated_pawns()
        # evaluation += self.evaluate_mobility() | VERY SLOW
        evaluation += self.evaluate_check()
        evaluation += self.evaluate_center_control()
        # evaluation += self.evaluate_attack() | VERY SLOW
        evaluation += self.evaluate_piece_square_tables()
        evaluation += self.evaluate_development()

        self.evaluated_boards[key] = evaluation
        return evaluation 
    

    def minimax(self, depth, alpha, beta):
        if depth == 0 or self.board.is_game_over():
            return self.evaluate_board()
        
        if self.board.white_to_move:
            best_eval = NEGATIVE_INFINITY
            for move in self.board.generate_legal_moves(True):
                self.board.make_move(move)
                eval = self.minimax(depth - 1, alpha, beta)
                self.board.undo_move()
                best_eval = max(best_eval, eval)
                alpha = max(alpha, best_eval)
                if beta <= alpha:
                    break

        else:
            best_eval = POSITIVE_INFINITY
            for move in self.board.generate_legal_moves(False):
                self.board.make_move(move)
                eval = self.minimax(depth - 1, alpha, beta)
                self.board.undo_move()
                best_eval = min(best_eval, eval)
                beta = min(beta, best_eval)
                if beta <= alpha:
                    break

        return best_eval


    def find_best_move(self):
        start_time = time.time()
        starting_player = self.board.white_to_move
        best_move = None

        if starting_player: # white 
            best_eval = NEGATIVE_INFINITY
            alpha = NEGATIVE_INFINITY
            beta = POSITIVE_INFINITY
            for move in self.board.generate_legal_moves(True):
                self.board.make_move(move)
                eval = self.minimax(self.depth - 1, alpha, beta)
                self.board.undo_move()
                if eval > best_eval:
                    best_eval = eval
                    best_move = move
                alpha = max(alpha, best_eval)
        else: # black
            best_eval = POSITIVE_INFINITY
            alpha = NEGATIVE_INFINITY
            beta = POSITIVE_INFINITY
            for move in self.board.generate_legal_moves(False):
                self.board.make_move(move)
                eval = self.minimax(self.depth - 1, alpha, beta)
                self.board.undo_move()
                if eval < best_eval:
                    best_eval = eval
                    best_move = move
                beta = min(beta, best_eval)

        print(f"Best move: {decode_move(best_move)} with evaluation: {best_eval}")
        print(f"Time taken: {time.time() - start_time} seconds")
        return best_move, best_eval


if __name__ == '__main__':
    import cProfile
    import pstats
    import csv

    board = Board()
    # board.load_fen('rnbqkbnr/ppppp2p/5p2/6p1/4PP2/8/PPPP2PP/RNBQKBNR w - - 0 1')
    # board.make_move(encode_move(3, 71, 0b1101))
    # board.load_fen('rnbqkbnr/ppppp2p/5p2/6pQ/4PP2/8/PPPP2PP/RNB1KBNR b - - 0 1')
    engine = Engine(board, depth=3)

    # engine.find_best_move()

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