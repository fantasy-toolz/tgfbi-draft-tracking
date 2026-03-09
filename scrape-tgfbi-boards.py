from bs4 import BeautifulSoup
import pandas as pd
import os
import time
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
from selenium.webdriver.firefox.options import Options





def scrape_drafts(leagues):
    url = 'https://draft.shgn.com/nfc/public/dp/{0}/grid'
    driver = webdriver.Firefox()
    dfs = []
    for league in leagues:
        # league = 810
        driver.get(url.format(league))
        time.sleep(np.random.randint(low = 20, high = 25, size = 1)[0])
        #time.sleep(np.random.randint(low = 12, high = 16, size = 1)[0])
        
        html = driver.page_source
        soup = BeautifulSoup(html)
        #with open("output.html", "w") as file: # For easier manipulation
        #    file.write(str(soup))
        
        table_data      = soup.find("table", { "class" : "table table-bordered table-condensed player-table-new team-num-15 table-scrollable-body"})      
        rows = []
        pick_count = 1
        for row in table_data.findAll("tr"):
            cells = row.findAll("td")
            try:
                pick_round = int(row.find("th").text)
                for td in row.findAll("td"):  
                    data = [element.text for element in td.find_all("span")]
                    if len(data) > 0:
                        rows.append([pick_round, pick_count, str(data[1]) +" " + str(data[-1]), str(data[-2])])
                        if pick_round % 2 == 0:
                            pick_count = pick_count - 1
                        else:
                            pick_count = pick_count + 1
                if pick_round % 2 == 0:
                    pick_count = 1 
                else:
                    pick_count = 15
            except:
                pass
        
        headers = ["Round Number", "Round Pick", "Name", "Team"]
        df = pd.DataFrame(rows, columns=headers)
        df = df.sort_values(["Round Number", "Round Pick"], ascending=[True, True])
        df = df.reset_index(drop=True)
        df['Overall Pick'] = df.index +1
        dfs.append(df)
    
    # Create a single DataFrame from all the scraping    
    tgfbi_df = dfs[0]
    for league_df in dfs[1:]:
        tgfbi_df = pd.concat([tgfbi_df, league_df])
    
    return tgfbi_df


def make_hist(in_df, in_name, round_len):
    # in_name = 'Jose Abreu'
    # in_df = tgfbi_df
    play_df = in_df.loc[in_df['Name']==in_name].copy()
    play_df = play_df[['Overall Pick']]
    bin_ranges = list(range(1,451, round_len))
    n, bins, patches = plt.hist(play_df['Overall Pick'], bins = bin_ranges, facecolor='green', alpha=0.75)
    plt.xlabel('Pick Number')
    plt.ylabel('Picks')
    plt.title(in_name)
    plt.axis([0, 450, 0, 25]) #n.max()])
    print(n.max())
    plt.grid(True)
    
    plt.show()
    

# Input Variables
league_list = list(range(1062, 1083+1))
tgfbi_df = scrape_drafts(league_list)
# # tgfbi_1df = pd.read_csv('tgfbi_2023.csv')
# # tgfbi_df['ADP'] = tgfbi_df['Overall Pick'].groupby([i_df['Name', 'Team']).transform('mean')
# # tgfbi_df['MIN'] = tgfbi_df['Overall Pick'].groupby(tgfbi_df['Name', 'Team']).transform('min')
# # tgfbi_df['MAX'] = tgfbi_df['Overall Pick'].groupby(tgfbi_df['Name', 'Team']).transform('max')
# # tgfbi_df['bigdiff'] = tgfbi_df['MAX'] - tgfbi_df['MIN'] 

tgfbi_df_adp = tgfbi_df.groupby(['Name', 'Team'], as_index = False)['Overall Pick'].mean()
tgfbi_df_adp.columns = ['Name', 'Team', 'ADP']
tgfbi_df_min = tgfbi_df.groupby(['Name', 'Team'], as_index = False)['Overall Pick'].min()
tgfbi_df_min.columns = ['Name', 'Team', 'MIN']
tgfbi_df_max = tgfbi_df.groupby(['Name', 'Team'], as_index = False)['Overall Pick'].max()
tgfbi_df_max.columns = ['Name', 'Team', 'MAX']

tgfbi_df_summary = tgfbi_df[
    ['Round Number', 'Round Pick', 'Name', 'Team', 'Overall Pick']
    ].merge(tgfbi_df_adp, on = ['Name', 'Team'], how = 'left')
tgfbi_df_summary = tgfbi_df_summary.merge(tgfbi_df_min, on = ['Name', 'Team'], how = 'left')
tgfbi_df_summary = tgfbi_df_summary.merge(tgfbi_df_max, on = ['Name', 'Team'], how = 'left')
tgfbi_df_summary['Spread'] = tgfbi_df_summary['MAX'] - tgfbi_df_summary['MIN'] 

tgfbi_df.to_csv('tgfbi_all.csv')

# Summary Stats
print(len(tgfbi_df.loc[tgfbi_df['Overall Pick']==450]))

# do a quick check by picking a random player
players = [
    'Edwin Diaz'
    ]
for player in players:
    # make_hist(tgfbi_df, player, 10)
    print(player)
    print(list(tgfbi_df_adp.loc[tgfbi_df_adp['Name']==player]['ADP'])[0])


for indx,name in enumerate(tgfbi_df['Name'].value_counts().index):
    tgfbi_df_summary.loc[tgfbi_df_summary['Name']==name, 'Leagues Drafted'] = tgfbi_df['Name'].value_counts().values[indx].astype(int)  

tgfbi_df_summary['ADP'] = tgfbi_df_summary['ADP'].round(2)
tgfbi_df_summary = tgfbi_df_summary.drop(columns=['Round Number', 'Round Pick', 'Overall Pick'])
tgfbi_df_summary['Leagues Drafted'] = tgfbi_df_summary['Leagues Drafted'].astype(int)
tgfbi_df_summary = tgfbi_df_summary.sort_values('ADP')
tgfbi_df_summary = tgfbi_df_summary.drop_duplicates(subset=['Name'], keep='first')

tgfbi_df_summary.to_csv('tgfbi_adp.csv', index = False)