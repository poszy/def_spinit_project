
class Board:

    # default constructor
    def __init__(self):
        self.var = "self"

    def get_question(category):
        """Gets the next question in point value from the board.

            Args:
            category: A string containing a category from the board.

            Returns:
            a key-value pair containing a question from the board.
         """

        question = random(category)

        return question


    def is_catagory_available(category):
        """
        Checks to see if there are any available questions in a category.

        Args:
        category: A string containing a category from the board.

        Returns:
        a boolean.
        """

        return False

