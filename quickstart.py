from __future__ import print_function
import pickle
import os.path
import json
import firebase_admin
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from firebase_admin import credentials
from firebase_admin import firestore

#manage secrets

with open('secrets.json') as f:
    secrets = json.loads(f.read())

def get_secret(setting, secrets=secrets):
    '''
    Get the secret variable or return exception
    '''
    try:
        return secrets[setting]
    except KeyError:
        error_msg = "Issue setting up the {0} environment variable".format(setting)
        EnvironmentError(error_msg)


# Use a service account
FIREBASE_CERTIFICATE = get_secret("FIREBASE_CERTIFICATE")
cred = credentials.Certificate(FIREBASE_CERTIFICATE)
firebase_admin.initialize_app(cred)

db = firestore.client()

hearts_ref = db.collection(u'lonely-hearts')
docs = hearts_ref.get()
# values = [
#     [
#         # Cell values ...
#     ],
#     # Additional rows ...
# ]

values = []
for doc in docs:
    lonely_heart = doc.to_dict()
    row = [lonely_heart["Name"], lonely_heart["Likes"], lonely_heart["Dislikes"], lonely_heart["IdealDate"]]
    values.append(row)

# If modifying these scopes, delete the file token.pickle.
GOOGLE_SHEETS_SCOPE = get_secret("SHEETS_SCOPE")
SCOPES = [GOOGLE_SHEETS_SCOPE]

# The ID and range of a sample spreadsheet.

SAMPLE_SPREADSHEET_ID = get_secret("SPREADSHEET_ID")
SAMPLE_RANGE_NAME = get_secret("RANGE")

def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    GOOGLE_SHEETS_SECRETS_FILENAME = get_secret('GOOGLE_SHEETS_SECRETS_FILE')

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                GOOGLE_SHEETS_SECRETS_FILENAME , SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)
    # Call the Sheets API
    sheet = service.spreadsheets()
    body = {
        'values': values
    }
    result = sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME, valueInputOption='RAW', body=body).execute()
    print('{0} cells updated.'.format(result.get('updatedCells')))

if __name__ == '__main__':
    main()