from bs4      import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.select import Select
from requests import get
from time     import sleep
from re       import compile
from json     import loads
from logs     import log
from collections import defaultdict

CHECK_REPECHAGE = False

BASE_FTL = "https://www.fencingtimelive.com"
#EVENT = "https://www.fencingtimelive.com/events/results/2A9E29A163E94077BD9BCF4F1EF8E6EE"
EVENT_SEARCH = "https://www.usafencing.org/natresults"
options = webdriver.ChromeOptions()
#options.add_argument('headless')

def fna(t):
    fn=t.find("span", class_="tcfn")
    ln=t.find("span", class_="tcln").decode_contents()
    if fn:ln+=" "+fn.decode_contents()
    return ln

def sn(e):
    try:
        e.select_by_index(e.options.index(e.first_selected_option) + 1)
    except Exception as e:
        print(e)


PARSERS = {
    ("/pools", "/tableaus"): {
        "base": lambda u: BASE_FTL,
        "find_pools": lambda s: [i.findParent() for i in s.find_all("img", src="/img/poolInverse.png")],
        "find_tabls": lambda s: [i.findParent() for i in s.find_all("img", src="/img/tableauInverse.png")],
        "preload": lambda u: lambda driver: None,
        "tds": {
            "is_info": lambda c: "tbb" in c or "tbbr" in c,
            "is_score": lambda c: class_ and "tscoref" in c,
            "get_score": lambda t: t.find("span", class_="tsco"),
            "find_name": fna,
            "rounds": "th"
        },
        "table_select": "table.elimTableau",
        "nextitem": lambda d: lambda: d.find_element_by_css_selector("button#nextBut"),
        "next": lambda el: el.click(),

        "pools": {
            "table": "table.table",
            "pool_row": lambda r: r.find_elements_by_css_selector("tr.poolRow"),
            "find_players": lambda i: i.find("span", class_="poolCompName").text,
            "find_name": lambda r: r.find("span", class_="poolCompName").text,
            "find_matches": lambda r: [i.find("span").text for i in r.find_all("td", class_="poolScore")],
            "find_stats": lambda s: [i.text for i in s.find_all("td", class_="poolResult")]
        }
    },
    "#Round": {
        "base": lambda u: u,
        "find_pools": lambda s: [j for i, j in enumerate(s.select("a.jumpListItem1")) if i % 2 == 0][:-1],
        "find_tabls": lambda s: [j for i, j in enumerate(s.select("a.jumpListItem1")) if i % 2 == 1],
        "preload": lambda u: lambda driver: driver.find_elements_by_css_selector("a.jumpListItem1")[int(u[-1])-1].click(),
        "tds": {
            "is_info": lambda c: ("tableauBorderBottom" in c or "tableauBorderBottomRight" in c) and "tableauNameCell" in c,
            "is_score": lambda c: 1,
            "get_score": lambda t: t.select("span.tableauReferee")[0].findParent() if t.select("span.tableauReferee") else False,
            "find_name": lambda t: t.select("span.tableauCompName")[0].text,
            "rounds": "td"
        },
        "table_select": "table.elimTableau",
        "nextitem": lambda d: lambda: Select([i for i in d.find_elements_by_css_selector("select.viewSelect") if i.is_displayed()][0]),
        "next": sn,

        "pools": {
            "table": "table.pool",
            "pool_row": lambda r: r.find_elements_by_css_selector("tr.poolOddRow") + r.find_elements_by_css_selector("tr.poolEvenRow"),
            "find_players": lambda i: i.find("td", class_="poolNameCol").decode_contents().split("<")[0],
            "find_name": lambda r: r.find("td", class_="poolNameCol").decode_contents().split("<")[0],
            "find_matches": lambda r: [i.text for i in r.find_all("td", class_="poolScoreCol")],
            "find_stats": lambda s: [i.text for i in s.find_all("td", class_="poolResultCol")]
        }
    },
    # "askfred": {}
}

EURL_TO_PARSER = {
    "https://www.fencingtimelive.com/events": ("/pools", "/tableaus"),
    "https://www.usfencingresults.org/": "#Round"
}

