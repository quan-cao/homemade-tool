import pandas as pd
from datetime import datetime

import accounts
from utils import play_with_gsheet

def quit_action(dct):
    userName = dct['userNameVar']
    session_id = dct['session_id']
    version = dct['version']
    email = dct['emailVar']
    email2 = dct['emailVar2']
    emailDefault = dct['emailDefault']
    emailDefault2 = dct['emailDefault2']
    password = dct['passVar']
    password2 = dct['passVar2']
    passDefault = dct['passDefault']
    passDefault2 = dct['passDefault2']
    teleId = dct['teleIdVar']
    teleId2 = dct['teleIdVar2']
    teleIdDefault = dct['teleIdDefault']
    teleIdDefault2 = dct['teleIdDefault2']
    rememberMe = dct['rememberMeVar']
    rememberMe2 = dct['rememberMeVar2']
    keywords = dct['keywordsVar']
    keywords2 = dct['keywordsVar2']
    blacklistKeywords = dct['blacklistKeywordsVar']
    blacklistKeywords2 = dct['blacklistKeywordsVar2']
    groupIdList = dct['groupIdListVar']
    chromePath = dct['chromePath']

    if dct['session_id'] != '':
        closeAppDf = pd.DataFrame({'username':userName, 'session_id':session_id, 'version':version, 'action':'close_app',
            'time':datetime.now(), 'keywords':'', 'blacklist_keywords':'', 'group_id':groupIdList}, index=[0])
        play_with_gsheet(accounts.spreadsheetIdData, 'Sheet1', closeAppDf, 'append')

    with open('info.txt', 'w', encoding='utf-8') as f:
        f.write(f"""{email if rememberMe == 1 else emailDefault}
{password if rememberMe == 1 else passDefault}
{teleId if rememberMe == 1 else teleIdDefault}
{keywords}
{blacklistKeywords}
{chromePath}
{email2  if rememberMe2 == 1 else emailDefault2}
{password2 if rememberMe2 == 1 else passDefault2}
{teleId2 if rememberMe2 == 1 else teleIdDefault2}
{keywords2}
{blacklistKeywords2}
{groupIdList}
{userName}""")