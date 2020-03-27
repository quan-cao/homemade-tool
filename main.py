import tkinter as tk
from tkinter import ttk
from tkinter import E, W, X, BOTTOM, SUNKEN
from tkinter import filedialog

import pandas as pd
import os, sys, re, threading, requests, time
from os import path
from datetime import datetime
import accounts

from utils.session import generate_session_id
from utils.gsheetApi import play_with_gsheet
from utils.checkValidation import check_validation
from utils.getRegex import get_regex
from utils.quitAction import quit_action
from utils.addWindows import add_manual, add_about
from utils.pushTele import push_tele
from utils.resourcePath import resource_path

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

root = tk.Tk()

def chrome_path(): # Select chromedriver path
    global chromePath
    global statusBar
    statusBar['text'] = 'Browsing to chromedriver.exe'
    chromePath = filedialog.askopenfilename(initialdir='/', title='Select File', filetypes=(('Executables', '*.exe'), ('All files', '*.*')))
    statusBar['text'] = statusBarText

def log_in_facebook(driver, email, password):
    driver.get('https://www.facebook.com')
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.NAME, 'email'))).send_keys(email)
    time.sleep(2)
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.NAME, 'pass'))).send_keys(password)
    time.sleep(1)
    driver.switch_to.active_element.send_keys(Keys.RETURN)

