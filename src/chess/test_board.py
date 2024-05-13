import unittest
from board import Board
from pieces import Piece

STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

checkmate_position = "1r5K/r7/8/8/8/8/8/3k4 w - - 0 1"
stalemate_position = "7K/r7/8/8/8/8/8/3k2r1 w - - 0 1"

class TestChessBoard(unittest.TestCase):
    def setUp(self):
        """Set up a new chess board for each test."""
        self.board = Board()
        self.board.init_board()

    def test_init_board(self):
        """Test if the board initializes correctly with the starting FEN."""
        self.assertEqual(self.board.generate_FEN(), STARTING_FEN)

    def test_set_board(self):
        """Test setting a custom board setup."""
        custom_board = [[None] * 8 for _ in range(8)]
        custom_board[0][0] = Piece('R')  # Example: place a rook at 0,0
        self.board.set_board(custom_board)
        self.assertIsInstance(self.board.get_piece(0, 0), Piece)

    def test_get_piece(self):
        """Test retrieving a piece from a specified location."""
        self.board.select_piece(0, 1)  # Select knight
        piece = self.board.get_piece(0, 1)
        self.assertIsInstance(piece, Piece)
        self.assertEqual(piece.type, 'N')

    def test_is_piece(self):
        """Test checking if there is a piece at the specified location."""
        self.assertTrue(self.board.is_piece(0, 0))  # Starting position rook
        self.assertFalse(self.board.is_piece(3, 3))  # Empty space at start

    def test_select_and_deselect_piece(self):
        """Test selecting and deselecting a piece."""
        self.board.select_piece(0, 1)  # Select knight
        self.assertEqual(self.board.selected_piece, [0, 1])
        self.board.deselect_piece()
        self.assertIsNone(self.board.selected_piece)

    def test_piece_selected(self):
        """Test if a piece is currently selected."""
        self.assertFalse(self.board.piece_selected())
        self.board.select_piece(0, 1)
        self.assertTrue(self.board.piece_selected())

    def test_move_piece(self):
        """Test moving a piece to a new location."""
        self.board.select_piece(1, 4)  # Select pawn
        self.board.make_move(3, 4)  # Move pawn two spaces forward
        self.assertIsNone(self.board.get_piece(1, 4))  # Old position empty
        self.assertIsInstance(self.board.get_piece(3, 4), Piece)  # New position has pawn

    def test_has_legal_moves(self):
        """Test checking for legal moves available for a piece."""
        self.board.select_piece(0, 1)  # Select knight
        self.assertTrue(self.board.has_legal_moves(0, 1))  # Knights have moves at start

    def test_is_game_over(self):
        """Test if the game over check works correctly."""
        self.assertFalse(self.board.is_game_over())  # At start, game is not over

    def test_is_stalemate(self):
        """Test stalemate detection."""
        # Setup a stalemate position manually or through a series of moves
        self.assertFalse(self.board.is_stalemate())  # Not a stalemate at start

    def test_is_checkmate(self):
        """Test checkmate detection."""
        self.assertFalse(self.board.is_checkmate())  # Not a checkmate at start

    def test_ally_king_in_check(self):
        """Test detection of the ally king being in check."""
        self.assertFalse(self.board.ally_king_in_check())  # At start, no check

    def test_make_move(self):
        """Test making a move and updating game state."""
        initial_fen = self.board.generate_FEN()
        self.board.select_piece(1, 4)  # Select pawn
        self.board.make_move(2, 4)  # Move forward one space
        self.assertNotEqual(self.board.generate_FEN(), initial_fen)

    def test_undo_move(self):
        """Test undo functionality to revert the last move."""
        initial_fen = self.board.generate_FEN()
        self.board.select_piece(1, 4)  # Select pawn
        self.board.make_move(2, 4)  # Move forward one space
        self.board.undo_move()  # Undo the move
        self.assertEqual(self.board.generate_FEN(), initial_fen)

    def test_FEN_to_board_and_generate_FEN(self):
        """Test FEN string conversion to board setup and vice versa."""
        fen = "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq - 0 1"
        self.board.FEN_to_board(fen)
        self.assertEqual(self.board.generate_FEN(), fen)

    def test_board_initialization(self):
        """Test board initialization to the starting position."""
        self.assertEqual(self.board.generate_FEN(), STARTING_FEN)

    def test_select_piece(self):
        """Test selecting a piece on the board."""
        self.board.select_piece(0, 0)  # Selecting a rook at the starting position
        self.assertEqual(self.board.selected_piece, [0, 0])

    def test_checkmate(self):
        """Test checkmate detection."""
        # You would set up a board state here that represents a checkmate scenario
        # For simplicity, assume we set it up directly or simulate moves to reach that state
        self.board.FEN_to_board(checkmate_position)
        self.assertTrue(self.board.is_checkmate())

    def test_stalemate(self):
        """Test stalemate detection."""
        # Similar to checkmate, set up a stalemate position
        self.board.FEN_to_board(stalemate_position)
        self.assertTrue(self.board.is_stalemate())

    def test_legal_moves(self):
        """Test the generation of legal moves."""
        # Setup the board in a certain configuration, and check if the generated legal moves are correct
        self.board.select_piece(0, 1)  # Select knight at the beginning
        moves = self.board.get_legal_moves(0, 1)
        expected_moves = [(2, 0), (2, 2)]  # Assuming only these two moves are legal
        self.assertEqual(set(moves), set(expected_moves))

if __name__ == '__main__':
    unittest.main()
