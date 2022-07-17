from board.board import Board
# import score_keeper.score_keeper import ScoreKeeper
import logging
import pickle

logging.basicConfig(level=logging.INFO)
HEADER_SIZE = 10

# https://www.youtube.com/watch?v=s6HOPw_5XuY

# pickling and buffering : https://pythonprogramming.net/pickle-objects-sockets-tutorial-python-3/

import socket
import threading

NUM_PLAYERS = 3
MAX_SPINS = 3
BYTE_ENCODING = 'utf-8'


class Message:
	def __init__(self, code, args):
		self.code = code
		self.args = args


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

		self.request_map = {1: "SPIN", 2: "SEE_SCORE", 3: "SELECT_CATEGORY"}

		# SETUP SUBSYSTEMS
		self.board = Board()

		self.num_spins = 0

	# self.ExecutiveLogic = ExecutiveLogic()
	# self.score_keeper = ScoreKeeper()
	# self.wheel = Wheel()

	def host_game(self):
		server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # setup server socket
		server.bind((self.host_ip, self.port))
		logging.info("server starting a game, listening for players on port: " + str(self.port))
		server.listen(NUM_PLAYERS - 1)  # listen for 2 connections. 3 player game

		client, addr = server.accept()  # next player connection

		# player_id_command = 'PlayerID,' + str(self.new_player_id)
		player_id_command = Message("PlayerID", self.new_player_id)
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

		while self.num_spins <= MAX_SPINS:
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
				parse_request = client_request.split(',', 1)
				logging.info("client request type:" + str(type(client_request)) + str(client_request)) # self.request_map)
				logging.info("Server received request from user: " + self.request_map[int(parse_request[0])])

				request_command = self.request_map[int(parse_request[0])]


				# command = ""
				command = Message("None", [])
				if request_command == "SPIN":
					logging.info("Server messaging WHEEL to SPIN ")

					# send message to Wheel!
					wheel_result = "History"  # TODO: get spin result from wheel
					logging.info("Server got spin result from WHEEL:" + wheel_result)
					# command = Message("SPIN_RESULT", wheel_result)
					command = Message("SPIN_RESULT", wheel_result)
					self.num_spins += 1

				elif request_command == "SEE_SCORE":
					logging.info("Server received SEE SCORE request from user")

					# get current score from the scorekeeper
					logging.info(
						"Server getting scores from the scorekeeper")  # TODO get current score from the scorekeeper
					# scores = self.scorekeeper.getScores()
					scores = {1: 100, 2: 100, 3: 100, 4: 100}

					command = Message("SCORE", scores)
					print("SCORES:", scores)

				elif request_command == "SELECT_CATEGORY":
					logging.info("Server received category selection from user")

					# get next question from the board
					logging.info("Server getting question from the board")  # TODO get question from board

					next_question = "What is a byte?"
					# command = "QUESTION," + next_question
					command = Message("QUESTION", next_question)


				self.send_command(client, command)

			# send question message to the clients

	# self.game_over = True
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
		command = pickle.dumps(command)

		# if isinstance(command, str):
		# 	command = pickle.dumps(command, -1)

			# client.send(msg)  # command to client
		# elif isinstance(command, bytes):
		msg = bytes(f"{len(command):<{HEADER_SIZE}}", BYTE_ENCODING) + command  # add fixed length header to message
		print(msg[HEADER_SIZE:])
		client.send(msg)  # command to client


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
