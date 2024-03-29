from ui.user_interface import UserInterface

import socket
import threading
import logging
from tkinter import *
from tkinter import ttk
from server import Message, QueryStatus, MessageType, Messenger
from ui import s
import pygame.mixer
from tkinter.messagebox import showinfo

NUM_PLAYERS = 3
SRV_IP = 'localhost'
SRV_PORT = 5555
BYTE_ENCODING = 'utf-8'
HEADER_SIZE = 10
MUSIC_FILE = 'resources/audio/Jeopardy-theme-song.mp3'

logging.basicConfig(level=logging.INFO)


class Client(Messenger):

    # default constructor
    def __init__(self, srv_ip, srv_port):
        self.host_ip = srv_ip
        self.srv_port = srv_port
        self.player_id = None
        self.game_over = False

        self.ui = UserInterface()  # TODO (UI): Unused. Fill in with any required arguments.

        # self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # another TCP socket
        self.strl = s.S()

        # init music player
        pygame.mixer.init()
        pygame.mixer.music.load(MUSIC_FILE)

        """
        CREATE ROOT FRAME
        """
        # Start Window Manager
        self.root = Tk()

        # Set default size of window
        self.root.geometry(self.strl.window_dimensions)
        self.root.title(self.strl.lobby_title_bar)
        self.s = ttk.Style()
        self.s.configure('new.TFrame', background='#7AC5CD')

        """
        CREATE TOP FRAME
        """
        self.frame_top = ttk.Frame(self.root, style='new.TFrame')
        # Every Frame should have these global labels
        self.label_round_val = StringVar()
        lbl_round = ttk.Label(self.frame_top, textvariable=self.label_round_val, padding="10", width="20")
        lbl_round.pack(side=LEFT)
        self.label_round_val.set(self.strl.main_lbl_current_round+"1")

        self.label_spins_val = StringVar()
        lbl_spins = ttk.Label(self.frame_top, textvariable=self.label_spins_val, padding="10", width="30")
        lbl_spins.pack(side=LEFT)
        self.label_spins_val.set(self.strl.main_lbl_spins_remain+"50")

        self.label_score_val = StringVar()
        lbl_score = ttk.Label(self.frame_top, textvariable=self.label_score_val, padding="10", width="20")
        lbl_score.pack(side=LEFT)
        self.label_score_val.set(self.strl.main_lbl_current_score + "0")

        self.label_tokens_val = StringVar()
        lbl_token = ttk.Label(self.frame_top, textvariable=self.label_tokens_val, padding="10", width="20")
        lbl_token.pack(side=LEFT)
        self.label_tokens_val.set(self.strl.main_lbl_current_tokens+"0")


        # Place the top frame
        self.frame_top.pack()

        self.style = ttk.Style()
        self.style.layout('TNotebook.Tab', [])  # turn off tabs

        # Create Notebook in Root Frame
        # This will carkry our pagination
        self.note = ttk.Notebook(self.root)

        """
        CREATE SUB FRAMES
        """
        self.lobby_frame_1 = ttk.Frame(self.note)
        self.lbl_player_wait = ttk.Label(self.lobby_frame_1,
                                         text='Press the button to enter the game.  ',
                                         padding="10", width="300")
        self.lbl_player_wait.pack(side=TOP)

        # Add Frame to Notebook. This is the Lobby Frame
        self.note.add(self.lobby_frame_1)

        # Create Wheel Frame
        self.wheel_frame_2 = ttk.Frame(self.note)
        self.populate_spin_frame()

        # Add Frame to Notebook
        self.note.add(self.wheel_frame_2)
        self.note.pack(expand=1, fill='both', padx=5, pady=5)
        self.category_selected = StringVar()

        # Create Question Frame
        self.prompt_frame_3 = ttk.Frame(self.note)

        # Add Frame to Notebook
        self.note.add(self.prompt_frame_3)
        self.note.pack(expand=2, fill='both', padx=5, pady=5)

        # Wait for Client to send turn signal, for now it is initiated by button
        self.btn_play = ttk.Button(self.lobby_frame_1, text="Connect to Game", command=self.connect_to_game)
        self.btn_play.pack(side=BOTTOM, padx=50)

        """
        CREATE BOTTOM FRAME
        """
        self.frame_bottom = ttk.Frame(self.root, style='new.TFrame')

        # Every Frame should have these global labels
        self.lbl_info = ttk.Label(self.frame_bottom, text='Informational Panel:  ', padding="10", width="20")
        self.lbl_info.pack()

        # Place the top frame
        self.frame_bottom.pack(side=BOTTOM)

        # self.root.after(3000, self.load_lobby_frame)
        self.root.mainloop()
        # self.root.after(3000, self.load_lobby_frame)

    # Helper function
    def __update_scores_tokens_spins(self, scores, tokens, spins_remain, curr_round):
        self.label_round_val.set(self.strl.main_lbl_current_round+str(curr_round))

        my_score = str(scores[self.player_id])
        self.label_score_val.set(self.strl.main_lbl_current_score+my_score)

        my_tokens = str(tokens[self.player_id])
        self.label_tokens_val.set(self.strl.main_lbl_current_tokens+my_tokens)

        spins_remain = str(spins_remain)
        self.label_spins_val.set(self.strl.main_lbl_spins_remain + spins_remain)

    def __clear_frame(self, frame):
        for widget in frame.winfo_children():  # get all the children widgets in the frame
            widget.destroy()

    def load_lobby_frame(self):
        self.note.select(0)

    def load_spin_frame(self):
        self.note.select(1)

    def load_prompt_frame(self):
        self.note.select(2)

    def __start_music(self):
        pygame.mixer.music.play(loops=1)

    def __stop_music(self):
        pygame.mixer.music.stop()

    def populate_spin_frame(self):
        #### END TEXT INTERFACE ####
        lbl_player_question = ttk.Label(self.wheel_frame_2, text=self.strl.player_turn_spin, padding="10", width="300")
        lbl_player_question.pack(side=TOP)
        self.btn_spin = ttk.Button(self.wheel_frame_2, text=self.strl.wheel_btn_spin, command=self.send_spin_command)
        self.btn_spin.pack(side=BOTTOM, padx=50)

    def prompt_jeopardy_question(self, tile, jeopardy_category):
        self.__clear_frame(self.prompt_frame_3)
        lbl_category = ttk.Label(self.prompt_frame_3, text=f"Category: {jeopardy_category}: {tile.points}",
                                 padding="10",
                                 width="300")
        lbl_category.pack(side=TOP)

        a = str(tile.question)

        lbl_player_question = ttk.Label(self.prompt_frame_3, text=a, padding="10", width="300")
        lbl_player_question.pack(side=TOP)
        print(str(tile.question))
        an = tile.answers

        self.gAnswers = StringVar()
        self.gAnswers.set("WR0NG")  # just put a default wrong answer
        ## radio buttons
        for c in tile.answers:
            r = ttk.Radiobutton(
                self.prompt_frame_3,
                text=c,
                value=c,
                variable=self.gAnswers,
            )

            r.pack(side=TOP)

        ## Submit button
        btn_submit = ttk.Button(
            self.prompt_frame_3,
            text=self.strl.question_btn_submit,
            command=self.submit_answer
        )
        btn_submit.pack(side=BOTTOM, )

    def prompt_category_choice(self, options, messageType):
        self.__clear_frame(self.prompt_frame_3)
        self.load_prompt_frame()

        if messageType == MessageType.PLAYERS_CHOICE:
            prompt_text = "Player's Choice: select a question category for your turn"
            lbl_category = ttk.Label(self.prompt_frame_3, text=prompt_text, padding="10",
                                     width="300")
            lbl_category.pack(side=TOP)
        elif messageType == MessageType.OPPONENTS_CHOICE:

            prompt_text = "Opponent's Choice: select a question category for your opponent to answer"
            lbl_category = ttk.Label(self.prompt_frame_3, text=prompt_text, padding="10",
                                     width="300")
            lbl_category.pack(side=TOP)

        self.category_selected = StringVar()
        self.category_selected.set(options[0])  #give this a default value in case the user doesn't select one
        ## radio buttons
        for category in options:
            r = ttk.Radiobutton(
                self.prompt_frame_3,
                text=category,
                value=category,
                variable=self.category_selected,
            )

            r.pack(side=TOP)

        ## Submit button

        btn_submit = ttk.Button(
            self.prompt_frame_3,
            text=self.strl.category_btn_submit,
            # use lambda function to include parameters to button call
            command=lambda: self.submit_category_choice(messageType)
        )
        btn_submit.pack(side=BOTTOM, )


        # Create Select category Label
        self.lbl_selected_category = Label(self.wheel_frame_2, text=" ")
        self.lbl_selected_category.pack()

    def send_spin_command(self):
        self.send_command(self.server, Message(MessageType.SPIN, []))
        self.load_prompt_frame()

    def connect_to_game(self):
        """
        Connects client to a game server. Called once, before the beginning of the game.
        Spawns new thread for handle_connection.
        """
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # another TCP socket
        self.server.connect((self.host_ip, self.srv_port))
        self.load_prompt_frame()

        lbl_category = ttk.Label(self.prompt_frame_3, text=self.strl.player_wait_str,
                                 padding="10",
                                 width="300")
        lbl_category.pack(side=TOP)

        logging.info("Connecting to the game self.server")
        threading.Thread(target=self.handle_connection, args=(self.server,)).start()  # start threading immediately

    def handle_connection(self, server):
        """
        Main loop for client. Runs in a separate thread for the duration of the game.
        Listens for self.server requests, gets input from user, then returns info to self.server.
        :param server: Reference to server object
        :return: void
        """
        logging.info("Entered handle_connections")

        self.__set_player_id()  # Receive this client's player ID from self.server

        while not self.game_over:  # Loop until game ends
            parsed_message = self.buffer_message(server)  # Wait for message from self.server
            logging.info(f"Client received message from server: %s", parsed_message.code)

            response_info = []

            if parsed_message.code == MessageType.EMPTY:
                response_info = []

            elif parsed_message.code == MessageType.PLAYER_ID:
                raise Exception(f"This client (ID %s) was already assigned a player ID!", self.player_id)

            elif parsed_message.code == MessageType.JEOPARDY_QUESTION:
                self.__start_music()
                [jeopardy_category, tile] = parsed_message.args

                self.prompt_jeopardy_question(tile, jeopardy_category)

            elif parsed_message.code == MessageType.PLAYERS_CHOICE:
                [open_categories] = parsed_message.args  # TODO: Why is this client receiving its own player ID?

                self.prompt_category_choice(open_categories, MessageType.PLAYERS_CHOICE)

            elif parsed_message.code == MessageType.OPPONENTS_CHOICE:
                [open_categories] = parsed_message.args  # TODO: Why is this client receiving its own player ID?



                self.prompt_category_choice(open_categories, MessageType.OPPONENTS_CHOICE)

            elif parsed_message.code == MessageType.SPIN:
                _ = parsed_message.args

                self.load_spin_frame()


            elif parsed_message.code == MessageType.END_GAME:
                [winner_player_id] = parsed_message.args

                self.load_prompt_frame()
                self.__clear_frame(self.prompt_frame_3)
                if len(winner_player_id) == 2:  # in case there is a tie for winner
                    game_end_text = f"Game over... \nPlayers {winner_player_id[0]} and {winner_player_id[1]} have won the game!"
                elif len(winner_player_id) >2:
                    start_winners = ",".join(winner_player_id[0:-1])  # exclude last winner
                    game_end_text = f"Game over... \nPlayers {start_winners} and {winner_player_id[-1]} have won the game!"
                else:
                    game_end_text = f"Game over... \nPlayer {winner_player_id} has won the game!"

                lbl_winner = ttk.Label(self.prompt_frame_3, text=game_end_text, padding="10",
                                       width="300")
                lbl_winner.pack(side=TOP)

                self.game_over = True
                response_info = []

            elif parsed_message.code == MessageType.UPDATE_SCORES:
                [scores_dict, tokens_dict, num_spins_remaining, curr_round] = parsed_message.args

                # TODO (UI): Update the UI to display all players' scores and tokens, number of spins
                self.__update_scores_tokens_spins(scores_dict, tokens_dict, num_spins_remaining, curr_round)
                response_info = []
                self.send_command(self.server, Message(parsed_message.code, response_info))
                # clear the screen of the question and answers
                self.__clear_frame(self.prompt_frame_3)

                lbl_category = ttk.Label(self.prompt_frame_3, text=self.strl.player_wait_str,
                                         padding="10",
                                         width="300")
                lbl_category.pack(side=TOP)

            elif parsed_message.code == MessageType.SPIN_RESULT:
                [spin_result] = parsed_message.args

                # TODO (UI): Update the UI to display the result of the previous spin
                # TODO (UI): Delete text interface code below

                ### BEGIN TEXT INTERFACE ###
                print(f"You Spun: {spin_result}\n")
                #### END TEXT INTERFACE ####

                response_info = []
                self.send_command(self.server, Message(parsed_message.code, response_info))

            else:
                raise Exception(f"Client {self.player_id} received unknown MessageType: {parsed_message.code}")

            # self.send_command(self.server, Message(parsed_message.code, response_info))

    def __prompt_user_from_list(self, prompt_list: list):
        """
        Print out the contents of a list, and prompt the user to pick one.
        :param prompt_list: List of strings to pick from (e.g. a list of answers to a Jeopardy question)
        :return: (string) The answer that the user selected
        """
        # Print out the options in the list
        for i in range(0, len(prompt_list)):
            print("----- " + str(i) + ") " + str(prompt_list[i]))
        # Ask user to select an option from the list
        selected_index = None
        while selected_index not in range(0, len(prompt_list)):
            max_index = str(len(prompt_list) - 1)
            user_input = input(f"Enter option number (0-{max_index}): ")
            try:
                selected_index = int(user_input)  # in case user inputs non-int value
            except:
                selected_index = None  # re-prompt user to enter index

        print(f"You selected option #{selected_index}, {prompt_list[selected_index]}")

        return prompt_list[selected_index]

    def __set_player_id(self):
        """
        Waits for a player ID from server, then stores it in this client's self.player_id
        :param server: Reference to the server object
        :return:
        """
        logging.info("Waiting for player_id...")
        while not self.game_over:

            parsed_message = self.buffer_message(self.server)
            logging.info("Received message with command code: %s", parsed_message.code)

            if parsed_message.code == MessageType.PLAYER_ID:
                self.player_id = parsed_message.args[0]
                logging.info("Player ID %s received", self.player_id)
                return

    ########
    # TODO: Functions deprecated below this point?
    ########
    def refresh_score(self, score):
        """
		Send out the updated score to the clients

		Args:
		score: updated score

		Returns:
			None
		"""

        pass

    def refresh_display(self, category, score):
        pass

    def spin_again(self):
        pass

    def notify_spin(self):
        pass

    def submit_category_choice(self, messageType):
        selected_category = self.category_selected.get()
        print(f"user answer: {selected_category}, {type(selected_category)}")
        response_info = [selected_category]
        # return response_info
        print(response_info)
        self.send_command(self.server, Message(messageType, response_info))

        # clear the screen of the question and answers
        self.__clear_frame(self.prompt_frame_3)

    def submit_answer(self):
        self.__stop_music()
        userAnswer = self.gAnswers.get()
        print(f"user answer: {userAnswer}, {type(userAnswer)}")
        response_info = [userAnswer]
        # return response_info
        print(response_info)
        self.send_command(self.server, Message(MessageType.JEOPARDY_QUESTION, response_info))



gameplayer = Client(SRV_IP, SRV_PORT)
# gameplayer.connect_to_game(SRV_IP, SRV_PORT)

# player2 = Client()
# player2.connect_to_game(SRV_IP, SRV_PORT+1)
