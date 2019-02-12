from __future__ import print_function
# from googleapiclient.discovery import build
# from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2 import service_account
import googleapiclient.discovery


from firebase_admin import credentials
from firebase_admin import firestore
import firebase_admin
import pickle
import os.path
import json


def update_sheet(request):
    """
    Authenticate into firebase and Sheets API and transfer newly added documents
    in 'lonely-hearts' collection into the lonely hearts google sheets.
    """
    with open('secrets.json') as f:
        secrets = json.loads(f.read())

    # initialise Firebase application instance if not already initialised
    # and get documents from the 'lonely-hearts' collection
    
    if (not len(firebase_admin._apps)):
        FIREBASE_CERTIFICATE = secrets['FIREBASE_CERTIFICATE']
        cred = credentials.Certificate(FIREBASE_CERTIFICATE)
        firebase_admin.initialize_app(cred)

    db = firestore.client()
    hearts_ref = db.collection(u'lonely-hearts')
    docs = hearts_ref.get()

    values = []
    for doc in docs:
        lonely_heart = doc.to_dict()
        row = [lonely_heart["Name"], lonely_heart["Likes"], lonely_heart["Dislikes"], lonely_heart["IdealDate"]]
        values.append(row)

    GOOGLE_SHEETS_SCOPE = secrets["SHEETS_SCOPE"]
    SHEETS_SERVICE_ACCOUNT = secrets["SHEETS_SERVICE_ACCOUNT"]
    SCOPES = [GOOGLE_SHEETS_SCOPE]
    

    # The ID and range of a sample spreadsheet.
    creds = service_account.Credentials.from_service_account_file(
        SHEETS_SERVICE_ACCOUNT, scopes=SCOPES
    )

    sheets_service = googleapiclient.discovery.build('sheets', 'v4', credentials=creds)

    SAMPLE_SPREADSHEET_ID = secrets["SPREADSHEET_ID"]
    SAMPLE_RANGE_NAME = secrets["RANGE"]
    # sqladmin = googleapiclient.discovery.build('sheets', 'v1beta3', credentials=credentials)
    # service = build('sheets', 'v4', credentials=creds)
    # Call the Sheets API
    body = {
        'values': values
    }
    result = sheets_service.spreadsheets().values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME, valueInputOption='RAW', body=body).execute()
    print('{0} cells updated.'.format(result.get('updatedCells')))
    return '{0} cells updated.'.format(result.get('updatedCells'))

# if __name__ == '__main__':
#     update_sheet()