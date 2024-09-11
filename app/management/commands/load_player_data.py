import string
import random
import csv
import os
import datetime

from django.core.management.base import BaseCommand
from django.conf import settings

from project.models import PlayerStat, GoalStat, AssitStat, OtherStat
from app.models import ClubPoint, Team, Tournament, Season, Player, PlayerRecord, BirthYear, PlayerNationality, Position

#To run the code enter: python manage.py load_data

class Command(BaseCommand):
    help = 'load data from csv'

    def handle(self, *args, **kwargs):
        data = 'PL-player-stats-2001-2002.csv'
        results = []
        with open(os.path.join(settings.BASE_DIR, 'static/data/Stats/'+data), 'r', encoding='utf8') as f:
            reader = csv.reader(f)
            #print(reader)
            for i, row in enumerate(reader):
                if i == 0:
                    pass
                else:
                    
                    #all_rows = ''.join(row)
                    #row = row.split()
                    player_name = row[1].split(' ', 1)
                    print(len(player_name))
                    print(row[15])

                    if len(player_name) >= 2:
                        print(player_name[0])
            
                    
                    obj = PlayerRecord(
                        player=Player.objects.get_or_create(
                            first_name=player_name[0], last_name=( player_name[1] if len(player_name) >= 2 else ''),
                            nationality=PlayerNationality.objects.get_or_create(
                                country_code=row[2],
                            )[0],
                            year_of_birth=BirthYear.objects.get_or_create(
                                year=row[6],
                            )[0],
                        )[0]
                                                            ,
                        club=Team.objects.get_or_create(name=row[4])[0],
                        season=Season.objects.get_or_create(name=row[25], year=2001)[0],
                        position=Position.objects.get_or_create(position=row[3])[0],
                        age=row[5],
                        match_played=row[7],
                        starts=row[8],
                        minutes_played=row[9],
                        assists=row[12],
                        goals=row[11],
                        card_yellow=(0 if row[17] == '' else row[17]),
                        card_red=(0 if row[18] == '' else row[18]),
                        penalty=(0 if row[15] == '' else row[15]),
                        goals_assist=row[13],
                        goals_penalty=(0 if row[14] == '' else row[14]),
                    )
                    print('============')
                    print('============')

                    results.append(obj)
                    
            save_data = PlayerRecord.objects.bulk_create(results)
                    
            
