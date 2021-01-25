import unittest
from main import Minesweeper

class TestsMinesweeper(unittest.TestCase):
    def test_getNeighbors(self):
        minesweeper = Minesweeper()
        self.assertEqual(False, True)


if __name__ == '__main__':
    unittest.main()

