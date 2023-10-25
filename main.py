import json
import os
import signal
import time

from custom_exceptions import timeout_handler
from scrap import google_search, get_company_size_and_industry, linked_search, quit_driver, start_driver
from sheets import google_auth, get_sheets_data, update_sheet

# Get environment variables
SHEETS_FILE_ID = os.getenv('SHEETS_FILE_ID')
SHEET_NAME = os.getenv('SHEET_NAME')
SHEET_ID = int(os.getenv('SHEET_ID'))
COMPANY_NAME_COLUMN = os.getenv('COMPANY_NAME_COLUMN')
LINKEDIN_PROFILE_COLUMN = os.getenv('LINKEDIN_PROFILE_COLUMN')
COMPANY_SIZE_COLUMN = os.getenv('COMPANY_SIZE_COLUMN')
COMPANY_INDUSTRY_COLUMN = os.getenv('COMPANY_INDUSTRY_COLUMN')
STAT_FILE_NAME = os.getenv('STAT_FILE_NAME')

# Initialize Google Sheets
sheet_service = google_auth()

def driver_process(driver, company_name, name_profile_map):
    """
        This function takes in a driver, company_name, and name_profile_map as parameters.
        It prints the company_name and then initializes an empty dictionary called company_details.

        The function then checks if the company_profile exists in the name_profile_map dictionary.
        If it does, it assigns the corresponding value to company_profile.
        If not, it calls the linked_search(driver, company_name) function.
        If that returns None, it calls the google_search(driver, company_name) function.
        The result of either function call is assigned to company_profile.

        If company_profile is not None, the function proceeds to clean up the URL by removing any query parameters.
        It then removes any trailing slashes from the URL and prints the search result for company_name and the cleaned up company_profile.
        The company_profile is then assigned to the LINKEDIN_PROFILE_COLUMN key in the company_details dictionary.

        The function then calls the get_company_size_and_industry(driver, f'{company_profile}/about/') function
        to get the company size and industry information.
        The results are printed and assigned to the COMPANY_SIZE_COLUMN and COMPANY_INDUSTRY_COLUMN keys in the company_details dictionary.

        Finally, the function returns the company_details dictionary.
    """
    print(f'\ncompany_name: {company_name}')
    company_details = {}
    company_profile = name_profile_map.get(company_name) or linked_search(driver, company_name) or google_search(driver, company_name)
    if company_profile:
        company_profile = company_profile.split('?')[0]
        company_profile = company_profile.rstrip('/')
        print(f'search result for: {company_name} is company_profile: {company_profile}')
        company_details[LINKEDIN_PROFILE_COLUMN] = company_profile
        print(f'getting company size and industry for: {company_name}, {company_profile}')
        company_size, company_industry = get_company_size_and_industry(driver, f'{company_profile}/about/')
        print(f'company size and industry results for: {company_name}, {company_profile} is company_size: {company_size}, company_industry: {company_industry}')
        company_details[COMPANY_SIZE_COLUMN] = company_size
        company_details[COMPANY_INDUSTRY_COLUMN] = company_industry
    return company_details


