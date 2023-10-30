# Get environment variables
import os


# Google Sheets config
SHEETS_FILE_ID = os.getenv('SHEETS_FILE_ID')
SHEET_NAME = os.getenv('SHEET_NAME')
SHEET_ID = int(os.getenv('SHEET_ID'))

COMPANY_NAME_COLUMN = os.getenv('COMPANY_NAME_COLUMN')
LINKEDIN_PROFILE_COLUMN = os.getenv('LINKEDIN_PROFILE_COLUMN')
COMPANY_SIZE_COLUMN = os.getenv('COMPANY_SIZE_COLUMN')
COMPANY_INDUSTRY_COLUMN = os.getenv('COMPANY_INDUSTRY_COLUMN')

# LinkedIn config
LINKEDIN_COOKIES_FILE_NAME = os.getenv('LINKEDIN_COOKIES_FILE_NAME')
LINKEDIN_NOT_LOGGED_IN_PATHS = ['/signup/cold-join', '/signup', '/login', '/authwall']

# Google Auth config
# If modifying these scopes, delete the file token.json.
SCOPES = (
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/spreadsheets.readonly',
)

TOKEN_FILE_PATH = os.getenv('TOKEN_FILE_PATH')
CREDENTIAL_FILE_PATH = os.getenv('CREDENTIAL_FILE_PATH')

# Stat config
STAT_FILE_NAME = os.getenv('STAT_FILE_NAME')
