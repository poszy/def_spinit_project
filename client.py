from ui.user_interface import UserInterface

import socket
import threading
import logging
from tkinter import *
from tkinter import ttk
from server import Message, QueryStatus, MessageType, Messenger
from ui import s
import pygame.mixer
from wheel.wheel import Sector
from tkinter.messagebox import showinfo

import random
import time
import tkinter
from PIL import Image, ImageTk

NUM_PLAYERS = 3
SRV_IP = 'localhost'
SRV_PORT = 5555
BYTE_ENCODING = 'utf-8'
HEADER_SIZE = 10
MUSIC_FILE = 'resources/audio/Jeopardy-theme-song.mp3'
# global demo

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
        self.lobby_frame_0 = ttk.Frame(self.note)
        self.lbl_player_wait = ttk.Label(self.lobby_frame_0,
                                         text='Press the button to enter the game.  ',
                                         padding="10", width="300")
        self.lbl_player_wait.pack(side=TOP)

        # Add Frame to Notebook. This is the Lobby Frame
        self.note.add(self.lobby_frame_0)

        # Create Wheel Frame
        self.spin_prompt_frame_1 = ttk.Frame(self.note)
        self.populate_spin_prompt_frame()

        # Add Frame to Notebook
        self.note.add(self.spin_prompt_frame_1)
        self.note.pack(expand=1, fill='both', padx=5, pady=5)
        self.category_selected = StringVar()


        # Create Spinning Wheel Frame
        self.spinning_wheel_frame_2 = ttk.Frame(self.note)
        # self.populate_spinning_frame()

        # Add Frame to Notebook
        self.note.add(self.spinning_wheel_frame_2)
        self.note.pack(expand=2, fill='both', padx=5, pady=5)


        # Create Question Frame
        self.prompt_frame_3 = ttk.Frame(self.note)

        # Add Frame to Notebook
        self.note.add(self.prompt_frame_3)
        self.note.pack(expand=2, fill='both', padx=5, pady=5)
        self.note.add(self.prompt_frame_3)
        self.note.pack(expand=3, fill='both', padx=5, pady=5)

        # Wait for Client to send turn signal, for now it is initiated by button
        self.btn_play = ttk.Button(self.lobby_frame_0, text="Connect to Game", command=self.connect_to_game)
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

    def load_spin_prompt_frame(self):
        self.note.select(1)

        # self.btn_spin = ttk.Button(self.canvas, text="Spin the Wheel", command=self.load_wheel_spinning_frame)
        # self.btn_spin.place(x=500, y=900)

        # self.send_spin_command()

    def load_wheel_spinning_frame(self):
        self.note.select(2)

        self.filename = 'ui/ROUND1.png'

        self.canvas = tkinter.Canvas(self.spinning_wheel_frame_2, width=1000, height=1200)
        self.canvas.place(x=0,y=0)

        # Create a Label Widget to display the text or Image
        self.lbl_wheel_arrow = ttk.Label(self.canvas, text="↓", font=("Helvetica", 45))
        self.lbl_wheel_arrow.place(x=500, y=100)

        self.process_next_frame = self.draw(self.demo).__next__  # Using "next(self.draw())" doesn't work

        self.spinning_wheel_frame_2.after(3, self.process_next_frame)


        # self.btn_ctn = ttk.Button(self.canvas, text="Continue", command=self.load_prompt_frame)
        # self.btn_ctn.place(x=500, y=900)

    def __start_music(self):
        pygame.mixer.music.play(loops=1)

    def __stop_music(self):
        pygame.mixer.music.stop()

    def prompt_continue_after_spin_result(self):

        self.load_wheel_spinning_frame()

        # self.btn_spin.pack_forget()  # hide submit button


    def continue_after_spin_result(self):
        self.lbl_spin_res.set(self.strl.spin_result_label)  # clear old spin result
        self.btn_continue.pack_forget()  # hide continue button
        self.spin_result.pack_forget()  # hide old spin result
        response_info = []
        self.send_command(self.server, Message(MessageType.SPIN_RESULT, response_info))
        self.btn_spin.pack(side=BOTTOM, padx=50)  # put spin button back
        self.load_prompt_frame()

    def load_prompt_frame(self):
        self.note.select(3)

    def populate_spin_prompt_frame(self):
        #### END TEXT INTERFACE ####
        self.filename = 'blank.png'
        self.image = Image.open(self.filename)
        self.tkimage = ImageTk.PhotoImage(self.image)
        self.canvas = tkinter.Canvas(self.spin_prompt_frame_1, width=1000, height=1200)
        self.canvas.create_image(500, 500, image=self.tkimage)
        self.canvas.place(x=0, y=0)
        lbl_player_question = ttk.Label(self.spin_prompt_frame_1, text=self.strl.player_turn_spin, padding="10", width="300")
        lbl_player_question.pack(side=TOP)
        self.btn_spin = ttk.Button(self.spin_prompt_frame_1, text=self.strl.wheel_btn_spin, command=self.send_spin_command)
        self.btn_spin.pack(side=BOTTOM, padx=50)  # put spin button on screen first


        # don's show this yet
        self.btn_continue = ttk.Button(self.spin_prompt_frame_1, text=self.strl.continue_button_label, command=self.continue_after_spin_result)

        self.lbl_spin_res = StringVar()
        self.lbl_spin_res.set(self.strl.spin_result_label)
        self.spin_result = ttk.Label(self.spin_prompt_frame_1, textvar=self.lbl_spin_res,
                                     padding="10",
                                     width="300")

    # def populate_spinning_frame(self):

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
        self.lbl_selected_category = Label(self.spin_prompt_frame_1, text=" ")
        self.lbl_selected_category.pack()

    def send_spin_command(self):
        cc = self.category_selected.get()
        self.send_command(self.server, Message(MessageType.SPIN, cc))
        #self.load_prompt_frame()

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

        logging.info(f"Connecting to the game self.server {self.srv_port}")
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
                self.load_prompt_frame()
                self.__start_music()
                [jeopardy_category, tile] = parsed_message.args

                lbl_category = ttk.Label(self.prompt_frame_3, text=f"Category: {jeopardy_category}: {tile.points}", padding="10",
                                         width="300")
                lbl_category.pack(side=TOP)

                self.prompt_jeopardy_question(tile, jeopardy_category)


            elif parsed_message.code == MessageType.PLAYERS_CHOICE:
                [open_categories] = parsed_message.args  # TODO: Why is this client receiving its own player ID?

                prompt_text = "Player's Choice: select a question category for your turn"
                lbl_category = ttk.Label(self.prompt_frame_3, text=prompt_text, padding="10",
                                         width="300")
                lbl_category.pack(side=TOP)

                self.prompt_category_choice(open_categories, MessageType.PLAYERS_CHOICE)

            elif parsed_message.code == MessageType.OPPONENTS_CHOICE:
                [open_categories] = parsed_message.args  # TODO: Why is this client receiving its own player ID?

                self.prompt_category_choice(open_categories, MessageType.OPPONENTS_CHOICE)

            elif parsed_message.code == MessageType.SPIN:
                _ = parsed_message.args

                self.load_spin_prompt_frame()


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
                if curr_round == 2:
                    self.filename = 'ui/ROUND22.png'

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

                # O(1) Super Algorithm
                print(f"secret spin result: {spin_result}")

                if type(spin_result) == str:
                    result_str = self.strl.spin_result_label + spin_result
                else:
                    spin_result = spin_result.name
                    result_str = self.strl.spin_result_label + spin_result

                self.lbl_spin_res.set(result_str)
                print(f"secret spin result: {spin_result}")

                if spin_result == "A IS FOR AUTUMN":
                    demo = 12
                elif spin_result == Sector.LOSE_TURN.name or spin_result == Sector.BANKRUPT.name:
                    demo = 42
                elif spin_result == "UU COMPLETE ME":
                    demo = 72
                elif spin_result == "1 WORD, 2 MEANINGS":
                    demo = 102
                elif spin_result == "1970s TV":
                    demo = 132
                elif spin_result == "3 Ns":
                    demo = 162
                elif spin_result == "3 VOWELS IN A ROW":
                    demo = 189
                elif spin_result == "4-LETTER WORDS":
                    demo = 222
                elif spin_result == "4-SYLLABLE WORDS":
                    demo = 252
                elif spin_result == Sector.SPIN_AGAIN.name:
                    demo = 276
                elif spin_result == Sector.FREE_TURN.name:
                    demo = 312
                elif spin_result == '"ISM"s':
                    demo = 336
                elif spin_result == Sector.OPPONENTS_CHOICE.name or spin_result == Sector.PLAYERS_CHOICE.name:
                    demo = 358


                ### Round Two Logic xD
                elif spin_result == 'A BOROUGH BURIAL':
                    demo = 12
                # elif spin_result == "LOSE TURN":
                #     demo = 36
                elif spin_result == "ACM Awards":
                    demo = 60
                elif spin_result == "A SHRUBBERY!":
                    demo = 120
                elif spin_result == "AMERICAN HISTORY":
                    demo = 132
                elif spin_result == "AFTER MATH":
                    demo = 156
                elif spin_result == "ALL MY TROUBLES":
                    demo = 216
                elif spin_result == "ALTRUISTIC ATHLETES":
                    demo = 240
                elif spin_result == "ALL THINGS BELGIAN":
                    demo = 262
                # elif spin_result == "SPIN AGAIN":
                #     demo = 276
                # elif spin_result == "FREE TOKEN":
                #     demo = 336
                elif spin_result == 'BODIES OF WATER':
                    demo = 360
                else:
                    demo = 0

                self.demo = demo
                print("demo " + str(demo))

                self.prompt_continue_after_spin_result()

                # response_info = []
                # self.send_command(self.server, Message(parsed_message.code, response_info))

            else:
                raise Exception(f"Client {self.player_id} received unknown MessageType: {parsed_message.code}")

            # self.send_command(self.server, Message(parsed_message.code, response_info))

    def __prompt_user_from_list(self, prompt_list: list):
        """from PIL import Image, ImageTk

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

        # clear the screen of the question and answers
        self.__clear_frame(self.prompt_frame_3)

    def draw(self, iteration):

        demo = iteration
        print("demo: " + str(demo))

        self.spinning_wheel_frame_2.after(3, self.process_next_frame)


        image = Image.open(self.filename)
        #tkimage = ImageTk.PhotoImage(image.rotate(angle))
        #canvas_obj = self.canvas.create_image(500, 500, image=tkimage)
        # Create a photoimage object of the image in the path
        # Create an object of tkinter ImageTk


        angle = 0
        print(self.process_next_frame)

        n = 0
        #rr = random.choice(self.iterations)
        rr =  demo
        print( "Random iteration: " + str (rr))
        spin_time = rr + 372
        print(spin_time)

        while n <= spin_time:
            tkimage = ImageTk.PhotoImage(image.rotate(angle))
            canvas_obj = self.canvas.create_image(500, 500, image=tkimage)

            #Process next frame
            self.spinning_wheel_frame_2.after_idle(self.process_next_frame)

            # Delete previous state of image
            yield
            self.canvas.delete(canvas_obj)

            # Angle controls the speed
            angle += 12


            angle %= 360
            time.sleep(0.002)
            print(n)

            # Keeping up with frames.
            n = n + 12

            if n == spin_time:

                if rr == 60:

                    print("category 1")
                    self.demo_category='1 WORD, 2 MEANINGS'

                elif rr == 96:

                    print("category 2")
                    self.demo_category='1 WORD, 2 MEANINGS'

                elif rr == 120:

                    print("category 3")
                    self.demo_category='1 WORD, 2 MEANINGS'

                elif rr == 156:

                    print("category  4")
                    self.demo_category='1 WORD, 2 MEANINGS'

                elif rr == 180:

                    print("category 5")
                    self.demo_category='1 WORD, 2 MEANINGS'

                elif rr == 216:

                    print("category 6")
                    self.demo_category='1 WORD, 2 MEANINGS'

                elif rr == 240:

                    print("category 7")
                    self.demo_category='1 WORD, 2 MEANINGS'
                elif rr == 276:

                    print("category 8")
                    self.demo_category='1 WORD, 2 MEANINGS'
                elif rr == 300:

                    print("category 9")
                    self.demo_category='1 WORD, 2 MEANINGS'
                elif rr == 336:

                    print("category 10")
                    self.demo_category='1 WORD, 2 MEANINGS'

                elif rr == 360:
                    print("category 11")
                    self.demo_category='1 WORD, 2 MEANINGS'

                else:
                    print("category 0")
                    self.demo_category='1 WORD, 2 MEANINGS'

        # self.canvas.delete(canvas_obj)
        time.sleep(2)
        self.load_spin_prompt_frame()
        self.btn_continue.pack(side=BOTTOM, )
        self.spin_result.pack(side=TOP)  # show the spin result
        self.btn_spin.pack_forget()
        # self.load_prompt_frame()
        # self.send_spin_command()


gameplayer = Client(SRV_IP, SRV_PORT)
# gameplayer.connect_to_game(SRV_IP, SRV_PORT)

# player2 = Client()
# player2.connect_to_game(SRV_IP, SRV_PORT+1)
