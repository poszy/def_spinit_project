import csv
from collections import defaultdict
import random
import locale
locale.setlocale( locale.LC_ALL, 'en_US.UTF-8' )
import logging

# pulled questions from JArchive: https://github.com/whymarrh/jeopardy-parser
# now, pull questions from CSV
NUM_WRONG_ANS = 2
NUM_QUESTIONS_PER_CATEGORY = 5
NUM_ROUNDS = 2
NUM_CATEGORIES_PER_ROUND = 6
ROUND_1_POINTS = [200, 400, 600, 800, 1000]

class Tile:
    def __init__(self, question, answers, r_answer, points):
        self.question = question  # String
        self.answers = answers  # list of answers
        self.r_answer = r_answer  # the correct answer to the question
        self.points = points  # int

    # interface
    def check_answer(self, player_ans):
        """
            Checks player's answer against the actual answer

            Args:
            playerAns: string. The player's answer from the list of answers

            Returns:
            user_correct: a boolean representing whether or not the user's selection was correct
            points: int, number of points the question is worth
        """
        # logging.info(f"Checking answer player's {player_ans}, right answer: {self.r_answer}")
        user_correct = (player_ans == self.r_answer)

        return user_correct, self.points


class TileLoader:

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
        """
        Read questions from JArchive file
        :param filename: string. relative path from main.py to the JArchive file
        :return:
        dict_from_csv: dictionary. mapping of categories to list of questions in that category
        ans_choices_by_category: dictionary. mapping of category names to a list of possible multiple choice answers
        """
        ans_choices_by_category = defaultdict(set)
        dict_from_csv = defaultdict(list)
        with open(filename, mode='r', encoding = "ISO-8859-1") as csv_file:
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
        """
        Some categories from JArchive don't have enough questions in them. Remove those categories so they cannot be
        selected
        :param dict_from_csv: dictionary. mapping of categories to list of questions in that category
        :param ans_choices_by_category: dictionary. mapping of category names to a list of possible multiple choice
        answers
        :return:
        dict_from_csv: dictionary. mapping of categories to list of questions in that category. All remaining categories
        must have correct number of questions
        """
        # remove categories with too few answers
        for category, ansChoices in ans_choices_by_category.items():
            if len(ansChoices) != NUM_QUESTIONS_PER_CATEGORY:  # category doesn't have enough questions, or has too many
                # remove from the list!
                if category in dict_from_csv:  # hasn't already been deleted
                    del dict_from_csv[category]
        return dict_from_csv

    def __make_question_multiple_choice(self, possibleAnswers, rightAnswer):
        """
        Make a multiple choice question based on a list of possible answers drawn from answers to the other questions in
        the category.
        :param possibleAnswers: list of possible answers
        :param rightAnswer: string. the actual answer to the question
        :return:
        shuffled_ans: list. a list of answer choices. The correct answer is randomly placed in the shuffled_ans list
        """
        # pick 2 possible answers that are incorrect
        possibleAnswers.remove(rightAnswer)
        wrongAnsList = random.sample(possibleAnswers, NUM_WRONG_ANS)  # these are incorrect choices

        ansOptions = wrongAnsList + [rightAnswer]

        # shuffle the indices of the answers
        index_shuf = list(range(len(ansOptions)))
        random.shuffle(index_shuf)
        shuffled_ans = []  # holds all the possible answers shuffled randomly
        for i in index_shuf:
            shuffled_ans.append(ansOptions[i])

        return shuffled_ans

    def __questions_to_tiles(self, dict_from_csv, ans_choices_by_category):
        """
        Take a dictionary of questions and answers and convert them to tiles
        :param dict_from_csv: dictionary of question -> answer pairs
        :param ans_choices_by_category
        :return:
        category_tiles: dictionary. mapping category name to mapping of point value to tile
        """
        category_tiles = {}
        for category, questions in dict_from_csv.items():
            category_tiles[category] = {}
            for questionIDX in range(len(questions)):
                question = questions[questionIDX]
                myCategory = question["category"]
                possibleAnswers = set(ans_choices_by_category[myCategory])
                rightAnswer = question["answer"]

                shuffled_ans = self.__make_question_multiple_choice(possibleAnswers, rightAnswer)

                clue = question["clue"]
                # point_str = question["value"]  # use point values fom the CSV
                # point_str = locale.atoi(point_str)  # OK with commas for thousands place
                # points = int(point_str)

                # set point values as though this was round 1.
                points = ROUND_1_POINTS[questionIDX]
                new_tile = Tile(clue, shuffled_ans, rightAnswer, points)
                category_tiles[category][points] = new_tile
        return category_tiles

    def __make_rounds(self, tiles_by_category):
        """
        Randomly select categories and the corresponding tiles to form rounds
        :param tiles_by_category: dictionary. mapping category name to mapping of point value to tile
        :return: rounds: dictionary. mapping round number to categories of tiles
        """
        round_one = ["A IS FOR AUTUMN","UU COMPLETE ME", '1 WORD, 2 MEANINGS', "1970s TV", "3 Ns", "4-LETTER WORDS", "4-SYLLABLE WORDS", '"ISM"s', "3 VOWELS IN A ROW"]

        round_two = ["A SHRUBBERY!", "ALL THINGS BELGIAN", "BODIES OF WATER", "AFTER MATH", "ALL MY TROUBLES","ALTRUISTIC ATHLETES",'A BOROUGH BURIAL', 'ACM Awards', "AMERICAN HISTORY"]

        rounds = {}
        for round_num in range(1, NUM_ROUNDS + 1):
            rounds[round_num] = {}
            # TODO: for the demo, select specific categories as round 1 and round 2, or do it in order of CSV appearance
            # categories_in_round = random.sample(tiles_by_category.keys(), NUM_CATEGORIES_PER_ROUND)
            if round_num == 1:
                categories_in_round = round_one
                # print(f"chose categories {categories_in_round}")
            elif round_num == 2:
                categories_in_round = round_two
            logging.info(f"Chosen Round {round_num} categories: {categories_in_round}")
            for cat_name in categories_in_round:
                if round_num == 2:  # 2nd round, point values doubled
                    tiles_in_cat = tiles_by_category[cat_name]
                    # print(f"ROUND: {round_num}, {tiles_in_cat}")
                    doubled_points_cat = {}
                    for points, tile in tiles_in_cat.items():
                        # print(f"tile: {tile}")
                        # print(f"old tile points: {tile.points}")
                        tile.points = tile.points * 2
                        # print(f"new tile points: {tile.points}")
                        doubled_points_cat[points*2] = tile
                    rounds[round_num][cat_name] = doubled_points_cat
                elif round_num == 1:
                    rounds[round_num][cat_name] = tiles_by_category[cat_name]
                else:
                    # some other round ...?
                    pass

            print(f"Round {round_num} point values: {rounds[round_num].items()}")
        self.rounds = rounds
