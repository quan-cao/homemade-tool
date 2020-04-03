import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
import threading

class ExtractDataWindow(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        topFrame = ttk.Frame(self.parent)

        userNameFrame = tk.Frame(topFrame, pady=3)
        userNameLbl = ttk.Label(userNameFrame, text='Username')
        userNameLbl.grid(row=0, sticky='E')
        userNameEntry = ttk.Entry(userNameFrame)
        userNameEntry.grid(row=0, column=1, ipadx=15, padx=5)
        userNameFrame.pack()

        fromTimeFrame = tk.Frame(topFrame, pady=3)
        fromTimeLbl = ttk.Label(fromTimeFrame, text='From time')
        fromTimeLbl.grid(sticky='E')
        fromTimeEntry = DateEntry(fromTimeFrame)
        fromTimeEntry.grid(row=0, column=1)
        toTimeLbl = ttk.Label(fromTimeFrame, text='To time')
        toTimeLbl.grid(sticky='E', row=0, column=2)
        toTimeEntry = DateEntry(fromTimeFrame)
        toTimeEntry.grid(row=0, column=3)
        fromTimeFrame.pack()

        btn = ttk.Button(topFrame, text='Try this', command=lambda: self.test_func(fromTimeEntry.get_date(), toTimeEntry.get_date()))
        btn.pack()

        topFrame.pack()
    def test_func(_, fromTime, toTime):
        print(fromTime, '\n', toTime)