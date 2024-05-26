# from src.chess.engine.PSQT import PSQT
import time
from src.chess.PSQT import PSQT, PHASE_WEIGHTS, TOTAL_PHASE
from src.chess.board import Board



def calculate_phase(board):
    phase = 0

    for square in board:
        if square != 0:
            phase += PHASE_WEIGHTS[square & 7]

    return phase / TOTAL_PHASE # this is a float between 0 and 1

def get_piece_square_table_value(piece, square, phase):

    opening_table = PSQT["Opening"][piece]
    endgame_table = PSQT["Endgame"][piece]

    rank = square // 8
    file = square % 8

    opening_value = opening_table[7 - rank][file]
    endgame_value = endgame_table[7 - rank][file]

    return opening_value * (1 - phase) + endgame_value * phase

def evaluate_psqt(board: Board):
    phase = calculate_phase(board.board)

    score = 0

    # TODO: switch to using board.white_pieces and board.black_pieces
    for square, piece in enumerate(board.board):
        if piece != 0:
            score += get_piece_square_table_value(piece, square, phase)

    return score









def evaluate(board: Board):
    evaluation = 0
    
    # Material
    evaluation += evaluate_psqt(board)

    # TODO: add more evaluation terms

    return evaluation




NEGATIVE_INFINITY = -float("inf")
POSITIVE_INFINITY = float("inf")

class Engine:
    def __init__(self, board: Board, depth: int = 6, time_limit_ms: int = 2500):
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



    def time_exceeded(self):
        return (time.time() - self.start_time) * 1000 >= self.time_limit_ms
    
    def quiescence_search(self):
        # TODO: implement quiescence search
        return evaluate(self.board)

    def minimax(self, depth, alpha, beta):
        # TODO: review this code
        if depth == 0 or self.time_exceeded():
            return self.quiescence_search()

        if self.board.white_to_move:
            best_eval = NEGATIVE_INFINITY
            for move in self.board.generate_legal_moves(True):
                self.board.make_move(move)
                value = self.minimax(depth - 1, alpha, beta)
                self.board.undo_move()
                best_eval = max(best_eval, value)
                alpha = max(alpha, value)
                if beta <= alpha:
                    break

        else:
            best_eval = POSITIVE_INFINITY
            for move in self.board.generate_legal_moves(False):
                self.board.make_move(move)
                value = self.minimax(depth - 1, alpha, beta)
                self.board.undo_move()
                best_eval = min(best_eval, value)
                beta = min(beta, value)
                if beta <= alpha:
                    break

        return best_eval
    
    def find_best_move(self, result_container):
        # TODO: check if this code is correct
        self.start_time = time.time()
        starting_player = self.board.white_to_move
        best_move = None
        best_eval = NEGATIVE_INFINITY if starting_player else POSITIVE_INFINITY

        alpha = NEGATIVE_INFINITY
        beta = POSITIVE_INFINITY

        for current_depth in range(1, self.depth + 1):

            if starting_player:
                for move in self.board.generate_legal_moves(True):
                    self.board.make_move(move)
                    value = self.minimax(current_depth - 1, alpha, beta)
                    self.board.undo_move()
                    if value > best_eval:
                        best_eval = value
                        best_move = move
                    alpha = max(alpha, value)
                    if beta <= alpha:
                        break

            else:
                for move in self.board.generate_legal_moves(False):
                    self.board.make_move(move)
                    value = self.minimax(current_depth - 1, alpha, beta)
                    self.board.undo_move()
                    if value < best_eval:
                        best_eval = value
                        best_move = move
                    beta = min(beta, value)
                    if beta <= alpha:
                        break

            result_container.append((best_move, best_eval, False))
            print(f"Depth: {current_depth}, Best move: {best_move}, Best eval: {best_eval}")


        result_container.append((best_move, best_eval, True))
        print(f"Best move: {best_move}, Best eval: {best_eval}")