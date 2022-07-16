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
		client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # another TCP socket
		client.connect((host, port))
		logging.info("connected to the game")
		threading.Thread(target= self.handle_connection, args=(client,)).start()  # start threading immediately

	def handle_connection(self, client):
		# check for round over?
		# self.ExecutiveLogic

		while not self.game_over:
			turn_message = ""

			turn_message = "Client registering to server"
			client.send(turn_message.encode("utf"))  # send message to game server
			# if self.whose_turn == self.player_id:  # it's my turn
			# 	# player takes a turn
			#
			# 	# spin wheel
			#
			# 	turn_message = "turn over"
			client.send(turn_message.encode("utf"))  # send message to game server
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

