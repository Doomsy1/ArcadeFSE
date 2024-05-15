import unittest
from board import Piece, Move, Board, STARTING_FEN, piece_values

class TestPiece(unittest.TestCase):
    def test_initialization(self):
        p = Piece('P', (0, 1))
        self.assertEqual(p.type, 'p')
        self.assertTrue(p.is_white)
        self.assertEqual(p.value, piece_values['p'])
        self.assertEqual(p.position, (0, 1))
        
        p = Piece(None, (0, 1))
        self.assertIsNone(p.type)
        self.assertIsNone(p.is_white)
        self.assertEqual(p.value, 0)
        self.assertEqual(p.position, (0, 1))

    def test_promote(self):
        p = Piece('p', (0, 1))
        p.promote()
        self.assertEqual(p.type, 'q')
        self.assertEqual(p.value, piece_values['q'])

class TestMove(unittest.TestCase):
    def test_initialization(self):
        m = Move((0, 1), (0, 2))
        self.assertEqual(m.start, (0, 1))
        self.assertEqual(m.end, (0, 2))

    def test_equality(self):
        m1 = Move((0, 1), (0, 2))
        m2 = Move((0, 1), (0, 2))
        self.assertEqual(m1, m2)
        m3 = Move((1, 1), (0, 2))
        self.assertNotEqual(m1, m3)

class TestBoard(unittest.TestCase):
    def setUp(self):
        self.board = Board()

    def test_parse_fen(self):
        self.board.parse_fen(STARTING_FEN)
        self.assertEqual(self.board.generate_fen(), STARTING_FEN)

    def test_generate_fen(self):
        fen = self.board.generate_fen()
        self.assertEqual(fen, STARTING_FEN)

    def test_make_and_undo_move(self):
        initial_fen = self.board.generate_fen()
        move = Move((0, 1), (0, 3))
        self.board.make_move(move)
        self.board.undo_move()
        self.assertEqual(self.board.generate_fen(), initial_fen)

    def test_pawn_moves(self):
        self.board.parse_fen(STARTING_FEN)
        pawn_moves = self.board.generate_pawn_moves(self.board.get_piece((0, 1)))
        expected_moves = [Move((0, 1), (0, 2)), Move((0, 1), (0, 3))]
        self.assertEqual(pawn_moves, expected_moves)

    def test_rook_moves(self):
        self.board.parse_fen("8/8/8/8/8/8/R7/8 w - - 0 1")
        rook_moves = self.board.generate_rook_moves(self.board.get_piece((0, 1)))
        self.assertIn(Move((0, 1), (0, 7)), rook_moves)

    def test_king_moves(self):
        self.board.parse_fen("8/8/8/4K3/8/8/8/8 w - - 0 1")
        king_moves = self.board.generate_king_moves(self.board.get_piece((4, 4)))
        expected_moves = [Move((4, 4), (5, 4)), Move((4, 4), (3, 4))]
        self.assertIn(expected_moves[0], king_moves)
        self.assertIn(expected_moves[1], king_moves)

    def test_is_check(self):
        self.board.parse_fen("4k3/8/8/8/8/4R3/8/4K3 w - - 0 1")
        self.assertTrue(self.board.is_check(False))
        self.board.parse_fen("4k3/8/8/8/8/8/8/4K3 w - - 0 1")
        self.assertFalse(self.board.is_check(False))

    def test_is_checkmate(self):
        self.board.parse_fen("R3k3/8/4K3/8/8/8/8/8 b - - 0 1")
        self.assertTrue(self.board.is_checkmate())
        self.board.parse_fen("4k3/8/8/8/8/8/8/4K3 w - - 0 1")
        self.assertFalse(self.board.is_checkmate())

    def test_is_draw(self):
        self.board.parse_fen("4k3/7n/8/8/8/8/8/4K3 w - - 50 1")
        self.assertTrue(self.board.is_draw())
        self.board.parse_fen("4k3/8/8/8/8/8/8/4K3 w - - 0 1")
        self.assertTrue(self.board.is_draw())

    def test_is_stalemate(self):
        self.board.parse_fen("4k3/2Q3K1/8/8/8/8/8/8 b - - 0 1")
        self.assertTrue(self.board.is_stalemate())

    def test_is_insufficient_material(self):
        self.board.parse_fen("4k3/8/8/8/8/8/8/4K3 w - - 0 1")
        self.assertTrue(self.board.is_insufficient_material())

    def test_is_game_over(self):
        self.board.parse_fen("4k3/8/8/8/8/8/2Q5/4K3 w - - 0 1")
        self.assertFalse(self.board.is_game_over())
        self.board.parse_fen("4k3/8/8/8/8/8/8/4K3 w - - 0 1")
        self.assertTrue(self.board.is_game_over())

    def test_moving_to_check_enemy_king(self):
        self.board.parse_fen("4k3/8/4K3/8/8/8/8/3Q4 w - - 0 1")
        move = Move((3, 0), (3, 6))
        self.board.make_move(move)
        self.assertFalse(self.board.is_game_over())
        only_legal_move = Move((4, 7), (5, 7))
        legal_moves = self.board.generate_legal_moves()
        self.assertIn(only_legal_move, legal_moves)
        move = Move((3, 6), (5, 6))
        self.board.make_move(move)
        self.board.white_to_move = not self.board.white_to_move
        self.assertTrue(self.board.is_checkmate()) # <- fails

if __name__ == '__main__':
    unittest.main()