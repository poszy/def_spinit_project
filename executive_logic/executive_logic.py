from board.board import Board
from score_keeper.score_keeper import ScoreKeeper
from ui.user_interface import UserInterface
from wheel.wheel import Wheel, Sector
from server import GameServer
from server import Message, MessageType
from enum import Enum
import time

MAX_SPINS = 50


class QueryStatus(Enum):
    SERVER_TO_CLIENT = 1  # Information is being sent from Executive Logic to Server to Client
    CLIENT_TO_SERVER = 2  # Information is being sent from Client to Server to Executive Logic
    STANDBY = 3  # No information is being sent right now


class ExecutiveLogic:
    def __init__(self, srv_ip, srv_port):
        self.board = Board()  # Board object
        self.score_keeper = ScoreKeeper()  # ScoreKeeper object
        self.wheel = Wheel(["food", "politics", "history", "math", "sports"])  # Wheel object
        self.ui = UserInterface()  # UI Object
        self.game_server = GameServer(srv_ip, srv_port, self)  # GameServer object

        self.is_game_running = True  # True if game is ongoing, False otherwise
        self.num_spins = 0  # Number of times wheel has been spun this round (round ends after MAX_SPINS)

        self.query_status = QueryStatus.STANDBY
        self.query_response = Message(MessageType.EMPTY, [])

    def __execute_category(self, jeopardy_category, player_id, round_num):
        """
        Controls the flow of a Jeopardy question. Called when a "category" sector is the result of a wheel spin.
        :param jeopardy_category: Name of jeopardy category
        :return: void
        """
        tile = self.board.get_tile(jeopardy_category, round_num)  # Get tile from board
        self.__query_server(MessageType.JEOPARDY_QUESTION, [player_id, tile])  # Display tile to user, wait for response
        _, [user_answer] = self.query_response.code, self.query_response.args
        is_correct, points = tile.check_answer(user_answer)
        self.score_keeper.update_score(player_id, is_correct, points)
        self.__update_scores_tokens_spins()

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

        elif wheel_result == Sector.LOSE_TURN:  # If result is another wheel sector, handle logic
            # TODO: Rewrite to prompt player to use token. Currently just uses a token if it's available.
            if self.score_keeper.use_token(curr_player_id)[0]:  # Use token if available
                self.__update_scores_tokens_spins()
                self.__execute_turn(curr_player_id, round_num)  # Spin again
            else:  # Otherwise, end player turn
                return

        elif wheel_result == Sector.FREE_TURN:
            self.score_keeper.add_token(curr_player_id)  # Give the player a token
            self.__update_scores_tokens_spins()
            self.__execute_turn(curr_player_id, round_num)  # Spin

        elif wheel_result == Sector.BANKRUPT:
            self.score_keeper.bankrupt(curr_player_id)
            self.__update_scores_tokens_spins()
            return  # End player turn

        elif wheel_result == Sector.PLAYERS_CHOICE:
            self.__query_server(MessageType.PLAYERS_CHOICE, [curr_player_id, round_num])
            _, [chosen_category] = self.query_response
            self.__execute_category(chosen_category, curr_player_id, round_num)

        elif wheel_result == Sector.OPPONENTS_CHOICE:
            self.__query_server(MessageType.OPPONENTS_CHOICE, [curr_player_id, round_num])
            _, [chosen_category] = self.query_response
            self.__execute_category(chosen_category, curr_player_id, round_num)

        elif wheel_result == Sector.SPIN_AGAIN:
            self.__execute_turn(curr_player_id, round_num)  # Spin again

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
            curr_player_id = self.__next_player(curr_player_id)
            self.__query_server(MessageType.SPIN, [curr_player_id])  # Notify player that it's their turn,  ask them to push a button to spin the wheel, and wait for their response
            self.__execute_turn(curr_player_id, round_num)

        pass

    def run_game(self):
        """
        Main game loop. Controls logic through the flow of the entire game.
        :return:
        """
        self.is_game_running = True

        for round_num in [1, 2]:
            self.board.reset_board(round_num)
            self.__execute_round(round_num)

        self.__end_game()

    def __end_game(self):
        """
        Handles end-of-game logic. Called once, after the last round has ended.
        :return: void
        """
        winner_id = self.score_keeper.determine_winner()
        self.__query_server(MessageType.END_GAME, [winner_id])  # Tell server who won, and to end game
        self.is_game_running = False

    def __next_player(self, curr_player_id):
        """
        Increments ID of current player (self.curr_player_id). In a 3-player game, cycles between 0, 1, and 2.
        :return: void
        """

        if curr_player_id is None:
            return 0
        else:
            return (curr_player_id + 1) % self.game_server.players.count()

    def __spin_wheel(self):
        """
        Called whenever the wheel must be spun. Increments spin counter and returns spin result.
        :return: Result of wheel spin
        """
        self.num_spins += 1
        return self.wheel.get_spin_result()

    def __query_server(self, command: MessageType, args: list):
        """
        Called whenever information must be obtained from the server (e.g. asking the user for something).
        :param command: (QueryCommand) The command to be executed, like "SPIN" or "SEE_SCORE"
        :param args: (list) Any additional arguments that must be sent to the server
        :return: void
        """
        self.query_response = Message(MessageType.EMPTY, [])  # Clear server's previous response
        self.query_status = QueryStatus.SERVER_TO_CLIENT  # Tell server we want to query client
        self.server_message = Message(command, args)  # Store the query in self.server_message for server to read

        while self.query_response.code is not command:  # Wait for a response of the right type from the server
            time.sleep(0.1)
            pass

        self.query_status = QueryStatus.STANDBY  # Reset query status to standby

    def store_query(self, command: MessageType, args: list):
        """
        Called by the server to return the result of a query from __query_server.
        :param command: (QueryCommand) The command that was executed, like "SPIN" or "SEE_SCORE"
        :param args: (list) Any information that must be returned to ExecLogic
        :return: void
        """
        self.query_response = (command, args)  # Store server response in self.query_response

    def __update_scores_tokens_spins(self):
        self.__query_server(MessageType.UPDATE_SCORES,
                            [self.score_keeper.get_scores(), self.score_keeper.get_tokens(), self.num_spins])

    ########
    # TODO: All methods below this point may be deprecated?
    ########
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
