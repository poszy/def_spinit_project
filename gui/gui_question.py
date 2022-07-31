from tkinter import *
from tkinter import ttk
from elements import s
from elements import label

import os
import sys
# Append parent directory to import path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from board import questions
from tkinter.messagebox import showinfo

class AQuestion(ttk.Frame):

    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)

        self.strl = s.S()
        self.s = ttk.Style()
        self.s.configure('new.TFrame', background='#7AC5CD')
        self.questions = questions.Questions()

        question_obj = self.questions.get_tile("politics", 1)
        aQuestion = question_obj['question']
        aAnswers  = question_obj['answers']
        self.rAnswer   = question_obj['rAnswer']
        self.points  = question_obj['points']

        lbl_question = ttk.Label(self, text =aQuestion, font=("Helvetica", 20),padding=10).pack(side=TOP)


        #Split the answers by , delimiter
        aAnswers_split = aAnswers.split(',')

        choice = ((aAnswers_split[0], 'Answer a'),
         (aAnswers_split[1], 'Answer b'),
         (aAnswers_split[2], 'Answer c'),
         (aAnswers_split[3], 'Answer D'))

        self.gAnswers = StringVar()
        ## radio buttons
        for c in choice:
            i = 0
            r = ttk.Radiobutton(
                self,
                text=c[i],
                value=c,
                variable=self.gAnswers,

            )
            i = i + i

            r.pack(side = TOP)
        ## Submit button
        btn_submit = ttk.Button(
            self,
            text=self.strl.question_btn_submit,
            command = self.show_selected_size
            )

        btn_submit.pack( side = BOTTOM, )


        #lbl_answers  = ttk.Label(self, text =aAnswers, font=("Helvetica", 12),padding=10).pack(side = LEFT)


    def show_selected_size(self):
            #print(self.gAnswers.get())
            #print(type(self.gAnswers.get()))
            if self.gAnswers.get() == self.rAnswer:
                showinfo(title=self.strl.question_show_info_correct_answer, message=self.gAnswers.get())
            else:
                showinfo(title=self.strl.question_show_info_wrong_answer, message=self.gAnswers.get())




#a = AQuestion()
