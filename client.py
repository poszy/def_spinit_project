# from ui.user_interface import UserInterface

import socket
import threading
import logging
import pickle

NUM_PLAYERS = 3
SRV_IP = 'localhost'
SRV_PORT = 5555
BYTE_ENCODING = 'utf-8'
HEADER_SIZE = 10

logging.basicConfig(level=logging.INFO)

class Message:
	def __init__(self, code, args):
		self.code = code
		self.args = args

class Client:

	# default constructor
	def __init__(self):
		self.player_id = 1
		self.whose_turn = 1  # pointer to curent player taking turn
		self.game_over = False

		self.categories = ["Delicious Bytes", "String Theory", "Logic Games", "So Random"]

	# SETUP SUBSYSTEMS
	# self.ui = UserInterface()

	def connect_to_game(self, host, port):
		server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # another TCP socket
		server.connect((host, port))
		logging.info("Connecting to the game server")
		threading.Thread(target=self.handle_connection, args=(server,)).start()  # start threading immediately

	def buffer_message(self, client):
		msg_flag = True
		buffer = b''
		while True:
			pkt = client.recv(100)  # buffer the received data
			if not pkt:
				client.close
				break
			if msg_flag:
				print("new message length:", pkt[:HEADER_SIZE])
				msg_length = int(pkt[:HEADER_SIZE])
				msg_flag = False

			buffer += pkt
			full_msg_length = len(buffer)
			logging.info("message buffer length:" + str(full_msg_length))

			if len(buffer) - HEADER_SIZE == msg_length:
				logging.info("Full message received with length:" + str(full_msg_length))

				print(buffer[HEADER_SIZE:])
				# server_message = pkt.decode(BYTE_ENCODING)
				server_message = pickle.loads(buffer[HEADER_SIZE:])
				msg_flag = True
				buffer = b''
				# parsed_message = server_message.split(",", 1)
				logging.info("-------------------------------------------------")
				logging.info("Received message from server: %s", server_message)

				return server_message # parsed_message

	def handle_connection(self, client):
		logging.info("Entered handle_connections")
		# check for round over?
		# self.ExecutiveLogic
		while not self.game_over:
			parsed_message = self.buffer_message(client)

			if parsed_message.code == "PlayerID":
				self.player_id = parsed_message.args

			elif parsed_message.code == "SPIN_RESULT":
				logging.info("Received spin result was: " + parsed_message.args)
				if parsed_message.code == "SPIN_AGAIN":
					spin_again = "1"
					spin_again_command = Message("1", [])
					client.send_command(spin_again_command)
					# client.send(spin_again.encode("utf"))  # send message to game server

			elif parsed_message.code == "SCORE":
				logging.info("Received current scores: ", parsed_message.args)

				dict_scores = parsed_message.args
				logging.info("Received scores: ", dict_scores)
				print("SCORES: ", dict_scores)

			turn_message = ""
			print("Enter a command for the game server:")
			print("----- 1) Spin the wheel")
			print("----- 2) See scores")
			print("----- 3) Select Category")

			turn_message = str(input("Command: "))

			# Let player select the category
			if turn_message == "3":
				print("Category Options:")
				options = range(0, len(self.categories))
				for cat in options:
					print("----- " + str(cat) + ") " + str(self.categories[cat]))
					selected_category = ""
				options_str = [str(opt) for opt in options]
				while selected_category not in options_str:
					selected_category = input("Enter category number (1-" + str(len(self.categories)) + "): ")

				turn_message += "," + selected_category

			client.send(str(turn_message).encode("utf"))  # send message to game server

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
	def send_command(self, client, command):
		command = pickle.dumps(command)
		msg = bytes(f"{len(command):<{HEADER_SIZE}}", BYTE_ENCODING) + command  # add fixed length header to message
		print(msg[HEADER_SIZE:])
		client.send(msg)  # command to server

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