# Utility method to create Soup or Driver instance from url
def make_soup(url, _special_preload=lambda driver:None, headless=False, driver=None):
    if headless:
        if not driver: driver = webdriver.Chrome('./chromedriver', options=options)
        driver.get(url)
        if _special_preload: _special_preload(driver)
        return driver
    return BeautifulSoup(get(url).text, features="html.parser")

def parse_pools(driver, parser):
    sleep(3) # wait for page to load
    fencer_id = 0
    for pool_n, rows in enumerate([i for i in driver.find_elements_by_css_selector(parser["pools"]["table"]) if i.is_displayed()], start=1): # extract pool tables
                   # convert each row to soup obj for easier paring
        rows = list(map(lambda r: BeautifulSoup(r.get_attribute('innerHTML'), features="html.parser"), parser["pools"]["pool_row"](rows))) # extract rows
        # players = [i.find("span", class_="poolCompName").text for i in rows]
        players = [parser["pools"]["find_players"](i) for i in rows]
        for row in rows:
            # name = row.find("span", class_="poolCompName").text # extract text
            name = parser["pools"]["find_name"](row)
            matches = parser["pools"]["find_matches"](row)
            stats = parser["pools"]["find_stats"](row) # extract data
            if stats:
                v, v_m, ts, tr, ind = map(str, stats) # extract statistics
                yield [fencer_id, name, v, v_m, ts, tr, ind, ','.join(matches), ','.join(i for i in players if i != name)]
                fencer_id += 1
    driver.close()

def parse_tableau(driver, parser):
    sleep(3) # wait for page to load

    # store nextbtn as an updatable reference
    # nextbtn = lambda: driver.find_element_by_css_selector("button#nextBut")
    next_el = parser["nextitem"](driver)
    games = {}
    round_names = []
    done = []
    offset = 0

    while ('' not in round_names) and (' ' not in round_names): # nextbtn().is_enabled() or first_loop:
        # extract table into soup
        table = BeautifulSoup([i for i in driver.find_elements_by_css_selector(parser["table_select"]) if i.is_displayed()][0].get_attribute("innerHTML"), features='html.parser')
        rounds, *rows = table.find_all("tr")
        for r in rounds.find_all(parser["tds"]["rounds"]): # rounds.find_all("th"):
            n = r.decode_contents().replace(u'\xa0', '')
            if n == ' ' or not n.strip() or not n:
                round_names.append('')
                games[''] = []
            elif n not in games:
                round_names.append(n)
                games[n] = []

        for tr in rows:
            for i, (name, td) in enumerate(zip(map(lambda i: i.decode_contents(), rounds.find_all(parser["tds"]["rounds"])), tr.find_all("td"))):
                if name in done: continue
                # extract class from td
                class_ = td.attrs.get('class')
                rn = name.replace(u'\xa0', u'')  # round_names[i + offset]
                # if not class_: continue

                # if "tbb" in class_ or "tbbr" in class_:
                if class_ and parser["tds"]["is_info"](class_):
                    # decode name
                    # player_name = td.find("span", class_="tcln").decode_contents()
                    # first_name = td.find("span", class_="tcfn")
                    player_name = parser["tds"]["find_name"](td)
                    # first_name = parser["tds"]["first_name"](td)
                    # if first_name:
                    #     player_name += " " + first_name.decode_contents()

                    # add to last game or create new game if last game is full

                    cg = games.get(rn)
                    # check if last game is actually full or it's just score
                    if cg and (len(cg[-1]) < 2 or (len(cg[-1]) == 2 and cg[-1][-1][0].isdigit())):
                        games[rn][-1].append(player_name)
                    else:
                        games[rn].append([player_name])
                # elif "tscoref" in class_:
                # note: for some parsers class_ is not a requirement so no class_ and necessary
                elif parser["tds"]["is_score"](class_):
                    # score = td.find("span", class_="tsco")
                    score = parser["tds"]["get_score"](td)
                    if score:
                        dc = score.decode_contents()
                        if len(dc) > 1:
                            g=games[round_names[round_names.index(rn) - 1]]
                            last_idx = list(filter(lambda i: not (any(j[0].isdigit() for j in g[i]) or any('BYE' in j for j in g[i])), range(0, len(g))))[0]
                            # games[round_names[round_names.index(rn) - 1]]
                            g[last_idx].append(dc.split("<")[0])

        for i in range(1): #len(round_names) - len(done) - 1):
            parser["next"](next_el())
            offset += 1
            sleep(1)
        offset -= 1
        sleep(3)

        #offset += 1
        done.extend(round_names)

    # del games['']

    game_id = 0
    for a, b in games.items():
        if a == '': continue
        else:
            # print("Round", a)
            next_name = round_names[round_names.index(a) + 1]
            # print("Next games:")
            for i, j in enumerate(games[next_name]):
                b[i * 2].append(j[0])
                if not next_name == '':
                    b[i * 2 + 1].append(j[1] if not j[1][0].isdigit() else j[2])
        for game in b:
            try:
                c, d, *e, w = game
                if not e:
                    if d[0].isdigit():
                        yield [game_id, c, w, d, a, w]
                    else:
                        yield [game_id, c, d, "0-0", a, w]
                elif d[0].isdigit():
                    yield [game_id, c, e[0], d, a, w]
                else:
                    yield [game_id, c, d, e[0], a, w]
                game_id += 1
            except ValueError as ve:
                log.error(f"{ve} -> {game}")

    driver.close()

