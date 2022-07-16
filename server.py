from board.board import Board
# import score_keeper.score_keeper import ScoreKeeper
import logging

logging.basicConfig(level=logging.INFO)
# from collections import defaultdict

# https://www.youtube.com/watch?v=s6HOPw_5XuY

import socket
import threading

NUM_PLAYERS = 3


class GameServer:

	# default constructor
	def __init__(self, srv_ip, srv_port):
		self.host_ip = srv_ip
		self.port = srv_port

		self.player_id = 1
		self.whose_turn = 1  # pointer to curent player taking turn
		self.game_over = False

		self.new_player_id = 1
		self.players = []  # keep track of players

		self.request_map = {1: "SPIN", 2: "SEE_SCORE", 3: "LIST_PLAYERS"}

		# SETUP SUBSYSTEMS
		self.board = Board()

	# self.ExecutiveLogic = ExecutiveLogic()
	# self.score_keeper = ScoreKeeper()
	# self.wheel = Wheel()

	def host_game(self):
		server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # setup server socket
		server.bind((self.host_ip, self.port))
		logging.info("server starting a game, listening for players on port: " + str(self.port))
		server.listen(NUM_PLAYERS - 1)  # listen for 2 connections. 3 player game

		client, addr = server.accept()  # next player connection

		player_id_command = 'PlayerID,' + str(self.new_player_id)
		self.send_command(client, player_id_command)

		# client.send(bytes('Player add client to the players database
		self.players.append(self.new_player_id)
		self.new_player_id += 1

		threading.Thread(target=self.handle_connection, args=(client,)).start()  # start threading immediately
		server.close()  # handle one game

	# def connect_to_game(self, host, port):
	# 	client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # another TCP socket
	# 	client.connect((self.host, self.port))
	# 	logging.info("connected to the game")
	# 	threading.Thread(target= self.handle_connection, args=(client,)).start()  # start threading immediately

	def handle_connection(self, client):
		# check for round over?
		# self.ExecutiveLogic

		while not self.game_over:
			turn_message = ""

			logging.info("Handling connections...")

			# if self.whose_turn == self.player_id:  # it's my turn
			# 	# player takes a turn
			#
			# 	# spin wheel
			#
			# 	turn_message = "turn over"
			# 	client.send(turn_message.encode("utf"))  # send message to game server

			# else:  # not my turn!
			data = client.recv(100)
			if not data:
				client.close()
				break
			else:
				client_request = data.decode('utf')
				# parse_request = client_request.split(',')
				print("client request type:", type(client_request), client_request, self.request_map)
				logging.info("Server received request from user: " + self.request_map[int(client_request)])

				request_command = self.request_map[int(client_request)]

				if (request_command == "SPIN"):
					logging.info("Server messaging WHEEL to SPIN ")

					# send message to Wheel!
					wheel_result = "History"  # TODO: get spin result from wheel
					logging.info("Server got spin result from WHEEL:" + wheel_result)
					self.send_command(client, "SPIN_RESULT," + wheel_result)
			self.game_over = True
			# # command = parse_request[0]
			# args = parse_request[1:]
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
		client.send(bytes(command, 'utf-8'))  # command to client
		# client.close()  # close connection

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
