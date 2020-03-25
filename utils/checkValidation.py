from utils.gsheetApi import play_with_gsheet
from tkinter import messagebox
import accounts

def check_validation(master, type, version=None, email=None, teleId=None):
    try:
        checkVersionDf = play_with_gsheet(accounts.spreadsheetIdInfo, 'Sheet1')
    except:
        messagebox.showerror(title='No Connection', message='Please connect to Internet')
        quit()
    checkDf = checkVersionDf[checkVersionDf.version == version]

    if len(checkDf) == 0:
        messagebox.showerror(title='Error', message='Something\'s wrong.\nPlease re-download the latest version.')
        quit()
    else:
        if type == 'version':
            if checkDf.active.iloc[0] == 'FALSE':
                if checkDf.message.iloc[0] == 'deprecated':
                    messagebox.showerror(title='Version Deprecated', message='This version has been deprecated.\nPlease download the latest version.')
                    quit()
                elif checkDf.message.iloc[0] == 'maintain':
                    messagebox.showerror(title='Maintain', message='The app is under maintainance. Please try again later.')
                    quit()

        elif type == 'user':
            checkDf = checkDf.fillna('')
            if (email in checkDf.blacklist_email.iloc[0].split(',')) or (teleId in checkDf.blacklist_tele.iloc[0].split(',')):
                messagebox.showerror(title='Error', message='Something\'s wrong.\nPlease contact dev for more information.')
                quit()
