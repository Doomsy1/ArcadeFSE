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

    
if __name__ == '__main__':
    unittest.main()