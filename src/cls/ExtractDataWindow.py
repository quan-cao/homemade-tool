import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
from tkinter import filedialog, messagebox
from utils import play_with_gsheet
import accounts
import threading, os
import pandas as pd

class ExtractDataWindow(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.controller = controller

        self.dirToSave = os.getcwd()

        mainFrame = ttk.Frame(self.parent)

        userNameFrame = tk.Frame(mainFrame, pady=3)
        userNameLbl = ttk.Label(userNameFrame, text='Username')
        userNameLbl.grid(row=0, sticky='E', padx=2)
        self.userNameEntry = ttk.Entry(userNameFrame, textvariable=self.controller.userNameVar)
        self.userNameEntry.grid(row=0, column=1, ipadx=60, padx=5)
        userNameFrame.pack()

        timeFrame = tk.Frame(mainFrame, pady=3)
        fromTimeLbl = ttk.Label(timeFrame, text='From time')
        fromTimeLbl.grid(sticky='E', padx=2)
        self.fromTimeEntry = DateEntry(timeFrame)
        self.fromTimeEntry.grid(row=0, column=1, padx=2)
        toTimeLbl = ttk.Label(timeFrame, text='To time')
        toTimeLbl.grid(sticky='E', row=0, column=2, padx=2)
        self.toTimeEntry = DateEntry(timeFrame)
        self.toTimeEntry.grid(row=0, column=3, padx=2)
        timeFrame.pack()

        fileFrame = tk.Frame(mainFrame, pady=3)
        fileNameLbl = ttk.Label(fileFrame, text='File name')
        fileNameLbl.grid(row=0, column=0, padx=2)
        fileNameEntry = ttk.Entry(fileFrame)
        fileNameEntry.grid(row=0, column=1, padx=2, ipadx=60, sticky='ew')
        fileFrame.pack()

        buttonFrame = tk.Frame(mainFrame, pady=3)
        dirBtn = ttk.Button(buttonFrame, text='Choose where to save files', command=self.chooseDir)
        dirBtn.grid(row=0, columnspan=2, pady=5)
        getAdsPostBtn = ttk.Button(buttonFrame, text='Get Ads Posts', command=lambda: self.extract_ads_posts(fileNameEntry.get()))
        getAdsPostBtn.grid(row=1, column=0, padx=4)
        GetGroupPostsBtnbtn = ttk.Button(buttonFrame, text='Get Group Posts', command=lambda: self.extract_groups_posts(fileNameEntry.get()))
        GetGroupPostsBtnbtn.grid(row=1, column=1, padx=4)
        buttonFrame.pack()

        mainFrame.pack(fill='x')

    def extract_ads_posts(self, fileName):
        if not fileName:
            messagebox.showinfo(title='Missing Information', message='Please fill file name.')
        else:
            self.controller.statusBar['text'] = 'Extracting Ads Data...'
            extractDf = play_with_gsheet(accounts.spreadsheetIdAdsPosts, self.userNameEntry.get())
            extractDf['imported_time'] = pd.to_datetime(extractDf['imported_time'])
            extractDf = extractDf[(extractDf.imported_time >= pd.to_datetime(self.fromTimeEntry.get())) & (extractDf.imported_time <= pd.to_datetime(self.toTimeEntry.get()))].iloc[:, :-1]
            extractDf.to_excel(self.dirToSave + '\\' + fileName + '.xlsx', index=False)
            self.controller.statusBar['text'] = 'Ads data saved'

    def extract_groups_posts(self, fileName):
        if not fileName:
            messagebox.showinfo(title='Missing Information', message='Please fill file name.')
        else:
            self.controller.statusBar['text'] = 'Extracting Groups data...'
            extractDf = play_with_gsheet(accounts.spreadsheetIdGroupPosts, self.userNameEntry.get())
            extractDf['time'] = pd.to_datetime(extractDf['time'])
            extractDf = extractDf[(extractDf.time >= pd.to_datetime(self.fromTimeEntry.get())) & (extractDf.time <= pd.to_datetime(self.toTimeEntry.get()))]
            extractDf.to_excel(self.dirToSave + '\\' + fileName + '.xlsx', index=False)
            self.controller.statusBar['text'] = 'Groups data saved'

    def chooseDir(self):
        self.dirToSave = filedialog.askdirectory()