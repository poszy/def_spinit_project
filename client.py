from ui.user_interface import UserInterface

import socket
import threading
import logging
from tkinter import *
from tkinter import ttk
from server import Message, QueryStatus, MessageType, Messenger
from board.questions import Tile
from ui import s
from tkinter.messagebox import showinfo

NUM_PLAYERS = 3
SRV_IP = 'localhost'
SRV_PORT = 5555
BYTE_ENCODING = 'utf-8'
HEADER_SIZE = 10

logging.basicConfig(level=logging.INFO)


class Client(Messenger):

    # default constructor
    def __init__(self):

        self.player_id = None
        self.game_over = False
        self.SRV_IP = 'localhost'
        self.SRV_PORT = 5555

        #self.ui = UserInterface()  # TODO (UI): Unused. Fill in with any required arguments.

        self.categories = ["Delicious Bytes", "String Theory", "Logic Games", "So Random"]  # TODO: Should receive Jeopardy board from Server at start of round
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # another TCP socket
        self.strl = s.S()

        """
        CREATE ROOT FRAME
        """
        # Start Window Manager
        self.root = Tk()


        #self.gameplayer.connect_to_game(SRV_IP, SRV_PORT)


        # Set default size of window
        self.root.geometry(self.strl.window_dimensions)
        self.root.title(self.strl.lobby_title_bar)
        self.s = ttk.Style()
        self.s.configure('new.TFrame', background='#7AC5CD')



        """
        CREATE TOP FRAME
        """
        self.frame_top=ttk.Frame(self.root, style='new.TFrame')
        #Every Frame should have these global labels
        self.lbl_round=ttk.Label(self.frame_top,text=self.strl.main_lbl_current_round, padding="10", width="20")
        self.lbl_round.pack(side=LEFT)

        self.lbl_score=ttk.Label(self.frame_top,text=self.strl.main_lbl_current_score, padding="10", width="20")
        self.lbl_score.pack(side=LEFT)

        self.lbl_turn=ttk.Label(self.frame_top,text=self.strl.main_lbl_current_turn, padding="10", width="20")
        self.lbl_turn.pack(side=LEFT)

        self.lbl_token=ttk.Label(self.frame_top,text=self.strl.main_lbl_current_tokens, padding="10", width="20")
        self.lbl_token.pack(side=LEFT)

        #Place the top frame
        self.frame_top.pack()

        self.style = ttk.Style()
        self.style.layout('TNotebook.Tab', []) # turn off tabs

        # Create Notebook in Root Frame
        # This will carkry our pagination
        self.note = ttk.Notebook(self.root)


        """
        CREATE SUB FRAMES
        """
        self.f1 = ttk.Frame(self.note)
        self.lbl_player_wait=ttk.Label(self.f1, text='It is currently your turn, click the button below to spin the wheel.  ', padding="10", width="300")
        self.lbl_player_wait.pack(side=TOP)

        # Add Frame to Notebook. This is the Lobby Frame
        self.note.add(self.f1)


        # Create Wheel Frame
        self.f2 = ttk.Frame(self.note)

        # Add Frame to Notebook
        self.note.add(self.f2)
        self.note.pack(expand=1, fill='both', padx=5, pady=5)
        self.catagory_selected = StringVar()

        ## initial menu text
        self.catagory_selected.set( "Choose Catagory" )
        # Create Dropdown menu
        self.drp_menu_catagory_selection = OptionMenu( self.f2 , self.catagory_selected , "Delicious Bytes", "String Theory", "Logic Games", "So Random" )
        self.drp_menu_catagory_selection.pack()
        # Create button, it will change label text


        #self.btn_choose_catagory = Button( self.f2 , text = "Choose Catagory" , command = self.submit_catagory(self.cc).pack())
        self.btn_choose_catagory = Button( self.f2 , text = "Choose Catagory" ).pack()

        # Create Select Catagory Label
        self.lbl_selected_catagory = Label( self.f2 , text = " " )
        self.lbl_selected_catagory.pack()


        # Create Question Frame
        self.f3 = ttk.Frame(self.note)

        # Add Frame to Notebook
        self.note.add(self.f3)
        self.note.pack(expand=2, fill='both', padx=5, pady=5)

        # Wait for Client to send turn singal, for now it is initiated by button
        self.btn_play = ttk.Button(self.f1,text="Connect to Game", command=self.load_spin_frame)
        self.btn_play.pack( side = BOTTOM, padx=50)




        """
        CREATE BOTTOM FRAME
        """
        self.frame_bottom=ttk.Frame(self.root, style='new.TFrame')

        #Every Frame should have these global labels
        self.lbl_info=ttk.Label(self.frame_bottom,text='Informational Pannel:  ', padding="10", width="20")
        self.lbl_info.pack()


        #Place the top frame
        self.frame_bottom.pack(side=BOTTOM)

        #self.root.after(3000, self.load_lobby_frame)
        self.root.mainloop()
        #self.root.after(3000, self.load_lobby_frame)

    # Helper function
    def load_lobby_frame(self):
        self.note.select(0)
    def load_spin_frame(self):

        self.note.select(1)
        self.connect_to_game(self.SRV_IP, self.SRV_PORT)

    def load_question_frame(self):
        cc = self.catagory_selected.get()
        self.send_command(self.server, Message(MessageType.SPIN, cc))
        self.note.select(2)



    def connect_to_game(self, host, port):
        """
        Connects client to a game server. Called once, before the beginning of the game.
        Spawns new thread for handle_connection.
        """
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # another TCP socket
        self.server.connect((host, port))
        logging.info("Connecting to the game server")
        threading.Thread(target=self.handle_connection, args=(self.server,)).start()  # start threading immediately

    def handle_connection(self, server):
        """
        Main loop for client. Runs in a separate thread for the duration of the game.
        Listens for server requests, gets input from user, then returns info to server.
        :param server: Reference to server object
        :return: void
        """
        logging.info("Entered handle_connections")

        self.__set_player_id(server)  # Receive this client's player ID from server

        while not self.game_over:  # Loop until game ends
            parsed_message = self.buffer_message(server)  # Wait for message from server
            logging.info(f"Client received message from server: %s", parsed_message.code)

            response_info = []

            if parsed_message.code == MessageType.EMPTY:
                response_info = []

            elif parsed_message.code == MessageType.PLAYER_ID:
                raise Exception(f"This client (ID %s) was already assigned a player ID!", self.player_id)

            elif parsed_message.code == MessageType.JEOPARDY_QUESTION:
                [player_id, tile] = parsed_message.args  # TODO: Why is this client receiving its own player ID?

                # TODO (UI): Display question (tile.question) and answer choices (tile.answers) to user
                # TODO (UI): Get back user answer and store in user_answer
                # TODO (UI): Delete text interface code below

                user_answer = None  # Note: user_answer should be a string from tile.answers, like user_answer = tile.answers[1]

                ### BEGIN TEXT INTERFACE ###
                # Note: Expecting tile.answers to be a list of strings
                print("Here's your question:")
                a = str(tile.question)

                self.lbl_player_question=ttk.Label(self.f3, text=a, padding="10", width="300")
                self.lbl_player_question.pack(side=TOP)
                print(str(tile.question))
                an = tile.answers
                #aAnswers_split = an.split(',')

                choice = ((an[0], 0),
                (an[1], 1),
                (an[2], 2))

                self.gAnswers = StringVar()
                self.aAnswers = an[2]
                ## radio buttons
                for c in choice:
                    i = 0
                    r = ttk.Radiobutton(
                        self.f3,
                        text=c[i],
                        value=c,
                        variable=self.gAnswers,

                    )
                    i = i + i

                    r.pack(side = TOP)

                b = self.gAnswers.get()
                print(b)
                ## Submit button
                btn_submit = ttk.Button(
                    self.f3,
                    text=self.strl.question_btn_submit,
                    command = self.show_submit_answer
                    )
                btn_submit.pack( side = BOTTOM, )
                #b = self.gAnswers.get()
                #c = b[-1]
                #response_info = [c]


                #user_answer =  self.__prompt_user_from_list(tile.answers)
                #user_answer = self.__prompt_user_from_list(tile.answers)
                #print(user_answer)
                #response_info = [user_answer]
                #print(response_info)
                #print(parsed_message.code)
                #self.send_command(server, Message(parsed_message.code, response_info))


                #### END TEXT INTERFACE ####




            elif parsed_message.code == MessageType.PLAYERS_CHOICE:
                [player_id, round_num] = parsed_message.args  # TODO: Why is this client receiving its own player ID?

                # TODO (UI): Ask this player to select a Jeopardy category for them to answer
                # TODO (UI): Get back user's selected category and store in chosen_category
                # TODO (UI): Delete text interface code below

                chosen_category = None

                ### BEGIN TEXT INTERFACE ###
                print("Player's Choice!")
                print("Select a Jeopardy category:")
                chosen_category = self.__prompt_user_from_list(self.categories)
                #### END TEXT INTERFACE ####

                response_info = [chosen_category]

            elif parsed_message.code == MessageType.OPPONENTS_CHOICE:
                [player_id, round_num] = parsed_message.args  # TODO: Why is this client receiving its own player ID?

                # TODO (UI): Ask this player to select a Jeopardy category for their opponent to answer
                # TODO (UI): Get back user's selected category and store in chosen_category
                # TODO (UI): Delete text interface code below

                chosen_category = None

                ### BEGIN TEXT INTERFACE ###
                print("Opponent's Choice!")
                print("Select a Jeopardy category for your opponent to answer:")
                chosen_category = self.__prompt_user_from_list(self.categories)
                #### END TEXT INTERFACE ####

                response_info = []

            elif parsed_message.code == MessageType.SPIN:
                [player_id] = parsed_message.args  # TODO: Why is this client receiving its own player ID?

                # TODO (UI): Ask this player to push a button to spin the wheel
                # TODO (UI): Delete text interface code below

                ### BEGIN TEXT INTERFACE ###
                print("Spin the wheel!")
                #self.root.bind('<Return>', self.handle_connection)
                #input("Press enter to spin the wheel")
                #### END TEXT INTERFACE ####
                self.btn_spin = ttk.Button(self.f2,text="Pass to question frame", command=self.load_question_frame)
                self.btn_spin.pack( side = BOTTOM, padx=50)

                #response_info = []

            elif parsed_message.code == MessageType.END_GAME:
                [winner_player_id] = parsed_message.args

                # TODO (UI): Tell player the game has ended, and display the winning player id
                # TODO (UI): Delete text interface code below

                ### BEGIN TEXT INTERFACE ###
                print("\n==========================\nEND OF GAME\n==========================\n")
                print(f"Player {winner_player_id} has won!")
                input("Press enter to end the game")
                #### END TEXT INTERFACE ####

                self.game_over = True
                response_info = []

            elif parsed_message.code == MessageType.UPDATE_SCORES:
                [scores_dict, tokens_dict, num_spins_remaining] = parsed_message.args

                # TODO (UI): Update the UI to display the new scores, number of tokens, and number of spins to players
                # TODO (UI): Delete text interface code below

                ### BEGIN TEXT INTERFACE ###
                print("\nUPDATED GAME VALUES:")
                print(f"Number of Spins Remaining This Round: {num_spins_remaining}")
                for player_id in scores_dict:
                    print(f"Player {player_id}: {scores_dict[player_id]} points | {tokens_dict[player_id]} tokens")
                print("")
                #### END TEXT INTERFACE ####

                response_info = []
                self.send_command(server, Message(parsed_message.code, response_info))
                #self.note.select(1)


            else:
                raise Exception(f"Client {self.player_id} received unknown MessageType: {parsed_message.code}")

            #self.send_command(server, Message(parsed_message.code, response_info))

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
            selected_index = int(input(f"Enter option number (0-{max_index}): "))

        print(f"You selected option #{selected_index}")

        return prompt_list[selected_index]

    def __set_player_id(self, server):
        """
        Waits for a player ID from Server, then stores it in this client's self.player_id
        :param server: Reference to the Server object
        :return:
        """
        logging.info("Waiting for player_id...")
        while not self.game_over:

            parsed_message = self.buffer_message(server)
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

    def show_submit_answer(self):
        #print(self.gAnswers.get())

        #print(self.gAnswers)
        #print(self.aAnswers)
        b = self.gAnswers.get()
        c = b[-1]
        f = int(c)


        #if self.gAnswers.get() == self.aAnswers:
            #showinfo(title=self.strl.question_show_info_correct_answer, message=self.gAnswers.get())
        #else:
            #showinfo(title=self.strl.question_show_info_wrong_answer, message=self.gAnswers.get())

        response_info = [c]
        #return response_info
        print(response_info)
        self.send_command(self.server, Message(MessageType.JEOPARDY_QUESTION, response_info))
        return

gameplayer = Client()
gameplayer.connect_to_game(SRV_IP, SRV_PORT)

# player2 = Client()
# player2.connect_to_game(SRV_IP, SRV_PORT+1)
