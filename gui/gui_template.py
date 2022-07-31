from tkinter import *
from tkinter import ttk
from elements import s

# Build Objects from our string class
# and Tkinter
class Template(ttk.Frame):

    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        self.l1=ttk.Label(self,text='Template Frame:  ', padding="10", width="20")
        self.l1.pack(side=LEFT)





