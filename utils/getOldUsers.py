from utils.gsheetApi import play_with_gsheet
import accounts

def get_old_users(master, statusBar):
    global oldUsersList
    statusBar['text'] = 'Getting old users...'
    dfOldUsers = play_with_gsheet(accounts.spreadsheetIdHubspot, 'Sheet1')
    oldUsersList = dfOldUsers.id
    oldUsersList.to_csv('oldUsersList.csv', index=False)
    statusBar['text'] = 'Old users updated.'