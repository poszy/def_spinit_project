from board.questions import Questions

import logging

logging.basicConfig(level=logging.INFO)
QUESTIONS_FILE = 'board/JArchive-questions.csv'  # need to use relative path from current working directory of main.py!


class Board:

    # default constructor
    def __init__(self):
        self.questions = Questions(QUESTIONS_FILE)

    def get_tile(self, category, round_num):
        """Gets the next question in point value from the board.

            Args:
            category: A string containing a category from the board.

            Returns:
            a key-value pair containing a question from the board.
         """

        # logging.info(f"BOARD:(get_question) -- Checking is_available({category})")
        is_available = self.is_category_available(category, round_num)

        if is_available:
            # logging.info("BOARD:(get_question) -- Returning Question from Questions")
            return self.questions.get_tile(category, round_num)
        else:
            # logging.info("BOARD:(get_question) -- Category is not available")
            # logging.info("BOARD:(get_question) -- Please Spin again")
            pass

    def is_category_available(self, category, round_num):
        """
        Checks to see if there are any available questions in a category.

        Args:
        category: A string containing a category from the board.

        Returns:
        a boolean.
        """
        # print(f"BOARD:(is_category_available) -- checking if category {category} is available ")
        available = self.questions.is_category_open(category, round_num)

        return available

    def get_available_categories(self, round_num):
        """
        Returns a list of available categories
        Args:
        round: an int representing the current round

        Returns:
        a boolean.
        """
        # print(f"BOARD:(is_category_available) -- returning available categories for round {round} ")
        available = self.questions.get_open_categories(round_num)

        return available

    def reset_board(self, new_round_num):
        """
        Called at the start of a new round. Changes Jeopardy game board to a new set of questions and answers, with new point totals.
        May throw an error if no new board is available?

        :param new_round_num: The number of the new round (1 or 2). Used to calculate how many points each question is worth.
        :return: void
        """
        pass
