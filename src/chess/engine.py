from board import Board

class Engine:
    def __init__(self, board: Board, depth: int = 3):
        self.board = board
        self.max_depth = depth

    def evaluate_board(self):
        """
        Evaluate the board position
        Negative score means black is winning
        Positive score means white is winning
        """
        # checkmate
        if self.board.is_checkmate():
            if self.board.turn == 'white':
                return -1000
            else:
                return 1000
            
        # stalemate
        if self.board.is_stalemate():
            return 0

        # material evaluation
        evaluation = 0
        for row in self.board.game_board:
            for piece in row:
                if piece:
                    if piece.team == 'white':
                        evaluation += piece.value
                    else:
                        evaluation -= piece.value
        return evaluation
    
    def negamax(self, depth, alpha, beta):
        if depth == 0 or self.board.is_game_over():
            return self.evaluate_board()

        max_score = -float('inf')
        for move in self.board.list_all_moves():
            self.board.full_move(move[0], move[1])
            score = -self.negamax(depth - 1, -beta, -alpha)
            self.board.undo_move()

            max_score = max(max_score, score)
            alpha = max(alpha, score)
            if alpha >= beta:
                break
        return max_score
    
    def get_best_move(self):
        best_move = None
        max_score = -float('inf')
        for move in self.board.list_all_moves():
            self.board.full_move(move[0], move[1])
            score = -self.negamax(self.max_depth - 1, -float('inf'), float('inf'))
            self.board.undo_move()

            if score > max_score:
                max_score = score
                best_move = move
        return best_move