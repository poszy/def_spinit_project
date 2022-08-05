import csv
from collections import defaultdict
import random
from questions import Tile

# pulled questions from JArchive: https://github.com/whymarrh/jeopardy-parser
# now, pull questions from CSV
QUESTIONS_FILE = 'JArchive-questions.csv'
NUM_WRONG_ANS = 2
NUM_QUESTIONS_PER_CATEGORY = 5
NUM_ROUNDS = 2
NUM_CATEGORIES_PER_ROUND = 6


class TileLoader():

    # default constructor
    def __init__(self, filename):
        self.filename = filename
        self.ans_choices_by_category = set([])

        dict_from_csv, ans_choices_by_category = self.__read_questions_in(self.filename)
        dict_from_csv = self.__remove_small_categories(dict_from_csv, ans_choices_by_category)
        tiles_by_category = self.__questions_to_tiles(dict_from_csv, ans_choices_by_category)
        del ans_choices_by_category, dict_from_csv
        self.__make_rounds(tiles_by_category)

    def __read_questions_in(self, filename):
        ans_choices_by_category = defaultdict(set)
        dict_from_csv = defaultdict(list)
        with open(filename, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    cols = ", ".join(row)
                    print(f'Column names are {cols}')  # category, round, value, clue, answer
                    line_count += 1
                else:
                    dict_from_csv[row["category"]].append(row)
                    ans_choices_by_category[row["category"]].add(row["answer"])
                line_count += 1
        return dict_from_csv, ans_choices_by_category

    def __remove_small_categories(self, dict_from_csv, ans_choices_by_category):
        # remove categories with too few answers
        for category, ansChoices in ans_choices_by_category.items():
            if len(ansChoices) < NUM_QUESTIONS_PER_CATEGORY:  # category doesn't have enough questions
                # remove from the list!
                if category in dict_from_csv:  # hasn't already been deleted
                    del dict_from_csv[category]
        return dict_from_csv

    def __get_ans_options(self, possibleAnswers, rightAnswer):
        # pick 2 possible answers that are
        possibleAnswers.remove(rightAnswer)
        wrongAnsList = random.sample(possibleAnswers, NUM_WRONG_ANS)

        ansOptions = wrongAnsList + [rightAnswer]

        # shuffle the indices of the answers
        index_shuf = list(range(len(ansOptions)))
        random.shuffle(index_shuf)
        shuffled_ans = []
        for i in index_shuf:
            shuffled_ans.append(ansOptions[i])
        # keep index of actual answer
        actual_answer_index = index_shuf[-1]

        return shuffled_ans, actual_answer_index

    def __questions_to_tiles(self, dict_from_csv, ans_choices_by_category):
        """
        Take a dictionary of questions and answers and convert them to tiles
        :param dict_from_csv: dictionary of question -> answer pairs
        :param ans_choices_by_category
        """
        category_tiles = {}
        for category, questions in dict_from_csv.items():
            category_tiles[category] = {}
            for questionIDX in range(len(questions)):
                question = questions[questionIDX]
                myCategory = question["category"]
                possibleAnswers = set(ans_choices_by_category[myCategory])
                rightAnswer = question["answer"]

                shuffled_ans, actual_answer_index = self.__get_ans_options(possibleAnswers, rightAnswer)

                clue = question["clue"]
                points = question["value"]
                new_tile = Tile(clue, shuffled_ans, actual_answer_index, points)
                category_tiles[category][points] = new_tile
        return category_tiles

    def __make_rounds(self, tiles_by_category):
        rounds = {}
        for round_num in range(1, NUM_ROUNDS + 1):
            rounds[round_num] = {}
            categories_in_round = random.sample(tiles_by_category.keys(), NUM_CATEGORIES_PER_ROUND)
            # print(f"chose categories {categories_in_round}")
            for cat in categories_in_round:
                rounds[round_num][cat] = tiles_by_category[cat]
        self.rounds = rounds


questions_in = TileLoader(QUESTIONS_FILE)
for round, cat in questions_in.rounds.items():
    print(cat)
