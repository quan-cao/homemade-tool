from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

from utils import push_tele, get_regex, play_with_gsheet, check_validation, resource_path

import pandas as pd
import accounts
import time, requests, re
from datetime import datetime, timedelta

def log_in_facebook(driver, email, password):
    driver.get('https://www.facebook.com')
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.NAME, 'email'))).send_keys(email)
    time.sleep(2)
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.NAME, 'pass'))).send_keys(password)
    time.sleep(1)
    driver.switch_to.active_element.send_keys(Keys.RETURN)

def get_fb_posts(driver, teleId, groupId, kwRegex, blacklistKwRegex, oldUsersList):
    dataframe = pd.DataFrame(columns=['phone', 'time', 'content', 'post', 'profile', 'group'])

    driver.get(f'https://facebook.com/groups/{groupId}?sorting_setting=CHRONOLOGICAL')
    posts = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'userContentWrapper')))
    for p in posts:
        if (p.find_element_by_class_name('_5ptz')
            .find_element_by_class_name('timestampContent')
            .text in ['Vừa xong', '1 phút', '2 phút', '3 phút', '4 phút', '5 phút',
                        'Just now', '1 min', '2 mins', '3 mins', '4 mins', '5 mins']):
            try:
                p.find_element_by_class_name('see_more_link_inner').click()
            except: pass

            content = p.find_element_by_class_name('userContent').text
            if content == '':
                break
            else:

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
                    if phone in oldUsersList:
                        break
                    else:
                        try:
                            post = p.find_element_by_class_name('_5pcq').get_attribute('href')
                        except:
                            break

                        post_time = pd.to_datetime(p.find_element_by_class_name('_5ptz').get_attribute('data-utime'), unit='s') + timedelta(hours=7)

                        dataframe = dataframe.append({'phone':phone, 'time':post_time, 'content':content,
                                                    'post':post, 'profile':profile, 'group':groupId}, ignore_index=True)
                else:
                    continue
    dataframe = dataframe.drop_duplicates(subset='post')
    dataframe = dataframe.drop_duplicates(subset='content')
    return dataframe

def scrape_groups(app):
    if not app.userNameVar.get():
        app.statusBar['text'] = 'Please fill Username'
    elif (not app.emailVar2.get()) or (not app.passVar2.get()):
        app.statusBar['text'] = 'Please fill Facebook account'
    else:
        check_validation('user', app.version, app.emailVar2.get(), app.teleIdVar2.get())
        app.statusBar['text'] = 'Scraping in Groups...'

        # Get keywords
        kwRegex = get_regex(app.keywordsVar2.get())
        blacklistKwRegex = get_regex(app.blacklistKeywordsVar2.get(), blacklist=True)

        userName = app.userNameVar.get()
        email = app.emailVar2.get()
        password = app.passVar2.get()
        teleId = app.teleIdVar2.get()
        keywords = app.keywordsVar2.get()
        blacklistKeywords = app.blacklistKeywordsVar2.get()
        groupIdList = app.groupIdListVar.get()
        groupIdList = groupIdList.split(',')

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
            driver = webdriver.Chrome(executable_path=app.chromePath, options=options)
            # driver = webdriver.Edge(executable_path=app.chromePath)
            log_in_facebook(driver, email, password)
        except Exception:
            app.statusBar['text'] = 'Chromedriver not found'
        
        beginCrawlDf = pd.DataFrame({'username':userName, 'session_id':app.session_id, 'version':app.version, 'action':'begin_crawl_groups', 'time':datetime.now(),
            'keywords':keywords, 'blacklist_keywords':blacklistKeywords, 'group_id': app.groupIdListVar.get()}, index=[0])
        play_with_gsheet(accounts.spreadsheetIdData, 'Sheet1', beginCrawlDf, 'append')

        try:
            play_with_gsheet(accounts.spreadsheetIdGroupPosts, method='new_sheet', sheetName=userName, numRow=1, numCol=6)
            df = pd.DataFrame(columns=['phone', 'time', 'content', 'post', 'profile', 'group'])
            play_with_gsheet(accounts.spreadsheetIdGroupPosts, _range=userName, dataframe=df, method='write')
        except: # Existed sheet
            pass

        while True:
            for groupId in groupIdList:
                try:
                    oldPostsDf = play_with_gsheet(accounts.spreadsheetIdGroupPosts, userName)
                    newPosts = get_fb_posts(driver, teleId, groupId.strip(), kwRegex, blacklistKwRegex, app.oldUsersList)
                    if len(newPosts) > 0:
                        newPosts = newPosts[(~newPosts.post.isin(oldPostsDf.post)) & (~newPosts.content.isin(oldPostsDf.content))]
                        if len(newPosts) > 0:
                            push_tele(teleId, 'groups', df=newPosts)
                            play_with_gsheet(accounts.spreadsheetIdGroupPosts, _range=userName, dataframe=newPosts, method='append')
                        
                except Exception as err:
                    if type(err).__name__ in ['WebDriverException', 'NoSuchWindowException', 'ProtocolError']:
                        app.statusBar['text'] = 'Scrape Ended'
                        endCrawlDf = pd.DataFrame({'username':userName, 'session_id':app.session_id, 'version':app.version, 'action':'end_crawl_groups', 'time':datetime.now(),
                            'keywords':keywords, 'blacklist_keywords':blacklistKeywords, 'group_id':app.groupIdListVar.get()}, index=[0])
                        play_with_gsheet(accounts.spreadsheetIdData, 'Sheet1', endCrawlDf, 'append')
                        break
                    elif type(err).__name__ == 'MaxRetryError':
                        try:
                            driver.quit()
                        except:
                            driver = webdriver.Chrome(executable_path=app.chromePath, options=options)
                            log_in_facebook(driver, email, password)
                            continue
                    else:
                        err_text = f"Error: {type(err).__name__}.\n{str(err)}\nFrom {email} at session <b>{app.session_id}</b>"
                        data = {
                            'chat_id': '807358017',
                            'text': err_text,
                            'parse_mode': 'HTML'
                        }
                        requests.post("https://api.telegram.org/bot{token}/sendMessage".format(token=accounts.botToken), data=data)
                        continue