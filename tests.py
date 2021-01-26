import unittest
from main import MagicMinesweeper
from tkinter import Tk
from collections import deque

minesweeper = MagicMinesweeper(Tk())

class TestsMinesweeper(unittest.TestCase):
    def test_get_neighbors(self):
        minesweeper.restart()
        neighbors = minesweeper.get_neighbors(0, 0)
        self.assertEqual(3, len(neighbors))
        n = neighbors[0]["coordinates"]["x"]
        self.assertEqual(True, (n == 0 or 1) and n != -1)
        self.assertEqual(0, n)

        neighbors = minesweeper.get_neighbors(4, 5)
        self.assertEqual(8, len(neighbors))

        neighbors = minesweeper.get_neighbors(8, 9)
        self.assertEqual(5, len(neighbors))

    def test_refresh_labels(self):
        minesweeper.restart()
        minesweeper.flagCount = 2
        minesweeper.refresh_labels()
        self.assertEqual("Flags: " + str(minesweeper.flagCount), minesweeper.labels["flags"].cget('text'))
        minesweeper.mines = 5
        minesweeper.refresh_labels()
        self.assertEqual("Mines: " + str(minesweeper.mines), minesweeper.labels["mines"].cget('text'))

    def test_on_click(self):
        minesweeper.restart()
        #afterMagicField
        minesweeper.afterMagicField = True
        minesweeper.on_click(minesweeper.fields[2][2])
        image = minesweeper.fields[2][2]["button"].cget('image')
        self.assertEqual(minesweeper.images["plain"].name, image)
        self.assertEqual(False, minesweeper.afterMagicField)

        minesweeper.restart()
        #isMine
        minesweeper.afterMagicField = False
        field = minesweeper.fields[1][0]
        field["isMine"] = True
        minesweeper.on_click(field)
        image = field["button"].cget('image')
        self.assertEqual(minesweeper.images["mine"].name, image)

        minesweeper.restart()
        # magic
        minesweeper.afterMagicField = False
        field = minesweeper.fields[1][0]
        field["magic"] = True
        minesweeper.on_click(field)
        self.assertEqual(True, minesweeper.afterMagicField)

    def test_on_right_click(self):
        minesweeper.restart()
        # flagged
        field = minesweeper.fields[1][1]
        field["state"] = 2
        minesweeper.on_right_click(field)
        image = field["button"].cget('image')
        self.assertEqual(minesweeper.images["plain"].name, image)

        minesweeper.restart()
        # plain
        field = minesweeper.fields[1][0]
        field["state"] = 0
        minesweeper.on_right_click(field)
        image = field["button"].cget('image')
        self.assertEqual(minesweeper.images["flag"].name, image)

    def test_clear_field(self):
        minesweeper.restart()
        q = deque()
        field = minesweeper.fields[5][5]
        field["mines"] = 0
        minesweeper.clear_field(field, q)
        image = field["button"].cget('image')
        self.assertEqual(minesweeper.images["clicked"].name, image)
        self.assertEqual(1, len(q))

if __name__ == '__main__':
    unittest.main()


