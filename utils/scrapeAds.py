from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

from utils.pushTele import push_tele
from utils.getRegex import get_regex
from utils.gsheetApi import play_with_gsheet
from utils.checkValidation import check_validation
from utils.resourcePath import resource_path
from utils.messages import *

import pandas as pd
import accounts
import time, requests, re
from datetime import datetime

def log_in_facebook(driver, email, password):
    driver.get('https://www.facebook.com')
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.NAME, 'email'))).send_keys(email)
    time.sleep(2)
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.NAME, 'pass'))).send_keys(password)
    time.sleep(1)
    driver.switch_to.active_element.send_keys(Keys.RETURN)

def scrape_ads(master, version, statusBar, chromePath, session_id, keywordsVar, blacklistKeywordsVar, emailVar, passVar, teleIdVar, oldUsersList):

    if (not emailVar.get()) or (not passVar.get()):
        statusBar['text'] = 'Please fill Facebook account'
    else:
        check_validation(master, 'user', version=version, email=emailVar.get(), teleId=teleIdVar.get())

        statusBar['text'] = 'Scraping for Ads...'

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

        beginCrawlDf = pd.DataFrame({'session_id':session_id, 'version':version, 'action':'begin_crawl_ads', 'time':datetime.now(), 'email':email,
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
                                            checkPhone = 0
                                            for p in phones:
                                                if p in oldUsersList:
                                                    checkPhone += 1
                                            if checkPhone == 0:
                                                push_tele(teleId, 'ads', name, facebook, phones)
                                            else:
                                                pageSet.add(page)
                                                break
                                        else:
                                            phones = ''
                                            push_tele(teleId, 'ads', name, facebook, phones)
                                        pageSet.add(page)
                                        postDf = pd.DataFrame({'telegram_id':teleId, 'name':name, 'page':page, 'facebook':facebook, 'phone':str(phones), 'imported_time':datetime.now()}, index=[0])
                                        play_with_gsheet(accounts.spreadsheetIdPosts, _range=email, dataframe=postDf, method='append')
                                        driver.close()
                                        driver.switch_to.window(driver.window_handles[0])
            except Exception as err:
                if type(err).__name__ in ['WebDriverException', 'NoSuchWindowException', 'ProtocolError']:
                    statusBar['text'] = 'Scrape Ended'
                    endCrawlDf = pd.DataFrame({'session_id':session_id, 'version':version, 'action':'end_crawl_ads', 'time':datetime.now(), 'email':email,
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