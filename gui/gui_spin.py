
from tkinter import *
from tkinter import ttk
# Import Strings
from elements import s

# Append parent directory to import path
import sys,os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from wheel import wheel

class Spin(ttk.Frame):

    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        super().__init__()
        self.strl = s.S()
        self.spin_logic=wheel.Wheel()
        self.lbl_wheel_frame=ttk.Label(self, text=self.strl.wheel_frame, padding="10", width="20")
        self.lbl_wheel_frame.pack(side=LEFT)

        self.btn_spin = ttk.Button(self,text=self.strl.wheel_btn_spin, command= self.spin_logic.get_spin_result)

        self.btn_spin.pack( side = BOTTOM, padx=50)




