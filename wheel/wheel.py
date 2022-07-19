 import random

class Wheel:

    def __init__(self):
        self.this = ""
        self.catagory_list = ["food","politics","history","math","sports"]


    def get_spin_result(self):
        """Gets the spin result.

            Args:
            None

            Returns:
            a string containing the catagory
         """

        #Poc logic. Generate random # 0-4
        rand = random.randint(0,4)

        # Access catagory_list with that number
        spin_result = self.catagory_list[rand]

        return spin_result

    def update_catagories(self, catagory_list):
        """Updates the catagories

            Args:
            category: A list of strings containing categories from the board.

            Returns: an updated verion of self.catagory_list
         """

        # Grab the origonal catagory_list from obj creation
        # and modify the catagories that are passed in from this function
        # Dummy Logic
        self.catagory = self.catagory_list - catagory_list


        return self.catagory_list
