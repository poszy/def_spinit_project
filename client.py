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
# logging.disable(level=logging.INFO)  # Disable logging for demo


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
        self.label_round_val.set(self.strl.main_lbl_current_round+"0")

        self.label_spins_val = StringVar()
        lbl_spins = ttk.Label(self.frame_top, textvariable=self.label_spins_val, padding="10", width="30")
        lbl_spins.pack(side=LEFT)
        self.label_spins_val.set(self.strl.main_lbl_spins_remain+"50")

        self.label_score_val = StringVar()
        lbl_score = ttk.Label(self.frame_top, textvariable=self.label_score_val, padding="10", width="20")
        lbl_score.pack(side=LEFT)
        self.label_score_val.set(self.strl.main_lbl_current_score + "0")

        self.label_current_turn_val = StringVar()
        lbl_turn = ttk.Label(self.frame_top, textvariable=self.label_current_turn_val, padding="10", width="20")
        lbl_turn.pack(side=LEFT)
        self.label_current_turn_val.set(self.strl.main_lbl_current_turn + "0")

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
                                         text='It is currently your turn, click the button below to spin the wheel.  ',
                                         padding="10", width="300")
        self.lbl_player_wait.pack(side=TOP)

        # Add Frame to Notebook. This is the Lobby Frame
        self.note.add(self.lobby_frame_1)

        # Create Wheel Frame
        self.wheel_frame_2 = ttk.Frame(self.note)

        # Add Frame to Notebook
        self.note.add(self.wheel_frame_2)
        self.note.pack(expand=1, fill='both', padx=5, pady=5)
        self.category_selected = StringVar()

        ## initial menu text
        self.category_selected.set("Choose category")
        # Create Dropdown menu
        self.drp_menu_category_selection = OptionMenu(self.wheel_frame_2, self.category_selected, "Delicious Bytes",
                                                      "String Theory", "Logic Games", "So Random")
        self.drp_menu_category_selection.pack()
        # Create button, it will change label text

        # self.btn_choose_category = Button( self.wheel_frame_2 , text = "Choose category" , command = self.submit_category(self.cc).pack())
        self.btn_choose_category = Button(self.wheel_frame_2, text="Choose category").pack()

        # Create Select category Label
        self.lbl_selected_category = Label(self.wheel_frame_2, text=" ")
        self.lbl_selected_category.pack()

        # Create Prompt Frame
        self.prompt_frame_3 = ttk.Frame(self.note)

        # Add Frame to Notebook
        self.note.add(self.prompt_frame_3)
        self.note.pack(expand=2, fill='both', padx=5, pady=5)

        # Wait for Client to send turn signal, for now it is initiated by button
        self.btn_play = ttk.Button(self.lobby_frame_1, text="Connect to Game", command=self.populate_spin_frame)
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
    def __update_scores_tokens_spins(self, scores, tokens, spins_remain):
        logging.info("update_scores_tokens_spins...")
        # clear the screen of the question and answers
        self.__clear_frame(self.prompt_frame_3)

        my_score = str(scores[self.player_id])
        self.label_score_val.set(self.strl.main_lbl_current_score+my_score)

        my_tokens = str(tokens[self.player_id])
        self.label_tokens_val.set(self.strl.main_lbl_current_tokens+my_tokens)

        # TODO: add spin count
        spins_remain = str(spins_remain)
        self.label_spins_val.set(self.strl.main_lbl_spins_remain+spins_remain)

    def __clear_frame(self, frame):
        for widget in frame.winfo_children():  # get all the children widgets in the frame
            widget.destroy()

    def load_lobby_frame(self):
        self.note.select(0)

    def load_spin_frame(self):
        self.note.select(1)

    def load_prompt_frame(self):
        self.note.select(2)

    def __start_music(self, music_file):
        pygame.mixer.init()
        pygame.mixer.music.load(music_file)
        pygame.mixer.music.play(loops=1)

    def __stop_music(self):
        pygame.mixer.music.stop()


    def populate_spin_frame(self):
        #### END TEXT INTERFACE ####
        self.btn_spin = ttk.Button(self.wheel_frame_2, text="Spin the Wheel", command=self.send_spin_command)
        self.btn_spin.pack(side=BOTTOM, padx=50)
        self.connect_to_game(self.host_ip, self.srv_port)
        self.load_prompt_frame()

    def send_spin_command(self):
        cc = self.category_selected.get()
        self.send_command(self.server, Message(MessageType.SPIN, cc))
        self.load_prompt_frame()

    def connect_to_game(self, host, port):
        """
        Connects client to a game server. Called once, before the beginning of the game.
        Spawns new thread for handle_connection.
        """
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # another TCP socket
        self.server.connect((host, port))
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
                [player_id, jeopardy_category, tile] = parsed_message.args
                if player_id != self.player_id:  # not the active player
                    response_info = []
                    self.send_command(self.server, Message(parsed_message.code, response_info))

                self.load_prompt_frame()  # in case it's not your turn, still want to see question

                a = str(tile.question)

                lbl_category = ttk.Label(self.prompt_frame_3, text=f"Category: {jeopardy_category}", padding="10", width="300")
                lbl_category.pack(side=TOP)

                lbl_player_question = ttk.Label(self.prompt_frame_3, text=a, padding="10", width="300")
                lbl_player_question.pack(side=TOP)
                logging.info(f"[Client: JEOPARDY QUESTION]: {str(tile.question)}")
                an = tile.answers

                self.gAnswers = StringVar()
                self.aAnswers = an[2]
                ## radio buttons
                for c in tile.answers:
                    r = ttk.Radiobutton(
                        self.prompt_frame_3,
                        text=c,
                        value=c,
                        variable=self.gAnswers,
                    )

                    r.pack(side=TOP)

                if player_id == self.player_id:  # I am the active player

                    self.__start_music(MUSIC_FILE)
                    ## Submit button
                    btn_submit = ttk.Button(
                        self.prompt_frame_3,
                        text=self.strl.question_btn_submit,
                        command=self.submit_answer
                    )
                    btn_submit.pack(side=BOTTOM, )
                else:
                    lbl_category = ttk.Label(self.prompt_frame_3, text=f"Opponent's Turn", padding="20",
                                             width="300")
                    lbl_category.pack(side=BOTTOM)



            elif parsed_message.code == MessageType.PLAYERS_CHOICE:
                [open_categories] = parsed_message.args

                # TODO (UI): Ask this player to select a Jeopardy category for them to answer
                # TODO (UI): Get back user's selected category and store in chosen_category
                # TODO (UI): Delete text interface code below

                chosen_category = None

                ### BEGIN TEXT INTERFACE ###
                print("Player's Choice!")
                print("Select a Jeopardy category:")
                chosen_category = self.__prompt_user_from_list(open_categories)
                #### END TEXT INTERFACE ####

                response_info = [chosen_category]

            elif parsed_message.code == MessageType.OPPONENTS_CHOICE:
                [open_categories] = parsed_message.args

                # TODO (UI): Ask this player to select a Jeopardy category for their opponent to answer
                # TODO (UI): Get back user's selected category and store in chosen_category
                # TODO (UI): Delete text interface code below

                chosen_category = None

                ### BEGIN TEXT INTERFACE ###
                print("Opponent's Choice!")
                print("Select a Jeopardy category for your opponent to answer:")
                chosen_category = self.__prompt_user_from_list(open_categories)
                #### END TEXT INTERFACE ####

                response_info = [chosen_category]

            elif parsed_message.code == MessageType.SPIN:
                _ = parsed_message.args

                self.load_spin_frame()


            elif parsed_message.code == MessageType.END_GAME:
                [winner_player_id] = parsed_message.args

                # TODO (UI): Tell player the game has ended, and display the winning player id
                # TODO (UI): Delete text interface code below

                ### BEGIN TEXT INTERFACE ###
                print("\n==========================\nEND OF GAME\n==========================\n")
                print(f"Player {winner_player_id} has won!\n\n")
                #input("Press enter to end the game")
                #### END TEXT INTERFACE ####

                self.game_over = True
                response_info = []

            elif parsed_message.code == MessageType.UPDATE_SCORES:
                [scores_dict, tokens_dict, num_spins_remaining] = parsed_message.args

                # TODO (UI): Update the UI to display all players' scores and tokens, number of spins
                self.__update_scores_tokens_spins(scores_dict, tokens_dict, num_spins_remaining)
                response_info = []
                self.send_command(self.server, Message(parsed_message.code, response_info))

            elif parsed_message.code == MessageType.SPIN_RESULT:
                [spin_result] = parsed_message.args

                # TODO (UI): Update the UI to display the result of the previous spin
                # TODO (UI): Delete text interface code below

                logging.info(f"You Spun: {spin_result}\n")

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
            max_index = str(len(prompt_list)-1)
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

    def submit_answer(self):
        self.__stop_music()
        # print(self.gAnswers.get())

        # print(self.gAnswers)
        # print(self.aAnswers)
        userAnswer = self.gAnswers.get()
        print(f"user answer: {userAnswer}, {type(userAnswer)}")
        response_info = [userAnswer]
        # return response_info
        print(response_info)
        self.send_command(self.server, Message(MessageType.JEOPARDY_QUESTION, response_info))

        # clear the screen of the question and answers
        self.__clear_frame(self.prompt_frame_3)


gameplayer = Client(SRV_IP, SRV_PORT)
# gameplayer.connect_to_game(SRV_IP, SRV_PORT)

# player2 = Client()
# player2.connect_to_game(SRV_IP, SRV_PORT+1)
