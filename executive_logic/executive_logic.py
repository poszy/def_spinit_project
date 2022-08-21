from board.board import Board
from score_keeper.score_keeper import ScoreKeeper
from ui.user_interface import UserInterface
from wheel.wheel import Wheel, Sector
from server import GameServer, QueryStatus, Message, MessageType
import logging
import random

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter.messagebox import showinfo

MAX_SPINS = 50
NUM_ROUNDS = 2
MAX_NUM_PLAYERS = 3
DEFAULT_QUESTIONS_FILE = './JArchive-questions.csv'  # need to use relative path from current working directory of main.py!


class ExecutiveLogic:
    def __init__(self, srv_ip, srv_port):
        configuration = ConfigWindow()
        if not configuration.filename:  # in case did not select a file
            configuration.filename = DEFAULT_QUESTIONS_FILE  # need to use relative path from current working directory of main.py!
        self.board = Board(configuration.filename)  # Board object
        self.score_keeper = ScoreKeeper()  # ScoreKeeper object
        self.wheel = Wheel(self.board.get_available_categories(1))  # pull categories from board round 1
        # logging.info(f"added {self.board.get_available_categories(1)} sectors to wheel")
        self.ui = UserInterface()  # UI Object
        logging.info(f"Start server for {configuration.num_players.get()} player(s)")
        self.game_server = GameServer(srv_ip, srv_port, configuration.num_players.get(), self)  # GameServer object

        self.is_game_running = True  # True if game is ongoing, False otherwise
        self.num_spins = 0  # Number of times wheel has been spun this round (round ends after MAX_SPINS)

        self.query_status = QueryStatus.STANDBY
        self.query_response = Message(MessageType.EMPTY, [])
        self.waiting_on_player_id = None
        self.curr_round = 0

    def run_game(self):
        """
        Main game loop. Controls logic through the flow of the entire game.
        :return:
        """
        self.is_game_running = True
        for player_id in self.game_server.players:
            self.score_keeper.initialize_player(player_id)

        for round_num in range(0, NUM_ROUNDS):
            self.curr_round = round_num
            self.board.reset_board(round_num)
            self.score_keeper.new_round()
            self.__execute_round(round_num)

        self.__end_game()

    def __execute_round(self, round_num):
        """
        Controls the flow of one round.
        :param round_num: Number of current round (1 or 2).
        :return: void
        """
        self.num_spins = 0
        curr_player_id = None
        # End round when spins >= 50 or no available questions
        while self.num_spins < MAX_SPINS and self.board.get_available_categories(round_num):
            curr_player_id = self.__next_player(curr_player_id)
            logging.info(f"Starting player %d's turn", curr_player_id)
            self.__execute_turn(curr_player_id, round_num)  # Start turn

    def __execute_turn(self, curr_player_id, round_num):
        """
        Controls the flow of one turn. Called at the start of the turn.
        :param curr_player_id: ID of player whose turn is starting
        :return: void
        """
        # Wait for player to confirm spin
        self.__query_server(curr_player_id, MessageType.SPIN, [])

        # Get result from wheel spin
        if self.num_spins >= MAX_SPINS:
            return
        wheel_result = self.__spin_wheel(curr_player_id)

        # If result is a Jeopardy category, call execute_category
        if self.wheel.is_jeopardy_category(wheel_result):
            if not self.board.is_category_available(wheel_result,
                                                    round_num):  # If category has no more questions, spin again
                self.__execute_turn(curr_player_id, round_num)  # Spin again
            else:
                is_correct = self.__execute_category(wheel_result, curr_player_id,
                                                     round_num)  # Ask player Jeopardy question
                if is_correct:  # If player is correct, they spin again
                    self.__execute_turn(curr_player_id, round_num)  # Spin again

        # If result is another wheel sector, handle logic
        elif wheel_result == Sector.LOSE_TURN:
            # TODO: Rewrite to prompt player to use token. Currently just uses a token if it's available.
            if self.score_keeper.use_token(curr_player_id)[0]:  # Use token if available
                self.__update_scores_tokens_spins(curr_player_id)
                self.__execute_turn(curr_player_id, round_num)  # Spin again
            else:  # Otherwise, end player turn
                return

        elif wheel_result == Sector.FREE_TURN:
            self.score_keeper.add_token(curr_player_id)  # Give the player a token
            self.__update_scores_tokens_spins(curr_player_id)
            self.__execute_turn(curr_player_id, round_num)  # Spin

        elif wheel_result == Sector.BANKRUPT:
            self.score_keeper.bankrupt(curr_player_id)
            self.__update_scores_tokens_spins(curr_player_id)
            return  # End player turn

        elif wheel_result == Sector.PLAYERS_CHOICE:
            open_categories = self.board.get_available_categories(round_num)
            self.__query_server(curr_player_id, MessageType.PLAYERS_CHOICE, [open_categories])
            _, [chosen_category] = self.query_response.code, self.query_response.args

            is_correct = self.__execute_category(chosen_category, curr_player_id, round_num)
            if is_correct:  # If player is correct, they spin again
                self.__execute_turn(curr_player_id, round_num)  # Spin again


        elif wheel_result == Sector.OPPONENTS_CHOICE:
            open_categories = self.board.get_available_categories(round_num)
            random_opponent_id = self.__select_rand_opponent(curr_player_id)
            self.__query_server(random_opponent_id, MessageType.OPPONENTS_CHOICE, [open_categories])
            _, [chosen_category] = self.query_response.code, self.query_response.args

            is_correct = self.__execute_category(chosen_category, curr_player_id, round_num)
            if is_correct:  # If player is correct, they spin again
                self.__execute_turn(curr_player_id, round_num)  # Spin again

        elif wheel_result == Sector.SPIN_AGAIN:
            self.__execute_turn(curr_player_id, round_num)  # Spin again

        else:
            raise Exception("Wheel result '" + str(wheel_result) + "' is not a valid wheel category!")

    def __execute_category(self, jeopardy_category, curr_player_id, round_num):
        """
        Controls the flow of a Jeopardy question. Called when a "category" sector is the result of a wheel spin.
        :param jeopardy_category: Name of jeopardy category
        :return: is_correct (bool): True if the player's answer was correct, False otherwise
        """
        tile = self.board.get_tile(jeopardy_category, round_num)  # Get tile from board
        self.__query_server(curr_player_id, MessageType.JEOPARDY_QUESTION,
                            [jeopardy_category, tile])  # Display tile to user, wait for response

        _, user_answer = self.query_response.code, self.query_response.args
        if len(user_answer) == 1:
            user_answer = user_answer[0]
        if len(user_answer) > 1:  # this is weird...
            print("user_answer has more than one entry")
        is_correct, points = tile.check_answer(user_answer)
        self.score_keeper.update_score(curr_player_id, is_correct, points)
        self.__update_scores_tokens_spins(curr_player_id)
        return is_correct

    def __end_game(self):
        """
        Handles end-of-game logic. Called once, after the last round has ended.
        :return: void
        """
        winner_id = self.score_keeper.determine_winner()
        self.__notify_all_players(MessageType.END_GAME, [winner_id])  # Tell server who won, and to end game
        self.is_game_running = False

    def __next_player(self, curr_player_id):
        """
        Increments ID of current player (self.curr_player_id). In a 3-player game, cycles between 0, 1, and 2.
        :return: void
        """

        if curr_player_id is None:
            return 0
        else:
            return (curr_player_id + 1) % self.game_server.num_players

    def __spin_wheel(self, curr_player_id):
        """
        Called whenever the wheel must be spun. Increments spin counter and returns spin result.
        :return: Result of wheel spin
        """
        self.num_spins += 1
        spin_result = self.wheel.get_spin_result()
        self.__query_server(curr_player_id, MessageType.SPIN_RESULT, [spin_result])
        return spin_result

    def __query_server(self, player_id: int, command: MessageType, args: list):
        """
        Called whenever information must be obtained from the server (e.g. asking the user for something).
        Stalls until a response is received. Will only accept a response of the type that was requested.
        :param command: (MessageType) The command to be executed, like "JEOPARDY_CATEGORY" or "PLAYERS_CHOICE"
        :param args: (list) Any additional arguments that must be sent to the server
        :return: void
        """
        if self.query_status != QueryStatus.STANDBY:  # Wait for previous query to complete
            pass

        self.query_response = Message(MessageType.EMPTY, [])  # Clear server's previous response
        self.server_message = Message(command, args)  # Store the query in self.server_message for server to read
        self.waiting_on_player_id = player_id

        self.query_status = QueryStatus.SERVER_TO_CLIENT  # Tell server we want to query client

        while self.query_status is not QueryStatus.STANDBY:  # Wait for a response from the server
            pass

        logging.info(f"QUERY_SERVER RESPONSE CODE: {self.query_response.code}")

    def store_query(self, command: MessageType, args: list):
        """
        Called by the server to return the result of a query from __query_server.
        :param command: (MessageType) The command that was executed, like "JEOPARDY_CATEGORY" or "PLAYERS_CHOICE"
        :param args: (list) Any information that must be returned to ExecLogic
        :return: void
        """
        self.query_response = Message(command, args)  # Store server response in self.query_response

    def __update_scores_tokens_spins(self, curr_player_id):
        """
        Called after a game value is updated that should be reflected in the UI display.
        Sends server the current player scores, player tokens, and number of spins remaining.
        :return: void
        """
        self.__query_server(curr_player_id, MessageType.UPDATE_SCORES,
                            [self.score_keeper.get_scores(), self.score_keeper.get_tokens(),
                             MAX_SPINS - self.num_spins, self.curr_round])

    def __notify_all_players(self, command: MessageType, args: list):
        """
        Called to send a message to all players.
        Used to update all players on other players' spins, score updates, etc.
        :return: void
        """
        for player_id in self.game_server.players:
            self.__query_server(player_id, command, args)

    def __select_rand_opponent(self, curr_player_id):
        opponent_ids = []
        for player_id in self.game_server.players:
            if player_id != curr_player_id:
                opponent_ids.append(player_id)

        if len(opponent_ids) == 0:
            return curr_player_id  # Return current player in single-player game
        else:
            return random.choice(opponent_ids)  # Otherwise, return a random opponent that isn't the current player


