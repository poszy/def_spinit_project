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

    def check_question(self, category):

        print("QUESTIONS:(check_question) -- Checking Category: " + str(category))

        if category == "politics":

            if len(self.politics) == 0:
                print("QUESTIONS:(check_question) -- Category has no more questions available. Returning False")
                return False
            else:
                print("QUESTIONS:(check_question) -- Category: " + str(category) + " has questions. Returning True")
                return True

        if category == "food":

            if len(self.food) == 0:
                print("QUESTIONS:(check_question) -- Category has no more questions available. Returning False")
                return False
            else:
                print("QUESTIONS:(check_question) -- Category: " + str(category) + " has questions. Returning True")
                return True

    def get_question(self, category):

        if category == "politics":
            print("QUESTIONS:(get_question) -- current iterator value " + str(self.politics_iterator))
            # Get Question that's next in line
            print("QUESTIONS:(get_question) -- got question ")
            question = self.politics[self.politics_iterator]["question"]

            print("QUESTIONS:(get_question) -- removed question from category ")
            # Delete the question from Dictionary
            del self.politics[self.politics_iterator]

            # Dictionary indexes do not update. so we have to track the indexes
            # With a global variable
            print("QUESTIONS:(get_question) -- incrementing iterator ")
            self.politics_iterator = self.politics_iterator + 1

            print("QUESTIONS:(get_question) -------------------------------------- ")
            return question

        if category == "food":
            print("QUESTIONS:(get_question) -- current iterator value " + str(self.food_iterator))
            # Get Question that's next in line
            print("QUESTIONS:(get_question) -- got question ")
            question = self.food[self.food_iterator]["question"]

            print("QUESTIONS:(get_question) -- removed question from category ")
            # Delete the question from Dictionary
            del self.food[self.food_iterator]

            # Dictionary indexes do not update. so we have to track the indexes
            # With a global variable
            print("QUESTIONS:(get_question) -- incrementing iterator ")
            self.food_iterator = self.food_iterator + 1

            print("QUESTIONS:(get_question) -------------------------------------- ")
            return question

# a = Questions()
# a.check_question("politics")
# a.get_question("politics")
# a.get_question("politics")
# a.get_question("politics")
# a.get_question("politics")
# a.get_question("politics")

# a.get_question("food")
