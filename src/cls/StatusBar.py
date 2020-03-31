import tkinter as tk

class StatusBar:
    def __init__(self, master):
        self.master = master
        self.statusBar = tk.Label(self.master, text=self.master.statusBarText, bd=1, relief='sunken', anchor='w')
        self.statusBar.pack(side='bottom', fill='x')