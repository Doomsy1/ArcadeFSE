import unittest
from board import *

INITIAL_BOARD = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

# A position where white is checkmated
WHITE_CHECKMATED_BOARD = '3K2r1/7r/8/8/8/8/8/3k4 w - - 0 1'

# A position where black is checkmated
BLACK_CHECKMATED_BOARD = '3K4/8/8/8/8/8/6R1/3k3R w - - 0 1'

# A position where white is stalemated
WHITE_STALEMATED_BOARD = '3K4/1k3q2/8/8/8/8/8/8 w - - 0 1'

# A position where black is stalemated
BLACK_STALEMATED_BOARD = '3K4/8/8/8/8/8/1Q3Q2/3k4 w - - 0 1'


class TestBoard(unittest.TestCase):
    def setUp(self):
        self.board = Board()

    def test_is_piece(self):
        self.assertTrue(self.board.is_piece(0))
        self.assertTrue(self.board.is_piece(16))
        self.assertFalse(self.board.is_piece(32))

    def test_is_empty(self):
        self.assertFalse(self.board.is_empty(0))
        self.assertTrue(self.board.is_empty(32))

    def test_is_white(self):
        self.assertTrue(self.board.is_white(0))
        self.assertFalse(self.board.is_white(112))

    def test_is_black(self):
        self.assertTrue(self.board.is_black(112))
        self.assertFalse(self.board.is_black(1))

    def test_is_pawn(self):
        self.assertTrue(self.board.is_pawn(16))
        self.assertFalse(self.board.is_pawn(1))

    def test_is_knight(self):
        self.assertFalse(self.board.is_knight(0))
        self.assertTrue(self.board.is_knight(1))

    def test_is_bishop(self):
        self.assertTrue(self.board.is_bishop(2))
        self.assertFalse(self.board.is_bishop(1))

    def test_is_rook(self):
        self.assertTrue(self.board.is_rook(0))
        self.assertFalse(self.board.is_rook(1))

    def test_is_queen(self):
        self.assertTrue(self.board.is_queen(3))
        self.assertFalse(self.board.is_queen(4))

    def test_is_king(self):
        self.assertFalse(self.board.is_king(3))
        self.assertTrue(self.board.is_king(4))

    def test_get_piece(self):
        self.assertEqual(self.board.get_piece(16), 0b1001)
        self.assertEqual(self.board.get_piece(0), 0b1100)

    def test_set_piece(self):
        self.board.set_piece(0b1010, 32) # 0b1010 is a knight
        self.assertTrue(self.board.piece_bitboards[0b1010] & (1 << 32)) # 32nd bit is set to 1
        self.assertFalse(self.board.empty_squares_bitboard & (1 << 32)) # 32nd bit is set to 0
        self.assertTrue(self.board.colour_bitboards[0b1] & (1 << 32)) # 32nd bit is set to 1

    def test_clear_square(self):
        self.board.clear_square(0)
        self.assertTrue(self.board.empty_squares_bitboard & (1 << 0)) # 0th bit is set to 1
        self.assertFalse(self.board.colour_bitboards[0b1] & (1 << 0)) # 0th bit is set to 0
        self.assertTrue(self.board.empty_squares_bitboard & (1 << 0)) # 0th bit is set to 1

    def test_move_piece(self):
        self.board.move_piece(0b1001, 16, 32) # move the pawn from 16 to 32
        self.assertTrue(self.board.piece_bitboards[0b1001] & (1 << 32)) # 32nd bit is set to 1
        self.assertFalse(self.board.piece_bitboards[0b1001] & (1 << 16)) # 16th bit is set to 0
        self.assertTrue(self.board.colour_bitboards[0b1] & (1 << 32)) # 32nd bit is set to 1
        self.assertFalse(self.board.colour_bitboards[0b1] & (1 << 16)) # 16th bit is set to 0
        self.assertTrue(self.board.empty_squares_bitboard & (1 << 16)) # 16th bit is set to 1
        self.assertFalse(self.board.empty_squares_bitboard & (1 << 32)) # 32nd bit is set to 0

    def test_load_fen(self):
        self.board.load_fen(INITIAL_BOARD)

        # white pawns
        self.assertTrue(self.board.piece_bitboards[0b1001] & (1 << 16)) # 16th bit is set to 1
        self.assertTrue(self.board.piece_bitboards[0b1001] & (1 << 17)) # 17th bit is set to 1

        # black pawns
        self.assertTrue(self.board.piece_bitboards[0b0001] & (1 << 96)) # 96th bit is set to 1
        self.assertTrue(self.board.piece_bitboards[0b0001] & (1 << 97)) # 97th bit is set to 1

        # white knights
        self.assertTrue(self.board.piece_bitboards[0b1010] & (1 << 1)) # 1st bit is set to 1
        self.assertTrue(self.board.piece_bitboards[0b1010] & (1 << 6)) # 6th bit is set to 1

        # black knights
        self.assertTrue(self.board.piece_bitboards[0b0010] & (1 << 113)) # 113th bit is set to 1
        self.assertTrue(self.board.piece_bitboards[0b0010] & (1 << 118)) # 118th bit is set to 1

        # white bishops
        self.assertTrue(self.board.piece_bitboards[0b1011] & (1 << 2)) # 2nd bit is set to 1
        self.assertTrue(self.board.piece_bitboards[0b1011] & (1 << 5)) # 5th bit is set to 1

        # black bishops
        self.assertTrue(self.board.piece_bitboards[0b0011] & (1 << 114)) # 114th bit is set to 1
        self.assertTrue(self.board.piece_bitboards[0b0011] & (1 << 117)) # 117th bit is set to 1

        # white rooks
        self.assertTrue(self.board.piece_bitboards[0b1100] & (1 << 0)) # 0th bit is set to 1
        self.assertTrue(self.board.piece_bitboards[0b1100] & (1 << 7)) # 7th bit is set to 1

        # black rooks
        self.assertTrue(self.board.piece_bitboards[0b0100] & (1 << 112)) # 112th bit is set to 1
        self.assertTrue(self.board.piece_bitboards[0b0100] & (1 << 119)) # 119th bit is set to 1

        # white queen
        self.assertTrue(self.board.piece_bitboards[0b1101] & (1 << 3)) # 3rd bit is set to 1

        # black queen
        self.assertTrue(self.board.piece_bitboards[0b0101] & (1 << 115)) # 115th bit is set to 1

        # white king
        self.assertTrue(self.board.piece_bitboards[0b1110] & (1 << 4)) # 4th bit is set to 1

        # black king
        self.assertTrue(self.board.piece_bitboards[0b0110] & (1 << 116)) # 116th bit is set to 1

        # white colour bitboard
        self.assertTrue(self.board.colour_bitboards[0b1] & (1 << 0)) # 0th bit is set to 1

        # black colour bitboard
        self.assertTrue(self.board.colour_bitboards[0b0] & (1 << 112)) # 112th bit is set to 1


    def test_generate_fen(self):
        self.board.load_fen(INITIAL_BOARD)
        self.assertEqual(self.board.generate_fen(), INITIAL_BOARD)

    def test_make_move(self):
        move = encode_move(17, 33, 0b1001)
        self.board.make_move(move)
        self.assertTrue(self.board.piece_bitboards[0b1001] & (1 << 33)) # 33rd bit is set to 1
        self.assertTrue(self.board.colour_bitboards[0b1] & (1 << 33)) # 33rd bit is set to 1
        self.assertTrue(self.board.empty_squares_bitboard & (1 << 17)) # 17th bit is set to 1

    def test_undo_move(self):
        move = encode_move(18, 34, 0b1001)
        self.board.make_move(move)
        self.board.undo_move()
        self.assertTrue(self.board.piece_bitboards[0b1001] & (1 << 18)) # 18th bit is set to 1
        self.assertFalse(self.board.piece_bitboards[0b1001] & (1 << 34)) # 34th bit is set to 0
        self.assertTrue(self.board.colour_bitboards[0b1] & (1 << 18)) # 18th bit is set to 1
        self.assertTrue(self.board.empty_squares_bitboard & (1 << 34)) # 34th bit is set to 1

    def test_is_valid_square(self):
        self.assertTrue(self.board.is_valid_square(0))
        self.assertFalse(self.board.is_valid_square(128))

    def test_generate_sliding_moves(self):
        self.board.load_fen('3K4/8/8/3B4/3b4/8/5p2/3k4 w - - 0 1')
        moves = self.board.generate_sliding_moves(0b1011, 67, BISHOP_DIRECTIONS)
        self.assertEqual(len(moves), 13)

    def test_generate_knight_moves(self):
        self.board.load_fen('3K3N/8/8/8/3b4/8/5p2/3k4 w - - 0 1')
        moves = self.board.generate_knight_moves(0b1010, 119)
        self.assertEqual(len(moves), 2)

        self.board.load_fen('3K4/6N1/8/8/3b4/8/5p2/3k4 w - - 0 1')
        moves = self.board.generate_knight_moves(0b1010, 102)

    def test_generate_pawn_moves(self):
        moves = self.board.generate_pawn_moves(0b1001, 16)
        self.assertEqual(len(moves), 2)

    def test_generate_king_moves(self):
        self.board.load_fen('3K4/6N1/8/8/3b4/8/5p2/3k4 w - - 0 1')
        moves = self.board.generate_king_moves(0b1110, 115)
        self.assertEqual(len(moves), 5)

    def test_generate_moves(self):
        moves = self.board.generate_moves(True)
        self.assertEqual(len(moves), 20) # 20 legal moves in the initial position

    def test_is_check(self):
        self.assertFalse(self.board.is_check(True))
        self.assertFalse(self.board.is_check(False))

    def test_is_checkmate(self):
        # the initial position is not a checkmate
        self.assertFalse(self.board.is_checkmate(True))
        self.assertFalse(self.board.is_checkmate(False))

        self.board.load_fen(WHITE_CHECKMATED_BOARD)
        self.assertTrue(self.board.is_checkmate(True))

        self.board.load_fen(BLACK_CHECKMATED_BOARD)
        self.assertTrue(self.board.is_checkmate(False))

    def test_is_stalemate(self):
        # the initial position is not a stalemate
        self.assertFalse(self.board.is_stalemate(True))
        self.assertFalse(self.board.is_stalemate(False))

        self.board.load_fen(WHITE_STALEMATED_BOARD)
        self.assertTrue(self.board.is_stalemate(True))

        self.board.load_fen(BLACK_STALEMATED_BOARD)
        self.assertTrue(self.board.is_stalemate(False))

    def test_is_draw(self):
        # the initial position is not a draw
        self.assertFalse(self.board.is_draw())

    def test_generate_legal_moves(self):
        # the initial position has 20 legal moves
        moves = self.board.generate_legal_moves(True)
        self.assertEqual(len(moves), 20)

if __name__ == '__main__':
    unittest.main()