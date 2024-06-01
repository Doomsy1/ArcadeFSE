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















NEGATIVE_INFINITY = -9999999
POSITIVE_INFINITY = 9999999

class Engine:
    def __init__(self, board: Board, depth: int = 1, time_limit_ms: int = 5000):
        self.board = board.__copy__()
        self.depth = depth
        self.time_limit_ms = time_limit_ms

        self.history_table = {}
        self.cached_generations = {}
        self.start_time = 0

    def update_board(self, board: Board):
        '''Used to sync the engine's board with the actual board.'''
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
    
    def calculate_mvv_lva(self, move):
        '''Most valuable victim, least valuable attacker.'''
        victim_piece = Piece.get_type(move[3])
        attacker_piece = Piece.get_type(move[2])
        promotion_piece = Piece.get_type(move[4])

        if victim_piece == 0:
            return attacker_piece + promotion_piece
        return victim_piece*2 - attacker_piece + promotion_piece

    def order_moves(self, unordered_moves):
        '''Order moves based on the history heuristic, MVV/LVA, and other factors.'''

        move_scores = []
        for move in unordered_moves:
            history_score = lambda move: self.history_table.get(move, 0)
            # might be None if the move is not in the history table

            mvv_lva_score = self.calculate_mvv_lva(unordered_moves[0])

            check_score = 5 if self.board.is_checking_move(move) else 0
            # TODO: add tactical evaluation
            # TODO: add static exchange evaluation

            move_score = history_score(move)*10 + mvv_lva_score + check_score

            move_scores.append((move, move_score))

        move_scores.sort(key=lambda x: x[1], reverse=True)
        return [move[0] for move in move_scores]



    def get_ordered_moves(self): # TODO: add a parameter to generate_legal_moves to only generate capture moves
        key = self.board.hash_board()
        if key in self.cached_generations:
            moves = self.cached_generations[key]
        else:
            self.move_generations += 1
            moves = self.board.generate_legal_moves()
        return self.order_moves(moves)

    def evaluate(self):
        '''Evaluate the current board position. 
        Return a score where positive is good for white and negative is good for black.'''
        self.positions_evaluated += 1
        evaluation = 0
        if self.board.is_game_over():
            return self.evaluate_terminal()
        
        # Material
        evaluation += evaluate_psqt(self.board.board)

        # TODO: add more evaluation terms

        return evaluation

    def evaluate_terminal(self):
        if self.board.is_checkmate():
            return NEGATIVE_INFINITY if self.board.white_to_move else POSITIVE_INFINITY
        return 0
    
    def update_history_score(self, move, depth):
        if move not in self.history_table:
            self.history_table[move] = 0
        self.history_table[move] += 2 ** depth

    def minimax(self, depth, alpha, beta):
        if self.time_exceeded():
            raise Exception("Time exceeded")

        if depth == 0 or self.board.is_game_over():
            return self.evaluate()

        if self.board.white_to_move:
            max_eval = NEGATIVE_INFINITY
            for move in self.get_ordered_moves():
                self.board.make_move(move)
                eval = self.minimax(depth - 1, alpha, beta)
                self.board.undo_move()
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    self.update_history_score(move, depth)
                    break
            return max_eval
        else:
            min_eval = POSITIVE_INFINITY
            for move in self.get_ordered_moves():
                self.board.make_move(move)
                eval = self.minimax(depth - 1, alpha, beta)
                self.board.undo_move()
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    self.update_history_score(move, depth)
                    break
            return min_eval

    def find_best_move(self, depth):
        best_eval = NEGATIVE_INFINITY if self.board.white_to_move else POSITIVE_INFINITY
        moves = self.get_ordered_moves()

        best_move = random.choice(moves)
        alpha = NEGATIVE_INFINITY
        beta = POSITIVE_INFINITY

        for move in moves:
            self.board.make_move(move)
            eval = self.minimax(depth - 1, alpha, beta)
            self.board.undo_move()

            if self.board.white_to_move:
                if eval > best_eval:
                    best_eval = eval
                    best_move = move
                alpha = max(alpha, eval)
            else:
                if eval < best_eval:
                    best_eval = eval
                    best_move = move
                beta = min(beta, eval)

        return best_move, best_eval

    def iterative_deepening(self, result_container: list):
        """Perform an iterative deepening search."""
        # TODO: quiescence search (necessary)
        # TODO: transposition table (necessary)
        # TODO: killer moves (necessary)

        # TODO: parallel search (maybe)
        # TODO: null move pruning (maybe)
        # TODO: aspiration windows (maybe)
        # TODO: late move reduction (maybe)
        # TODO: futility pruning (maybe)
        
        self.start_time = time.time()
        self.positions_evaluated = 0
        self.move_generations = 0

        depth = 1
        while not self.time_exceeded():
            try:
                best_move, best_eval = self.find_best_move(depth)
            except Exception as e:
                print(e)
                break
            print(f"Depth: {depth}, Best move: {best_move}, Best eval: {best_eval}")
            result_container.append((best_move, best_eval, False))
            depth += 1
            if best_eval == POSITIVE_INFINITY or best_eval == NEGATIVE_INFINITY:
                break

            time_elapsed = (time.time() - self.start_time) * 1000
            if time_elapsed * 2 >= self.time_limit_ms:
                break

        print(f"Time taken: {(time.time() - self.start_time) * 1000:.2f} ms, Positions evaluated: {self.positions_evaluated}, Move generations: {self.move_generations}")
        result_container.append((best_move, best_eval, True))


# result_container = []
# (best_move, best_eval, is_final)