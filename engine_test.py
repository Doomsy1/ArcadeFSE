from src.chess.engine import evaluate, Engine
from src.chess.board import Board
import unittest

class TestEngine(unittest.TestCase):
    def test_evaluate(self):
        b = Board()
        evaluation = evaluate(b)
        self.assertEqual(evaluation, 0)


if __name__ == "__main__":
    unittest.main()