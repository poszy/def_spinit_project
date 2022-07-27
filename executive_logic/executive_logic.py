from board.board import Board
from score_keeper.score_keeper import ScoreKeeper
from ui.user_interface import UserInterface
from wheel.wheel import Wheel
from server import Messenger
from server import GameServer

MAX_SPINS = 50


class ExecutiveLogic:
    def __init__(self, srv_ip, srv_port):
        self.board = Board()
        self.score_keeper = ScoreKeeper()
        self.wheel = Wheel(["food", "politics", "history", "math", "sports"])
        self.ui = UserInterface()
        self.game_server = GameServer(srv_ip, srv_port, self)

        self.num_spins = 0

    def __execute_category(self, jeopardy_category, player_id, round_num):
        """
        Controls the flow of a Jeopardy question. Called when a "category" sector is the result of a wheel spin.
        :param jeopardy_category: Name of jeopardy category
        :return: void
        """
        tile = self.board.get_tile(jeopardy_category, round_num)
        # TODO: Display tile.question and tile.answers to user, wait for response
        user_answer = "Placeholder for the user's answer" # TODO: See line above
        is_correct, points = tile.check_answer(user_answer)
        self.score_keeper.update_score(player_id, is_correct, points)
        # TODO: Display updated point totals to UI

    def __execute_turn(self, curr_player_id, round_num):
        """
        Controls the flow of one turn. Called at the start of the turn.
        :param curr_player_id: ID of player whose turn is starting
        :return: void
        """
        if self.num_spins >= MAX_SPINS:
            return
        wheel_result = self.__spin_wheel()  # Spin wheel
        self.game_server.notify_spin_result(curr_player_id, wheel_result)

        if self.wheel.is_jeopardy_category(wheel_result):  # If result is a Jeopardy category, call execute_category
            self.__execute_category(wheel_result, curr_player_id, round_num)
        elif wheel_result == "lose_turn":  # If result is another wheel sector, handle logic
            # TODO: Rewrite to prompt player to use token. Currently just uses a token if it's available.
            if self.score_keeper.use_token(curr_player_id)[0]:  # Use token if available
                self.__execute_turn(curr_player_id, round_num)  # Spin again
            else:  # Otherwise, end player turn
                return
        elif wheel_result == "free_turn":  # TODO: These strings should be part of an enum that's shared with Wheel
            self.score_keeper.add_token(curr_player_id)
            self.__execute_turn(curr_player_id, round_num)  # Spin again
        elif wheel_result == "bankrupt":
            self.score_keeper.bankrupt(curr_player_id)
            return  # End player turn
        elif wheel_result == "players_choice":
            pass  # TODO
        elif wheel_result == "opponents_choice":
            pass  # TODO
        elif wheel_result == "spin_again":
            self.__execute_turn(curr_player_id, round_num)
        else:
            raise Exception("Wheel result '" + wheel_result + "' is not a valid wheel category!")

    def __execute_round(self, round_num):
        """
        Controls the flow of one round.
        :param round_num: Number of current round (1 or 2).
        :return: void
        """
        curr_player_id = None

        while self.num_spins < MAX_SPINS and self.board.get_available_categories(
                round_num):  # End round when spins >= 50 or no available questions
            self.__next_player(curr_player_id)
            # self.game_server.notify_player(curr_player_id) # TODO: Notify player that it's their turn, ask them to push a button to spin the wheel, and wait for their response.
            self.__execute_turn(curr_player_id, round_num)

        pass

    def run_game(self):
        """
        Main game loop. Controls logic through the flow of the entire game.
        :return:
        """
        for round_num in [1, 2]:
            self.board.reset_board(round_num)
            self.__execute_round(round_num)

        self.__end_game()

    def __end_game(self):
        winner_id = self.score_keeper.determine_winner()
        # TODO: Tell server who won, display info, end game

    def __next_player(self, curr_player_id):
        """
        Increments ID of current player (self.curr_player_id). In a 3-player game, cycles between 0, 1, and 2.
        :return: void
        """

        if curr_player_id is None:
            curr_player_id = 0
        else:
            curr_player_id += 1
            curr_player_id %= self.game_server.players.count()

    def __spin_wheel(self):
        self.num_spins += 1
        return self.wheel.get_spin_result()

    def notify_spin(self):
        self.num_spins += 1
        return self.num_spins

    def whose_turn(self,
                   curr_player_id):  # TODO: This method may require changing curr_player_id to a class variable, or passing the information down from Executive Logic to the class that needs it. Revisit later.
        """
        Returns name of the player who is currently taking their turn, or None if no one is currently taking a turn.
        :return: (string) Player name
        """
        if curr_player_id is None:
            return None
        else:
            return self.game_server.players[self.curr_player_id]

    def update_turn(self):
        # return the next player
        return "Luis"

    def select_rand_opponent(self):
        return "Opponent"
