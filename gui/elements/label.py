from tkinter import *
from tkinter import ttk

class Label:

    def __init(self):
        self.frame = ""
        self.text = ""


    def create_label(self, frame, text):
        self.frame=ttk.Label(self.frame,text=self.text, padding="10", width="20")
        self.frame.pack(side=LEFT)
