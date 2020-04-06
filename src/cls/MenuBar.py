import tkinter as tk
from utils.texts import *
from tkinter import messagebox
from cls.ExtractDataWindow import ExtractDataWindow

class MenuBar(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        menu = tk.Menu()

        helpMenu = tk.Menu(menu, tearoff=0)
        extractMenu = tk.Menu(menu, tearoff=0)

        menu.add_cascade(label='File', menu=extractMenu)
        menu.add_cascade(label='Help', menu=helpMenu)

        helpMenu.add_command(label='Manual', command=self.add_manual)
        helpMenu.add_separator()
        helpMenu.add_command(label='About', command=self.add_about)

        extractMenu.add_command(label='Extract data', command=self.addExtractDataWindow)

        self.parent.config(menu=menu)

    def add_manual(self):
        try:
            if self.manualWindow.state() == 'normal':
                self.manualWindow.focus()
        except:
            self.manualWindow = tk.Toplevel(self.parent)
            self.manualWindow.title('Manual')
            manualFrame = tk.Frame(self.manualWindow)
            manualTxt = tk.Text(manualFrame, wrap='word', padx=20, pady=5, spacing1=8, bd=3, bg='#ededed', relief='flat')
            manualTxt.insert('insert', manualText)
            manualTxt.configure(state='disabled', font=("Rouge", 10))
            manualTxt.pack(fill='both', expand=True)
            manualFrame.pack(fill='both', expand=True)

    def add_about(self):
        messagebox.showinfo(title='About', message=aboutText)

    def addExtractDataWindow(self):
        try:
            if self.w.state() == 'normal':
                self.w.focus()
        except:
            self.w = tk.Toplevel(self.parent)
            self.w.title('Extract Data')
            self.w.resizable(0,0)
            windows = ExtractDataWindow(self.w, self.parent)