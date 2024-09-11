"""
#https://fbref.com/en/squads/abdce579/2023/Palmeiras-Stats
https://fbref.com/en/squads/639950ae/Flamengo-Stats
https://fbref.com/en/squads/157b7fee/Bahia-Stats
https://fbref.com/en/squads/d9fdd9d9/Botafogo-RJ-Stats
https://fbref.com/en/squads/03ff5eeb/Cruzeiro-Stats
https://fbref.com/en/squads/2091c619/Athletico-Paranaense-Stats
https://fbref.com/en/squads/5f232eb1/Sao-Paulo-Stats
https://fbref.com/en/squads/f98930d1/Red-Bull-Bragantino-Stats
https://fbref.com/en/squads/6f7e1f03/Internacional-Stats
https://fbref.com/en/squads/422bb734/Atletico-Mineiro-Stats
"""

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

seasons = ["2000", "2001", "2002", "2003", "2004", "2005",
             "2006", "2007", "2008", "2009", "2010",
             "2011", "2012", "2013", "2014", "2015",
             "2016", "2017", "2018", "2019", "2020",
             "2021", "2022", "2023", "2024"]

codes = ["abdce579", "639950ae", "157b7fee", "d9fdd9d9", "03ff5eeb", "2091c619", "5f232eb1",
         "f98930d1", "6f7e1f03", "422bb734",]

clubs = ["Palmeiras", "Flamengo","Bahia","Botafogo-RJ","Cruzeiro","Athletico-Paranaense",
         "Sao-Paulo","Red-Bull-Bragantino","Internacional","Atletico-Mineiro"]



def scrape_club_history(season):
    
    data =[]
    club_data = f"https://fbref.com/en/squads/03ff5eeb/{season}/Cruzeiro-Stats"
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
        for season in seasons:
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
        stor = os.path.join(root, f"static/data/brazil-teams/Cruzeiro-{season}.csv")
        print(stor)
        df_club_history.to_csv(stor)
