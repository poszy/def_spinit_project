 
from tkinter import *
from tkinter import ttk

import gui_template
import gui_spin
import gui_question

# Import Strings
from elements import s

class GUI:

    def __init__(self):
        self.strl = s.S()

        """
        CREATE ROOT FRAME
        """
        # Start Window Manager
        self.root = Tk()

        # Set default size of window
        self.root.geometry(self.strl.window_dimensions)
        self.root.title(self.strl.lobby_title_bar)
        self.s = ttk.Style()
        self.s.configure('new.TFrame', background='#7AC5CD')



        """
        CREATE TOP FRAME
        """
        self.frame_top=ttk.Frame(self.root, style='new.TFrame')
        #Every Frame should have these global labels
        self.lbl_round=ttk.Label(self.frame_top,text=self.strl.main_lbl_current_round, padding="10", width="20")
        self.lbl_round.pack(side=LEFT)

        self.lbl_score=ttk.Label(self.frame_top,text=self.strl.main_lbl_current_score, padding="10", width="20")
        self.lbl_score.pack(side=LEFT)

        self.lbl_turn=ttk.Label(self.frame_top,text=self.strl.main_lbl_current_turn, padding="10", width="20")
        self.lbl_turn.pack(side=LEFT)

        self.lbl_token=ttk.Label(self.frame_top,text=self.strl.main_lbl_current_tokens, padding="10", width="20")
        self.lbl_token.pack(side=LEFT)

        #Place the top frame
        self.frame_top.pack()

        self.style = ttk.Style()
        self.style.layout('TNotebook.Tab', []) # turn off tabs

        # Create Notebook in Root Frame
        # This will carkry our pagination
        self.note = ttk.Notebook(self.root)


        """
        CREATE SUB FRAMES
        """
        self.f1 = ttk.Frame(self.note)
        self.lbl_player_wait=ttk.Label(self.f1, text='This is the lobby. Please wait for turn!  ', padding="10", width="300").pack(side=TOP)

        # Add Frame to Notebook. This is the Lobby Frame
        self.note.add(self.f1)


        # Create Wheel Frame
        self.f2 = gui_spin.Spin(self.note)

        # Add Frame to Notebook
        self.note.add(self.f2)
        self.note.pack(expand=1, fill='both', padx=5, pady=5)


        # Create Question Frame
        self.f3 = gui_question.AQuestion(self.note)

        # Add Frame to Notebook
        self.note.add(self.f3)
        self.note.pack(expand=2, fill='both', padx=5, pady=5)

        # Wait for Client to send turn singal, for now it is initiated by button
        self.btn_play = ttk.Button(self.f1,text="Pass to Spin Fragment", command=self.load_spin_frame)
        self.btn_play.pack( side = BOTTOM, padx=50)


        self.btn_spin = ttk.Button(self.f2,text="Pass to question frame", command=self.load_question_frame)
        self.btn_spin.pack( side = BOTTOM, padx=50)

        """
        CREATE BOTTOM FRAME
        """
        self.frame_bottom=ttk.Frame(self.root, style='new.TFrame')

        #Every Frame should have these global labels
        self.lbl_info=ttk.Label(self.frame_bottom,text='Informational Pannel:  ', padding="10", width="20")
        self.lbl_info.pack()


        #Place the top frame
        self.frame_bottom.pack(side=BOTTOM)

        #self.root.after(3000, self.load_lobby_frame)
        self.root.mainloop()
        #self.root.after(3000, self.load_lobby_frame)

    # Helper function
    def load_lobby_frame(self):
        self.note.select(0)
    def load_spin_frame(self):
        self.note.select(1)
    def load_question_frame(self):
        self.note.select(2)

a = GUI()