def scraping(): # Web Scraping
    global driver
    global kwRegex, blacklistKwRegex
    global teleId, name, page, facebook, phones
    global oldUsersList

    if (not emailVar.get()) or (not passVar.get()):
        statusBar['text'] = 'Please fill Facebook account'
    else:
        check_validation(root, 'user', version=version, email=emailVar.get(), teleId=teleIdVar.get())

        statusBar['text'] = 'Scraping...'

        options = webdriver.ChromeOptions()
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-infobars")
        options.add_argument("--mute-audio")
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--silent')
        options.add_argument('--log-level=OFF')
        # options.add_argument('--headless')
        try:
            driver = webdriver.Chrome(executable_path=resource_path(chromePath), options=options)
        except Exception:
            statusBar['text'] = 'Chromedriver not found'
        
        # Get keywords
        kwRegex = get_regex(keywordsVar.get())
        blacklistKwRegex = get_regex(blacklistKeywordsVar.get(), blacklist=True)

        email = emailVar.get()
        password = passVar.get()
        teleId = teleIdVar.get()
        keywords = keywordsVar.get()
        blacklistKeywords = blacklistKeywordsVar.get()

        log_in_facebook(driver, email, password)

        beginCrawlDf = pd.DataFrame({'session_id':session_id, 'version':version, 'action':'begin_crawl', 'time':datetime.now(), 'email':email,
            'telegram_id':teleId, 'keywords':keywords, 'blacklist_keywords':blacklistKeywords}, index=[0])
        play_with_gsheet(accounts.spreadsheetIdData, 'Sheet1', beginCrawlDf, 'append')

        try:
            play_with_gsheet(accounts.spreadsheetIdPosts, method='new_sheet', sheetName=email, numRow=1, numCol=5)
            df = pd.DataFrame(columns=['telegram_id', 'name', 'page', 'facebook', 'phone', 'imported_time'])
            play_with_gsheet(accounts.spreadsheetIdPosts, _range=email, dataframe=df, method='write')
            pageSet = set([])
        except: # Existed sheet
            oldPostsDf = play_with_gsheet(accounts.spreadsheetIdPosts, _range=email)
            oldPage = oldPostsDf.page.tolist()
            pageSet = set(oldPage)
        # Scrape
        while True:
            try:
                while len(driver.window_handles) > 1:
                    driver.switch_to.window(driver.window_handles[-1])
                    driver.close()
                driver.get('https://www.facebook.com')
                for _ in range(30):
                    # Scroll down to bottom
                    elems = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, '_4-u2')))
                    driver.switch_to.active_element.send_keys(Keys.PAGE_DOWN)
                    for e in elems[7:]:
                        if e.text != '':
                            if (e.text.find('Sponsored') != -1 or e.text.find('Được tài trợ') != -1):
                                if not re.findall(blacklistKwRegex, e.text, re.IGNORECASE) and re.findall(kwRegex, e.text, re.IGNORECASE):
                                    try:
                                        page = WebDriverWait(e, 20).until(EC.presence_of_element_located((By.CLASS_NAME, '_5pb8'))).get_attribute('href').split('/')[3]
                                    except:
                                        try:
                                            page = e.find_element_by_link_text(e.find_element_by_class_name('_7tae').text).get_attribute('href').split('/')[3]
                                        except:
                                            if e.find_element_by_class_name('_7tae').text.find('like') != -1:
                                                page = e.find_element_by_link_text(re.sub('\.$', '', e.find_element_by_class_name('_7tae').text.split(' like ')[1])).get_attribute('href').split('/')[3]
                                            elif e.find_element_by_class_name('_7tae').text.find('thích') != -1:
                                                page = e.find_element_by_link_text(re.sub('\.$', '', e.find_element_by_class_name('_7tae').text.split(' thích ')[1])).get_attribute('href').split('/')[3]
                                    if page not in pageSet:
                                        # Get page info
                                        driver.execute_script(f"window.open('{'https://www.facebook.com/' + page + '/about?ref=page_internal'}');")
                                        driver.switch_to.window(driver.window_handles[-1])
                                        name = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, '_64-f'))).text
                                        facebook = 'https://www.facebook.com/' + page
                                        try:
                                            pageInfo = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, 'content')))
                                            phoneList = re.findall(r'\b(((0|84|\+84)[-.\s]?\d{1,3}[-.\s]?\d{2,4}[-.\s]?\d{2,4}[-.\s]?\d{2,4})|((1800|1900)[-.\s]\d+[-.\s]\d+))\b', pageInfo.text)
                                        except:
                                            phoneList = []
                                        if phoneList != []:
                                            phones = []
                                            for i in range(0, len(phoneList)):
                                                phone = phoneList[i][0]
                                                phone = re.sub(r'\D+', '', phone)
                                                phone = re.sub(r'^0', '84', phone)
                                                if phone not in phones:
                                                    phones.append(phone)
                                            for p in phones:
                                                if p not in oldUsersList:
                                                    push_tele(teleId, name, facebook, phones)
                                        else:
                                            phones = ''
                                            push_tele(teleId, name, facebook, phones)
                                        pageSet.add(page)
                                        postDf = pd.DataFrame({'telegram_id':teleId, 'name':name, 'page':page, 'facebook':facebook, 'phone':str(phones), 'imported_time':datetime.now()}, index=[0])
                                        play_with_gsheet(accounts.spreadsheetIdPosts, _range=email, dataframe=postDf, method='append')
                                        driver.close()
                                        driver.switch_to.window(driver.window_handles[0])
            except Exception as err:
                if type(err).__name__ in ['WebDriverException', 'NoSuchWindowException', 'ProtocolError']:
                    statusBar['text'] = 'Scrape Ended'
                    endCrawlDf = pd.DataFrame({'session_id':session_id, 'version':version, 'action':'end_crawl', 'time':datetime.now(), 'email':email,
                                'telegram_id':teleId, 'keywords':keywords, 'blacklist_keywords':blacklistKeywords}, index=[0])
                    play_with_gsheet(accounts.spreadsheetIdData, 'Sheet1', endCrawlDf, 'append')
                    break
                elif type(err).__name__ == 'MaxRetryError':
                    try:
                        driver.quit()
                    except:
                        driver = webdriver.Chrome(executable_path=chromePath, options=options)
                        log_in_facebook(driver, email, password)
                        continue
                else:
                    err_text = f"Error: {type(err).__name__}.\n{str(err)}\nFrom {email} at session <b>{session_id}</b>"
                    data = {
                        'chat_id': '807358017',
                        'text': err_text,
                        'parse_mode': 'HTML'
                    }
                    requests.post("https://api.telegram.org/bot{token}/sendMessage".format(token=accounts.botToken), data=data)
                    continue

def get_old_users(statusBar):
    global oldUsersList
    statusBar['text'] = 'Getting old users...'
    dfOldUsers = play_with_gsheet(accounts.spreadsheetIdHubspot, 'Sheet1')
    oldUsersList = dfOldUsers.id
    oldUsersList.to_csv('oldUsersList.csv', index=False)
    statusBar['text'] = 'Old users updated.'

def start_scraping_thread():
    global scrapingThread
    scrapingThread = threading.Thread(target=scraping, daemon=True, name='scraping_thread')
    scrapingThread.start()

