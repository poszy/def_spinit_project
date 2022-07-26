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
        politics_tiles = {100: Tile('politics question 1', ['a', 'b', 'c'], 2, 100),
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

        #print("QUESTIONS:(check_question) -- Checking Category: " + str(category))
        category_open = False
        if round in range(1, NUM_ROUNDS + 1):  # 2 rounds max
            this_round_board = self.rounds[round]
            category_open = len(this_round_board) > 0  # at least one point value tile remaining in category
        return category_open

    def get_open_categories(self, round):
        open_categories = []
        if round in range(1, NUM_ROUNDS + 1):  # 2 rounds max
            for category_name, questions_dict in self.rounds[round].items():
                if len(questions_dict) > 0:  # category questions dict still has questions
                    open_categories.append(category_name)
        return open_categories

    def get_tile(self, category, round):
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
            return False

# a = Questions()
# a.check_question("politics")
# a.get_tile("politics")
# a.get_tile("politics")
# a.get_tile("politics")
# a.get_tile("politics")
# a.get_tile("politics")

# a.get_tile("food")
