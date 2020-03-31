import tkinter as tk
from tkinter import ttk
from tkinter import E, W, X, BOTTOM, SUNKEN
from tkinter import filedialog

import pandas as pd
import os, threading
from datetime import datetime
import accounts

from utils.session import generate_session_id
from utils.gsheetApi import play_with_gsheet
from utils.checkValidation import check_validation
from utils.quitAction import quit_action
from utils.addWindows import add_manual, add_about
from utils.resourcePath import resource_path
from utils.scrapeAds import scrape_ads
from utils.scrapeGroups import scrape_groups

def chrome_path(): # Select chromedriver path
    global chromePath
    global statusBar
    statusBar['text'] = 'Browsing to chromedriver.exe'
    chromePath = filedialog.askopenfilename(initialdir='/', title='Select File', filetypes=(('Executables', '*.exe'), ('All files', '*.*')))
    statusBar['text'] = statusBarText

def get_old_users(statusBar):
    global oldUsersList
    statusBar['text'] = 'Getting old users...'
    dfOldUsers = play_with_gsheet(accounts.spreadsheetIdHubspot, 'Sheet1')
    oldUsersList['id'] = oldUsersList.id.astype(str)
    oldUsersList = dfOldUsers.id
    oldUsersList.to_csv('oldUsersList.csv', index=False)
    statusBarText = 'Old users updated.'

def start_get_old_users_thread():
    global oldUsersThread
    oldUsersThread = threading.Thread(target=get_old_users, args=(statusBar,), daemon=True, name='get_old_users_thread')
    oldUsersThread.start()

def start_scrape_ads_thread():
    global scrapeAdsThread
    scrapeAdsThread = threading.Thread(target=scrape_ads, args=(root, version, statusBar, chromePath, session_id, keywordsVar, blacklistKeywordsVar,
                                    emailVar, passVar, teleIdVar, oldUsersList,), daemon=True, name='scraping_ads_thread')
    scrapeAdsThread.start()

def start_scrape_groups_thread():
    global scrapeGroupsThread
    scrapeGroupsThread = threading.Thread(target=scrape_groups, args=(root, groupIdListVar, version, statusBar, chromePath, session_id, keywordsVar2,
                                        blacklistKeywordsVar2, emailVar2, passVar2, teleIdVar2, oldUsersList), daemon=True, name='scraping_groups_thread')
    scrapeGroupsThread.start()

def start_append_gsheet():
    df = pd.DataFrame({'session_id':session_id, 'version':version, 'action':'start_app', 'time':datetime.now(),
                    'email':[[emailDefault, emailDefault2]] if emailDefault != emailDefault2 else emailDefault,
                    'telegram_id':[[teleIdDefault, teleIdDefault2]] if teleIdDefault != teleIdDefault2 else teleIdDefault,
                    'keywords':'', 'blacklist_keywords':'', 'group_id': groupIdListDefault}, index=[0])
    appendThread = threading.Thread(target=play_with_gsheet, args=(accounts.spreadsheetIdData, 'Sheet1', df, 'append'), daemon=True)
    appendThread.start()

root = tk.Tk()
## Window/App Info
# root.geometry('600x400') # Default window size
root.resizable(0,0) # Lock window size
root.title("Homemade tool")

session_id = generate_session_id()
version = '0.2.0'
## End Window/App Info

# Load Old Users List
if os.path.exists('oldUsersList.csv'):
    oldUsersList = pd.read_csv('oldUsersList.csv', dtype={'id':str})
    oldUsersList = oldUsersList.id.tolist()
    statusBarText = 'Status Bar is cool'
else:
    statusBarText = 'Old users list not found'
    oldUsersList = []

# Load default accounts
if not os.path.exists('info.txt'):
    with open('info.txt', 'w', encoding='utf-8') as f:
        f.write('\n'*11)
    with open('info.txt', 'r', encoding='utf-8') as f:
        info = f.read()
        info = info.split('\n')
else:
    with open('info.txt', 'r', encoding='utf-8') as f:
        info = f.read()
        info = info.split('\n')

try:
    emailDefault = info[0].strip()
    passDefault = info[1].strip()
    teleIdDefault = info[2].strip()
    keywordsDefault = info[3].strip()
    blacklistKeywordsDefault = info[4].strip()
    chromePath = info[5].strip()
    emailDefault2 = info[6].strip()
    passDefault2 = info[7].strip()
    teleIdDefault2 = info[8].strip()
    keywordsDefault2 = info[9].strip()
    blacklistKeywordsDefault2 = info[10].strip()
    groupIdListDefault = info[11].strip()
