import string
import random
import csv
import os
import datetime

from django.core.management.base import BaseCommand
from django.conf import settings

from app.models import ClubPoint, Team, Tournament, Season

#To run the code enter: python manage.py load_all_data

class Command(BaseCommand):
    help = 'load data from csv'

    def handle(self, *args, **kwargs):
        data = 'data.csv'
        results = []
        with open(os.path.join(settings.BASE_DIR, 'static/all_data/'+data), 'r', encoding='utf8') as f:
            reader = csv.reader(f)
            #print(reader)
            for i, row in enumerate(reader):
                if i == 0:
                    pass
                else:
                    match_year = datetime.datetime.strptime(str(row[2]), '%Y-%m-%d').year
                    
                    obj = ClubPoint(
                        date=row[2],
                        club=Team.objects.get_or_create(name=row[9])[0],
                        season=Season.objects.get_or_create(name=row[10], year=match_year)[0],
                        tournament=Tournament.objects.get_or_create(name=row[11])[0],
                        ground=row[8],
                        matchweek=row[0],
                        outcome=row[1],
                        goals_scored=row[6],
                        goals_against=row[5],
                        club_against=Team.objects.get_or_create(name=row[7].title())[0],
                    )

                    results.append(obj)
                    
            save_data = ClubPoint.objects.bulk_create(results)
                    
            
