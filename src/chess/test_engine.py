import unittest
from board import Board
from engine import Engine

class TestChessEngine(unittest.TestCase):

    def setUp(self):
        self.board = Board()
        self.board.FEN_to_board("4k3/Q6Q/8/8/8/8/PPPPP1PP/RNB1KBNq w - - 0 1")
        self.engine = Engine(self.board)

    def test_mate_in_one(self):
        self.board.FEN_to_board("4k3/Q6Q/8/8/8/8/PPPPP1PP/RNB1KBNq w - - 0 1")
        best_move = self.engine.get_best_move()
        # make the move and check if the game is over
        self.board.full_move(best_move[0], best_move[1])
        self.assertTrue(self.board.is_game_over(), "Game should be over due to checkmate")

    def test_best_move_within_list(self):
        # Ensure that the mate in one move is found by the board
        self.board.FEN_to_board("4k3/Q6Q/8/8/8/8/PPPPP1PP/RNB1KBNq w - - 0 1")
        moves = self.board.list_all_moves()
        mate_in_one = ((6, 0), (7, 0))
        self.assertIn(mate_in_one, moves, "Mate in one move not found")

    def test_game_over(self):
        # Setting up a checkmate position to test game over condition
        self.board.FEN_to_board("4k2Q/Q7/8/8/8/8/PPPPP1PP/RNB1KBNq b KQkq - 0 1")
        self.assertTrue(self.board.is_game_over(), "Game should be over due to checkmate")

    def test_legal_moves(self):
        # Ensure that a queen can move to deliver checkmate
        self.board.FEN_to_board("4k3/Q6Q/8/8/8/8/PPPPP1PP/RNB1KBNq w - - 0 1")
        legal_moves = self.board.get_legal_moves(6, 0)  # Moves for queen at (6, 0)
        self.assertIn((7, 0), legal_moves, "Queen should be able to move to (7, 0) to checkmate")

    def test_evaluation(self):
        # Position where white should have an overwhelmingly positive score
        self.board.FEN_to_board("4k3/Q6Q/8/8/8/8/PPPPP1PP/RNB1KBNq w - - 0 1")
        evaluation = self.engine.evaluate_board()
        self.assertTrue(evaluation > 0, "Evaluation should be highly positive for white")

    def test_undo_move(self):
        # Perform a move and then undo it, check if the board returns to the initial state
        initial_FEN = self.board.generate_FEN()
        self.board.full_move((1, 6), (0, 7))  # Any valid move
        self.board.undo_move()
        self.assertEqual(initial_FEN, self.board.generate_FEN(), "Undo move did not restore the original board state")

if __name__ == "__main__":
    unittest.main()
