# Get environment variables
import os


# Google Sheets config
SHEETS_FILE_ID = os.getenv('SHEETS_FILE_ID')
SHEET_NAME = os.getenv('SHEET_NAME')
SHEET_ID = int(os.getenv('SHEET_ID'))

COMPANY_NAME_COLUMN = os.getenv('COMPANY_NAME_COLUMN', 'A')
LINKEDIN_PROFILE_COLUMN = os.getenv('LINKEDIN_PROFILE_COLUMN', 'B')
COMPANY_SIZE_COLUMN = os.getenv('COMPANY_SIZE_COLUMN', 'C')
COMPANY_INDUSTRY_COLUMN = os.getenv('COMPANY_INDUSTRY_COLUMN', 'D')

# LinkedIn config
LINKEDIN_COOKIES_FILE_NAME = os.getenv('LINKEDIN_COOKIES_FILE_NAME', 'linkedin_cookies.json')
LINKEDIN_NOT_LOGGED_IN_PATHS = ['/signup/cold-join', '/signup', '/login', '/authwall']

# Google Auth config
# If modifying these scopes, delete the file token.json.
SCOPES = (
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/spreadsheets.readonly',
)

TOKEN_FILE_PATH = os.getenv('TOKEN_FILE_PATH', 'token.json')
CREDENTIAL_FILE_PATH = os.getenv('CREDENTIAL_FILE_PATH', 'credentials.json')

# Stat config
STAT_FILE_NAME = os.getenv('STAT_FILE_NAME', 'stat.json')
DEFAULT_FUNCTION_TIMEOUT = int(os.getenv('DEFAULT_FUNCTION_TIMEOUT', 1000)) # in seconds
