import logging

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

#To run the code enter: python manage.py update_credits

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Adds 10 credits to every user daily'

    def handle(self, *args, **kwargs):
        User = get_user_model()

        users = User.objects.all()
        for user in users:
            user.user_credits += 10
            user.save()

            logger.info(f'Updated {user.username} with 10 credits')
            
        self.stdout.write(self.style.SUCCESS('Successfully updated credits for all users'))



#Using huey

"""
#myproject/huey.py
from huey import RedisHuey

huey = RedisHuey('app')

#settings.py
from myproject.huey import huey

HUEY = huey

#app/tasks.py
import logging

from huey.contrib.djhuey import periodic_task, crontab

from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)

@periodic_task(crontab(minute='0', hour='0')) #Runs at 12:00 AM every day
@periodic_task(crontab(minute='0', hour='0', day_of_week='1,3,5')) #Runs at 12:00 AM on Mon, Wed, Fri
def update_user_credits():
    User = get_user_model()
    users = User.objects.all()
    for user in users:
        user.user_credits += 10
        user.save()
        logger.info(f'Updated {user.username} with 10 credits')
            
    print('Successfully updated credits for all users')
#python manage.py run_huey

"""
