# Run setup
import logging
from executive_logic import executive_logic

PORT = 5555
SRV_IP = 'localhost'

# my_ui = user_interface()
# my_ui.runSetup()
#
# my_ui.startGame()

logging.basicConfig(level=logging.INFO)

game = executive_logic.ExecutiveLogic(SRV_IP, PORT)
game.game_server.host_game()  # this is the game maker's laptop
