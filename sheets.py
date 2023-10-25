from __future__ import print_function

import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = (
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/spreadsheets.readonly',
)

# environment variables
TOKEN_FILE_PATH = os.getenv('TOKEN_FILE_PATH')
CREDENTIAL_FILE_PATH = os.getenv('CREDENTIAL_FILE_PATH')
LINKEDIN_PROFILE_COLUMN = os.getenv('LINKEDIN_PROFILE_COLUMN')
COMPANY_SIZE_COLUMN = os.getenv('COMPANY_SIZE_COLUMN')
COMPANY_INDUSTRY_COLUMN = os.getenv('COMPANY_INDUSTRY_COLUMN')

SHEETS = None

def google_auth(sheet_file_id=None):
    """
        Authenticates the user using Google Sheets API.

        Args:
            sheet_file_id (str, optional): The file ID of the Google Sheets document to access. Defaults to None.

        Returns:
            Resource: The Google Sheets resource object.

        Raises:
            HttpError: If there is an error accessing the Sheets API.
    """
    global SHEETS

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(TOKEN_FILE_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE_PATH, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIAL_FILE_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(TOKEN_FILE_PATH, 'w') as token:
            token.write(creds.to_json())

    try:
        SHEETS = build('sheets', 'v4', credentials=creds)
        if sheet_file_id:
            # Retrieve the documents contents from the Docs service.
            sheet = SHEETS.spreadsheets().get(spreadsheetId=sheet_file_id).execute()
            print('The title of the sheet is: {}'.format(sheet.get('properties').get('title')))
        return SHEETS
    except HttpError as err:
        print(err)

def get_sheets_data(service=None, sheet_file_id=None, sheet_name=None, column_range=None):
    """(private) Returns data from Google Sheets source. It gets all rows of
        'Sheet1' (the default Sheet in a new spreadsheet), but drops the first
        (header) row. Use any desired data range (in standard A1 notation).
    """
    if not service:
        service = SHEETS
    return service.spreadsheets().values().get(spreadsheetId=sheet_file_id,
                                               range=f'{sheet_name}{f"!{column_range}" if column_range else ""}').execute().get(
        'values', [])
    # skip header row


def update_sheet(service=None, sheet_file_id=None, sheet_id=None, values=None, company_map=None):
    """
        Updates a Google Sheet with the specified values.

        Parameters:
            service (object): The Google Sheets service object.
            sheet_file_id (str): The ID of the Google Sheet file.
            sheet_id (str): The ID of the specific sheet in the Google Sheet file.
            values (list): A list of rows to update in the sheet.
            company_map (dict): A dictionary mapping company names to column values.

        Returns:
            None
    """
    # Initialize a list to store batch update requests
    batch_requests = []

    # Iterate through the rows
    for row_index, row in enumerate(values, start=1):
        # Check if the value in column E is 'abc'
        if row and row[0] in company_map:
            # Create a request to update columns F, G, and H for this row
            update_request = {
                'updateCells': {
                    'rows': [
                        {
                            'values': [
                                {'userEnteredValue': {'stringValue': company_map.get(row[0], {}).get(LINKEDIN_PROFILE_COLUMN, '')}},  # Update column B
                                {'userEnteredValue': {'stringValue': company_map.get(row[0], {}).get(COMPANY_SIZE_COLUMN, '')}},  # Update column C
                                {'userEnteredValue': {'stringValue': company_map.get(row[0], {}).get(COMPANY_INDUSTRY_COLUMN, '')}}   # Update column D
                            ]
                        }
                    ],
                    'fields': 'userEnteredValue',
                    'start': {'sheetId': sheet_id, 'rowIndex': row_index - 1, 'columnIndex': 1}  # Start at column B (index 1)
                }
            }
            batch_requests.append(update_request)
    if not service:
        service = SHEETS
    # Send batch update requests to update the specified columns
    if batch_requests:
        request_body = {'requests': batch_requests}
        service.spreadsheets().batchUpdate(spreadsheetId=sheet_file_id, body=request_body).execute()
        print(f"Updated {len(batch_requests)} rows")
    else:
        print("No rows found in column E.")
