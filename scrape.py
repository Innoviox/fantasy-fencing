from bs4      import BeautifulSoup
from selenium import webdriver
from requests import get
from time     import sleep
from models   import Fencer

BASE = "https://www.fencingtimelive.com"
EVENT = "https://www.fencingtimelive.com/events/results/2A9E29A163E94077BD9BCF4F1EF8E6EE"
options = webdriver.ChromeOptions()
options.add_argument('headless')

# Utility method to create Soup or Driver instance from url
def make_soup(url, headless=False):
    if headless:
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        return driver
    return BeautifulSoup(get(url).text, features="html.parser")

def parse_pools(driver):
    sleep(3) # wait for page to load
    fencer_id = 0
    for pool_n, rows in enumerate(driver.find_elements_by_css_selector('table.table'), start=1): # extract pool tables
        rows = rows.find_elements_by_css_selector('tr.poolRow') # extract rows
        for row in map(lambda r: BeautifulSoup(r.get_attribute('innerHTML'), features="html.parser"), rows): # convert each row to soup obj for easier paring
            name = row.find("span", class_="poolCompName").text # extract text
            stats = [i.text for i in row.find_all("td", class_="poolResult")] # extract data
            v, v_m, ts, tr, ind = stats # extract statistics
            yield [fencer_id, name, v, v_m, ts, tr, ind]
            fencer_id += 1

def parse_tableau(driver):
    ...
        
def scrape_data(event_url):
    # Retrieve the full page
    full_soup = make_soup(event_url)
    
    # Retrieve pools link and tableau link
    pool_url = full_soup.find_all("img", src="/img/poolInverse.png")[0].findParent().attrs['href']
    pool_soup = make_soup(BASE+pool_url, headless=True)
    yield parse_pools(pool_soup)
    
    tabl_url = full_soup.find_all("img", src="/img/tableauInverse.png")[0].findParent().attrs['href']
    tabl_soup = make_soup(BASE+tabl_url)
    yield parse_tableau(tabl_soup)

def get_events():
    return [EVENT]