except:
    emailDefault = ''
    passDefault = ''
    teleIdDefault = ''
    keywordsDefault = ''
    blacklistKeywordsDefault = ''
    chromePath = ''
    emailDefault2 = ''
    passDefault2 = ''
    teleIdDefault2 = ''
    keywordsDefault2 = ''
    blacklistKeywordsDefault2 = ''
    groupIdListDefault = ''

# Bunch of Variable Holders
emailVar = tk.StringVar(value=emailDefault)
passVar = tk.StringVar(value=passDefault)
teleIdVar = tk.StringVar(value=teleIdDefault)
rememberMeVar = tk.IntVar()
rememberMeVar.set(1)
keywordsVar = tk.StringVar(value=keywordsDefault)
blacklistKeywordsVar = tk.StringVar(value=blacklistKeywordsDefault)

emailVar2 = tk.StringVar(value=emailDefault2)
passVar2 = tk.StringVar(value=passDefault2)
teleIdVar2 = tk.StringVar(value=teleIdDefault2)
rememberMeVar2 = tk.IntVar()
rememberMeVar2.set(1)
keywordsVar2 = tk.StringVar(value=keywordsDefault2)
blacklistKeywordsVar2 = tk.StringVar(value=blacklistKeywordsDefault2)
groupIdListVar = tk.StringVar(value=groupIdListDefault)

## Menu Bar
menu = tk.Menu(root)

helpMenu = tk.Menu(menu, tearoff=0)
menu.add_cascade(label='Help', menu=helpMenu)
helpMenu.add_command(label='Manual', command=lambda: add_manual(root))
helpMenu.add_separator()
helpMenu.add_command(label='About', command=lambda: add_about(root))

root.config(menu=menu)
## End Menu Bar

#### Tab control
tab_control = ttk.Notebook(root)

tab1 = tk.Frame(tab_control)
tab2 = tk.Frame(tab_control)

tab_control.add(tab1, text='Ads Posts')
tab_control.add(tab2, text='Group Posts')

## Tab 1
## Top Frame
topFrame = tk.Frame(tab1, pady=10)

# Email Row
emailLabel = tk.Label(topFrame, text='Email')
emailLabel.grid(row=0, sticky=E)

emailEntry = tk.Entry(topFrame, textvariable=emailVar)
emailEntry.grid(row=0, column=1, ipadx=15, padx=5)

# Password Row
passLabel = tk.Label(topFrame, text='Password')
passLabel.grid(row=1, sticky=E)

passEntry = tk.Entry(topFrame, textvariable=passVar, show='*')
passEntry.grid(row=1, column=1, ipadx=15)

# Telegram ID Row
teleIdLabel = tk.Label(topFrame, text='Telegram User ID')
teleIdLabel.grid(row=2, sticky=E)

teleIdEntry = tk.Entry(topFrame, textvariable=teleIdVar)
teleIdEntry.grid(row=2, column=1, ipadx=15)

# Remember Me Checkbox
rememberMeCB = tk.Checkbutton(topFrame, text='Remember Me', variable=rememberMeVar)
rememberMeCB.grid(columnspan=2)

# Keywords Row
keywordsLabel = tk.Label(topFrame, text='Keywords')
keywordsLabel.grid(row=4, sticky=E)

keywordsEntry = tk.Entry(topFrame, textvariable=keywordsVar)
keywordsEntry.grid(row=4, column=1, ipadx=15)

# Blacklist Keywords Row
blacklistKeywordsLabel = tk.Label(topFrame, text='Blacklist Keywords')
blacklistKeywordsLabel.grid(row=5, sticky=E)

blacklistKeywordsEntry = tk.Entry(topFrame, textvariable=blacklistKeywordsVar)
blacklistKeywordsEntry.grid(row=5, column=1, ipadx=15)

topFrame.pack()
## End Top Frame

## Low Frame
lowFrame = tk.Frame(tab1)

# Browse Chrome Button
browseChromeBtn = ttk.Button(lowFrame, text='Browse Chromedriver', command=chrome_path)
browseChromeBtn.grid(row=1, column=0)

# Get Old Users
getOldUsersBtn = ttk.Button(lowFrame, text='Get Old Users', command=start_get_old_users_thread)
getOldUsersBtn.grid(row=1, column=1)

# Scraping Button
scrapingBtn = ttk.Button(lowFrame, text='Start Scraping', command=start_scrape_ads_thread)
scrapingBtn.grid(row=2, columnspan=2, ipadx=5, ipady=5)

lowFrame.pack()
## End Low Frame
## End tab 1

## Tab 2
## Top Frame
topFrame2 = tk.Frame(tab2, pady=5)

