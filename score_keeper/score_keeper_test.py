import unittest
from score_keeper import ScoreKeeper
from collections import defaultdict

class MyTestCase(unittest.TestCase):
	# def __init__(self):
	# 	self.scorekeeper = ScoreKeeper()

	def test_check_answer(self):
		self.scorekeeper = ScoreKeeper()

		user_correct, updated_points = self.scorekeeper.check_answer("ansA", "ansB", 100, 0)
		self.assertFalse(user_correct)
		self.assertEqual(updated_points, {0: -100})

	def test_tally_points(self):
		self.scorekeeper = ScoreKeeper()

		updated_points = self.scorekeeper.tally_points(False, 10, -1)
		self.assertDictEqual(updated_points, {-1: -10})  # negative player ID int
		updated_points = self.scorekeeper.tally_points(False, 10, -1.0)  # negative player ID float
		self.assertDictEqual(updated_points, {-1: -20})
		updated_points = self.scorekeeper.tally_points(True, -110, 4)  # negative point value
		self.assertDictEqual(updated_points, {-1: -20, 4: -110})
		updated_points = self.scorekeeper.tally_points(True, 100, "Player1")
		self.assertDictEqual(updated_points, {-1: -20, 4: -110, "Player1": 100})  # string player ID
		updated_points = self.scorekeeper.tally_points(True, 100, 3)
		self.assertDictEqual(updated_points, {-1: -20, 4: -110, "Player1": 100, 3: 100})  # add points
		updated_points = self.scorekeeper.tally_points(True, 110, 4)
		self.assertDictEqual(updated_points, {-1: -20, 4: 0, "Player1": 100, 3: 100})  # points back to zero
		self.assertEqual(updated_points[555], 0)  # point value for new player

	def test_has_token(self):
		scorekeeper = ScoreKeeper()
		self.assertIs(type(scorekeeper.has_token("playerA")), bool)
		self.assertFalse(scorekeeper.has_token("playerA"))
		scorekeeper.playerTokens["playerA"] = 2  # give this player multiple tokens
		self.assertTrue(scorekeeper.has_token("playerA"))
		self.assertFalse(scorekeeper.has_token("playerB"))  # not in token dict
		self.assertFalse(scorekeeper.has_token(2))

	def test_use_token(self):
		scorekeeper = ScoreKeeper()
		unsuccess, new_tokens = scorekeeper.use_token("playerA")
		self.assertFalse(unsuccess)  # player has no playerTokens
		self.assertIs(type(new_tokens), defaultdict)

		scorekeeper.playerTokens = {"playerA": -3}  # assign negative playerTokens
		unsuccess2, neg_tokens = scorekeeper.use_token("playerA")
		self.assertEqual(neg_tokens["playerA"], -3)
		self.assertFalse(unsuccess2)  # player has negative playerTokens

		scorekeeper.playerTokens = {101: 3}  # positive playerTokens
		self.assertEqual(scorekeeper.playerTokens[101], 3)
		for tk in [2, 1, 0]:
			success, pos_tokens = scorekeeper.use_token(101)
			self.assertTrue(success)
			self.assertEqual(scorekeeper.playerTokens[101], tk)

		unsuccess, zero_tokens = scorekeeper.use_token(101)  # zero playerTokens
		self.assertFalse(unsuccess)
		self.assertEqual(zero_tokens[101], 0)

	def test_get_tokens(self):
		scorekeeper = ScoreKeeper()
		tokens_dict = {101: 3}
		scorekeeper.playerTokens = tokens_dict # positive playerTokens
		self.assertEqual(scorekeeper.get_tokens(), tokens_dict)


	def test_get_scores(self):
		scorekeeper = ScoreKeeper()
		scores_dict = {101: 3}
		scorekeeper.playerPoints = scores_dict # positive playerTokens
		self.assertEqual(scorekeeper.get_scores(), scores_dict)


	def test_bankrupt(self):
		pass

	def test_determine_winner(self):
		pass


if __name__ == '__main__':
	unittest.main()
