from bs4      import BeautifulSoup
from selenium import webdriver
from requests import get
from time     import sleep
from models   import Fencer, Game

BASE = "https://www.fencingtimelive.com"
#EVENT = "https://www.fencingtimelive.com/events/results/2A9E29A163E94077BD9BCF4F1EF8E6EE"
EVENT_SEARCH = "https://member.usafencing.org/search/tournaments/national?search=&filter_by_weapon=2&filter_by_gender=3&event_scopes=&filter_by_type=1&filter_by_event_type=&filter_by_show=past&designated="
options = webdriver.ChromeOptions()
#options.add_argument('headless')

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
                   # convert each row to soup obj for easier paring
        rows = list(map(lambda r: BeautifulSoup(r.get_attribute('innerHTML'), features="html.parser"), rows.find_elements_by_css_selector('tr.poolRow'))) # extract rows
        players = [i.find("span", class_="poolCompName").text for i in rows]
        for row in rows: 
            name = row.find("span", class_="poolCompName").text # extract text
            matches = [i.find("span").text for i in row.find_all("td", class_="poolScore")]
            stats = [i.text for i in row.find_all("td", class_="poolResult")] # extract data
            v, v_m, ts, tr, ind = map(str, stats) # extract statistics
            yield [fencer_id, name, v, v_m, ts, tr, ind, ','.join(matches), ','.join(i for i in players if i != name)]
            fencer_id += 1
    driver.close()

def parse_tableau(driver):
    sleep(3) # wait for page to load
    
    # store nextbtn as an updatable reference
    nextbtn = lambda: driver.find_element_by_css_selector("button#nextBut")
    games = {}
    round_names = []
    done = []
    offset = 0
    first_loop = False

    while '' not in round_names: # nextbtn().is_enabled() or first_loop:
        if not nextbtn().is_enabled(): first_loop = False
        # extract table into soup
        table = BeautifulSoup(driver.find_element_by_css_selector("table.elimTableau").get_attribute("innerHTML"), features='html.parser')
        rounds, *rows = table.find_all("tr")

        for r in rounds.find_all("th"):
            n = r.decode_contents()
            if n not in games:
                round_names.append(n)
                games[n] = []
        
        for tr in rows:
            for i, (name, td) in enumerate(zip(map(lambda i: i.decode_contents(), rounds.find_all("th")), tr.find_all("td"))):
                if name in done: continue
                # extract class from td
                class_ = td.attrs.get('class')
                if not class_: continue

                if "tbb" in class_ or "tbbr" in class_:
                    # decode name
                    player_name = td.find("span", class_="tcln").decode_contents()
                    first_name = td.find("span", class_="tcfn")
                    if first_name:
                        player_name += " " + first_name.decode_contents()

                    # add to last game or create new game if last game is full
                    rn = name# round_names[i + offset]
                    cg = games[rn]
                    # check if last game is actually full or it's just score
                    if cg and (len(cg[-1]) < 2 or (len(cg[-1]) == 2 and cg[-1][-1][0].isdigit())):
                        games[rn][-1].append(player_name)
                    else:
                        games[rn].append([player_name])
                    
                elif "tscoref" in class_:
                    score = td.find("span", class_="tsco")
                    if score:
                        dc = score.decode_contents()
                        if len(dc) > 1:
                            g=games[round_names[round_names.index(name) - 1]]
                            last_idx = list(filter(lambda i: not (any(j[0].isdigit() for j in g[i]) or any('BYE' in j for j in g[i])), range(0, len(g))))[0]
                            games[round_names[round_names.index(name) - 1]][last_idx].append(dc.split("<")[0])

        for i in range(1): #len(round_names) - len(done) - 1):
            nextbtn().click()
            offset += 1
            sleep(1)
        offset -= 1
        sleep(3)
        
        #offset += 1
        done.extend(round_names)

    del games['']
    
    game_id = 0
    for a, b in games.items():
        for game in b:
            c, d, *e = game
            if not e:
                yield [game_id, c, d, "0-0", a]
            elif d[0].isdigit():
                yield [game_id, c, e[0], d, a]
            else:
                yield [game_id, c, d, e[0], a]
            game_id += 1

    driver.close()
        
def combine_pools(pools):
    super_pool = []
    for pool in pools:
        for f in pool:
            old_fencer = [i for i in super_pool if i[1] == f[1]]
            if old_fencer:
                old_fencer = old_fencer[0]
                
                for i in range(2, len(f)):
                    old_fencer[i] += "-" + f[i]
                    
                super_pool.append(old_fencer)
            else:
                super_pool.append(f)
    yield from super_pool
        

def combine_tableaux(tabls):
    for t in tabls:
        yield from t
        
def scrape_data(event_url):
    # Retrieve the full page
    full_soup = make_soup(event_url)
    
    # Retrieve pools link and tableau link
    pools = []
    for pool in full_soup.find_all("img", src="/img/poolInverse.png"):
        pool_url = pool.findParent().attrs['href']
        pool_soup = make_soup(BASE+pool_url, headless=True)
        pools.append(parse_pools(pool_soup))

    tabls = []
    for tabl in full_soup.find_all("img", src="/img/tableauInverse.png"):
        tabl_url = tabl.findParent().attrs['href']
        tabl_soup = make_soup(BASE+tabl_url, headless=True)
        tabls.append(parse_tableau(tabl_soup))
    
    yield combine_pools(pools), combine_tableaux(tabls)

def get_events():
    # return [EVENT]
    # events = make_soup(EVENT_SEARCH)
    # for row in events.find("table").find_all("tr"):
    #     yield row.find("a", class_="d-block").text, row.find("a", class_="btn btn-sm btn-primary".split()).text
    yield "April Championship and NAC", "https://www.fencingtimelive.com/events/results/2A9E29A163E94077BD9BCF4F1EF8E6EE"
    yield "January NAC", "https://www.fencingtimelive.com/events/results/9828E06403B741498C70FB121ACA050B"    
