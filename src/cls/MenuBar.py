import tkinter as tk
from utils import messages
from tkinter import messagebox

class MenuBar(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        menu = tk.Menu()

        helpMenu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label='Help', menu=helpMenu)
        helpMenu.add_command(label='Manual', command=self.add_manual)
        helpMenu.add_separator()
        helpMenu.add_command(label='About', command=self.add_about)

        parent.config(menu=menu)

    def add_manual(self):
        try:
            if self.manualWindow.state() == 'normal':
                self.manualWindow.focus()
        except:
            self.manualWindow = tk.Toplevel(self.parent)
            self.manualWindow.title('Manual')
            manualFrame = tk.Frame(self.manualWindow)
            manualTxt = tk.Text(manualFrame, wrap='word', padx=20, pady=5, spacing1=8, bd=3, bg='#ededed', relief='flat')
            manualTxt.insert('insert', messages.manualText)
            manualTxt.configure(state='disabled', font=("Rouge", 10))
            manualTxt.pack(fill='both', expand=True)
            manualFrame.pack(fill='both', expand=True)

    def add_about(self):
        messagebox.showinfo(title='About', message=messages.aboutText)