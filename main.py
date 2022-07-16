
# Run setup
from server import GameServer
PORT = 5555

# my_ui = user_interface()
# my_ui.runSetup()
#
# my_ui.startGame()

game = GameServer()
game.host_game("localhost", PORT)  # this is the game maker's laptop
