from ui.user_interface import UserInterface
from server import Message, MessageType

import socket
import threading
import logging

from server import Message, Messenger
NUM_PLAYERS = 3
SRV_IP = 'localhost'
SRV_PORT = 5555
BYTE_ENCODING = 'utf-8'
HEADER_SIZE = 10

logging.basicConfig(level=logging.INFO)

class Client(Messenger):

	# default constructor
	def __init__(self):
		self.player_id = 1
		self.whose_turn = 1  # pointer to curent player taking turn
		self.game_over = False

		# TODO: should actually get from Game Board!
		self.categories = ["Delicious Bytes", "String Theory", "Logic Games", "So Random"]

		self.request_map = {"1": "SPIN", "2": "SEE_SCORE", "3": "SELECT_CATEGORY"}


	# SETUP SUBSYSTEMS
	# self.ui = UserInterface()

	def connect_to_game(self, host, port):
		server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # another TCP socket
		server.connect((host, port))
		logging.info("Connecting to the game server")
		threading.Thread(target=self.handle_connection, args=(server,)).start()  # start threading immediately

	def handle_connection(self, client):
		logging.info("Entered handle_connections")
		# check for round over?
		# self.ExecutiveLogic
		while not self.game_over:
			parsed_message = self.buffer_message(client)
			logging.info("Received message with command code: %s", parsed_message.code)

			if parsed_message.code == MessageType.PLAYER_ID:
				self.player_id = parsed_message.args[0]

			elif parsed_message.code == MessageType.SPIN_RESULT:
				logging.info("Received spin result was: " + parsed_message.args[0])

			elif parsed_message.code == MessageType.SPIN_AGAIN:
				spin_again_command = Message(MessageType.SPIN_AGAIN, [])
				client.send_command(spin_again_command)

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
					max_opt = str(len(self.categories)-1)
					selected_category = input(f"Enter category number (0- {max_opt}): ")
					print(f"selected_category = {selected_category}")
				command = Message(request, selected_category)  # include category in the message

			self.send_command(client, command)  # send message to game server

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
