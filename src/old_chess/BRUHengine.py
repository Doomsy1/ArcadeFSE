from board import Board, decode_move
import time

PIECE_VALUES = {
    0b1001: 1, # white pawn
    0b1010: 3, # white knight
    0b1011: 3, # white bishop
    0b1100: 5, # white rook
    0b1101: 9, # white queen
    0b1110: 1000, # white king

    0b0001: -1, # black pawn
    0b0010: -3, # black knight
    0b0011: -3, # black bishop
    0b0100: -5, # black rook
    0b0101: -9, # black queen
    0b0110: -1000, # black king
}

# evaluation factors
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

POSITIVE_INFINITY = float('inf')
NEGATIVE_INFINITY = float('-inf')

FILE_MASKS = [0x0101010101010101 << file for file in range(8)]

class Engine:
    def __init__(self, board: Board, depth: int, time_limit: int):
        self.board = board
        self.max_depth = depth
        self.time_limit = time_limit

    def evaluate_board(self):
        '''
        Evaluate the board based on:
        - piece values | DONE
        - mobility | DONE
        - check | DONE
        - double pawns | DONE
        - isolated pawns | DONE
        - backward pawns | TODO
        - passed pawns | TODO
        - center control | DONE
        - defending ally pieces | TODO
        - attacking enemy pieces | DONE
        - king safety | TODO 1
        - piece development | TODO 2
        - piece activity | TODO 3
        '''

        if self.board.is_checkmate(True):
            return NEGATIVE_INFINITY
        if self.board.is_checkmate(False):
            return POSITIVE_INFINITY
        
        if self.board.is_draw():
            return 0
        
        evaluation = 0

        evaluation += self.evaluate_piece_values()
        # evaluation += self.evaluate_piece_mobility()
        # evaluation += self.evaluate_check()
        # evaluation += self.evaluate_pawn_structure()
        evaluation += self.evaluate_center_control()
        # evaluation += self.evaluate_defending_ally_pieces()
        evaluation += self.evaluate_attacking_enemy_pieces()

        return evaluation
    
    def evaluate_piece_values(self):
        '''
        Evaluate the board based on piece values
        '''
        evaluation = 0

        occupied_squares = self.board.colour_bitboards[0b1] | self.board.colour_bitboards[0b0]
        for square in LEGAL_SQUARES:
            if occupied_squares & (1 << square):
                piece = self.board.get_piece(square)
                evaluation += PIECE_VALUES[piece]

        return evaluation
    
    def evaluate_piece_mobility(self):
        '''
        Evaluate the board based on piece mobility
        '''
        evaluation = 0

        white_moves = self.board.generate_legal_moves(True)
        black_moves = self.board.generate_legal_moves(False)

        evaluation += len(white_moves) - len(black_moves)

        return evaluation * MOBILITY_FACTOR
    
    def evaluate_check(self):
        '''
        Evaluate the board based on check
        '''
        evaluation = 0

        if self.get_is_check(True):
            return -CHECK_SCORE
        if self.get_is_check(False):
            return CHECK_SCORE
        
        return evaluation
    
    def evaluate_pawn_structure(self):
        '''
        Evaluate the board based on pawn structure
        '''
        evaluation = 0

        evaluation += self.evaluate_double_pawns()
        evaluation += self.evaluate_isolated_pawns()
        # evaluation += self.evaluate_backward_pawns()
        # evaluation += self.evaluate_passed_pawns()

        return evaluation

    def evaluate_double_pawns(self):
        '''
        Evaluate the board based on double pawns
        '''
        evaluation = 0

        for file_mask in FILE_MASKS:
            white_pawns = self.board.white_pieces & file_mask
            black_pawns = self.board.black_pieces & file_mask

            if bin(white_pawns).count('1') > 1:
                evaluation += DOUBLE_PAWNS_DISADVANTAGE

            if bin(black_pawns).count('1') > 1:
                evaluation -= DOUBLE_PAWNS_DISADVANTAGE

        return evaluation
    
    def evaluate_isolated_pawns(self):
        '''
        Evaluate the board based on isolated pawns
        '''
        evaluation = 0

        for file in range(8):
            file_mask = FILE_MASKS[file]

            left_mask = FILE_MASKS[file - 1] if file > 0 else 0
            right_mask = FILE_MASKS[file + 1] if file < 7 else 0

            white_left_pawns = self.board.piece_bitboards[0b1001] & left_mask
            white_pawns = self.board.piece_bitboards[0b1001] & file_mask
            white_right_pawns = self.board.piece_bitboards[0b1001] & right_mask

            black_left_pawns = self.board.piece_bitboards[0b0001] & left_mask
            black_pawns = self.board.piece_bitboards[0b0001] & file_mask
            black_right_pawns = self.board.piece_bitboards[0b0001] & right_mask

            if white_pawns and not white_left_pawns and not white_right_pawns:
                evaluation -= ISOLATED_PAWNS_DISADVANTAGE

            if black_pawns and not black_left_pawns and not black_right_pawns:
                evaluation += ISOLATED_PAWNS_DISADVANTAGE

        return evaluation
    
    def evaluate_backward_pawns(self): # TODO idk what a backward pawn is
        '''
        Evaluate the board based on backward pawns
        '''
        evaluation = 0

        return evaluation
    
    def evaluate_passed_pawns(self): # TODO idk what a passed pawn is
        '''
        Evaluate the board based on passed pawns
        '''
        evaluation = 0

        return evaluation
    
    def evaluate_center_control(self):
        '''
        Evaluate the board based on center control
        '''
        evaluation = 0

        center_squares = [27, 28, 35, 36]
        for square in center_squares:
            if self.board.is_white(square):
                evaluation += CENTER_CONTROL_ADVANTAGE
            if self.board.is_black(square):
                evaluation -= CENTER_CONTROL_ADVANTAGE
        
        return evaluation
    
    def evaluate_defending_ally_pieces(self): # TODO my generate move function doesn't include defending ally pieces
        '''
        Evaluate the board based on defending ally pieces
        '''
        evaluation = 0
        
        return evaluation
    
    def evaluate_attacking_enemy_pieces(self):
        '''
        Evaluate the board based on attacking enemy pieces
        '''
        evaluation = 0

        white_pieces = self.board.colour_bitboards[0b1]
        black_pieces = self.board.colour_bitboards[0b0]

        for square in LEGAL_SQUARES:
            if white_pieces & (1 << square):
                for move in self.board.generate_legal_moves(square):
                    decode_move(move)
                    _, _, _, _, _, _, capture, _ = decode_move(move)
                    if capture:
                        evaluation += ATTACKING_ENEMY_PIECES_ADVANTAGE

            elif black_pieces & (1 << square):
                for move in self.board.generate_legal_moves(square):
                    decode_move(move)
                    _, _, _, _, _, _, capture, _ = decode_move(move)
                    if capture:
                        evaluation -= ATTACKING_ENEMY_PIECES_ADVANTAGE

        return evaluation
    

    def negamax(self, depth, alpha, beta, color):
        '''
        Negamax algorithm with alpha-beta pruning
        '''
        if depth == 0 or self.board.is_game_over():
            return color * self.evaluate_board()
    
        best_score = NEGATIVE_INFINITY
        for move in self.board.generate_legal_moves(color):
            self.board.make_move(move)
            score = -self.negamax(depth - 1, -beta, -alpha, not color)
            self.board.undo_move()
            
            if score > best_score:
                best_score = score
            
            alpha = max(alpha, score)
            if alpha >= beta:
                break
        
        return best_score
    
    def find_best_move(self, depth):
        '''
        Find the best move using negamax
        '''
        best_move = 0
        best_score = NEGATIVE_INFINITY
        alpha = NEGATIVE_INFINITY
        beta = POSITIVE_INFINITY
        
        for move in self.board.generate_legal_moves(True):
            self.board.make_move(move)
            score = -self.negamax(depth - 1, -beta, -alpha, -1)
            self.board.undo_move()
            
            if score > best_score:
                best_score = score
                best_move = move
            
            alpha = max(alpha, score)
        
        return best_move
    
    def get_best_move(self): # TODO add iterative deepening and time limit
        start_time = time.time()

        best_move = self.find_best_move(self.max_depth)
        end_time = time.time()
        print(f"Time taken: {end_time - start_time} seconds")

        return best_move
    
if __name__ == "__main__":
    board = Board()
    engine = Engine(board, 3, 5)
    print(engine.get_best_move())