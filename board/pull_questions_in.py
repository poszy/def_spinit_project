import csv
from collections import defaultdict
import random

# pulled questions from JArchive: https://github.com/whymarrh/jeopardy-parser
# now, pull questions from CSV
QUESTIONS_FILE = 'JArchive-questions.csv'
NUM_WRONG_ANS = 2

def read_questions(filename):
    ans_choices_by_category = defaultdict(set)
    dict_from_csv = defaultdict(list)
    with open(filename, mode='r') as csv_file:

        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                cols = ", ".join(row)
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            # category, round, value, clue, answer
            # print(f'\t{row["category"]}: {row["clue"]} correct answer is {row["answer"]}.')
            else:
                dict_from_csv[row["category"]].append(row)
                ans_choices_by_category[row["category"]].add(row["answer"])


            line_count += 1
        print(f'Processed {line_count} lines.')
        # print(ans_choices_by_category)

        for category, questions in dict_from_csv.items():
            for questionIDX in range(len(questions)):
                question = questions[questionIDX]
                print("here")
                myCategory = question["category"]
                possibleAnswers = ans_choices_by_category[myCategory]
                # pick 2 possible answers that are
                possibleAnswers.remove(question["answer"])
                print(question["answer"], possibleAnswers)

                wrongAnsList = random.sample(possibleAnswers, NUM_WRONG_ANS)

                ansOptions = wrongAnsList + [question["answer"]]
                print(ansOptions)

                # shuffle the indices of the answers
                index_shuf = list(range(len(ansOptions)))
                random.shuffle(index_shuf)
                shuffled_ans = []
                for i in index_shuf:
                    shuffled_ans.append(ansOptions[i])
                # keep index of actual answer
                actual_answer_index = index_shuf[-1]

                dict_from_csv[category][questionIDX]["ans_idx"] = actual_answer_index
                dict_from_csv[category][questionIDX]["answerChoices"] = ansOptions

        for category, questions in dict_from_csv.items():
            for row in range(len(questions)):
                print(f'\t{row["category"]}: {row["clue"]}, answer choices: {row["answerChoices"]}')
                print(f'correct is{row["answerChoices"][row["ans_idx"]]}')

        # print(csv_reader)
    return csv_reader

read_questions(QUESTIONS_FILE)