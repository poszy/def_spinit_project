from server import GameServer
import logging
from collections import defaultdict
class InterfaceDemo(GameServer):

    def demo_all_interfaces(self):
        self.__demo_score_keeper()
        self.__demo_board()
        self.__demo_wheel()
        self.__demo_user_interface()
        self.__demo_executive_logic()

    def __demo_score_keeper(self):
        logging.info("\n\nPinging Scorekeeper Interfaces")
        add_items = [("Wil", 1000, 1), ("Luis", 9999, 3), ("Robyn", 1024, 0)]
        for player, pts, tokens in add_items:
            self.score_keeper.playerPoints[player] = pts
            self.score_keeper.playerTokens[player] = tokens
        logging.info("get_scores(): %s", self.score_keeper.get_scores())
        logging.info("get_tokens(): %s", self.score_keeper.get_tokens())
        logging.info("check_answer(): %s", self.score_keeper.check_answer("Right Answer", "Right Answer", 1, "Luis"))
        logging.info("has_token('Wil'): %s", self.score_keeper.has_token("Wil"))
        logging.info("use_token('Wil'): %s", self.score_keeper.use_token("Wil"))
        logging.info("bankrupt('Robyn'): %s", self.score_keeper.bankrupt("Robyn"))

    def __demo_board(self):
        logging.info("\n\nPinging Board Interfaces")

        logging.info("get_tile(): %s", self.board.get_tile("Category1", 1))
        logging.info("is_category_available(): %s", self.board.is_category_available("Category1", 1))
        logging.info("get_available_categories(): %s", self.board.get_available_categories(1))

    def __demo_wheel(self):
        logging.info("\n\nPinging Wheel Interfaces")

        logging.info("get_spint_result(): %s", self.wheel.get_spint_result())

    def __demo_user_interface(self):
        logging.info("\n\nPinging UI Interfaces")

    def __demo_executive_logic(self):
        logging.info("\n\nPinging Executive Logic Interfaces")

        logging.info("notifySpin(): %s", self.executive_logic.notifySpin())
        logging.info("getRound(): %s", self.executive_logic.getRound())
        logging.info("whoseTurn(): %s", self.executive_logic.whoseTurn())
        logging.info("selectRandOpponent(): %s", self.executive_logic.selectRandOpponent())


PORT = 5555
SRV_IP = 'localhost'
logging.basicConfig(level=logging.INFO)

game = InterfaceDemo(SRV_IP, PORT)
game.demo_all_interfaces()
