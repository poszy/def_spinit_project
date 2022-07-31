from ui.user_interface import UserInterface

import socket
import threading
import logging

from server import Message, QueryStatus, MessageType, Messenger
from board.questions import Tile

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
        self.whose_turn = 1  # TODO: Unused. Currently, each client doesn't know whose turn it is; they're only notified when server asks them something
        self.game_over = False

        self.ui = UserInterface()  # TODO (UI): Unused. Fill in with any required arguments.

        self.categories = ["Delicious Bytes", "String Theory", "Logic Games", "So Random"]  # TODO: Should receive Jeopardy board from Server at start of round


    # SETUP SUBSYSTEMS
    # self.ui = UserInterface()

    def connect_to_game(self, host, port):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # another TCP socket
        server.connect((host, port))
        logging.info("Connecting to the game server")
        threading.Thread(target=self.handle_connection, args=(server,)).start()  # start threading immediately

    def handle_connection(self, server):
        logging.info("Entered handle_connections")

        self.__set_player_id(server)  # Receive this client's player ID from server

        while not self.game_over:
            parsed_message = self.buffer_message(server)
            logging.info("Client received message from server: %s", parsed_message.code)

            response_info = []
            # TODO: Add logic for each of the received MessageTypes
            if parsed_message.code == MessageType.EMPTY:
                response_info = []

            elif parsed_message.code == MessageType.PLAYER_ID:
                raise Exception("This client (ID %s) was already assigned a player ID!", self.player_id)

            elif parsed_message.code == MessageType.JEOPARDY_QUESTION:
                [player_id, tile] = parsed_message.args  # TODO: Why is this client receiving its own player ID?

                # TODO (UI): Display question (tile.question) and answer choices (tile.answers) to user
                # TODO (UI): Get back user answer and store in user_answer
                # TODO (UI): Delete text interface code below

                user_answer = None  # Note: user_answer should be a string from tile.answers, like user_answer = tile.answers[1]

                ### BEGIN TEXT INTERFACE ###
                # Note: Expecting tile.answers to be a list of strings
                print("Here's your question:")
                print(str(tile.question))
                user_answer = self.__prompt_user_from_list(tile.answers)
                #### END TEXT INTERFACE ####

                response_info = [user_answer]

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

            elif parsed_message.code == MessageType.SPIN:
                [player_id] = parsed_message.args  # TODO: Why is this client receiving its own player ID?

                # TODO (UI): Ask this player to push a button to spin the wheel
                # TODO (UI): Delete text interface code below

                ### BEGIN TEXT INTERFACE ###
                print("Spin the wheel!")
                input("Press enter to spin the wheel")
                #### END TEXT INTERFACE ####

                response_info = []

            elif parsed_message.code == MessageType.END_GAME:
                [winner_player_id] = parsed_message.args

                # TODO (UI): Tell player the game has ended, and display the winning player id
                # TODO (UI): Delete text interface code below

                ### BEGIN TEXT INTERFACE ###
                print("\n==========================\nEND OF GAME\n==========================\n")
                print("Player %d has won!", winner_player_id)
                input("Press enter to end the game")
                #### END TEXT INTERFACE ####

                self.game_over = True
                response_info = []

            elif parsed_message.code == MessageType.UPDATE_SCORES:
                [scores_dict, tokens_dict, num_spins] = parsed_message.args

                # TODO (UI): Update the UI to display the new scores, number of tokens, and number of spins to players
                # TODO (UI): Delete text interface code below

                ### BEGIN TEXT INTERFACE ###
                print("\nUPDATED GAME VALUES:")
                print("Number of Spins: %d", num_spins)
                for player_id in scores_dict.keys:
                    print("Player %d: %d points | %d tokens", scores_dict[player_id], tokens_dict[player_id])
                print("")
                #### END TEXT INTERFACE ####

                response_info = []

            else:
                raise Exception("Client %d received unknown MessageType: %s", self.player_id, parsed_message.code)

            self.send_command(server, Message(parsed_message.code, response_info))

            """
            if parsed_message.code == MessageType.SPIN_RESULT:
                logging.info("Received spin result was: " + parsed_message.args[0])

            elif parsed_message.code == MessageType.SPIN_AGAIN:
                spin_again_command = Message(MessageType.SPIN_AGAIN, [])
                server.send_command(spin_again_command)

            elif parsed_message.code == MessageType.SEE_SCORE:
                logging.info("Received current scores: ", parsed_message.args)

                dict_scores = parsed_message.args
                print("SCORES: ", dict_scores)

            print("\n\n=====================================================\n\n")

            print("Enter a command for the game server:")
            print("----- 1) Spin the wheel")
            print("----- 2) See scores")
            print("----- 3) Select Category")

            turn_message = ""
            while turn_message not in self.request_map.keys():  # in case someone enters invalid option
                turn_message = str(input("Command: "))
            request = self.request_map[turn_message]  # map to request type

            command = Message(request, [])

            # Let player select the category
            if request == "SELECT_CATEGORY":
                print("Category Options:")
                options = range(0, len(self.categories))
                for cat in options:
                    print("----- " + str(cat) + ") " + str(self.categories[cat]))
                    selected_category = ""
                options_str = [str(opt) for opt in options]
                while selected_category not in options_str:
                    max_opt = str(len(self.categories) - 1)
                    selected_category = input(f"Enter category number (0- {max_opt}): ")
                    print(f"selected_category = {selected_category}")
                command = Message(request, selected_category)  # include category in the message
            
            self.send_command(server, command)  # send message to game server
            """

    def __prompt_user_from_list(self, prompt_list: list):
        """
        Print out the contents of a list, and prompt the user to pick one.
        :param prompt_list: List of strings to pick from (e.g. a list of answers to a Jeopardy question
        :return: (string) The answer that the user selected
        """
        # Print out the options in the list
        for i in range(0, len(prompt_list)):
            print("----- " + str(i) + ") " + str(prompt_list[i]))
        # Ask user to select an option from the list
        selected_index = None
        while selected_index not in range(0, len(prompt_list)):
            max_index = str(len(prompt_list))
            selected_index = int(input(f"Enter option number (0-{max_index}): "))

        print(f"You selected option #{selected_index}")

        return prompt_list[selected_index]

    # self.game_over = True
    # if self.whose_turn == self.player_id:  # it's my turn
    # 	# player takes a turn
    #
    # 	# spin wheel
    #
    # 	turn_message = "turn over"
    #
    #
    # else:  # not my turn!
    # 	data = client.recv(1024)
    # 	if not data:
    # 		client.close()
    # 		break
    # 	else:
    # 		parse_request = data.decode('utf').split(',')
    # 		command = parse_request[0]
    # 		args = parse_request[1:]
    # 		if parse_request[0] == 'select_category':  # opponent selects category
    # 			print("opponent" + self.player_id + "selecting the category")
    # 			pass
    # 		elif parse_request[0] =='check_answer': # check answer using server score_keeper
    # 			print("checking score!")
    # 			pass
    # 		# elif parse_request[0] == '' # some other command
    # 		else:
    # 			self.refresh_display()

    def __set_player_id(self, server):
        logging.info("Waiting for player_id...")
        while not self.game_over:

            parsed_message = self.buffer_message(server)
            logging.info("Received message with command code: %s", parsed_message.code)

            if parsed_message.code == MessageType.PLAYER_ID:
                self.player_id = parsed_message.args[0]
                logging.info("Player ID %s received", self.player_id)
                return

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


gameplayer = Client()
gameplayer.connect_to_game(SRV_IP, SRV_PORT)

# player2 = Client()
# player2.connect_to_game(SRV_IP, SRV_PORT+1)
