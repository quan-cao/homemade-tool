from utils.gsheetApi import play_with_gsheet
import pandas as pd
import accounts
from datetime import datetime

def quit_action(dct):
    session_id = dct['session_id']
    version = dct['version']
    email = dct['emailVar'].get()
    email2 = dct['emailVar2'].get()
    emailDefault = dct['emailDefault']
    emailDefault2 = dct['emailDefault2']
    password = dct['passVar'].get()
    password2 = dct['passVar2'].get()
    passDefault = dct['passDefault']
    passDefault2 = dct['passDefault2']
    teleId = dct['teleIdVar'].get()
    teleId2 = dct['teleIdVar2'].get()
    teleIdDefault = dct['teleIdDefault']
    teleIdDefault2 = dct['teleIdDefault2']
    rememberMe = dct['rememberMeVar'].get()
    rememberMe2 = dct['rememberMeVar2'].get()
    keywords = dct['keywordsVar'].get()
    keywords2 = dct['keywordsVar2'].get()
    blacklistKeywords = dct['blacklistKeywordsVar'].get()
    blacklistKeywords2 = dct['blacklistKeywordsVar2'].get()
    groupIdList = dct['groupIdListVar'].get()
    chromePath = dct['chromePath']

    if dct['session_id'] != '':
        closeAppDf = pd.DataFrame({'session_id':session_id, 'version':version, 'action':'close_app', 'time':datetime.now(),
        'email':[[email, email2]] if email != email2 else email, 'teleId':[[teleId, teleId2]] if teleId != teleId2 else teleId,
        'keywords':'', 'blacklist_keywords':'', 'group_id':groupIdList}, index=[0])
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
{groupIdList}""")