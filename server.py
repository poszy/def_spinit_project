from executive_logic.executive_logic import QueryStatus
import logging
import pickle
import time
from enum import Enum
import socket
import threading

logging.basicConfig(level=logging.INFO)
HEADER_SIZE = 10

# https://www.youtube.com/watch?v=s6HOPw_5XuY

# pickling and buffering : https://pythonprogramming.net/pickle-objects-sockets-tutorial-python-3/

NUM_PLAYERS = 3
MAX_SPINS = 3
BYTE_ENCODING = 'utf-8'


class MessageType(Enum):
	"""
	Enum of all message types that may be sent between executive <-> server <-> client.
	Part of the Message class. Always accompanied by a list of arguments, which is different based on the message type.

	Each message type will be sent by the Executive (requesting information), with some arguments.
	A message of the same type will then be sent by the Client (responding), with different arguments.
	"""
	EMPTY = 0					# No message.
									# Request  Args: 	[]
									# Response Args:	[]

	JEOPARDY_QUESTION = 1		# Called to ask server to ask client to answer a Jeopardy question.
									# Request  Args: 	[player_id, Wheel.tile]
									# Response Args:	[user_answer]

	PLAYERS_CHOICE = 2			# Called to ask server to ask client to ask a player to input a Jeopardy category.
									# Request  Args: 	[player_id, round_num]
									# Response Args:	[chosen_category]

	OPPONENTS_CHOICE = 3		# Called to ask server to ask client to ask a player to input a Jeopardy category.
									# Request  Args: 	[player_id, round_num]
									# Response Args:	[chosen_category]

	SPIN = 4					# Called to ask server to ask client to notify player it's their turn, and ask that player to spin the wheel.
									# Request  Args: 	[player_id]
									# Response Args:	[]

	END_GAME = 5				# Called to tell server that the game has ended.
									# Request  Args:	[winner_player_id]
									# Response Args:	[]

	UPDATE_SCORES = 6			# Called to tell server updated game values, to display to client.
									# Request  Args: 	[scores_dict, tokens_dict, num_spins]
									# Response Args:	[]

class Message:
	def __init__(self, code: MessageType, args: list):
		self.code = code
		self.args = args


class Messenger:
	def __init__(self, srv_ip, srv_port):
		self.host_ip = srv_ip
		self.port = srv_port

	def send_command(self, client, command):
		command = pickle.dumps(command)
		msg = bytes(f"{len(command):<{HEADER_SIZE}}", BYTE_ENCODING) + command  # add fixed length header to message
		# print(msg[HEADER_SIZE:])
		client.send(msg)  # command to client

	def buffer_message(self, client):
		msg_flag = True
		buffer = b''
		while True:
			pkt = client.recv(100)  # buffer the received data
			if not pkt:
				client.close
				break
			if msg_flag:
				# print("new message length:", pkt[:HEADER_SIZE])
				msg_length = int(pkt[:HEADER_SIZE])
				msg_flag = False

			buffer += pkt
			full_msg_length = len(buffer)
			# logging.info("message buffer length:" + str(full_msg_length))

			if len(buffer) - HEADER_SIZE == msg_length:
				logging.info("Full message received with length:" + str(full_msg_length))

				# print(buffer[HEADER_SIZE:])
				server_message = pickle.loads(buffer[HEADER_SIZE:])
				msg_flag = True
				buffer = b''
				# logging.info("-------------------------------------------------")
				# logging.info("Received message: %s", server_message)

				return server_message  # parsed_message


class GameServer(Messenger):

	# default constructor
	def __init__(self, srv_ip, srv_port, executive_logic):
		super().__init__(srv_ip, srv_port)
		self.host_ip = srv_ip
		self.port = srv_port
		self.executive_logic = executive_logic

		self.player_id = 1
		self.whose_turn = 1  # pointer to current player taking turn
		self.game_over = False

		self.new_player_id = 1
		self.players = []  # keep track of players

	def host_game(self):
		"""
		Game setup. Called by main.py.
		:return: void
		"""
		server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # setup server socket
		server.bind((self.host_ip, self.port))
		logging.info("server starting a game, listening for players on port: " + str(self.port))
		server.listen(NUM_PLAYERS - 1)  # listen for 2 connections. 3 player game

		client, addr = server.accept()  # next player connection

		# send new player its playerID
		player_id_command = Message("PlayerID", self.new_player_id)
		self.send_command(client, player_id_command)

		# client.send(bytes('Player add client to the players database
		self.players.append(self.new_player_id)
		self.new_player_id += 1

		threading.Thread(target=self.handle_connection, args=(client,)).start()  # start threading immediately
		server.close()  # handle one game

	def handle_connection(self, client):
		"""
		Handle incoming requests from ExecLogic and Client.
		Runs in a separate thread for the duration of the game.
		:param client: Instance of Client
		:return: void
		"""
		logging.info("Handling client connections...")

		while self.executive_logic.is_game_running:  # Loop while game is running
			if self.executive_logic.query_status == QueryStatus.CLIENT_TO_SERVER:  # Wait for response from client
				print("\n\n=====================================================\n\n")
				parsed_message = self.buffer_message(client)  # Wait for client response
				self.executive_logic.store_query(parsed_message.code, parsed_message.args)  # Store client response in executive logic
				logging.info("Received message with message type: %s", parsed_message.code)

			elif self.executive_logic.query_status == QueryStatus.SERVER_TO_CLIENT:  # Send message to client
				command = self.executive_logic.server_message  # Get Message from server
				self.send_command(client, command)  # Send Message to client

			elif self.executive_logic.query_status == QueryStatus.STANDBY:  # Wait for next request from exec or client
				time.sleep(0.1)
				continue
			else:
				raise Exception("Unknown query status in server!")



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

	def notify_spin_result(self, curr_player_id, wheel_result):
		"""
		Notifies client of a wheel spin result, so that it can display in the UI.
		:param curr_player_id: Player that spun the wheel.
		:param wheel_result: Result of the spin.
		:return: void
		"""
		pass
