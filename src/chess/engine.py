# from src.chess.engine.PSQT import PSQT
import random
import time
from src.chess.PSQT import PSQT, PHASE_WEIGHTS, TOTAL_PHASE
from src.chess.board import Board, Piece



def calculate_phase(board):
    phase = 0

    for square in board:
        if square != 0:
            phase += PHASE_WEIGHTS[square & 7]

    return phase / TOTAL_PHASE # this is a float between 0 and 1

def get_piece_square_table_value(piece, square, phase):

    opening_table = PSQT["Opening"][piece]
    endgame_table = PSQT["Endgame"][piece]

    opening_value = opening_table[square]
    endgame_value = endgame_table[square]

    return opening_value * (1 - phase) + endgame_value * phase

def evaluate_psqt(board):
    phase = calculate_phase(board)

    score = 0

    # TODO: switch to using board.white_pieces and board.black_pieces
    for square, piece in enumerate(board):
        if piece != 0:
            score += get_piece_square_table_value(piece, square, phase)

    return score









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
    
    def order_moves(self, unordered_moves):
        ordered_moves = []

        check_moves = []
        capture_moves = []
        non_capture_moves = []

        for move in unordered_moves:
            if self.board.is_checking_move(move):
                check_moves.append(move)
            elif move[3]:
                capture_moves.append(move)
            else:
                non_capture_moves.append(move)

        # order check moves based on the piece that is moving
        check_moves.sort(key=lambda move: move[2]) # least valuable piece first

        # order capture moves based on the piece that is getting captured
        capture_moves.sort(key=lambda move: (-move[3], move[2]))

        # order non-capture moves based on the piece that is moving
        non_capture_moves.sort(key=lambda move: -move[2]) # most valuable piece first

        ordered_moves.extend(check_moves)
        ordered_moves.extend(capture_moves)
        ordered_moves.extend(non_capture_moves)

        return ordered_moves


    def quiescence_search(self):
        if self.board.is_checkmate():
            return NEGATIVE_INFINITY if self.board.white_to_move else POSITIVE_INFINITY
        if self.board.is_stalemate():        
            return 0
        # TODO: implement quiescence search
        return evaluate(self.board)

    def minimax(self, depth, alpha, beta):
        if depth == 0 or self.time_exceeded():
            return self.quiescence_search()
        
        moves = self.board.generate_moves()
        moves = self.order_moves(moves)

        if self.board.white_to_move:
            best_eval = NEGATIVE_INFINITY
            for move in moves:
                self.board.make_move(move)
                eval = self.minimax(depth - 1, alpha, beta)
                self.board.undo_move()

                best_eval = max(best_eval, eval)
                alpha = max(alpha, eval)

                if beta <= alpha: # TODO: check
                    break

            return best_eval
        
        else:
            best_eval = POSITIVE_INFINITY
            for move in moves:
                self.board.make_move(move)
                eval = self.minimax(depth - 1, alpha, beta)
                self.board.undo_move()

                best_eval = min(best_eval, eval)
                beta = min(beta, eval)

                if beta <= alpha: # TODO: check
                    break

            return best_eval
        
    def find_best_move(self, depth):
        moves = self.board.generate_moves()
        best_move = random.choice(moves)
        best_eval = NEGATIVE_INFINITY if self.board.white_to_move else POSITIVE_INFINITY

        alpha = NEGATIVE_INFINITY
        beta = POSITIVE_INFINITY

        for move in self.order_moves(moves):
            self.board.make_move(move)
            eval = self.minimax(depth - 1, alpha, beta)
            self.board.undo_move()

            if self.board.white_to_move:
                alpha = max(alpha, eval)
                if eval > best_eval:
                    best_eval = eval
                    best_move = move

            else:
                beta = min(beta, eval)
                if eval < best_eval:
                    best_eval = eval
                    best_move = move

            if alpha >= beta: # TODO: check
                break

        return best_move, best_eval

    def iterative_deepening(self, result_container):
        self.start_time = time.time()
        
        for depth in range(1, self.depth + 1):
            best_move, best_eval = self.find_best_move(depth)
            result_container.append((best_move, best_eval, False))
            print(f"Depth: {depth}, Best move: {best_move}, Best eval: {best_eval}")

            if self.time_exceeded():
                print("Time exceeded")
                print(f"Depth: {depth}, Best move: {best_move}, Best eval: {best_eval}")
                result_container.append((best_move, best_eval, True))
                break


# result_container = []
# (best_move, best_eval, is_final)