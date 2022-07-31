# create frame style
from tkinter import ttk
s = ttk.Style()
s.configure('new.TFrame', background='#7AC5CD')

#create tabs within the frame
tab1 = ttk.Frame(mainframe, style='new.TFrame')
mainframe.add(tab1, text="Tab1")


tab2 = ttk.Frame(mainframe, style='new.TFrame')
mainframe.add(tab2, text="Tab2")


tab3 = ttk.Frame(mainframe, style='new.TFrame')
mainframe.add(tab3, text="Tab3")

tab4 = ttk.Frame(mainframe, style='new.TFrame')
mainframe.add(tab4, text="Tab4")

tab5 = ttk.Frame(mainframe, style='new.TFrame')
mainframe.add(tab5, text="Tab4")
