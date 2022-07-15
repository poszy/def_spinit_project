from collections import defaultdict


class ScoreKeeper:

    # default constructor
    def __init__(self):
        self.var = "self"
        # given a new key, initializes value to 0. Note: point values can be negative
        self.playerPoints = defaultdict(int)
        # given a new key, initializes value to 0 Note: # of tokens cannot be negative!
        self.tokens = defaultdict(int)

    def tally_points(self, user_correct, points, player_id):
        """
            Gets the new playerPoints totals

            Args:
            category: A string containing a category from the board.

            Returns:
            userCorrect: a boolean representing whether or not the user's selection was correct
        """
        if user_correct:
            self.playerPoints[player_id] += points
        else:
            self.playerPoints[player_id] -= points  # playerPoints can be negative
        return self.playerPoints

    # interface
    def check_answer(self, user_answer, actual_answer, points, player_id):
        """
            Gets the next question in point value from the board.

            Args:
            userAnswer: A string containing user's answer selection.
            actualAnswer: A string containing actual answer.
            playerPoints: mapping of playerIDs to their point totals
            player_id: the player who answered

            Returns:
            user_correct: a boolean representing whether or not the user's selection was correct
        """
        user_correct = (user_answer == actual_answer)

        updated_points = self.tally_points(user_correct, points, player_id)
        return user_correct, updated_points

    # interface
    def has_token(self, player_id):
        """Checks to see if there are any available questions in a category.

            Args:
            category: A string containing a category from the board.

            Returns:
            a boolean. True if that player has 1+ tokens, false if player has no tokens
        """
        return self.tokens[player_id] > 0

    # interface
    def use_token(self, player_id):
        """
            Use a token from the player's stash of tokens.

            Args:
            player_id: The identifier of the player using the token

            Returns:
            success: a boolean representing whether the call was success or failure
            tokens: a dict containing playerIDs mapped to their current token count
        """
        success = False
        if self.has_token(player_id):
            # only remove token if player has at least one
            self.tokens[player_id] -= 1
            success = True
        return success, self.tokens

    # interface
    def bankrupt(self, player_id):
        """
            Bankrupt the given player.
            Business rules: player score goes to 0. Player tokens set to 0.

            Args:
            player_id: the player's identification number

            Returns:
            success: a boolean representing whether the bankrupt call was success or failure
        """
        success = False
        self.playerPoints[player_id] = 0
        self.tokens[player_id] = 0
        return success

    def determine_winner(self):
        """
            Figures out who won.
            Assumes: players can tie

            Args:

            Returns:
            winners: list containing player_id(s) of the winner(s)
        """
        # don't want to just use builtin max, it will only return 1st encountered
        max_points = max(self.playerPoints.values())

        winners = list()  # winners will be empty list if no players
        for playerID, pts in self.playerPoints.items():
            if pts == max_points:
                winners.append(playerID)
        return winners
