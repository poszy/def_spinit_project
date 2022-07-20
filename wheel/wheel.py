import random


class Wheel:

    def __init__(self):
        self.this = ""
        self.category_list = ["food", "politics", "history", "math", "sports"]

    def get_spin_result(self):
        """Gets the spin result.

            Args:
            None

            Returns:
            a string containing the category
         """

        # Poc logic. Generate random # 0-4
        rand = random.randint(0, 4)

        # Access category_list with that number
        spin_result = self.category_list[rand]

        return spin_result

    def update_categories(self, category_list):
        """Updates the categories

            Args:
            category: A list of strings containing categories from the board.

            Returns: an updated version of self.category_list
         """

        # Grab the original category_list from obj creation
        # and modify the categories that are passed in from this function
        # Dummy Logic
        self.category_list = category_list

        return self.category_list
