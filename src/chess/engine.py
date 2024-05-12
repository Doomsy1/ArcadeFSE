from board import Board

class Engine:
    def __init__(self, board: Board, depth: int = 3):
        self.board = board
        self.max_depth = depth

    def evaluate_board(self): # TODO: make this more sophisticated
        '''
        Returns: float representing the evaluation of the current board position
        '''
        eval = 0

        # Material score
        material_score = 0
        for row in self.board.game_board:
            for piece in row:
                if piece:
                    material_score += piece.value if piece.team == self.board.turn else -piece.value

        if self.board.is_checkmate():
            return float('inf') if self.board.turn == 'white' else float('-inf')

        
        eval += material_score
        return eval

    def minimax(self, depth, alpha, beta, maximizing_player):
        '''
        Args:
            depth (int): The depth of the minimax tree
            alpha (int): The best value that the maximizing player currently can guarantee at the current depth
            beta (int): The best value that the minimizing player currently can guarantee at the current depth
            maximizing_player (bool): True if the current player is the maximizing player, False otherwise
        Returns:
            (int, ((start_row, start_col), (end_row, end_col))) tuple representing the best evaluation and the best move
            '''
        pass

    def get_best_move(self):
        '''
        Returns: ((start_row, start_col), (end_row, end_col)) tuple representing the best move
        '''
        pass
    
# test engine
if __name__ == "__main__":
    from board import Board
    board = Board()
    board.FEN_to_board("4k3/Q6Q/8/8/8/8/PPPPP1PP/RNB1KBNq w KQkq - 0 1")
    engine = Engine(board)


    print(engine.get_best_move())