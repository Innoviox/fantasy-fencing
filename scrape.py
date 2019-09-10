from bs4      import BeautifulSoup
from selenium import webdriver
from requests import get
from time     import sleep
from models   import Fencer, Game

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
    sleep(3) # wait for page to load
    
    # store nextbtn as an updatable reference
    nextbtn = lambda: driver.find_element_by_css_selector("button#nextBut")
    games = {}
    round_names = []
    offset = 0
    
    while nextbtn().is_enabled():
        # extract table into soup
        table = BeautifulSoup(driver.find_element_by_css_selector("table.elimTableau").get_attribute("innerHTML"), features='html.parser')
        rounds, *rows = table.find_all("tr")

        for r in rounds.find_all("th"):
            n = r.decode_contents().split()[-1]
            round_names.append(n)
            games[n] = []
        
        for tr in rows:
            for i, td in enumerate(tr.find_all("td")):
                # extract class from td
                class_ = td.attrs.get('class')
                if not class_: continue

                if "tbb" in class_ or "tbbr" in class_:
                    # decode name
                    player_name = td.find("span", class_="tcln").decode_contents()
                    first_name = td.find("span", class_="tcfn")
                    if first_name:
                        player_name += " " + first_name.decode_contents()

                    cg = games[round_names[i]]
                    if len(cg) == 0:
                        games[round_names[i]].append([player_name])
                    elif len(cg[-1]) < 2 or (len(cg[-1]) == 2 and cg[-1][-1][0].isdigit()):
                        games[round_names[i]][-1].append(player_name)
                    else:
                        games[round_names[i]].append([player_name])
                elif "tscoref" in class_:
                    score = td.find("span", class_="tsco")
                    if score:
                        dc = score.decode_contents()
                        if len(dc) > 1:
                            games[round_names[i - 1]][-1].append(dc.split("<")[0])
        
        nextbtn().click()
        sleep(2)
    
        
    
        
def scrape_data(event_url):
    # Retrieve the full page
    full_soup = make_soup(event_url)
    
    # Retrieve pools link and tableau link
    # pool_url = full_soup.find_all("img", src="/img/poolInverse.png")[0].findParent().attrs['href']
    # pool_soup = make_soup(BASE+pool_url, headless=True)
    # yield parse_pools(pool_soup)
    
    tabl_url = full_soup.find_all("img", src="/img/tableauInverse.png")[0].findParent().attrs['href']
    tabl_soup = make_soup(BASE+tabl_url, headless=True)
    yield parse_tableau(tabl_soup)

def get_events():
    return [EVENT]

for (pools, tableaus) in scrape_data(EVENT):
    for game in tableaus:
        print(game)
