import logging
from board.pull_questions_in import TileLoader

NUM_ROUNDS = 2


class Questions:

    # default constructor
    def __init__(self, filename):
        questions_in = TileLoader(filename)
        self.rounds = questions_in.rounds
        self.no_category = "There are no more questions left in this category. Spin Again"

    def is_category_open(self, category, round):
        """
        Checks to see if there are any available questions in a category.

        Args:
        category: A string containing a category from the board.


        Returns:
        a boolean.
        """
        print("QUESTIONS:(check_question) -- Checking Category: " + str(category))
        category_open = False
        if round in self.rounds and self.rounds[round]:  # 2 rounds max
            this_round_board = self.rounds[round]
            if category in this_round_board:  # make sure category is in this round
                this_categories_tiles = this_round_board[category]
                category_open = len(this_categories_tiles) > 0  # at least one point value tile remaining in category
        return category_open

    def get_open_categories(self, round):
        """
        Returns a list of available categories
        Args:
        round: an int representing the current round

        Returns:
        a boolean.
        """
        open_categories = []
        if round in range(1, NUM_ROUNDS + 1):  # 2 rounds max
            for category_name, questions_dict in self.rounds[round].items():
                if len(questions_dict) > 0:  # category questions dict still has questions
                    open_categories.append(category_name)
        return open_categories

    def get_tile(self, category, round):
        """Gets the next question in point value from the board.

            Args:
            category: A string containing a category from the board.

            Returns:
            a key-value pair containing a question from the board.
         """

        if round in range(1, NUM_ROUNDS + 1):  # 2 rounds max
            if category in self.rounds[round].keys():  # category exists
                questions_dict = self.rounds[round][category]
                if len(questions_dict) > 0:  # category questions dict still has questions
                    lowest_point_value = min(questions_dict.keys())
                    next_tile = questions_dict[lowest_point_value]

                    # Delete the question from Dictionary

                    del self.rounds[round][category][lowest_point_value]
                    logging.info(f"deleted {lowest_point_value}, remain dict is: {self.rounds[round][category]}")

                    return next_tile
                else:
                    raise Exception(f"get_tile tried to poll a category (%s) that was out of tiles!", category)
            else:
                raise Exception(f"Category %s does not exist on this game board!", category)
        else:
            raise Exception(f"Round number %s is not a valid round in questions.py!", str(round))


# a = Questions()
# a.is_category_open("politics", 1)
# rnd1_cats = a.get_open_categories(1)
# rnd2_cats = a.get_open_categories(2)
# cat1 = rnd1_cats[0]
# cat2 = rnd2_cats[-1]
# a.is_category_open(rnd1_cats, 1)
#
# print(rnd1_cats, cat1)
# print(rnd2_cats, cat2)
#
# for i in range(0, len(a.rounds[1][cat1].items()) + 1):
#     tile = a.get_tile(cat1, 1)
#     print(tile)
