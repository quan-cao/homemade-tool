import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog

import os, sys, threading, pickle
import pandas as pd
from datetime import datetime

import accounts
from utils import generate_session_id, play_with_gsheet, check_validation
from cls import *

class HomemadeApplication(tk.Tk):

    columns = ['email', 'password', 'teleId', 'keywords', 'blacklistKeywords', 'userName', 'chromePath',
                    'email2', 'password2', 'teleId2', 'keywords2', 'blacklistKeywords2', 'groupId']
    version = '0.2.3'

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        try:
            with open('info', 'rb') as f:
                default = pickle.load(f)
                self.default = default.iloc[0]
        except:
            self.default = pd.DataFrame([(','*12).split(',')], columns=self.columns).iloc[0]

        if os.path.exists('oldUsersList.csv'):
            oldUsersList = pd.read_csv('oldUsersList.csv', dtype={'id':str})
            self.oldUsersList = oldUsersList.id.tolist()
            self.statusBarText = 'Status Bar is cool'
        else:
            self.statusBarText = 'Old users list not found'
            self.oldUsersList = []

        self.title("Homemade tool")
        self.resizable(0,0)
        check_validation('version', self.version)

        self.session_id = generate_session_id()

        self.userNameVar = tk.StringVar(value=self.default.userName)
        self.emailVar = tk.StringVar(value=self.default.email)
        self.passVar = tk.StringVar(value=self.default.password)
        self.teleIdVar = tk.StringVar(value=self.default.teleId)
        self.rememberMeVar = tk.IntVar()
        self.rememberMeVar.set(1)
        self.keywordsVar = tk.StringVar(value=self.default.keywords)
        self.blacklistKeywordsVar = tk.StringVar(value=self.default.blacklistKeywords)

        self.emailVar2 = tk.StringVar(value=self.default.email2)
        self.passVar2 = tk.StringVar(value=self.default.password2)
        self.teleIdVar2 = tk.StringVar(value=self.default.teleId2)
        self.rememberMeVar2 = tk.IntVar()
        self.rememberMeVar2.set(1)
        self.keywordsVar2 = tk.StringVar(value=self.default.keywords2)
        self.blacklistKeywordsVar2 = tk.StringVar(value=self.default.blacklistKeywords2)
        self.groupIdListVar = tk.StringVar(value=self.default.groupId)

        self.chromePath = self.default.chromePath

        menu = MenuBar(self)
        tab_control = ttk.Notebook(self)
        AdsPostsTab = AdsPostsWindow(tab_control, self)
        GroupPostsTab = GroupPostsWindow(tab_control, self)
        tab_control.add(AdsPostsTab, text='Ads Posts')
        tab_control.add(GroupPostsTab, text='Group Posts')
        tab_control.pack(expand=1, fill='both')

        self.statusBar = tk.Label(self, text=self.statusBarText, bd=1, relief='sunken', anchor='w')
        self.statusBar.pack(side='bottom', fill='x')


    def chrome_path(self):
        self.statusBar['text'] = 'Browsing to chromedriver.exe'
        self.chromePath = filedialog.askopenfilename(initialdir='/', title='Select File', filetypes=(('Executables', '*.exe'), ('All files', '*.*')))
        self.statusBar['text'] = self.statusBarText


    def start_get_old_users_thread(self):
        def get_old_users():
            self.statusBar['text'] = 'Getting old users...'
            dfOldUsers = play_with_gsheet(accounts.spreadsheetIdHubspot, 'Sheet1')
            dfOldUsers['id'] = dfOldUsers.id.astype(str)
            dfOldUsers.to_csv('oldUsersList.csv', index=False)
            self.oldUsersList = dfOldUsers.id.tolist()
            self.statusBar['text'] = 'Old users updated.'

        oldUsersThread = threading.Thread(target=get_old_users, daemon=True, name='get_old_users_thread')
        oldUsersThread.start()


    def quit(self):
        info1 = [self.emailVar.get(), self.passVar.get(), self.teleIdVar.get(), self.keywordsVar.get(), self.blacklistKeywordsVar.get(), self.userNameVar.get(), self.chromePath] \
            if self.rememberMeVar.get() == 1 \
            else [self.default.email, self.default.password, self.default.teleId, self.default.keywords, self.default.blacklistKeywords, self.default.userName, self.chromePath]

        info2 = [self.emailVar2.get(), self.passVar2.get(), self.teleIdVar2.get(), self.keywordsVar2.get(), self.blacklistKeywordsVar2.get(), self.groupIdListVar.get()] \
            if self.rememberMeVar2.get() == 1 \
            else [self.default.userName2, self.default.email2, self.default.teleId2, self.default.password2, self.default.keywords2, self.default.blacklistKeywords2, self.default.groupId]

        saveInfo = pd.DataFrame([info1 + info2], columns=self.columns)

        with open('info', 'wb') as f:
            pickle.dump(saveInfo, f)

        df = pd.DataFrame({'username':self.userNameVar.get(), 'session_id':self.session_id, 'version':self.version, 'action':'close_app', 'time':datetime.now(),
        'keywords':'', 'blacklist_keywords':'', 'group_id':''}, index=[0])
        play_with_gsheet(accounts.spreadsheetIdData, 'Sheet1', df, 'append')