from board import Board
import time

class Engine:
    def __init__(self, board: Board, depth: int = 2):
        self.board = board
        self.max_depth = depth

        self.get_color_legal_moves_count = 0
        self.evaluate_board_count = 0
        self.negamax_count = 0

    def get_color_legal_moves(self, color: bool):
        """
        Get all legal moves for a given color
        """
        self.get_color_legal_moves_count += 1
        legal_moves = []
        for move in self.board.generate_legal_moves():
            if self.board.board[move.start[0]][move.start[1]].is_white == color:
                legal_moves.append(move)

        return legal_moves

    def evaluate_piece_values(self):
        """
        Evaluate the board position based on piece values
        """
        evaluation = 0
        for row in self.board.board:
            for piece in row:
                if piece:
                    if piece.is_white:
                        evaluation += piece.value
                    else:
                        evaluation -= piece.value
        return evaluation

    def evaluate_piece_mobility(self):
        """
        Evaluate the board position based on piece mobility
        """
        white_mobility = len(self.get_color_legal_moves(True))
        black_mobility = len(self.get_color_legal_moves(False))

        factor = 0.1
        evaluation = factor * (white_mobility - black_mobility)
        return evaluation

    def evaluate_check(self):
        """
        Evaluate the board position based on check
        """
        if self.board.is_check(self.board.white_to_move):
            if self.board.white_to_move:
                return -0.5
            else:
                return 0.5
        return 0
    
    def evaluate_pawn_structure(self):
        """
        Evaluate the board position based on pawn structure
        Double pawns, isolated pawns, backward pawns, passed pawns
        """
        evaluation = 0

        double_pawns_disadvantage = -0.5
        isolated_pawns_disadvantage = -0.5
        backward_pawns_disadvantage = -0.5
        passed_pawns_advantage = 0.5

        # double pawns
        for file in self.board.board:
            white_pawns = 0
            black_pawns = 0
            for piece in file:
                if piece and piece.type == "p":
                    if piece.is_white:
                        white_pawns += 1
                    else:
                        black_pawns += 1
            if white_pawns > 1:
                evaluation += double_pawns_disadvantage
            if black_pawns > 1:
                evaluation -= double_pawns_disadvantage

        # isolated pawns (check for pawns on either side (0<=file<=7))
        for file in range(8):
            white_pawns = 0
            black_pawns = 0
            for rank in range(8):
                if self.board.board[file][rank] and self.board.board[file][rank].type == "p":
                    if self.board.board[file][rank].is_white:
                        white_pawns += 1
                    else:
                        black_pawns += 1
            if white_pawns > 1:
                evaluation += isolated_pawns_disadvantage
            if black_pawns > 1:
                evaluation -= isolated_pawns_disadvantage

        # backward pawns
        for file in range(8):
            for rank in range(8):
                if self.board.board[file][rank] and self.board.board[file][rank].type == "p":
                    #

                    if self.board.board[file][rank].is_white:
                        if self.board.board[file][rank + 1] and self.board.board[file][rank + 1].type == "p":
                            evaluation += backward_pawns_disadvantage
                    else:
                        if self.board.board[file][rank - 1] and self.board.board[file][rank - 1].type == "p":
                            evaluation -= backward_pawns_disadvantage

        # passed pawns
        for file in range(8):
            for rank in range(8):
                if self.board.board[file][rank] and self.board.board[file][rank].type == "p":
                    if self.board.board[file][rank].is_white:
                        passed = True
                        for i in range(rank + 1, 8):
                            if self.board.board[i][file]:
                                passed = False
                                break
                        if passed:
                            evaluation += passed_pawns_advantage
                    else:
                        passed = True
                        for i in range(rank - 1, -1, -1):
                            if self.board.board[i][file]:
                                passed = False
                                break
                        if passed:
                            evaluation -= passed_pawns_advantage

        return evaluation

    def evaluate_center_control(self):
        """
        Evaluate the board position based on control of the center
        """
        evaluation = 0
        center = [(3, 3), (3, 4), (4, 3), (4, 4)]
        center_control_advantage = 0.1
        for square in center:
            if self.board.board[square[0]][square[1]]:
                if self.board.board[square[0]][square[1]].is_white:
                    evaluation += center_control_advantage
                else:
                    evaluation -= center_control_advantage
        return evaluation

    def evaluate_defending_ally_pieces(self):
        """
        Evaluate the board position based on defending ally pieces
        """
        evaluation = 0
        defending_ally_pieces_advantage = 0.1
        moves = self.board.generate_legal_moves()
        # if the start square of a move is the same as the end square the move, then the piece is defending an ally piece
        for move in moves:
            if move.start == move.end:
                if self.board.board[move.start[0]][move.start[1]].is_white:
                    evaluation += defending_ally_pieces_advantage
                else:
                    evaluation -= defending_ally_pieces_advantage

        return evaluation

    def evaluate_board(self):
        """
        Evaluate the board position
        Negative score means black is winning
        Positive score means white is winning
        """
        self.evaluate_board_count += 1
        # checkmate

        if self.board.is_checkmate():
            if self.board.white_to_move:
                return -1000
            else:
                return 1000
            
        # stalemate
        if self.board.is_stalemate():
            return 0

        evaluation = 0

        # material evaluation
        evaluation += self.evaluate_piece_values()

        # mobility evaluation
        evaluation += self.evaluate_piece_mobility()

        # check evaluation
        evaluation += self.evaluate_check()

        # pawn structure evaluation
        evaluation += self.evaluate_pawn_structure()

        # defending the center evaluation
        evaluation += self.evaluate_center_control()

        # defending ally pieces evaluation
        evaluation += self.evaluate_defending_ally_pieces()

        if abs(evaluation) > 5:
            print(f"evaluation: {evaluation}")
        return evaluation
    
    def negamax(self, depth, alpha, beta):
        """
        Negamax algorithm with alpha-beta pruning
        """
        self.negamax_count += 1
        if depth == 0:
            return self.evaluate_board()

        max_score = -10000
        for move in self.get_color_legal_moves(self.board.white_to_move):
            self.board.make_move(move)
            score = -self.negamax(depth - 1, -beta, -alpha)
            self.board.undo_move()

            if score >= beta:
                return score
            if score > max_score:
                max_score = score
            if score > alpha:
                alpha = score
        return max_score
        
    
    def get_best_move(self):
        """
        Get the best move for the current position
        """
        best_move = None
        max_score = -10000
        for move in self.get_color_legal_moves(self.board.white_to_move):
            self.board.make_move(move)
            score = -self.negamax(self.max_depth - 1, -10000, 10000)
            self.board.undo_move()

            if score > max_score:
                max_score = score
                best_move = move
        
        print(f"get_color_legal_moves_count: {self.get_color_legal_moves_count}\nevaluate_board_count: {self.evaluate_board_count}\nnegamax_count: {self.negamax_count}")
        return best_move