from tkinter import Toplevel, Frame, Text, messagebox, WORD, INSERT, BOTH, FLAT
from utils import messages

def add_manual(master):
    global manualWindow
    try:
        if manualWindow.state() == 'normal':
            manualWindow.focus()
    except:
        manualWindow = Toplevel(master)
        manualWindow.title('Manual')
        manualFrame = Frame(manualWindow)
        manualTxt = Text(manualFrame, wrap=WORD, padx=20, pady=5, spacing1=8, bd=3, bg='#ededed', relief=FLAT)
        manualTxt.insert(INSERT, messages.manualText)
        manualTxt.configure(state='disabled', font=("Rouge", 10))
        manualTxt.pack(fill=BOTH, expand=True)
        manualFrame.pack(fill=BOTH, expand=True)

def add_about(master):
    messagebox.showinfo(title='About', message=messages.aboutText)