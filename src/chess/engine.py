# from src.chess.engine.PSQT import PSQT
import json
import random
import time
from src.chess.PSQT import PSQT, PHASE_WEIGHTS, TOTAL_PHASE
from src.chess.board import Board, Piece

CHECK_SCORE = 1200
HISTORY_SCORE = 2500
VICTIM_SCORE_MULTIPLIER = 3


OPENINGS_FILE = "src\chess\condensed_openings.json"

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

    return opening_value * phase + endgame_value * (1 - phase)

def evaluate_psqt(board):
    phase = calculate_phase(board)

    score = 0

    for square, piece in enumerate(board):
        if piece != 0:
            score += get_piece_square_table_value(piece, square, phase)

    return score

def evaluate_mobility(board: Board):
    '''Evaluate the mobility of the pieces on the board.'''
    # generate attack map for each side

    white_attack_map = board.generate_attack_map(True)
    black_attack_map = board.generate_attack_map(False)

    white_mobility = sum(white_attack_map)
    black_mobility = sum(black_attack_map)

    return (white_mobility - black_mobility) * 2

def find_doubled_pawns(pawns_on_files):
    '''Find the number of doubled pawns given the number of pawns on each file.'''
    doubled_pawns = 0
    for count in pawns_on_files:
        if count > 1:
            doubled_pawns += count - 1
    return doubled_pawns

def find_isolated_pawns(pawns_on_files):
    '''Find the number of isolated pawns given the number of pawns on each file.'''
    isolated_pawns = 0

    for file, count in enumerate(pawns_on_files):
        if count == 0:
            continue
        if file == 0:
            if pawns_on_files[file+1] == 0:
                isolated_pawns += count
        elif file == 7:
            if pawns_on_files[file-1] == 0:
                isolated_pawns += count
        else:
            if pawns_on_files[file-1] == 0 and pawns_on_files[file+1] == 0:
                isolated_pawns += count

    return isolated_pawns

def find_pawn_chains(pawn_squares, direction):
    '''Find the number of pawn chains for each side.'''
    pawn_chains = 0
    for square in pawn_squares:
        for offset in [-1, 1]:
            if square + offset + direction in pawn_squares:
                pawn_chains += 1

    return pawn_chains

def evaluate_pawn_structure(board: Board):
    '''Evaluate the pawn structure of the board.'''
    # doubled pawns [done]
    # isolated pawns [done]
    # pawn chains [done]
    # passed pawns #TODO

    white_pawn_squares = [square for square in board.white_pieces if Piece.get_type(board.board[square]) == Piece.pawn]
    black_pawn_squares = [square for square in board.black_pieces if Piece.get_type(board.board[square]) == Piece.pawn]

    white_pawn_file_counts = [0] * 8
    black_pawn_file_counts = [0] * 8

    for square in white_pawn_squares:
        file = square % 8
        white_pawn_file_counts[file] += 1

    for square in black_pawn_squares:
        file = square % 8
        black_pawn_file_counts[file] += 1

    white_doubled_pawns = find_doubled_pawns(white_pawn_file_counts)
    black_doubled_pawns = find_doubled_pawns(black_pawn_file_counts)

    white_iso_pawns = find_isolated_pawns(white_pawn_file_counts)
    black_iso_pawns = find_isolated_pawns(black_pawn_file_counts)

    # white_passed_pawns, black_passed_pawns = find_passed_pawns(board)

    white_pawn_chains = find_pawn_chains(white_pawn_squares, 8)
    black_pawn_chains = find_pawn_chains(black_pawn_squares, -8)

    # more doubled pawns is bad
    doubled_pawn_eval = (black_doubled_pawns - white_doubled_pawns) * 13
    doubled_pawn_eval = (black_doubled_pawns - white_doubled_pawns) * 12

    # more isolated pawns is bad
    isolated_pawn_eval = (black_iso_pawns - white_iso_pawns) * 11

    # more pawn chains is good
    pawn_chain_eval = (white_pawn_chains - black_pawn_chains) * 9

    return doubled_pawn_eval + isolated_pawn_eval + pawn_chain_eval