def start():
    """
        This function is the starting point of the program.
        It performs the following steps:
        - Starts the timer.
        - Starts the driver.
        - Opens the stat JSON file and loads its contents.
        - Prints a message indicating the sheets data to be fetched.
        - Fetches the sheet data using the get_sheets_data() function.
        - Prints a message indicating the successful fetching of sheet data.
        - Retrieves the length of the sheet data.
        - Retrieves the row start and max count per cycle from the stat dictionary.
        - Iterates through slices of the sheet data.
        - Adds company names and name-profile mappings to sets and dictionaries.
        - Prints a message indicating the current slice of sheet data.
        - Iterates through the company names and processes each company.
        - Cancels the timer and retrieves the company data from the local company map.
        - Updates the local company map with default values if no data is found.
        - Updates the row start value.
        - Prints a message indicating the local company map and the number of rows processed.
        - Updates the sheet with the local company map if it is not empty.
        - Writes the updated stat dictionary to the stat JSON file.
        - Raises an exception for testing purposes.
        - Catches any exception and prints an error message.
        - Stops the timer.
        - Quits the driver.
        - Prints a message indicating the local company map and the number of rows processed.
        - Updates the sheet with the local company map if it is not empty.
        - Writes the updated stat dictionary to the stat JSON file.
    """
    try:
        start = time.time()
        driver = start_driver()
        try:
            with open(STAT_FILE_NAME, 'r') as stat_json_file:
                stat = json.load(stat_json_file)
        except FileNotFoundError:
           stat = {"row_start": 1, "max_count_per_cycle": 5}
        print(f'\n\nGetting sheets data for SHEETS_FILE_ID: {SHEETS_FILE_ID}, SHEET_NAME: {SHEET_NAME}, column: {COMPANY_NAME_COLUMN} to {COMPANY_INDUSTRY_COLUMN}')
        sheet_data = get_sheets_data(sheet_service, SHEETS_FILE_ID, SHEET_NAME, f'{COMPANY_NAME_COLUMN}:{COMPANY_INDUSTRY_COLUMN}')
        print('fetched sheet data')
        sheet_len = len(sheet_data)
        row_start = stat.get('row_start', 1)
        max_count_per_cycle = stat.get('max_count_per_cycle', 5)

        while(sheet_len > row_start):
            company_names = set()
            local_company_map = {}
            name_profile_map = {}
            row_end = min(sheet_len, row_start+max_count_per_cycle)
            sheet_data_slice = sheet_data[row_start:row_end]
            print(f'\n\nsheet_data_slice: row_start: {row_start}, row_end: {row_end}, data: {sheet_data_slice}')
            # Iterate through the values and add them to the set
            for row in sheet_data_slice:
                row_len = len(row)
                if row and not row_len > 2:  # Check for empty cells
                    company_names.add(row[0])
                    name_profile_map[row[0]] = row[1] if row_len == 2 else None
            print(f'\n\nunique company_names: {company_names}\n\n')

            for company_name in company_names:
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(500)
                try:
                    local_company_map[company_name] = driver_process(driver, company_name, name_profile_map)
                finally:
                    # Cancel the timer
                    signal.alarm(0)
                    company_data = local_company_map.get(company_name)
                    if not company_data:
                        local_company_map[company_name] = {}
                    local_company_map[company_name][LINKEDIN_PROFILE_COLUMN] = company_data.get(LINKEDIN_PROFILE_COLUMN, 'NA')
                    local_company_map[company_name][COMPANY_SIZE_COLUMN] = company_data.get(COMPANY_SIZE_COLUMN, 'NA')
                    local_company_map[company_name][COMPANY_INDUSTRY_COLUMN] = company_data.get(COMPANY_INDUSTRY_COLUMN, 'NA')
            
            row_start = row_end
            end = time.time()
            print(f'\n\nlocal_company_map: {local_company_map}, rows_processed: {row_end} in {end - start} seconds\n\n')
            if local_company_map:
                print(f'\n\nUpdating sheet: {SHEETS_FILE_ID}')
                update_sheet(sheet_service, SHEETS_FILE_ID, SHEET_ID, sheet_data, local_company_map)
                print(f'Updated the sheet: {SHEETS_FILE_ID}')
            
            stat = {'row_start': row_start, 'max_count_per_cycle': max_count_per_cycle}
            stat_json_object = json.dumps(stat, indent=4)
            with open(STAT_FILE_NAME, 'w') as stat_file:
                stat_file.write(stat_json_object)

    except Exception as ex:
        end = time.time()
        print(f'\n\n-------> in {end - start} seconds. Ex: {ex}\n\n')
    finally:
        quit_driver(driver)
        print(f'\n\nlocal_company_map: {local_company_map}, rows_processed: {row_end} in {end - start} seconds\n\n')
        if local_company_map:
            print(f'\n\nUpdating sheet: {SHEETS_FILE_ID}')
            update_sheet(sheet_service, SHEETS_FILE_ID, SHEET_ID, sheet_data, local_company_map)
            print(f'Updated the sheet: {SHEETS_FILE_ID}')
        
        stat = {'row_start': row_start, 'max_count_per_cycle': max_count_per_cycle}
        stat_json_object = json.dumps(stat, indent=4)
        with open(STAT_FILE_NAME, 'w') as stat_file:
            stat_file.write(stat_json_object)


if __name__ == '__main__':
    start()
