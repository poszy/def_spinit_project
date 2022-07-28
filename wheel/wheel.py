import random
from enum import Enum


class Sector(Enum):
    LOSE_TURN = "Lose Turn"
    FREE_TURN = "Free Turn"
    BANKRUPT = "Bankrupt"
    PLAYERS_CHOICE = "Player's Choice"
    OPPONENTS_CHOICE = "Opponent's Choice"
    SPIN_AGAIN = "Spin Again"


class Wheel:

    def __init__(self, jeopardy_categories):
        self.jeopardy_categories = jeopardy_categories
        self.other_sectors = [Sector.LOSE_TURN, Sector.FREE_TURN, Sector.BANKRUPT, Sector.PLAYERS_CHOICE,
                              Sector.OPPONENTS_CHOICE, Sector.SPIN_AGAIN]
        self.__update_sector_list()

    def get_spin_result(self):
        """Gets the spin result.

            Args:
            None

            Returns:
            a string containing the category
         """

        # Poc logic. Generate random number to get sector.
        rand = random.randint(0, len(self.sector_list))

        # Access category_list with that number
        spin_result = self.sector_list[rand]

        return spin_result

    def update_categories(self, jeopardy_categories):
        """Updates the categories

            Args:
            jeopardy_categories: A list of strings containing jeopardy categories from the board.

            Returns: an updated version of self.jeopardy_categories
         """

        # Grab the original jeopardy_categories from obj creation
        # and modify the categories that are passed in from this function
        self.jeopardy_categories = jeopardy_categories
        self.__update_sector_list()

        return self.jeopardy_categories

    def __update_sector_list(self):
        self.sector_list = self.jeopardy_categories + self.jeopardy_categories + self.other_sectors

    def is_jeopardy_category(self, sector_result):
        if sector_result in self.jeopardy_categories:
            return True
        elif sector_result in self.other_sectors:
            return False
        else:
            raise Exception("String '" + sector_result + "' is not a sector on the Wheel.")
