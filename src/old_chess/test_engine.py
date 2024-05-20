import unittest
from board import Board
from engine import Engine

class TestEngine(unittest.TestCase):
    def setUp(self):
        self.board = Board()
        self.engine = Engine(self.board, 3, 5)  # Depth: 3, Time Limit: 5 seconds

    def test_evaluate_board(self):
        # Test when the board is in checkmate
        self.board.load_fen('3K2r1/7r/8/8/8/8/8/3k4 w - - 0 1')
        self.assertEqual(self.engine.evaluate_board(), float('-inf'))

        # Test when the board is in stalemate
        self.board.load_fen('3K4/1k3q2/8/8/8/8/8/8 w - - 0 1')
        self.assertEqual(self.engine.evaluate_board(), 0)

        # Test when the board is in a normal position
        self.board.load_fen('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
        self.assertEqual(self.engine.evaluate_board(), 0)

    def test_evaluate_piece_values(self):
        self.board.load_fen('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
        self.assertEqual(self.engine.evaluate_piece_values(), 0)

        self.board.load_fen('3K4/8/8/8/8/8/6R1/3k3R w - - 0 1')
        self.assertEqual(self.engine.evaluate_piece_values(), 0)

    def test_evaluate_piece_mobility(self):
        self.board.load_fen('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
        self.assertEqual(self.engine.evaluate_piece_mobility(), 0)

        self.board.load_fen('3K4/8/8/8/8/8/6R1/3k3R w - - 0 1')
        self.assertEqual(self.engine.evaluate_piece_mobility(), 0)

    def test_evaluate_check(self):
        self.board.load_fen('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
        self.assertEqual(self.engine.evaluate_check(), 0)

        self.board.load_fen('3K2r1/7r/8/8/8/8/8/3k4 w - - 0 1')
        self.assertEqual(self.engine.evaluate_check(), -0.75)

    def test_evaluate_pawn_structure(self):
        self.board.load_fen('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
        self.assertEqual(self.engine.evaluate_pawn_structure(), 0)

        self.board.load_fen('3K4/8/8/8/8/8/6R1/3k3R w - - 0 1')
        self.assertEqual(self.engine.evaluate_pawn_structure(), 0)

    def test_evaluate_double_pawns(self):
        self.board.load_fen('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
        self.assertEqual(self.engine.evaluate_double_pawns(), 0)

        self.board.load_fen('3K4/8/8/8/8/8/6R1/3k3R w - - 0 1')
        self.assertEqual(self.engine.evaluate_double_pawns(), 0)

    def test_evaluate_isolated_pawns(self):
        self.board.load_fen('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
        self.assertEqual(self.engine.evaluate_isolated_pawns(), 0)

        self.board.load_fen('3K4/8/8/8/8/8/6R1/3k3R w - - 0 1')
        self.assertEqual(self.engine.evaluate_isolated_pawns(), 0)

    def test_evaluate_backward_pawns(self):
        self.board.load_fen('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
        self.assertEqual(self.engine.evaluate_backward_pawns(), 0)

        self.board.load_fen('3K4/8/8/8/8/8/6R1/3k3R w - - 0 1')
        self.assertEqual(self.engine.evaluate_backward_pawns(), 0)

    def test_evaluate_passed_pawns(self):
        self.board.load_fen('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
        self.assertEqual(self.engine.evaluate_passed_pawns(), 0)

        self.board.load_fen('3K4/8/8/8/8/8/6R1/3k3R w - - 0 1')
        self.assertEqual(self.engine.evaluate_passed_pawns(), 0)

    def test_evaluate_center_control(self):
        self.board.load_fen('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
        self.assertEqual(self.engine.evaluate_center_control(), 0)

        self.board.load_fen('3K4/8/8/8/8/8/6R1/3k3R w - - 0 1')
        self.assertEqual(self.engine.evaluate_center_control(), 0)

    def test_evaluate_defending_ally_pieces(self):
        self.board.load_fen('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
        self.assertEqual(self.engine.evaluate_defending_ally_pieces(), 0)

        self.board.load_fen('3K4/8/8/8/8/8/6R1/3k3R w - - 0 1')
        self.assertEqual(self.engine.evaluate_defending_ally_pieces(), 0)

    def test_evaluate_attacking_enemy_pieces(self):
        self.board.load_fen('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
        self.assertEqual(self.engine.evaluate_attacking_enemy_pieces(), 0)

        self.board.load_fen('3K4/8/8/8/8/8/6R1/3k3R w - - 0 1')
        self.assertEqual(self.engine.evaluate_attacking_enemy_pieces(), 0)

    def test_negamax(self):
        self.board.load_fen('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
        self.assertEqual(self.engine.negamax(3, float('-inf'), float('inf')), 0)

        self.board.load_fen('3K4/8/8/8/8/8/6R1/3k3R w - - 0 1')
        self.assertEqual(self.engine.negamax(3, float('-inf'), float('inf')), 0)

    
if __name__ == '__main__':
    unittest.main()