from utils.gsheetApi import play_with_gsheet
import pandas as pd
import accounts
from datetime import datetime

def quit_action(dct, driver=None):
    try:
        if driver != None:
            driver.quit()
        if dct['session_id'] != '':
            closeAppDf = pd.DataFrame({'session_id':dct['session_id'], 'version':dct['version'], 'action':'close_app', 'time':[datetime.now()], 'email':dct['emailVar'],
            'teleIdVar':dct['teleIdVar'], 'keywords':dct['keywordsVar'], 'blacklist_keywords':dct['blacklistKeywordsVar']})
            play_with_gsheet(accounts.spreadsheetIdData, 'Sheet1', closeAppDf, 'append')
        with open('info.txt', 'w', encoding='utf-8') as f:
            if dct['rememberMeVar'] == 1: # Store default account
                f.write(f"""{dct['emailVar']}
{dct['passVar']}
{dct['teleIdVar']}
{dct['keywordsVar']}
{dct['blacklistKeywordsVar']}
{dct['chromePath']}""")

            else:
                f.write(f"""{dct['emailDefault']}
{dct['passDefault']}
{dct['teleIdDefault']}
{dct['keywordsVar']}
{dct['blacklistKeywordsVar']}""")
    except:
        pass