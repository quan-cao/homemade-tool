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
import time
import requests
from datetime import datetime

def log_in_facebook(driver, email, password):
    driver.get('https://www.facebook.com')
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.NAME, 'email'))).send_keys(email)
    time.sleep(2)
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.NAME, 'pass'))).send_keys(password)
    time.sleep(1)
    driver.switch_to.active_element.send_keys(Keys.RETURN)

def get_fb_posts(driver, groupId, kwRegex, blacklistKwRegex):
    dataframe = pd.DataFrame(columns=['telegram_id', 'phone', 'time', 'content', 'post', 'profile'])

    driver.get(f'https://facebook.com/groups/{groupId}?sorting_setting=CHRONOLOGICAL')
    posts = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'userContentWrapper')))
    for p in posts:
        if p.text.find('Vừa xong') != -1 or p.text.find('1 phút') != -1:
            try:
                p.find_element_by_class_name('see_more_link_inner').click()
            except: pass

            content = p.find_element_by_class_name('userContent').text

            if len(re.findall(kwRegex, content, re.IGNORECASE)) != 0 and not re.findall(blacklistKwRegex, content, re.IGNORECASE):
                try:
                    profile = p.find_element_by_class_name('profileLink').get_attribute('href')
                except:
                    profile = p.find_element_by_link_text(p.find_element_by_class_name('_7tae').text).get_attribute('href')
                if profile.find('profile.php') == -1:
                    profile = profile.split('?')[0]
                else:
                    profile = profile.split('&')[0]

                try:
                    phone = re.search(r'([^0-9]+(0|84|\+84)[-.\s]?\d{1,3}[-.\s]?\d{2,4}[-.\s]?\d{2,4}[-.\s]?\d{2,4})', content).group()
                    phone = re.sub(r'\D+', '', phone)
                    phone = re.sub(r'^0', '84', phone)
                except:
                    phone = None
            
                try:
                    post = p.find_element_by_class_name('_5pcq').get_attribute('href')
                except:
                    break

                post_time = pd.to_datetime(p.find_element_by_class_name('_5ptz').get_attribute('data-utime'), unit='s') + pd.DateOffset(hour=16)

                dataframe = dataframe.append({'phone':phone, 'time':post_time, 'content':content,
                                              'post':post, 'profile':profile}, ignore_index=True)
            else: continue
    dataframe = dataframe.drop_duplicates(subset='post')
    return dataframe

def scrape_ads(master, groupIdList, version, statusBar, chromePath, session_id, keywordsVar, blacklistKeywordsVar, emailVar, passVar, teleIdVar, oldUsersList):

    if (not emailVar.get()) or (not passVar.get()):
        statusBar['text'] = 'Please fill Facebook account'
    else:
        check_validation(master, 'user', version=version, email=emailVar.get(), teleId=teleIdVar.get())

        statusBar['text'] = 'Scraping in Groups...'

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
            play_with_gsheet(accounts.spreadsheetIdGroupPosts, method='new_sheet', sheetName=email, numRow=1, numCol=5)
            df = pd.DataFrame(columns=['telegram_id', 'phone', 'time', 'content', 'post', 'profile'])
            play_with_gsheet(accounts.spreadsheetIdGroupPosts, _range=email, dataframe=df, method='write')
        except: # Existed sheet
            pass

        while True:
            for groupId in groupIdList:
                try:
                    oldPostsDf = play_with_gsheet(spreadsheetIdGroupPosts, 'Sheet1')
                    newPosts = get_fb_posts(driver, groupId, kwRegex, blacklistKwRegex)
                    newPosts = newPosts[(~newPosts.post.isin(oldPostsDf.post)) & (~newPosts.content.isin(oldPostsDf.content))]
                    if len(newPosts) > 0:
                        play_with_gsheet(accounts.spreadsheetIdGroupPosts, _range=email, dataframe=newPosts, method='append')
                        push_tele(teleId, 'groups', df=newPosts)
                except Exception as err:
                    if type(err).__name__ in ['WebDriverException', 'NoSuchWindowException', 'ProtocolError']:
                        statusBar['text'] = 'Scrape Ended'
                        endCrawlDf = pd.DataFrame({'session_id':session_id, 'version':version, 'action':'end_crawl_groups', 'time':datetime.now(), 'email':email,
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