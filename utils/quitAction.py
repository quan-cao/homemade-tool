from utils.gsheetApi import play_with_gsheet
import pandas as pd
import accounts
from datetime import datetime

def quit_action(dct):
    # try:
    if dct['session_id'] != '':
        closeAppDf = pd.DataFrame({'session_id':dct['session_id'], 'version':dct['version'], 'action':'close_app', 'time':[datetime.now()], 'email':dct['emailDefault'],
        'teleIdVar':dct['teleIdDefault'], 'keywords':'', 'blacklist_keywords':''})
        play_with_gsheet(accounts.spreadsheetIdData, 'Sheet1', closeAppDf, 'append')
    with open('info.txt', 'w', encoding='utf-8') as f:
        # if dct['rememberMeVar'] == 1: # Store default account
        f.write(f"""{dct['emailVar'].get() if dct['rememberMeVar'].get() == 1 else dct['emailDefault']}
{dct['passVar'].get()  if dct['rememberMeVar'].get() == 1 else dct['passDefault']}
{dct['teleIdVar'].get() if dct['rememberMeVar'].get() == 1 else dct['teleIdDefault']}
{dct['keywordsVar'].get()}
{dct['blacklistKeywordsVar'].get()}
{dct['chromePath']}
{dct['emailVar2'].get()  if dct['rememberMeVar2'].get() == 1 else dct['emailDefault2']}
{dct['passVar2'].get() if dct['rememberMeVar2'].get() == 1 else dct['passDefault2']}
{dct['teleIdVar2'].get() if dct['rememberMeVar2'].get() == 1 else dct['teleIdDefault2']}
{dct['keywordsVar2'].get()}
{dct['blacklistKeywordsVar2'].get()}
{dct['groupIdListVar'].get()}""")

#             else:
#                 f.write(f"""{dct['emailDefault']}
# {dct['passDefault']}
# {dct['teleIdDefault']}
# {dct['keywordsVar']}
# {dct['blacklistKeywordsVar']}""")
#     except:
        # pass