def _find(url, fn, base):
    for start, parser in PARSERS.items():
        if url.startswith(start):
            return fn(make_soup(base+url, parser["preload"](url), headless=True), parser)

find_pools = lambda url, base: _find(url, parse_pools, base)
find_tabls = lambda url, base: _find(url, parse_tableau, base)

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

def rankings(event_url):
    ranks = defaultdict(list)

    full_soup = make_soup(event_url)
    parser = [PARSERS[j] for i, j in EURL_TO_PARSER.items() if event_url.startswith(i)][0]
    base = parser["base"](event_url)

    for round in [2, 4]:
        if div := full_soup.select(f'#Round{round}Seeding'):
            table = div[0].select("table")[0]
            for row in table.select("tr")[1:]:
                try:
                    seed, name, *_ = row.select("td")
                    ranks[name].append(seed)
                except ValueError as e:
                    print(e)
        else:
            for name in ranks:
                ranks[name].append(0)
    for name in ranks:
        ranks[name].append(0)

    table = full_soup.select("#finalResults")[0].select("table")[0]
    for row in table.select("tr")[1:]:
        seed, name, *_ = row.select("td")
        ranks[name][-1] = seed

    for (n, r) in ranks.items():
        (p1, p2, *f) = r
        if f:
            yield (n.text, p1.text.strip("T"), p2.text.strip("T") if p2 else 0, f[0].text.strip("T") if f[0] else 0)

def scrape_data(event_url):
    # Retrieve the full page
    full_soup = make_soup(event_url)
    parser = [PARSERS[j] for i, j in EURL_TO_PARSER.items() if event_url.startswith(i)][0]
    base = parser["base"](event_url)
    # Retrieve pools link and tableau link

    r = rankings(event_url)

    pools = []
    for pool in parser["find_pools"](full_soup): # full_soup.find_all("img", src="/img/poolInverse.png"):
        pool_url = pool.attrs['href']
        pools.append(find_pools(pool_url, base))

    tabls = []
    for tabl in parser["find_tabls"](full_soup): # full_soup.find_all("img", src="/img/tableauInverse.png"):
        tabl_url = tabl.attrs['href']
        tabls.append(find_tabls(tabl_url, base))

    yield combine_pools(pools), combine_tableaux(tabls), r

