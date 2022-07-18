
from questions import Questions

import logging
logging.basicConfig(level=logging.INFO)

class Board:

    # default constructor
    def __init__(self):
        self.questions = Questions()

    def get_question(self, catagory):
        """Gets the next question in point value from the board.

            Args:
            category: A string containing a category from the board.

            Returns:
            a key-value pair containing a question from the board.
         """

        print("BOARD:(get_question) -- Checking isAvailable()")
        isAvailable = self.is_catagory_available(catagory)
        print("BOARD:(get_question) -- Got " + str(isAvailable) + " from isAvailable()")

        if isAvailable == True:
            print("BOARD:(get_question) -- Returning Question from Questions")


            return self.questions.get_question(catagory)
        else:
            logging.info("BOARD:(get_question) -- Catagory is not avialable")
            print("BOARD:(get_question) -- Please Spin again")



    def is_catagory_available(category):
        """
        Checks to see if there are any available questions in a category.

        Args:
        category: A string containing a category from the board.

        Returns:
        a boolean.
        """

        print("BOARD:(is_catagory_available) -- Setting boolean ")
        print("BOARD:(is_catagory_available) -- self.question.check_questions(catagory) ")
        boolean = self.questions.check_question(catagory)


        return boolean

