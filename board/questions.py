import logging

NUM_ROUNDS = 2


class Tile:
    def __init__(self, question, answers, r_answer, points):
        self.question = question  # String
        self.answers = answers  # list of answers
        self.r_answer = r_answer  # index of answer in the list of answers
        self.points = points  # int

    # interface
    def check_answer(self, player_ans):
        """
            Checks player's answer against the actual answer

            Args:
            playerAns: index of the player's answer in the list of answers

            Returns:
            user_correct: a boolean representing whether or not the user's selection was correct
            points: int, number of points the question is worth
        """
        user_correct = (player_ans == self.r_answer)

        return user_correct, self.points


class Questions:

    # default constructor
    def __init__(self):
        politics_tiles = {100: Tile('What are two rights of everyone living in the United States?', ['A. Freedom to petition the government and freedom to disobey traffic laws', 'B. Freedom of worship and freedom to make treaties with other countries', 'c. Freedom of speech and freedom to run for president'], 2, 100),
                          200: Tile('politics question 3', ['a', 'b', 'c'], 2, 200),
                          400: Tile('politics question 3', ['a', 'b', 'c'], 2, 400),
                          800: Tile('politics question 4', ['a', 'b', 'c'], 2, 800)
                          }

        food_tiles = {100: Tile('food question 1', ['a', 'b', 'c'], 2, 100),
                      200: Tile('food question 3', ['a', 'b', 'c'], 2, 200),
                      400: Tile('food question 3', ['a', 'b', 'c'], 2, 400),
                      800: Tile('food question 4', ['a', 'b', 'c'], 2, 800)
                      }

        self.rounds = {1: {"politics": politics_tiles, "food": food_tiles},
                       2: {"politics2": politics_tiles, "food2": food_tiles}}
        self.politics_iterator = 1

        self.food_iterator = 1
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

#a = Questions()
#a.check_question("politics")
#a.get_tile("politics", 1)
# a.get_tile("politics")
# a.get_tile("politics")
# a.get_tile("politics")
# a.get_tile("politics")

# a.get_tile("food")
