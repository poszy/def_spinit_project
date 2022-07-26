import logging


class Questions:

    # default constructor
    def __init__(self):
        self.politics = {
            1: {'question': 'politics question 1', 'answers': 'a, b, c, d', 'rAnswer': 'c', 'points': 100},
            2: {'question': 'politics question 2', 'answers': 'a, b, c, d', 'rAnswer': 'c', 'points': 200},
            3: {'question': 'politics question 3', 'answers': 'a, b, c, d', 'rAnswer': 'c', 'points': 400},
            4: {'question': 'politics question 4', 'answers': 'a, b, c, d', 'rAnswer': 'c', 'points': 800}, }
        self.politics_iterator = 1

        self.food = {
            1: {'question': 'food question 1', 'answers': 'a, b, c, d', 'rAnswer': 'c', 'points': 100},
            2: {'question': 'food question 2', 'answers': 'a, b, c, d', 'rAnswer': 'c', 'points': 200},
            3: {'question': 'food question 3', 'answers': 'a, b, c, d', 'rAnswer': 'c', 'points': 400},
            4: {'question': 'food question 4', 'answers': 'a, b, c, d', 'rAnswer': 'c', 'points': 800}, }
        self.food_iterator = 1
        self.no_category = "There are no more questions left in this category. Spin Again"

    def is_category_open(self, category):

        #print("QUESTIONS:(check_question) -- Checking Category: " + str(category))

        category_open = False
        if category == "politics":
            category_open = len(self.politics) > 0


        if category == "food":
            category_open = len(self.food) > 0

        #print(f"QUESTIONS:(check_question) -- Category: {category} is available: {category_open}")

        return category_open

    def get_open_categories(self, round):
        # TODO: incorporate the ROUND
        open_categories = []

        # for category_name, questions_dict in self.questions_dicts[round]:
        #     if len(questions_dict) > 0:  # category questions dict still has questions
        #         open_categories.append(category_name)
        open_categories = ["Politics", "Food"]
        return open_categories

    def get_tile(self, category, round):
        # TODO: implement code to work with round

        if category == "politics":
            #print("QUESTIONS:(get_tile) -- current iterator value " + str(self.politics_iterator))
            # Get Question that's next in line
            #print("QUESTIONS:(get_tile) -- got question ")
            question = self.politics[self.politics_iterator]

            #print("QUESTIONS:(get_tile) -- removed question from category ")
            # Delete the question from Dictionary
            del self.politics[self.politics_iterator]

            # Dictionary indexes do not update. so we have to track the indexes
            # With a global variable
            #print("QUESTIONS:(get_tile) -- incrementing iterator ")
            self.politics_iterator = self.politics_iterator + 1

            #print("QUESTIONS:(get_tile) -------------------------------------- ")
            return question

        if category == "food":
            #print("QUESTIONS:(get_tile) -- current iterator value " + str(self.food_iterator))
            # Get Question that's next in line
            #print("QUESTIONS:(get_tile) -- got question ")
            question = self.food[self.food_iterator]

            #print("QUESTIONS:(get_tile) -- removed question from category ")
            # Delete the question from Dictionary
            del self.food[self.food_iterator]

            # Dictionary indexes do not update. so we have to track the indexes
            # With a global variable
            #print("QUESTIONS:(get_tile) -- incrementing iterator ")
            self.food_iterator = self.food_iterator + 1

            #print("QUESTIONS:(get_tile) -------------------------------------- ")
            return question

# a = Questions()
# a.check_question("politics")
# a.get_tile("politics")
# a.get_tile("politics")
# a.get_tile("politics")
# a.get_tile("politics")
# a.get_tile("politics")

# a.get_tile("food")
