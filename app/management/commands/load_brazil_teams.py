import string
import random
import csv
import os
import datetime

from django.core.management.base import BaseCommand
from django.conf import settings

from project.models import PlayerStat, GoalStat, AssitStat, OtherStat
from app.models import ClubPoint, Team, Tournament, Season

#To run the code enter: python manage.py load_data

class Command(BaseCommand):
    help = 'load data from csv'

    def handle(self, *args, **kwargs):
        data = 'Palmeiras-2024'
        results = []
        with open(os.path.join(settings.BASE_DIR, 'static/data/brazil-teams/'+data), 'r', encoding='utf8') as f:
            reader = csv.reader(f)
            #print(reader)
            for i, row in enumerate(reader):
                if i == 0:
                    pass
                else:
        
                    matchweek = row[4].replace('Matchweek ', '')
                    match_zero = 0
                    number = range(1, 39)
                    print(matchweek)
                    print(number)
                    print(type(number))
                    print(type(matchweek))
                    
                    if matchweek in str(list(range(1, 39))):
                        print('Mzzzzzzzzzzzzz', matchweek)
                    else :
                        print('MW', int(0))
                    
                    club = row[10].title()
                    tournament = row[3].title()
                    print(row[1])
                    print(row[10].title())
                    match_year = datetime.datetime.strptime(str(row[1]), '%Y-%m-%d').year
                    print(match_year)
                    
                    obj = ClubPoint(
                        date=row[1],
                        club=Team.objects.get(name='Palmeiras'),
                        #season=Season.objects.get_or_create(name=row[22], year=match_year)[0],
                        season=Season.objects.get_or_create(name='-------', year=match_year)[0],
                        tournament=Tournament.objects.get_or_create(name=row[3])[0],
                        ground=row[6],
                        matchweek=( matchweek if matchweek in str(list(range(1, 39))) else int(0) ),
                        outcome=row[7],
                        goals_scored=row[8],
                        goals_against=row[9],
                        club_against=Team.objects.get_or_create(name=row[10].title())[0],
                    )
                    print('============')
                    print(obj.matchweek)
                    print('============')

                    results.append(obj)
                    
            save_data = ClubPoint.objects.bulk_create(results)
                    
            
