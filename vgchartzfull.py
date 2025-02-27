import time
from bs4 import BeautifulSoup, element
import urllib.request   # .request prefix required
import pandas as pd
import os               # To output to current directory
import numpy as np

pages = 64 # Should be all pages hopefully
rec_count = 0
rank = []
gname = []
platform = []
year = []
genre = []
critic_score = []
user_score = []
publisher = []
developer = []
sales_na = []
sales_pal = []
sales_jp = []
sales_ot = []
sales_gl = []
data_limit = 10
timeout = 50
urlhead = 'http://www.vgchartz.com/gamedb/?page='
urltail = '&console=&region=All&developer=&publisher=&genre=&boxart=Both&ownership=Both'
urltail += '&results=1000&order=Sales&showtotalsales=0&showtotalsales=1&showpublisher=0'
urltail += '&showpublisher=1&showvgchartzscore=0&shownasales=1&showdeveloper=1&showcriticscore=1'
urltail += '&showpalsales=0&showpalsales=1&showreleasedate=1&showuserscore=1&showjapansales=1'
urltail += '&showlastupdate=0&showothersales=1&showgenre=1&sort=GL'
mode = "w"
def write_out():
    """
    Writes scraped data to an output file, if w mode is detected, if first write is detected,
    switches to append mode after writing
    """
    columns = {
        'Rank': rank,
        'Name': gname,
        'Platform': platform,
        'Year': year,
        'Genre': genre,
        'Critic_Score': critic_score,
        'User_Score': user_score,
        'Publisher': publisher,
        'Developer': developer,
        'NA_Sales': sales_na,
        'PAL_Sales': sales_pal,
        'JP_Sales': sales_jp,
        'Other_Sales': sales_ot,
        'Global_Sales': sales_gl
    }
    df = pd.DataFrame(columns)

    # Changed output file logic
    outfile = os.path.join(os.path.abspath("."), "vgsales.csv")
    
    saved = False
    while not saved:
        try:
            df.to_csv(outfile, sep=",", encoding='utf-8', index=False, mode='a', header=False) # Now outputs to the current directory
            saved = True
        except Exception as e:
                print("IO error has occured, sleeping for 5 seconds. Close the output file if open, Description is below")
                print(e)
                time.sleep(5)
    print("Saved to {outfile}".format(outfile=outfile))
    

def flush_buffer():
    """
    Flushes out write buffers
    """
    global rank, gname, platform, year, genre, critic_score, user_score, publisher, developer, sales_na, sales_pal, sales_jp, sales_ot, sales_gl
    rank = []
    gname = []
    platform = []
    year = []
    genre = []
    critic_score = []
    user_score = []
    publisher = []
    developer = []
    sales_na = []
    sales_pal = []
    sales_jp = []
    sales_ot = []
    sales_gl = []

outfile = os.path.join(os.path.abspath("."), "vgsales.csv")
if os.path.exists(outfile):
        os.remove(outfile)
saved = False
while not saved:
    try:
        columns = {
        'Rank': rank,
        'Name': gname,
        'Platform': platform,
        'Year': year,
        'Genre': genre,
        'Critic_Score': critic_score,
        'User_Score': user_score,
        'Publisher': publisher,
        'Developer': developer,
        'NA_Sales': sales_na,
        'PAL_Sales': sales_pal,
        'JP_Sales': sales_jp,
        'Other_Sales': sales_ot,
        'Global_Sales': sales_gl
    }
        df = pd.DataFrame(columns)
        df = df[[
            'Rank', 'Name', 'Platform', 'Year', 'Genre',
            'Publisher', 'Developer', 'Critic_Score', 'User_Score',
            'NA_Sales', 'PAL_Sales', 'JP_Sales', 'Other_Sales', 'Global_Sales']]
        df.to_csv(outfile, sep=",", encoding='utf-8', index=False, mode='a') # Now outputs to the current directory
        saved = True
    except Exception as e:
        print("IO error has occured, sleeping for 5 seconds. Close the output file if open, Description is below")
        print(e)
        time.sleep(5)
        
for page in range(1, pages):
    surl = urlhead + str(page) + urltail
    soup = None
    while not soup:
        try:
            r = urllib.request.urlopen(surl, timeout=timeout).read()
            soup = BeautifulSoup(r, features="lxml")
        except Exception as e:
                print("HTTP error has occured, sleeping for 5 seconds. Description is below")
                print(e)
                time.sleep(5)
    print(f"Page: {page}")

    # vgchartz website is really weird so we have to search for
    # <a> tags with game urls

    game_tags = list(filter(
        lambda x: x.get('href').startswith('https://www.vgchartz.com/game/'),    # Changed the old get line, also http is no longer used 
        # discard the first 10 elements because those
        # links are in the navigation bar
        soup.find_all("a", href=True)   # Adjusted to only take exisitng href
    ))

    # This line can be boosted by multithreading but may not be feasible due to rate limiting
    for tag in game_tags:
        
        # add name to list
        gname.append(" ".join(tag.string.split()))
        print(f"{rec_count + 1} Fetch data for game {gname[-1]}")

        # get different attributes
        # traverse up the DOM tree
        data = tag.parent.parent.find_all("td")
        rank.append(np.int32(data[0].string))
        platform.append(data[3].find('img').attrs['alt'])
        publisher.append(data[4].string)
        developer.append(data[5].string)
        critic_score.append(
            float(data[6].string) if
            not data[6].string.startswith("N/A") else np.nan)
        user_score.append(
            float(data[7].string) if
            not data[7].string.startswith("N/A") else np.nan)
        sales_na.append(
            float(data[9].string[:-1]) if
            not data[9].string.startswith("N/A") else np.nan)
        sales_pal.append(
            float(data[10].string[:-1]) if
            not data[10].string.startswith("N/A") else np.nan)
        sales_jp.append(
            float(data[11].string[:-1]) if
            not data[11].string.startswith("N/A") else np.nan)
        sales_ot.append(
            float(data[12].string[:-1]) if
            not data[12].string.startswith("N/A") else np.nan)
        sales_gl.append(
            float(data[8].string[:-1]) if
            not data[8].string.startswith("N/A") else np.nan)
        release_year = data[13].string.split()[-1]
        # different format for year
        if release_year.startswith('N/A'):
            year.append('N/A')
        else:
            if int(release_year) >= 80:
                year_to_add = np.int32("19" + release_year)
            else:
                year_to_add = np.int32("20" + release_year)
            year.append(year_to_add)
        
        sub_soup = None
        while not sub_soup:
            # go to every individual website to get genre info, added try catch for rate limiting
            try:
                url_to_game = tag.attrs['href']
                site_raw = urllib.request.urlopen(url_to_game, timeout=timeout).read()
                sub_soup = BeautifulSoup(site_raw, "html.parser")
            except Exception as e:     # Too lazy to list every exception
                print("HTTP error has occured, sleeping for 5 seconds. Description is below")
                print(e)
                time.sleep(5)
        # again, the info box is inconsistent among games so we
        # have to find all the h2 and traverse from that to the genre name
        h2s = sub_soup.find("div", {"id": "gameGenInfoBox"}).find_all('h2')
        # make a temporary tag here to search for the one that contains
        # the word "Genre"
        temp_tag = element.Tag
        for h2 in h2s:
            if h2.string == 'Genre':
                temp_tag = h2
        genre.append(temp_tag.next_sibling.string)

        rec_count += 1
        if(rec_count % data_limit == 0):
            write_out()
            flush_buffer()
        

write_out()
flush_buffer()

