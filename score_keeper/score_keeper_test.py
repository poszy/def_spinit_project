import unittest
from score_keeper import ScoreKeeper


class MyTestCase(unittest.TestCase):
	def test_something(self):
		scorekeeper = ScoreKeeper()

		user_correct, updated_points = scorekeeper.check_answer("ansA", "ansB", 100, 0)
		self.assertEqual(user_correct, False)
		self.assertEqual(updated_points, {0: -100})


if __name__ == '__main__':
	unittest.main()
