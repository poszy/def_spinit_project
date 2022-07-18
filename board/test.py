import unittest

import board
import questions


class Test_Board_and_Question(unittest.TestCase):

    def test_get_tile(self):
        a = board.Board()
        exp_tiles = [{'question': 'politics question 1', 'answers': 'a, b, c, d', 'rAnswer': 'c', 'points': 100},
                     {'question': 'politics question 2', 'answers': 'a, b, c, d', 'rAnswer': 'c', 'points': 200},
                     {'question': 'politics question 3', 'answers': 'a, b, c, d', 'rAnswer': 'c', 'points': 400},
                     {'question': 'politics question 4', 'answers': 'a, b, c, d', 'rAnswer': 'c', 'points': 800}]

        for it in range(4):
            ret_quest = a.get_tile("politics", 1)
            self.assertEqual(ret_quest, exp_tiles[it])

        # category is empty
        empty_category_ret = a.get_tile("politics", 1)
        self.assertEqual(empty_category_ret, None)

        not_category_ret = a.get_tile("TUBBYWUBBY", 2)
        self.assertEqual(not_category_ret, None)

    def test_get_available_categories(self):
        b = board.Board()
        exp_tiles = [
            {'question': 'food question 1', 'answers': 'a, b, c, d', 'rAnswer': 'c', 'points': 100},
            {'question': 'food question 2', 'answers': 'a, b, c, d', 'rAnswer': 'c', 'points': 200},
            {'question': 'food question 3', 'answers': 'a, b, c, d', 'rAnswer': 'c', 'points': 400},
            {'question': 'food question 4', 'answers': 'a, b, c, d', 'rAnswer': 'c', 'points': 800}, ]
        avail = b.get_available_categories(1)
        self.assertIs(type(avail), list)
        self.assertEqual(len(avail), 2)


        for it in range(4):
            ret_quest = b.get_tile("food", 1)
        self.assertEqual(ret_quest, exp_tiles[it])

        # category is empty
        empty_category_ret = b.get_tile("food", 1)
        self.assertEqual(empty_category_ret, None)

        # category is empty

        avail = b.get_available_categories(1)
        # self.assertEqual(len(avail), 1)  # note yet implemented

        pass



if __name__ == '__main__':
    unittest.main()
