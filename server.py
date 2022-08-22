import logging
import pickle
from enum import Enum
import socket
import threading
import select
logging.basicConfig(level=logging.INFO)
HEADER_SIZE = 10

# https://www.youtube.com/watch?v=s6HOPw_5XuY

# pickling and buffering : https://pythonprogramming.net/pickle-objects-sockets-tutorial-python-3/

MAX_SPINS = 3
BYTE_ENCODING = 'utf-8'

class QueryStatus(Enum):
    SERVER_TO_CLIENT = 1  # Information is being sent from Executive Logic to Server to Client
    CLIENT_TO_SERVER = 2  # Information is being sent from Client to Server to Executive Logic
    STANDBY = 3  # No information is being sent right now


class MessageType(Enum):
    """
	Enum of all message types that may be sent between executive <-> server <-> client.
	Part of the Message class. Always accompanied by a list of arguments, which is different based on the message type.

	Each message type will be sent by the Executive (requesting information), with some arguments.
	A message of the same type will then be sent by the Client (responding), with different arguments.
	"""
    EMPTY = 0  # No message.
    # Request  Args: 	[]
    # Response Args:	[]

    PLAYER_ID = 1  # Called by server the first time it connects to a client. Assigns that client its unique player ID (0, 1, or 2).
    # Request Args:     []
    # Response Args:    []

    JEOPARDY_QUESTION = 2  # Called to ask server to ask client to answer a Jeopardy question.
    # Request  Args: 	[Board.tile]
    # Response Args:	[user_answer]

    PLAYERS_CHOICE = 3  # Called to ask server to ask client to ask a player to input a Jeopardy category.
    # Request  Args: 	[round_num]
    # Response Args:	[chosen_category]

    OPPONENTS_CHOICE = 4  # Called to ask server to ask client to ask a player to input a Jeopardy category.
    # Request  Args: 	[round_num]
    # Response Args:	[chosen_category]

    SPIN = 5  # Called to ask server to ask client to notify player it's their turn, and ask that player to spin the wheel.
    # Request  Args: 	[]
    # Response Args:	[]

    END_GAME = 6  # Called to tell server that the game has ended.
    # Request  Args:	[winner_player_id]
    # Response Args:	[]

    UPDATE_SCORES = 7  # Called to tell server updated game values, to display to client.
    # Request  Args: 	[scores_dict, tokens_dict, num_spins, curr_round]
    # Response Args:	[]

    UPDATE_BOARD = 8  # Called at the start of the round, to tell server/client what the board looks like
    # Request  Args:    [board]
    # Response Args:    []

    SPIN_RESULT = 9  # Called to tell server/client what the result of the latest spin was
    # Request  Args:    [sector_result]
    # Response Args:    []


class Message:
    def __init__(self, code: MessageType, args: list):
        self.code = code
        self.args = args


class Messenger:
    def __init__(self, srv_ip, srv_port):
        self.host_ip = srv_ip
        self.port = srv_port

    def select_readable(self, client_list):
        timeout = 1
        ready_to_read, ready_to_write, in_error = \
            select.select(
                client_list,
                [],
                [],
                timeout)
        return ready_to_read

    def select_writeable(self, client_list):
        timeout = 1
        ready_to_write, ready_to_write, in_error = \
            select.select(
                [],
                client_list,
                [],
                timeout)
        return ready_to_write

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
    def __init__(self, srv_ip, srv_port, num_players, executive_logic):
        super().__init__(srv_ip, srv_port)
        self.host_ip = srv_ip
        self.port = srv_port
        self.num_players = num_players

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # setup self.server_socket socket
        self.server_socket.bind((self.host_ip, self.port))
        logging.info("self.server_socket starting a game, listening for players on port: " + str(self.port))
        self.server_socket.listen(self.num_players)  # listen for players to join
        self.sockets_list = [self.server_socket]
        self.client_sock_dict = {}  # playerID: client socket

        self.executive_logic = executive_logic

        self.whose_turn = 1  # pointer to current player taking turn
        self.game_over = False

        self.next_player_id = 0
        self.players = []  # keep track of players

    def host_game(self):
        """
        Game setup. Called once, before the start of the game, by main.py.
        :return: void
        """
        # send each new player their playerID
        for _ in range(self.num_players):
            logging.info("Adding player %d", self.next_player_id)
            client_sock, addr = self.server_socket.accept()  # next player connection
            new_player_id = self.__get_new_player_id()
            self.client_sock_dict[new_player_id] = client_sock  # add them to the client socket dict

            player_id_command = Message(MessageType.PLAYER_ID, [new_player_id])
            self.send_command(client_sock, player_id_command)
            # threading.Thread(target=self.handle_connection, args=(client_sock, new_player_id,)).start()  # start thread for this client_sock

        self.executive_logic.run_game()
        self.server_socket.close()  # handle one game

    def __get_new_player_id(self):
        """
        Assigns new player a unique ID, and adds them to the player list
        :return: (int) Unique ID for a new player
        """
        self.players.append(self.next_player_id)
        tmp = self.next_player_id
        self.next_player_id += 1
        return tmp

    def handle_connection(self):
        """
        Handle incoming requests from ExecLogic and Client.
        Runs in a separate thread for the duration of the game.
        Separate thread for each player.
        :param client: Instance of Client
        :param this_player_id: ID of this client's player
        :return: void
        """
        # logging.info("Handling client connections...")

        if self.executive_logic.waiting_on_player_id is not None:
            client = self.client_sock_dict[self.executive_logic.waiting_on_player_id]  # just one client at a time right now
            if self.executive_logic.query_status == QueryStatus.CLIENT_TO_SERVER:  # Wait for response from client
                read_sockets = self.select_readable([client])
                for notified_socket in read_sockets:
                    if notified_socket != self.server_socket:
                        print("\n\n=====================================================\n\n")
                        parsed_message = self.buffer_message(notified_socket)  # Wait for client response
                        self.executive_logic.store_query(parsed_message.code,
                                                         parsed_message.args)  # Store client response in executive logic
                        logging.info("Server received message from client: %s", parsed_message.code)
                        self.executive_logic.query_status = QueryStatus.STANDBY  # Reset query status to standby

            elif self.executive_logic.query_status == QueryStatus.SERVER_TO_CLIENT:  # Send message to client
                client = self.client_sock_dict[self.executive_logic.waiting_on_player_id]  # just one client at a time right now
                write_sockets = self.select_writeable([client])
                for write_client in write_sockets:
                    command = self.executive_logic.server_message  # Get Message from server
                    self.send_command(write_client, command)  # Send Message to client
                    self.executive_logic.query_status = QueryStatus.CLIENT_TO_SERVER  # Switch query status to listen for response from client (#TODO: this means the client will be required to send some response for every message, including things like "update scores" when it really has nothing to say. Change?)
            else:
                # raise Exception("Unknown query status %s in server!", self.executive_logic.query_status)
                pass