class ConfigWindow:
    """
    Window with configuration options for the game

    """
    def __init__(self):
        win = self.__setup_window()
        self.__setup_file_picker(win)

        self.__setup_num_player_selector(win)

        close_button = ttk.Button(win, text="Start Game Server", command=win.destroy)
        close_button.pack(expand=True)

        # run the application
        win.mainloop()


    def __setup_window(self):
        """
        General window setup on the screen
        """
        win = tk.Tk()
        win.resizable(False, False)

        window_width = 300
        window_height = 200

        config_window_title = "Wheel of Jeopardy: Game Configuration"
        win.title(config_window_title)

        # Center the window
        # get the screen dimension
        screen_width = win.winfo_screenwidth()
        screen_height = win.winfo_screenheight()

        # find the center point
        center_x = int(screen_width / 2 - window_width / 2)
        center_y = int(screen_height / 2 - window_height / 2)

        # set the position of the window to the center of the screen
        win.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        return win

    def __setup_file_picker(self, win):
        """
        Add a button to allow the Game Maker to select a CSV file containing Jeopardy questions

        win: a window object
        """
        # open button
        open_button = ttk.Button(
            win,
            text='Select a Question File',
            command=self.__select_file
        )
        self.filename = ""
        open_button.pack(expand=True)

    def __setup_num_player_selector(self, win):
        """
        Add radio buttons to allow the Game Maker to select the exact number of players
        win: a window object
        """
        self.num_players = tk.IntVar()
        players = range(1, MAX_NUM_PLAYERS+1)

        # label
        label = ttk.Label(text="Number of players?")
        label.pack(fill='x', padx=5, pady=5)

        # radio buttons
        for n in players:
            r = ttk.Radiobutton(
                win,
                text=n,
                value=n,
                variable=self.num_players
            )
            r.pack(fill='x', padx=5, pady=5)

    def __select_file(self):
        """
        Pop-up to select a CSV file
        """
        filetypes = (
            ('CSV files', '*.csv'),
            # ('All files', '*.*')
        )

        self.filename = fd.askopenfilename(
            title='Open a file',
            initialdir='.',
            filetypes=filetypes)

        showinfo(
            title='Selected File',
            message=self.filename
        )