def get_events():
    # return (("Jan NAC 2017", "https://www.usfencingresults.org/results/2016-2017/./2017.01-JAN-NAC/FTEvent_2017Jan06_DV1ME.htm"),)
    # '''
    # yield "April Championship and NAC", "https://www.fencingtimelive.com/events/results/2A9E29A163E94077BD9BCF4F1EF8E6EE"
    # yield "OCT NAC", "https://www.usfencingresults.org/results/2018-2019/2018.10-OCT-NAC/FTEvent_2018Oct12_DV1ME.htm"
    # return
    #


    # FTL_DATA = "https://fencingtimelive.com/tournaments/list/data"
    # SCHEDULE = "https://fencingtimelive.com/tournaments/eventSchedule/{}"
    # driver = make_soup("data:,", headless=True)
    # for tournament in loads(get(FTL_DATA).text):
    #     name, schedlink = tournament["name"], make_soup(SCHEDULE.format(tournament["id"]), headless=True, driver=driver)
    #     schedlink = BeautifulSoup(schedlink.page_source, "html.parser")
    #     st = schedlink.select("table.scheduleTable")
    #     # log.debug(SCHEDULE.format(tournament["id"]))
    #     if not st: continue
    #     for s in st:
    #         for tr_event in s.find_all("tr"):
    #             url = tr_event.find("a")
    #             if not url: continue
    #             url = BASE_FTL + url['href']
    #             msu = make_soup(url)
    #             _ev = msu.select("div.eventName")
    #             if not _ev: continue
    #             _ev = _ev[0].text
    #             if all(i in _ev for i in ["Div", " I ", "Men's", "Épée"]) and "Team" not in _ev:
    #                 # print(name, url)
    #                 yield name + msu.select("div.eventTime")[0].text, url

    UFR_DATA = "https://www.usfencingresults.org/results/20{}-20{}/"
    for a in range(11, 19):
        t_list = UFR_DATA.format(a, a + 1)
        t = make_soup(t_list).select("table.sortable")
        for sched in t[0].find_all("a", class_="name"):
            s_url = t_list + sched['href'].replace(" ", "%20")
            st = make_soup(s_url).select("table.dataTable")
            if not st: continue
            for tb in st:
                for tr_event in tb.find_all("tr"):
                    url = tr_event.find("a")
                    if not url: continue
                    url = s_url+'/'+url['href']
                    if 'DV1ME' not in url: continue
                    msu = make_soup(url)
                    _ev = msu.select("span.tournDetails")
                    if not _ev: continue
                    _ev = _ev[0].text
                    if all(i in _ev for i in ["Div", " I ", "Men's", "Epee"]) and "Team" not in _ev:
                        # print(sched['href'], url)
                        if CHECK_REPECHAGE or "Repechage" not in msu.text:
                            log.debug(f"Found valid url {url} (note: {'not ' if not CHECK_REPECHAGE else ''}checking repechage)")
                            yield sched['href'], url
                        else:
                            log.warning(f"Repechage found, skipping {url}")

    # ASK_FRED = "https://askfred.net/Results/past.php?f%5Bevent_weapon_eq%5D=Epee&f%5Bevent_gender_eq%5D=men&f%5Bevent_age_eq%5D=&f%5Bradius_mi%5D=300&vals%5Bloc%5D=&f%5Bname_contains%5D=&ops%5Bdate%5D=start_date_eq&vals%5Bdate%5D=&f%5Bevent_is_team%5D=&f%5Bevent_entries_gte%5D=&ops%5Bevent_rating%5D=event_rating_eq&vals%5Bevent_rating%5D=&f%5Bdivision_id%5D"
    # for page in range(5344 // 20):
    #     table = make_soup(ASK_FRED + f"&page_id={page + 1}").select("table#past-tours")[0]
    #     for row in table.find_all("tr"):
    #         link = row.find_all("a")[2]
    #         if "greyedout" not in link.attrs.get('class', []):
    #             print(link['href'])\
# '''

##    yield "April Championship and NAC", "https://www.fencingtimelive.com/events/results/2A9E29A163E94077BD9BCF4F1EF8E6EE"
##    yield "January NAC", "https://www.fencingtimelive.com/events/results/9828E06403B741498C70FB121ACA050B"
##    yield "National Championships and July Challenge", "https://www.fencingtimelive.com/events/results/3D1E58301F404058919BFD72DB0E6821"
##    yield "December NAC", "https://www.fencingtimelive.com/events/results/0E9AC4A22017471DB0243E68B1D6A902"
##    yield "October NAC", "https://www.fencingtimelive.com/events/results/5CEF42E54E9C42959C6629926C8D857B"

if __name__ == "__main__":
    for event, event_url in get_events():
        print(event_url)
        # for (pools, tableaus) in scrape_data(event_url):
        #     for i in pools:
        #         for k in i:
        #             ...
        #             #print(k)
        #     for j in tableaus:
        #         print(j)
