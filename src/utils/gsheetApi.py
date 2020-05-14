import pandas as pd
import pickle, os, sys, requests, logging

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from utils import resource_path

def gsheet_build_service(token_refresh=True):
    tokenPath = resource_path(r'src\token.pickle')
    with open(tokenPath, 'rb') as token:
        credentials = pickle.load(token)
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token and token_refresh:
            credentials.refresh(Request())
    service = build('sheets', 'v4', credentials=credentials)
    return service


def play_with_gsheet(spreadsheetId=None, _range=None, dataframe=None, method='read', sheetName=None, numRow=None, numCol=None, first_time=True, service=None):
    """
    method: {'read', 'write', 'clear', 'append', 'new_sheet'}
    """
    
    if first_time:
        service = gsheet_build_service()

    if method == 'read':
        result = service.spreadsheets().values().get(spreadsheetId=spreadsheetId, range=_range).execute()
        values = result.get('values', [])
        df = pd.DataFrame(values)
        df = df.iloc[1:].rename(columns=df.iloc[0])
        return df
    
    if method == 'write':
        values = [dataframe.columns.values.astype(str).tolist()] + dataframe.astype(str).values.tolist()
        data = [
            {
                'range': _range,
                'values': values
            }
        ]
        body = {
            'valueInputOption':'RAW',
            'data':data
        }
        
        try:
            service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheetId, body=body).execute()
        except:
            logging.error('Write error !')

    if method == 'clear':
        body = {
            'ranges':_range
        }
        
        service.spreadsheets().values().batchClear(spreadsheetId=spreadsheetId, body=body).execute()
            
    if method == 'append' and len(dataframe) > 0:
        body = {
            'values': dataframe.astype(str).values.tolist()
        }
        
        try:
            service.spreadsheets().values().append(spreadsheetId=spreadsheetId, range=_range,
                                                        valueInputOption='RAW', insertDataOption='INSERT_ROWS',
                                                        body=body).execute()
        except:
            logging.error('Append error !')

    if method == 'new_sheet':
        body = {
            'requests': [
                {
                    "addSheet": {
                        "properties": {
                            "title": sheetName,
                            "gridProperties": {
                                "rowCount": numRow,
                                "columnCount": numCol
                            }
                        }
                    }
                }
            ]
        }
        service.spreadsheets().batchUpdate(spreadsheetId=spreadsheetId, body=body).execute()