import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

import os, sys, threading
import pandas as pd
from datetime import datetime

import accounts
from utils import generate_session_id, play_with_gsheet, check_validation, merge_var
from cls import *

class HomemadeApplication(tk.Tk):
    if not os.path.exists('info.txt'):
        with open('info.txt', 'w', encoding='utf-8') as f:
            f.write('\n'*12)
        with open('info.txt', 'r', encoding='utf-8') as f:
            info = f.read()
            info = info.split('\n')
    else:
        with open('info.txt', 'r', encoding='utf-8') as f:
            info = f.read()
            info = info.split('\n')

    emailDefault = info[0].strip()
    passDefault = info[1].strip()
    teleIdDefault = info[2].strip()
    keywordsDefault = info[3].strip()
    blacklistKeywordsDefault = info[4].strip()
    chromePath = info[5].strip()
    userNameDefault = info[12].strip()
    emailDefault2 = info[6].strip()
    passDefault2 = info[7].strip()
    teleIdDefault2 = info[8].strip()
    keywordsDefault2 = info[9].strip()
    blacklistKeywordsDefault2 = info[10].strip()
    groupIdListDefault = info[11].strip()

    if os.path.exists('oldUsersList.csv'):
        oldUsersList = pd.read_csv('oldUsersList.csv', dtype={'id':str})
        oldUsersList = oldUsersList.id.tolist()
        statusBarText = 'Status Bar is cool'
    else:
        statusBarText = 'Old users list not found'
        oldUsersList = []

    version = '0.2.2'

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title("Homemade tool")
        self.resizable(0,0)
        check_validation('version', self.version)

        self.session_id = generate_session_id()

        self.userNameVar = tk.StringVar(value=self.userNameDefault)
        self.emailVar = tk.StringVar(value=self.emailDefault)
        self.passVar = tk.StringVar(value=self.passDefault)
        self.teleIdVar = tk.StringVar(value=self.teleIdDefault)
        self.rememberMeVar = tk.IntVar()
        self.rememberMeVar.set(1)
        self.keywordsVar = tk.StringVar(value=self.keywordsDefault)
        self.blacklistKeywordsVar = tk.StringVar(value=self.blacklistKeywordsDefault)

        self.emailVar2 = tk.StringVar(value=self.emailDefault2)
        self.passVar2 = tk.StringVar(value=self.passDefault2)
        self.teleIdVar2 = tk.StringVar(value=self.teleIdDefault2)
        self.rememberMeVar2 = tk.IntVar()
        self.rememberMeVar2.set(1)
        self.keywordsVar2 = tk.StringVar(value=self.keywordsDefault2)
        self.blacklistKeywordsVar2 = tk.StringVar(value=self.blacklistKeywordsDefault2)
        self.groupIdListVar = tk.StringVar(value=self.groupIdListDefault)

        self.start_append_gsheet()

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
        from tkinter import filedialog
        self.statusBar['text'] = 'Browsing to chromedriver.exe'
        self.chromePath = filedialog.askopenfilename(initialdir='/', title='Select File', filetypes=(('Executables', '*.exe'), ('All files', '*.*')))
        self.statusBar['text'] = self.statusBarText

    def start_get_old_users_thread(self):
        def get_old_users():
            self.statusBar['text'] = 'Getting old users...'
            dfOldUsers = play_with_gsheet(accounts.spreadsheetIdHubspot, 'Sheet1')
            dfOldUsers['id'] = dfOldUsers.id.astype(str)
            self.oldUsersList = dfOldUsers.id
            self.oldUsersList.to_csv('oldUsersList.csv', index=False)
            self.statusBarText = 'Old users updated.' 
            self.statusBar['text'] = self.statusBarText
        oldUsersThread = threading.Thread(target=get_old_users, daemon=True, name='get_old_users_thread')
        oldUsersThread.start()

    def start_append_gsheet(self):
        email = merge_var(self.emailDefault, self.emailDefault2)
        teleId = merge_var(self.teleIdDefault, self.teleIdDefault2)

        df = pd.DataFrame({'username':self.userNameDefault, 'session_id':self.session_id, 'version':self.version, 'action':'start_app', 'time':datetime.now(),
        'keywords':self.keywordsDefault, 'blacklist_keywords':self.blacklistKeywordsDefault, 'group_id':self.groupIdListDefault}, index=[0])
        appendThread = threading.Thread(target=play_with_gsheet, args=(accounts.spreadsheetIdData, 'Sheet1', df, 'append'), daemon=True)
        appendThread.start()

    def get_var(self):
        varStringList = ['userNameVar', 'session_id', 'version', 'emailVar', 'emailVar2', 'emailDefault', 'emailDefault2', 'passVar', 'passVar2', 'passDefault', 'passDefault2',
            'teleIdVar', 'teleIdVar2', 'teleIdDefault', 'teleIdDefault2', 'rememberMeVar', 'rememberMeVar2', 'keywordsVar', 'keywordsVar2', 
            'keywordsDefault', 'keywordsDefault2', 'blacklistKeywordsVar', 'blacklistKeywordsVar2', 'blacklistKeywordsDefault', 'blacklistKeywordsDefault2',
            'chromePath', 'groupIdListVar', 'groupIdListDefault']
        varList = [self.userNameVar, self.session_id, self.version, self.emailVar, self.emailVar2, self.emailDefault, self.emailDefault2, self.passVar, self.passVar2,
            self.passDefault, self.passDefault2, self.teleIdVar, self.teleIdVar2, self.teleIdDefault, self.teleIdDefault2, self.rememberMeVar, self.rememberMeVar2,
            self.keywordsVar, self.keywordsVar2, self.keywordsDefault, self.keywordsDefault2, self.blacklistKeywordsVar, self.blacklistKeywordsVar2,
            self.blacklistKeywordsDefault, self.blacklistKeywordsDefault2, self.chromePath, self.groupIdListVar, self.groupIdListDefault]

        varForDict = zip(varStringList, varList)

        dct = {}
        for k, v in varForDict:
            dct.setdefault(k, '')
            if k.find('Var') != -1:
                dct[k] = v.get()
            else:
                dct[k] = v

        return dct