def evaluate_king_safety(board: Board):
    '''Evaluate the safety of the kings on the board.'''
    # castling rights [done]
    # pawn shield # TODO
    # open files # TODO
    
    white_castling_rights = board.castling_rights & 0b1100
    black_castling_rights = board.castling_rights & 0b0011

    # count castling rights
    white_castling_eval = bin(white_castling_rights).count("1") * 15
    black_castling_eval = bin(black_castling_rights).count("1") * 15

    # pawn shield

    # open files

    return white_castling_eval - black_castling_eval




NEGATIVE_INFINITY = -9999999
POSITIVE_INFINITY = 9999999

class Engine:
    def __init__(self, board: Board, depth: int = 1, time_limit_ms: int = 25000):
        self.board = board.__copy__()
        self.depth = depth
        self.time_limit_ms = time_limit_ms

        self.history_table = {}
        self.cached_generations = {}
        self.transposition_table = {}
        self.start_time = 0

        self.load_openings()

    def load_openings(self):
        with open(OPENINGS_FILE, "r") as file:
            self.openings = json.load(file)

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

        victim_value = Piece.get_value(victim_piece)
        attacker_value = Piece.get_value(attacker_piece)
        promotion_value = Piece.get_value(promotion_piece)


        if victim_value == 0:
            return attacker_value + promotion_value
        return victim_value * VICTIM_SCORE_MULTIPLIER - attacker_value + promotion_value

    def order_moves(self, unordered_moves):
        '''Order moves based on the history heuristic, MVV/LVA, and other factors.'''

        move_scores = []
        for move in unordered_moves:
            history_score = lambda move: self.history_table.get(move, 0)

            mvv_lva_score = self.calculate_mvv_lva(unordered_moves[0])

            # TODO: speed up check detection
            check_score = 1 if self.board.is_checking_move(move) else 0

            # TODO: penalize moving to a square that is attacked by the opponent

            # TODO: add tactical evaluation
            # TODO: add static exchange evaluation

            move_score = history_score(move)*HISTORY_SCORE + mvv_lva_score + check_score * CHECK_SCORE

            move_scores.append((move, move_score))

        move_scores.sort(key=lambda x: x[1], reverse=True)
        return [move[0] for move in move_scores]



    def get_ordered_moves(self):
        self.move_generations += 1
        moves = self.board.generate_legal_moves()

        ordered_moves = self.order_moves(moves)
        return ordered_moves

    def evaluate(self):
        '''Evaluate the current board position. 
        Return a score where positive is good for white and negative is good for black.'''
        self.positions_evaluated += 1
        # threefold repetition
        if self.board.is_threefold_repetition():
            return 0
        # insufficient material
        if self.board.is_insufficient_material():
            return 0
        
        evaluation = 0
        
        # material
        evaluation += evaluate_psqt(self.board.board)

        # mobility
        evaluation += evaluate_mobility(self.board)

        # pawn structure
        evaluation += evaluate_pawn_structure(self.board)

        # king safety
        evaluation += evaluate_king_safety(self.board)

        # TODO: add more evaluation terms
        # Open file rooks and queens

        return evaluation
    
    def update_history_score(self, move, depth):
        if move not in self.history_table:
            self.history_table[move] = 0
        self.history_table[move] += 3 ** depth

    def quiescence_search(self, alpha, beta):
        if self.board.white_to_move:
            return self.quiescence_max(alpha, beta)
        else:
            return self.quiescence_min(alpha, beta)

    def quiescence_max(self, alpha, beta):
        moves = self.board.generate_legal_moves(capture_only=True)
        if len(moves) == 0: # no legal moves
            if self.board.is_check(True):
                return NEGATIVE_INFINITY # if white is in check, black wins
            return 0 # stalemate
        stand_pat = self.evaluate()
        if stand_pat >= beta:
            return beta
        if stand_pat > alpha:
            alpha = stand_pat

        for move in moves:
            self.board.make_move(move)
            score = self.quiescence_min(alpha, beta)
            self.board.undo_move()

            if score >= beta:
                return beta
            if score > alpha:
                alpha = score

        return alpha

    def quiescence_min(self, alpha, beta):
        moves = self.board.generate_legal_moves(capture_only=True)
        if len(moves) == 0: # no legal moves
            if self.board.is_check(False):
                return POSITIVE_INFINITY # if black is in check, white wins
            return 0 # stalemate
        stand_pat = self.evaluate()
        if stand_pat <= alpha:
            return alpha
        if stand_pat < beta:
            beta = stand_pat

        for move in moves:
            self.board.make_move(move)
            score = self.quiescence_max(alpha, beta)
            self.board.undo_move()

            if score <= alpha:
                return alpha
            if score < beta:
                beta = score

        return beta

    def minimax(self, depth, alpha, beta):
        if self.time_exceeded():
            raise Exception("Time exceeded")
        
        if self.board.is_threefold_repetition():
            return 0

        moves = self.get_ordered_moves()
        if len(moves) == 0: # no legal moves
            if self.board.is_check(self.board.white_to_move):
                return NEGATIVE_INFINITY if self.board.white_to_move else POSITIVE_INFINITY
            return 0 # stalemate
        
        if self.board.is_threefold_repetition():
            return 0
        
        if depth == 0:
            # return self.quiescence_search(alpha, beta) # broken
            return self.evaluate() 

        if self.board.white_to_move:
            max_eval = NEGATIVE_INFINITY
            for move in moves:
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
            for move in moves:
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
        # TODO: thinking during opponent's turn (necessary)
        # TODO: time management (necessary)
        # TODO: quiescence search (necessary)
        # TODO: transposition table (necessary)
        # TODO: killer moves (necessary)
        # TODO: parallel search (necessary)

        # TODO: opening book (maybe)
        # TODO: endgame tablebases (maybe)

        # TODO: null move pruning (maybe)
        # TODO: aspiration windows (maybe)
        # TODO: late move reduction (maybe)
        # TODO: futility pruning (maybe)

        fen = self.board.create_fen(ignore_en_passant=True)
        turn = self.board.white_to_move
        if fen in self.openings:
            opening_moves = self.openings[fen]
            # sort opening moves by score
            # they are formatted like this: move: score
            opening_moves = sorted(opening_moves.items(), key=lambda x: x[1], reverse=turn) # position is good for white
            opening_moves = [move[0].split(", ") for move in opening_moves]
            valid_moves = self.board.generate_legal_moves()
            move_found = False
            for opening_move in opening_moves:
                if move_found:
                    break

                for valid_move in valid_moves:
                    
                    if valid_move[0] == int(opening_move[0]) and valid_move[1] == int(opening_move[1]):
                        best_opening_move = valid_move
                        move_found = True
                        break
            if move_found:
                result_container.append((best_opening_move, None, True))
                return
            

        
        self.start_time = time.time()
        self.positions_evaluated = 0
        self.move_generations = 0
        self.cache_retreivals = 0

        moves = self.get_ordered_moves()
        if len(moves) == 0:
            return
        if len(moves) == 1:
            result_container.append((moves[0], None, True))
            return
        best_move = moves[0]
        best_eval = None

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

        print(f"Time taken: {(time.time() - self.start_time) * 1000:.2f} ms, Positions evaluated: {self.positions_evaluated}, Move generations: {self.move_generations}, Cache retrievals: {self.cache_retreivals}")
        result_container.append((best_move, best_eval, True))


# result_container = []
# (best_move, best_eval, is_final)