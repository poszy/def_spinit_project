from collections import defaultdict


class ScoreKeeper:

    # default constructor
    def __init__(self):
        self.var = "self"
        # given a new key, initializes value to 0. Note: point values can be negative
        self.player_points = defaultdict(int) # Dictionary of player_ids keys mapped to their overall scores for the game
        self.player_points_current_round = defaultdict(int) # Dictionary of player_ids mapped to their score for the round. Used to bankrupt players for the current round.
        # given a new key, initializes value to 0 Note: # of player_tokens cannot be negative!
        self.player_tokens = defaultdict(int)

    # interface
    def get_scores(self):
        """
            Gets the scores and player_tokens

            Args:


            Returns:
            scores: mapping of playerIDs to scores
        """
        return self.player_points

    # interface
    def get_tokens(self):
        """
            Gets the player_tokens

            Args:

            Returns:
            player_tokens: mappying of playerIDs to player_tokens
        """
        return self.player_tokens

    # interface
    def __has_token(self, player_id):
        """
        Checks to see if player has any tokens

        Args:
        player_id: the player's identifier

        Returns:
        a boolean. True if that player has 1+ player_tokens, false if player has no player_tokens
        """
        if player_id not in self.player_tokens.keys():  # in case someone replaced defaultdict with dict
            return False
        num_tokens = self.player_tokens[player_id]
        return num_tokens > 0

    # interface
    def use_token(self, player_id):
        """
            Use a token from the player's stash of player_tokens.

            Args:
            player_id: The identifier of the player using the token

            Returns:
            success: a boolean representing whether the call was success or failure
            player_tokens: a dict containing playerIDs mapped to their current token count
        """
        success = False
        if self.__has_token(player_id):
            # only remove token if player has at least one
            self.player_tokens[player_id] -= 1
            success = True
        return success, self.player_tokens

    # interface
    def bankrupt(self, player_id):
        """
            Bankrupt the given player for the current round.
            Business rules: player score goes to 0.

            Args:
            player_id: the player's identification number

            Returns:
            success: a boolean representing whether the bankrupt call was success or failure
        """
        success = True
        if self.player_points_current_round[player_id] > 0:
            self.player_points[player_id] -= self.player_points_current_round[player_id]
            self.player_points_current_round[player_id] = 0
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
        max_points = max(self.player_points.values())

        winners = list()  # winners will be empty list if no players
        for playerID, pts in self.player_points.items():
            if pts == max_points:
                winners.append(playerID)
        return winners

    def add_token(self, player_id):
        """
        Gives a player a token.
        :param player_id: 
        :return: 
        """""
        self.player_tokens[player_id] += 1

    def update_score(self, player_id, player_correct, points):
        """
        Changes a player's score.
        :param player_id: ID of player
        :param player_correct: (Boolean) True if player's answer was correct, False otherwise
        :param points: Number of points to add or subtract from player's total
        :return: void
        """
        if player_correct:
            self.player_points[player_id] += points
            self.player_points_current_round[player_id] += points
        else:
            self.player_points[player_id] -= points
            self.player_points_current_round[player_id] -= points

    def new_round(self):
        """
        Called when a new round begins.
        Resets every player's score for the current round (which is tracked separately from overall score) to 0.
        :return: void
        """
        self.player_points_current_round = defaultdict(int)

    def initialize_player(self, player_id):
        """
        Called at the start of the game.
        Lets scorekeeper know about a player in the game, and sets their scores to 0.
        :return: void
        """
        self.update_score(player_id, True, 0)