# Email Row
emailLabel2 = tk.Label(topFrame2, text='Email')
emailLabel2.grid(row=0, sticky=E)

emailEntry2 = tk.Entry(topFrame2, textvariable=emailVar2)
emailEntry2.grid(row=0, column=1, ipadx=15, padx=5)

# Password Row
passLabel2 = tk.Label(topFrame2, text='Password')
passLabel2.grid(row=1, sticky=E)

passEntry2 = tk.Entry(topFrame2, textvariable=passVar2, show='*')
passEntry2.grid(row=1, column=1, ipadx=15)

# Telegram ID Row
teleIdLabel2 = tk.Label(topFrame2, text='Telegram User ID')
teleIdLabel2.grid(row=2, sticky=E)

teleIdEntry2 = tk.Entry(topFrame2, textvariable=teleIdVar2)
teleIdEntry2.grid(row=2, column=1, ipadx=15)

# Remember Me Checkbox
rememberMeCB2 = tk.Checkbutton(topFrame2, text='Remember Me', variable=rememberMeVar2)
rememberMeCB2.grid(columnspan=2)

# Keywords Row
keywordsLabel2 = tk.Label(topFrame2, text='Keywords')
keywordsLabel2.grid(row=4, sticky=E)

keywordsEntry2 = tk.Entry(topFrame2, textvariable=keywordsVar2)
keywordsEntry2.grid(row=4, column=1, ipadx=15)

# Blacklist Keywords Row
blacklistKeywordsLabel2 = tk.Label(topFrame2, text='Blacklist Keywords')
blacklistKeywordsLabel2.grid(row=5, sticky=E)

blacklistKeywordsEntry2 = tk.Entry(topFrame2, textvariable=blacklistKeywordsVar2)
blacklistKeywordsEntry2.grid(row=5, column=1, ipadx=15)

# Group ID List
groupIdListLabel = tk.Label(topFrame2, text='Group IDs')
groupIdListLabel.grid(row=6, sticky=E)

groupIdListEntry = tk.Entry(topFrame2, textvariable=groupIdListVar)
groupIdListEntry.grid(row=6, column=1, ipadx=15)

topFrame2.pack()
## End Top Frame

## Low Frame
lowFrame2 = tk.Frame(tab2)

# Browse Chrome Button
browseChromeBtn = ttk.Button(lowFrame2, text='Browse Chromedriver', command=chrome_path)
browseChromeBtn.grid(row=1, column=0)

# Get Old Users
getOldUsersBtn = ttk.Button(lowFrame2, text='Get Old Users', command=start_get_old_users_thread)
getOldUsersBtn.grid(row=1, column=1)

# Scraping Button
scrapingBtn = ttk.Button(lowFrame2, text='Start Scraping', command=start_scrape_groups_thread)
scrapingBtn.grid(row=2, columnspan=2, ipadx=5, ipady=5)

lowFrame2.pack()
## End Low Frame
## End tab 2

tab_control.pack(expand=1, fill='both')
#### End tab control

## Status Bar
statusBar = tk.Label(root, text=statusBarText, bd=1, relief=SUNKEN, anchor=W)
statusBar.pack(side=BOTTOM, fill=X)
## End Status Bar

# Check valid & send info
check_validation(root, 'version', version=version)
start_append_gsheet()

root.mainloop()

varStringList = ['session_id', 'version', 'emailVar', 'emailVar2', 'emailDefault', 'emailDefault2', 'passVar', 'passVar2', 'passDefault', 'passDefault2',
     'teleIdVar', 'teleIdVar2', 'teleIdDefault', 'teleIdDefault2', 'rememberMeVar', 'rememberMeVar2', 'keywordsVar', 'keywordsVar2', 
     'keywordsDefault', 'keywordsDefault2', 'blacklistKeywordsVar', 'blacklistKeywordsVar2', 'blacklistKeywordsDefault', 'blacklistKeywordsDefault2',
     'chromePath', 'groupIdListVar', 'groupIdListDefault']
varList = [session_id, version, emailVar, emailVar2, emailDefault, emailDefault2, passVar, passVar2, passDefault, passDefault2,
    teleIdVar, teleIdVar2, teleIdDefault, teleIdDefault2, rememberMeVar, rememberMeVar2, keywordsVar, keywordsVar2,
    keywordsDefault, keywordsDefault2,blacklistKeywordsVar, blacklistKeywordsVar2, blacklistKeywordsDefault, blacklistKeywordsDefault2,
    chromePath, groupIdListVar, groupIdListDefault]

varForDict = zip(varStringList, varList)

dct = {}
for k, v in varForDict:
    dct.setdefault(k, '')
    dct[k] = v

quit_action(dct)