# from ui.user_interface import UserInterface

import socket
import threading
import logging


NUM_PLAYERS = 3
SRV_IP = 'localhost'
SRV_PORT = 5555
logging.basicConfig(level=logging.INFO)
class Client:

	# default constructor
	def __init__(self):
		self.player_id = 1
		self.whose_turn = 1  # pointer to curent player taking turn
		self.game_over = False

		# SETUP SUBSYSTEMS
		# self.ui = UserInterface()

	def connect_to_game(self, host, port):
		server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # another TCP socket
		server.connect((host, port))
		logging.info("Connecting to the game server")
		threading.Thread(target= self.handle_connection, args=(server,)).start()  # start threading immediately

	def handle_connection(self, client):
		# check for round over?
		# self.ExecutiveLogic

		while not self.game_over:
			data = client.recv(100)
			if not data:
				client.close()
				break
			else:
				server_message = data.decode('utf')
				parsed_message = server_message.split(",")
				logging.info("Received message from server: %s", server_message)

				if parsed_message[0] == "PlayerID":
					self.player_id = int(parsed_message[1])
				elif parsed_message[0] == "SPIN_RESULT":
					logging.info("Received spin result was: " + parsed_message[1])
					if parsed_message[0] == "SPIN_AGAIN":
						spin_again = "1"
						client.send(spin_again.encode("utf"))  # send message to game server


				turn_message = ""
				print("Enter a command for the game server:")
				print("----- 1) Spin the wheel")
				print("----- 2) See scores")
				print("----- 3) List players")

				turn_message = input("Command: ")
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
