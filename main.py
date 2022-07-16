
# Run setup
import logging
from server import GameServer
PORT = 5555
SRV_IP = 'localhost'

# my_ui = user_interface()
# my_ui.runSetup()
#
# my_ui.startGame()

logging.basicConfig(level=logging.INFO)


game = GameServer(SRV_IP, PORT)
game.host_game()  # this is the game maker's laptop
