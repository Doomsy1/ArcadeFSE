# from src.chess.engine.PSQT import PSQT
import random
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

def evaluate_psqt(board):
    phase = calculate_phase(board)

    score = 0

    # TODO: switch to using board.white_pieces and board.black_pieces
    for square, piece in enumerate(board):
        if piece != 0:
            score += get_piece_square_table_value(piece, square, phase)

    return score







def order_moves(unordered_moves):
    ordered_moves = []

    capture_moves = []
    non_capture_moves = []

    for move in unordered_moves:
        if move[3]:
            capture_moves.append(move)
        else:
            non_capture_moves.append(move)

    # order capture moves based on the piece that is getting captured
    capture_moves.sort(key=lambda move: (-move[3], move[2]))

    # order non-capture moves based on the piece that is moving
    non_capture_moves.sort(key=lambda move: -move[2])

    ordered_moves.extend(capture_moves)
    ordered_moves.extend(non_capture_moves)

    return ordered_moves

def evaluate(board: Board):
    evaluation = 0
    
    # Material
    evaluation += evaluate_psqt(board.board)

    # TODO: add more evaluation terms

    return evaluation



NEGATIVE_INFINITY = -9999999
POSITIVE_INFINITY = 9999999

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


        self.board.white_to_move = board.white_to_move
        self.board.castling_rights =  board.castling_rights
        self.board.en_passant_target_square = board.en_passant_target_square
        self.board.halfmove_clock = board.halfmove_clock
        self.board.fullmove_number = board.fullmove_number
        self.board.undo_stack = board.undo_stack.copy()


    def set_time_limit(self, time_limit_ms: int):
        self.time_limit_ms = time_limit_ms

    def time_exceeded(self):
        return (time.time() - self.start_time) * 1000 >= self.time_limit_ms
    
    def quiescence_search(self):
        if self.board.is_checkmate():
            return NEGATIVE_INFINITY if self.board.white_to_move else POSITIVE_INFINITY
        if self.board.is_stalemate():        
            return 0
        # TODO: implement quiescence search
        return evaluate(self.board)

    def minimax(self, depth, alpha, beta):
        # TODO: review this code
        if depth == 0 or self.time_exceeded():
            return self.quiescence_search()

        if self.board.white_to_move:
            best_eval = NEGATIVE_INFINITY
            for move in order_moves(self.board.generate_legal_moves()):
                self.board.make_move(move)
                value = self.minimax(depth - 1, alpha, beta)
                self.board.undo_move()
                best_eval = max(best_eval, value)
                alpha = max(alpha, value)
                if beta <= alpha:
                    break

        else:
            best_eval = POSITIVE_INFINITY
            for move in order_moves(self.board.generate_legal_moves()):
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

        for current_depth in range(1, self.depth + 1):
            ordered_moves = order_moves(self.board.generate_legal_moves())
            alpha = NEGATIVE_INFINITY
            beta = POSITIVE_INFINITY
            current_best_move = random.choice(ordered_moves)
            current_best_eval = NEGATIVE_INFINITY if starting_player else POSITIVE_INFINITY

            for move in ordered_moves:
                self.board.make_move(move)
                value = self.minimax(current_depth - 1, alpha, beta)
                self.board.undo_move()

                if starting_player:
                    if value > current_best_eval:
                        current_best_eval = value
                        current_best_move = move
                    alpha = max(alpha, value)
                else:
                    if value < current_best_eval:
                        current_best_eval = value
                        current_best_move = move
                    beta = min(beta, value)

                if beta <= alpha:
                    break

            # if the move will result in a checkmate, don't continue searching
            # if current_best_eval == POSITIVE_INFINITY or current_best_eval == NEGATIVE_INFINITY:
            #     best_move = current_best_move
            #     best_eval = current_best_eval
            #     break

            if current_best_move is None:
                break

            result_container.append((current_best_move, current_best_eval, False))
            print(f"Depth: {current_depth}, Best move: {current_best_move}, Best eval: {current_best_eval}")

            if self.time_exceeded():
                break
            best_move = current_best_move
            best_eval = current_best_eval


        result_container.append((best_move, best_eval, True))
        print(f"Best move: {best_move}, Best eval: {best_eval}")