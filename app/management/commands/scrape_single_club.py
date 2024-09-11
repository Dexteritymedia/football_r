import os
from pathlib import Path
import time
import csv

from django.core.management.base import BaseCommand
from django.conf import settings

import pandas as pd
import bs4
import requests

from project.models import PlayerStat, GoalStat, AssitStat, OtherStat
from app.models import ClubPoint, Team, Tournament

#To run the code enter: python manage.py load_data

seasons = ["2000-2001", "2001-2002", "2002-2003", "2003-2004", "2004-2005",
             "2005-2006", "2006-2007", "2007-2008", "2008-2009", "2009-2010",
             "2010-2011", "2011-2012", "2012-2013", "2013-2014", "2014-2015",
             "2015-2016", "2016-2017", "2017-2018", "2018-2019", "2019-2020",
             "2020-2021", "2021-2022", "2022-2023", "2023-2024"]

seasons_ = ["2020-2021", "2021-2022", "2022-2023", "2023-2024"]

codes = ["e297cd13", "4ba7cbea", "943e8050", "1df6b87e", "e4a775cb", "fd962109", "cd051869",
         "cff3d9bb", "361ca564", "19538871", "822bd0ba", "b8fd03ef", "18bb7c10",
         "b2b47a98", "d07537b9", "7c21e445", "d3fd31cc", "8602292d", "47c64c55",
         "8cec06e1",]

clubs = ["Luton-Town", "Bournemouth", "Burnley", "Sheffield-United",
         "Nottingham-Forest", "Fulham", "Brentford",
         "Chelsea", "Tottenham-Hotspur", "Manchester-United", "Liverpool",
         "Manchester-City", "Arsenal", "Newcastle-United", "Brighton-and-Hove-Albion",
         "West-Ham-United", "Everton", "Aston-Villa", "Crystal-Palace", "Wolverhampton-Wanderers",
         ]

club = "Manchester-United"
code = "19538871"

def scrape_club_history(season):
    #club_data = f"https://fbref.com/en/squads/18bb7c10/{years}/Arsenal-Stats"
    #https://fbref.com/en/squads/19538871/2013-2014/Manchester-United-Stats
    #https://fbref.com/en/squads/53a2f082/2022-2023/Real-Madrid-Stats
    #https://fbref.com/en/squads/add600ae/2022-2023/Dortmund-Stats

    
    data =[]
    club_data = f"https://fbref.com/en/squads/add600ae/{season}/Dortmund-Stats"
    print(club_data)
    response = requests.get(club_data)
    print(response)
    soup = bs4.BeautifulSoup(response.text, "html.parser")
    table_overall = soup.find(id="matchlogs_for")
    if table_overall == None:
        print("Club data does not exist")
    else:
        row = table_overall.select("tbody tr")
        for j in row:
            row_rank = j.find_all("th")
            row_data = j.find_all("td")
            row = [i.text for i in row_rank + row_data]
            data.append(row+[season]+[season]+[season])

    return data
    

class Command(BaseCommand):
    help = 'scrape data from online'

    def handle(self, *args, **kwargs):
        root = settings.BASE_DIR
        data =[]
        for season in seasons_:
            results = scrape_club_history(season)
            print(results)
            print("Compiling...")
            data.append(results)
            print("Waiting 5 seconds to start scraping again...")
            time.sleep(5)
        print("Saving to csv")
        print(data)
        data_to_list = [i for j in data for i in j]
        df_club_history = pd.DataFrame(data_to_list)
        stor = os.path.join(root, f"static/data/Dortmund-{season}.csv")
        print(stor)
        df_club_history.to_csv(stor)

    
