import json
import os
import time

# selenium 4
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup


LINKEDIN_COOKIES_FILE_NAME = os.getenv('LINKEDIN_COOKIES_FILE_NAME')
linkedin_not_logged_in = ['/signup/cold-join', '/signup', '/login', '/authwall']

def start_driver():
    """
        Start the driver and return the initialized WebDriver object.

        This function sets the User-Agent string to the specified value and 
        configures the ChromeOptions for headless browsing. It then installs 
        the Chrome driver and initializes the WebDriver object with the 
        configured options. Finally, it returns the initialized WebDriver object.

        Returns:
            driver (WebDriver): The initialized WebDriver object.
    """
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.62 Safari/537.36"

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--no-sandbox")
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument(f"--user-agent={user_agent}")

    print(f'\n\ninstalling driver')
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
    print(f'driver installed')
    return driver

def quit_driver(driver):
    """
        Quit the driver.

        Args:
            driver (WebDriver): The driver to quit.

        Returns:
            None
    """
    print(f'\n\nquitting driver')
    driver.quit()
    print(f'quit driver done')

cookies = None

def linkedin_login(driver):
    """
        Opens LinkedIn's login page, enters the username and password, and clicks on the login button.
        
        Args:
            driver (WebDriver): The WebDriver instance used to interact with the web page.
            
        Returns:
            None
    """
    global cookies
    driver.get("https://linkedin.com/uas/login")
    
    # waiting for the page to load
    time.sleep(5)
    
    username = driver.find_element(By.ID, "username")
    username.send_keys(os.getenv('LINKEDIN_USERNAME')) 
    
    pword = driver.find_element(By.ID, "password")
    pword.send_keys(os.getenv('LINKEDIN_PASSWORD'))       
    
    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    # waiting for the page to load
    time.sleep(10)

    # Check if the page contains the text "Start a post"
    if "Start a post" in driver.page_source:
        print("The page contains 'Start a post'.")
    else:
        print("The page does not contain 'Start a post'.")

    # Save linkedIn cookies
    cookies = driver.get_cookies()
    if cookies:
        print("Saving linkedIn cookies to file.")
        cookies_json_object = json.dumps(cookies, indent=4)
        with open(LINKEDIN_COOKIES_FILE_NAME, 'w') as stat_file:
            stat_file.write(cookies_json_object)

def scrap_page_driver(driver, url):
    """
        Scrapes a web page using the provided Selenium driver and extracts the company size and industry information.
        
        Args:
            driver (Selenium WebDriver): The Selenium WebDriver instance used to navigate the web page.
            url (str): The URL of the web page to scrape.
            
        Returns:
            tuple: A tuple containing the company size and industry information. If the information is not found, the corresponding value in the tuple will be None.
    """
    company_size = None
    company_industry = None
    # Find the element containing the company size
    print(f'\n\nscrap_page_driver for url: {url}')
    try:
        company_size_element = driver.find_element(By.XPATH, '//dt[text()="Company size"]/following-sibling::dd')
        company_size = company_size_element.text.split(' ')[0]
        print(f"Company size: {company_size}, url: {url}")
    except NoSuchElementException:
        company_size = None
        print(f"Company size not found, url: {url}")

    # Find the element containing the company industry
    try:
        industry_element = driver.find_element(By.XPATH, '//dt[text()="Industry"]/following-sibling::dd')
        company_industry = industry_element.text
        print(f"Company industry: {company_industry}, url: {url}")
    except NoSuchElementException:
        company_industry = None
        print(f"Company industry not found, url: {url}")
    return company_size, company_industry

def scrap_page_bs4(soup, url):
    """
        Scrapes the given page using BeautifulSoup and extracts the company size and industry information.
        
        Args:
            soup (BeautifulSoup): The BeautifulSoup object representing the HTML of the page.
            url (str): The URL of the page being scraped.
            
        Returns:
            Tuple[Optional[str], Optional[str]]: A tuple containing the company size (as a string) and the company industry (as a string). If the company size or industry is not found, the corresponding value in the tuple will be `None`.
    """
    company_size_no = None
    company_industry = None
    print(f'\n\nscrap_page for url: {url}')
    # Find the element containing the company size
    company_size_element = soup.find(lambda tag: tag.name == 'dt' and 'Company size' in tag.text)

    # Check if the element was found
    if company_size_element:
        # Get the following sibling which contains the actual company size
        company_size = company_size_element.find_next('dd').text.strip()
        company_size_no = company_size.split(' ')[0]
        print(f"Company size: {company_size}, url: {url}")
    else:
        print(f"Company size not found, url: {url}")

    # Find the element containing the company size
    industry_element = soup.find(lambda tag: tag.name == 'dt' and 'Industry' in tag.text)

    # Check if the element was found
    if industry_element:
        # Get the following sibling which contains the actual company size
        company_industry = industry_element.find_next('dd').text.strip()
        print(f"Company industry: {company_industry}, url: {url}")
    else:
        print(f"Company industry not found, url: {url}")
    return company_size_no, company_industry

