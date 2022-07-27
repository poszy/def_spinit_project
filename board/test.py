import unittest

import board
from questions import Questions, Tile


class Test_Board_and_Question(unittest.TestCase):

    def test_get_tile(self):
        a = board.Board()
        exp_tiles = {100: Tile('politics question 1', ['a', 'b', 'c'], 2, 100),
                     200: Tile('politics question 3', ['a', 'b', 'c'], 2, 200),
                     400: Tile('politics question 3', ['a', 'b', 'c'], 2, 400),
                     800: Tile('politics question 4', ['a', 'b', 'c'], 2, 800)
                     }

        for it in range(4):
            ret_quest = a.get_tile("politics", 1)
            self.assertEqual(ret_quest.points, exp_tiles[100*(2**it)].points)

        # category is empty
        empty_category_ret = a.get_tile("politics", 1)
        self.assertFalse(empty_category_ret)

        not_category_ret = a.get_tile("TUBBYWUBBY", 2)
        self.assertFalse(not_category_ret)

    def test_check_answer(self):
        b = board.Board()

        t = b.get_tile("politics", 1)

        user_correct, points = t.check_answer(1)
        self.assertFalse(user_correct)
        self.assertEqual(points, 100)
        user_correct, points = t.check_answer(2)
        self.assertTrue(user_correct)
        self.assertEqual(points, 100)

    def test_get_available_categories(self):
        b = board.Board()
        exp_tiles = {100: Tile('food question 1', ['a', 'b', 'c'], 2, 100),
                     200: Tile('food question 3', ['a', 'b', 'c'], 2, 200),
                     400: Tile('food question 3', ['a', 'b', 'c'], 2, 400),
                     800: Tile('food question 4', ['a', 'b', 'c'], 2, 800)
                     }
        avail = b.get_available_categories(1)
        self.assertIs(type(avail), list)
        self.assertEqual(len(avail), 2)

        for it in range(4):
            ret_quest = b.get_tile("food", 1)
            self.assertEqual(ret_quest.points, exp_tiles[100 * (2 ** it)].points)

        # category is empty
        empty_category_ret = b.get_tile("food", 1)
        self.assertFalse(empty_category_ret)

        # category is empty

        avail = b.get_available_categories(1)
        # self.assertEqual(len(avail), 1)  # note yet implemented

        pass


if __name__ == '__main__':
    unittest.main()