def start_get_old_users_thread():
    global oldUsersThread
    oldUsersThread = threading.Thread(target=get_old_users, args=(statusBar,), daemon=True, name='get_old_users_thread')
    oldUsersThread.start()

def start_append_gsheet():
    df = pd.DataFrame({'session_id':session_id, 'version':version, 'action':'start_app', 'time':datetime.now(), 'email':emailDefault,
                'telegram_id':teleIdDefault, 'keywords':keywordsDefault, 'blacklist_keywords':blacklistKeywordsDefault}, index=[0])
    appendThread = threading.Thread(target=play_with_gsheet, args=(accounts.spreadsheetIdData, 'Sheet1', df, 'append'), daemon=True)
    appendThread.start()

## Window Info
# root.geometry('600x400') # Default window size
root.resizable(0,0) # Lock window size
root.title("Homemade tool")

## App Info
session_id = generate_session_id()
version = '0.1.3'

## End App Info

# Load Old Users List
if path.exists('oldUsersList.csv'):
    oldUsersList = pd.read_csv('oldUsersList.csv')
    oldUsersList = oldUsersList.id
    statusBarText = 'Status Bar is cool'
else:
    statusBarText = 'Old users list not found'
    oldUsersList = []

## Menu Bar
menu = tk.Menu(root)

helpMenu = tk.Menu(menu, tearoff=0)
menu.add_cascade(label='Help', menu=helpMenu)
helpMenu.add_command(label='Manual', command=lambda: add_manual(root))
helpMenu.add_separator()
helpMenu.add_command(label='About', command=lambda: add_about(root))

root.config(menu=menu)
## End Menu Bar

## Status Bar
statusBar = tk.Label(root, text=statusBarText, bd=1, relief=SUNKEN, anchor=W)
statusBar.pack(side=BOTTOM, fill=X)
## End Status Bar

# Load default accounts
try:
    with open('info.txt', 'r', encoding='utf-8') as f:
        info = f.read()
        info = info.split('\n')
        emailDefault = info[0].strip()
        passDefault = info[1].strip()
        teleIdDefault = info[2].strip()
        keywordsDefault = info[3].strip()
        blacklistKeywordsDefault = info[4].strip()
        chromePath = info[5].strip()
except:
    emailDefault = ''
    passDefault = ''
    teleIdDefault = ''
    keywordsDefault = ''
    blacklistKeywordsDefault = ''
    chromePath = ''

# Bunch of Variable Holders
emailVar = tk.StringVar(value=emailDefault)
passVar = tk.StringVar(value=passDefault)
teleIdVar = tk.StringVar(value=teleIdDefault)
rememberMeVar = tk.IntVar()
rememberMeVar.set(1)
keywordsVar = tk.StringVar(value=keywordsDefault)
blacklistKeywordsVar = tk.StringVar(value=blacklistKeywordsDefault)

## Top Frame
topFrame = tk.Frame(root)

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
lowFrame = tk.Frame(root)

# Browse Chrome Button
browseChromeBtn = ttk.Button(lowFrame, text='Browse Chromedriver', command=chrome_path)
browseChromeBtn.grid(row=1, column=0)

# Get Old Users
getOldUsersBtn = ttk.Button(lowFrame, text='Get Old Users', command=start_get_old_users_thread)
getOldUsersBtn.grid(row=1, column=1)

# Scraping Button
scrapingBtn = ttk.Button(lowFrame, text='Start Scraping', command=start_scraping_thread)
scrapingBtn.grid(row=2, columnspan=2, ipadx=5, ipady=5)

lowFrame.pack()
## End Low Frame

# Check valid & send info
check_validation(root, 'version', version=version)
start_append_gsheet()

root.mainloop()

dct = {'session_id':session_id, 'version':version, 'emailVar':emailVar.get(), 'emailDefault':emailDefault, 'passVar':passVar.get(),
    'passDefault':passDefault, 'teleIdVar':teleIdVar.get(), 'teleIdDefault':teleIdDefault, 'rememberMeVar':rememberMeVar.get(),
    'keywordsVar':keywordsVar.get(), 'blacklistKeywordsVar':blacklistKeywordsVar.get(), 'chromePath':chromePath}

try:
    quit_action(dct, driver)
except:
    quit_action(dct)