def update_cookies(driver, url):
    """
        Update the cookies for the given driver and URL.
        
        Args:
            driver (WebDriver): The WebDriver instance used to navigate the web pages.
            url (str): The URL to update the cookies for.
        
        Returns:
            None
    """
    global cookies

    count = 0

    while any(item in driver.current_url for item in linkedin_not_logged_in):
        if count == 3:
            return
        print(f'{count}. url: {driver.current_url}')
        if cookies:
            print(f'\nWe have cookies, url: {url}')
            break
        else:
            print(f'\ngetting stored cookies, url: {url}')
            with open(LINKEDIN_COOKIES_FILE_NAME, 'r') as in_json_file:
                cookies = json.load(in_json_file)
            if cookies and count == 0:
                print(f'adding cookies, url: {url}')
                for cookie in cookies:
                    driver.add_cookie(cookie)
            else:
                print('LinkedIn login started')
                linkedin_login(driver)
                print('Logged in to LinkedIn')
        count += 1

    # Access LinkedIn as the authenticated user
    print(f'fetching url: {url}')
    driver.get(url)
    print(f'fetched url: {url}\n')

def get_company_size_and_industry(driver, url: str):
    """
        Retrieves the company size and industry information from a given URL using a web driver.

        Args:
            driver: The web driver object.
            url: The URL of the website to navigate to.

        Returns:
            A tuple containing the company size and industry information. If the information is not found, None is returned for both values.
    """
    # Navigate to a website
    driver.get(url)
    driver.implicitly_wait(5)
    if any(item in driver.current_url for item in linkedin_not_logged_in):
        update_cookies(driver, url)
    company_size_no = None
    company_industry = None
    count = 0
    while(not(company_size_no and company_industry)):
        if count == 3:
            break
        time.sleep(1+count)

        # Get and print the page title
        page_title = driver.title
        print(f'\n{count}. Page Title: {page_title}, url: {url}')

        company_size_no, company_industry = scrap_page_driver(driver, url)
        count += 1
    if not (company_size_no or company_industry):
        # Now you can access the content of the page after the popup is closed
        page_content = driver.page_source

        # Create a BeautifulSoup object to parse the page content
        soup = BeautifulSoup(page_content, 'html.parser')
        company_size_no, company_industry = scrap_page_bs4(soup, url)

    return company_size_no, company_industry

def linked_search(driver, name):
    """
        Searches for a company on LinkedIn using the provided name.

        Parameters:
            driver (WebDriver): The web driver to use for interacting with the browser.
            name (str): The name of the company to search for.

        Returns:
            str or None: The URL of the first search result, or None if no result is found.
    """
    try:
        print(f'\n\nLinkedin search: {name}')
        url = f"https://www.linkedin.com/search/results/companies/?keywords={name}"
        driver.get(url)
        driver.implicitly_wait(5)
        if any(item in driver.current_url for item in linkedin_not_logged_in):
            update_cookies(driver, url)
        count = 0
        href_attribute = None
        while(not href_attribute):
            if count == 3:
                return None
            time.sleep(1+count)
            first_result = driver.find_element(By.CSS_SELECTOR, ".reusable-search__result-container .entity-result__title-text a")
            if first_result:
                href_attribute = first_result.get_attribute("href")
            print(count, href_attribute)
        return href_attribute
    except:
        return None

def google_search(driver, name):
    """
        Searches for a given name on Google using the provided driver.
        
        Args:
            driver (WebDriver): The WebDriver instance used for the search.
            name (str): The name to search for.
        
        Returns:
            str: The href attribute of the first <a> tag found on the search page, 
                which corresponds to the Google search result for the given name.
                Returns None if no search result is found after three attempts.
    """
    print(f'\n\ngoogle search: {name}')
    q = f'https://www.google.com/search?q=site:linkedin.com/company/ AND "{name}"'
    driver.get(q)
    driver.implicitly_wait(5)
    count = 0
    href_attribute = None
    while(not href_attribute):
        if count == 3:
            return None
        time.sleep(1+count)

        print(f'{count}. Page Title: {driver.title}, name: {name}')
        page_content = driver.page_source

        # Create a BeautifulSoup object to parse the page content
        soup = BeautifulSoup(page_content, 'html.parser')

        search_element = soup.find(id='search')
        # print(search_element)
        if not search_element:
            print(f"No search_element, name: {name}")
            if 'Sign in' in driver.page_source:
                print(f"The page contains 'Sign in', getting query, name: {name}")
                driver.get(q)
                print(f'got query p, name: {name}')
            else:
                print(f"The page does not contain 'Sign in', name: {name}")
                # time.sleep(20)
            time.sleep(10)
            count += 1
            continue
        cite_element = search_element.find('cite')
        if not cite_element:
            print(f"No cite_element, name: {name}")
            count += 1
            continue
        first_a_tag = cite_element.find_previous('a')
        if not first_a_tag:
            print(f"No first_a_tag, name: {name}")
            count += 1
            continue

        # Get the 'href' attribute of the first <a> tag
        href_attribute = first_a_tag.get('href')
        print(href_attribute)
        
    return href_attribute
