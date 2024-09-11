import uuid
import datetime

from django.db import models
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.conf import settings

# Create your models here.


class SavedUrl(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=True)
    url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class CustomerPayment(models.Model):
    PLAN = (
        ('basic', 'Basic'),
        ('standard', 'Standard'),
        ('premium', 'Premium'),
    )
    SUBSCRIPTION = (
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(null=True, blank=True)
    date = models.DateTimeField(blank=True)
    transaction_id = models.CharField(max_length=50, null=True, blank=True)
    status = models.BooleanField(default=False)
    credit = models.PositiveIntegerField(null=True, blank=True)
    plan = models.CharField(max_length=50, null=True, choices=PLAN)
    subscription = models.CharField(max_length=50, null=True, choices=SUBSCRIPTION)
    expiry_date = models.DateTimeField(blank=True)

    def __str__(self):
        return f"{self.user} Plan: {self.plan}  Subscription: {self.subscription} Date: {self.date} Expiry Date: {self.expiry_date}"


    def save(self, *args, **kwargs):
        print(self.date)
        date = datetime.datetime.strptime(str(self.date), '%Y-%m-%d %H:%M:%S%z')
        if self.subscription == 'yearly':
            self.expiry_date = date + datetime.timedelta(days=365)
            if self.plan == 'basic':
                self.credit = 10 * 12
            elif self.plan == 'standard':
                self.credit = 100 * 12
            else:
                self.credit = 1000 * 12
        else:
            self.expiry_date = date + datetime.timedelta(days=31)
            
        super(CustomerPayment, self).save(*args, **kwargs)
            
    

class Tournament(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name.title()

    def number_of_team_entry(self):
        entries = Tournament.objects.get(name=self.name)
        return entries.tournament.count()

    def number_of_clubs_entry(self):
        entries = Tournament.objects.get(name=self.name)
        return entries.club_tournament.count()


class BirthYear(models.Model):
    year = models.IntegerField(unique=True)

    class Meta:
        ordering = ['year']

    def __str__(self):
        return self.year

class PlayerNationality(models.Model):
    country = models.CharField(max_length=100, blank=True)
    country_code = models.CharField(max_length=20, unique=True)

    class Meta:
        verbose_name_plural = "Player's Nationalities"

    def __str__(self):
        return self.country_code

class Position(models.Model):
    position = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.position
    
class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    logo = models.ImageField(upload_to='club_logos', null=True, blank=True)
    slug = models.SlugField(default=uuid.uuid4, null=True, blank=True)
    league = models.ForeignKey(Tournament, default=None, null=True, on_delete=models.SET_NULL, related_name='tournament',)

    def __str__(self):
        return self.name.title()

    def get_absolute_url(self):
        # Ensure this value is URL-friendly
        return reverse('team-list-page')

    def club_logo_img(self):
        #for image to appear in admin
        if self.logo:
            return mark_safe(
                '<img src="/media/%s" width="50" height="50" /.>' %(self.logo)
                )
        return None

    @property
    def logo_url(self):
        try:
            url = self.logo.url
        except:
            url = ''
        return url


    def number_of_matches_per_team(self):
        entries = Team.objects.get(name=self.name)
        return entries.Club_against.count()

    @property
    def logo_url(self):
        try:
            url = self.logo.url
        except:
            url = ''
        return url

    class Meta:
        ordering = ['name']

class Player(models.Model):
    first_name = models.CharField(max_length=500)
    last_name = models.CharField(max_length=500, blank=True, null=True)
    other_name = models.CharField(max_length=500, blank=True)
    #club = models.ForeignKey(Team, default=None, null=True, on_delete=models.SET_NULL)
    date_of_birth = models.DateField(blank=True, null=True)
    nationality = models.ForeignKey(PlayerNationality, default=None, null=True, on_delete=models.SET_NULL)
    year_of_birth = models.ForeignKey(BirthYear, default=None, null=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ['first_name','last_name']

    def __str__(self):
        return f'{self.first_name} {self.last_name} {self.other_name}'

    def player_age_month(self):
        if self.date_of_birth:
            age = datetime.date.today()-self.date_of_birth
        return int((age).days/365.25)

    def player_age(self):
        if self.year_of_birth:
            today = datetime.datetime.strptime(datetime.date.today(), '%Y-%m-%d').year
            age = today-self.year_of_birth.year
        return int((age).days/365.25)
            
        """
        today = datetime.date.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        """


class Season(models.Model):
    name = models.CharField(max_length=100)
    year = models.IntegerField()

    class Meta:
        ordering = ['name','year']

    def __str__(self):
        return self.name.title()



class PlayerRecord(models.Model):
    player = models.ForeignKey(Player, default=None, null=True, on_delete=models.SET_NULL)
    season = models.ForeignKey(Season, default=None, null=True, on_delete=models.SET_NULL)
    club = models.ForeignKey(Team, default=None, null=True, on_delete=models.SET_NULL)
    position = models.ForeignKey(Position, default=None, null=True, on_delete=models.SET_NULL)
    age = models.PositiveIntegerField(help_text="Player's age at this particular season")
    match_played = models.PositiveIntegerField()
    starts = models.PositiveIntegerField(help_text='Total number of matches started')
    minutes_played = models.PositiveIntegerField()
    goals = models.PositiveIntegerField()
    assists = models.PositiveIntegerField()
    card_yellow = models.PositiveIntegerField()
    card_red = models.PositiveIntegerField()
    penalty = models.PositiveIntegerField(help_text='Total number of penalties scored')
    goals_assist = models.PositiveIntegerField(help_text='Total number of goals and assits')
    goals_penalty = models.PositiveIntegerField(help_text='Total number of penalties and goals')

    def __str__(self):
        return f'Name: {self.player.first_name} {self.player.last_name} Season: {self.season.name} Goals: {self.goals}'

    class Meta:
        ordering = ['-goals']


class ClubPoint(models.Model):
    GROUND = (
        ('Home', 'Home'),
        ('Away', 'Away'),
        ('Neutral', 'Neutral'),
    )

    OUTCOME = (
        ('W', 'Win'),
        ('D', 'Draw'),
        ('L', 'Lose'),
    )

    MATCHWEEK = (
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
        (6, 6),
        (7, 7),
        (8, 8),
        (9, 9),
        (10, 10),
        (11, 11),
        (12, 12),
        (13, 13),
        (14, 14),
        (15, 15),
        (16, 16),
        (17, 17),
        (18, 18),
        (19, 19),
        (20, 20),
        (21, 21),
        (22, 22),
        (23, 23),
        (24, 24),
        (25, 25),
        (26, 26),
        (27, 27),
        (28, 28),
        (29, 29),
        (30, 30),
        (31, 31),
        (32, 32),
        (33, 33),
        (34, 34),
        (35, 35),
        (36, 36),
        (37, 37),
        (38, 38),
    )

    
    season  = models.ForeignKey(Season, default=None, null=True, on_delete=models.SET_NULL)
    date = models.DateField(blank=True, null=True)
    club = models.ForeignKey(Team, default=None, null=True, on_delete=models.SET_NULL, related_name='Club')
    club_against = models.ForeignKey(Team, default=None, null=True, on_delete=models.SET_NULL, related_name='Club_against')
    tournament = models.ForeignKey(Tournament, default=None, null=True, on_delete=models.SET_NULL, related_name='club_tournament')
    point = models.PositiveIntegerField(blank=True, null=True)
    total_point = models.PositiveIntegerField(blank=True, null=True)
    ground = models.CharField(max_length=50, choices=GROUND)
    outcome = models.CharField(max_length=10, choices=OUTCOME)
    matchweek = models.PositiveIntegerField(blank=True, null=True, choices=MATCHWEEK)
    goals_scored = models.PositiveIntegerField(blank=True, null=True)
    goals_against = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        ordering = ['-date']
        """
        constraints = [
            models.UniqueConstraint(fields=['club', 'club_against', 'date'], name='unique_match'),
        ]
        """

    def __str__(self):
        if self.ground == 'Away':
            return f'{self.club_against}-{self.club} {self.outcome} {self.ground}'
        return f'{self.club}-{self.club_against} {self.outcome} {self.ground}'

    def get_absolute_url(self):
    
        return reverse(
            'goal-analysis-page',
            kwargs={
                'team': self.club.name,
                'slug': self.club.slug,
                'season': self.season.name
            }
        )
    
    def save(self, *args, **kwargs):
        from django.db.models import Sum, F
        from django.db.models.expressions import Window
        from django.db.models.functions import Rank
        
        if self.outcome == 'W' and self.tournament.id == 1:
            self.point = int(3)
        elif self.outcome == 'D' and self.tournament.id == 1:
            self.point = int(1)
        else:
            self.point = int(0)
        
        season_ = ClubPoint.objects.filter(season=self.season, club=self.club, matchweek__lte=self.matchweek).values('season').annotate(total=Sum('point'))
        if season_.exists():
            print('tt', season_)
            season = [f"{item['total']}" for item in season_]
            print('uu', season[0])
            print(season)
            if season == ['None']:
                self.total_point = self.point
                print(self.total_point)
            else:
                self.total_point = season[0]
                print(season[0])
        else:
            pass

        position = ClubPoint.objects.filter(season=self.season).annotate(
            rank=Window(
                expression=Rank(),
                order_by=F('point').desc()
            ),
        )
        print(position)
        
        super(ClubPoint, self).save(*args, **kwargs)

class MatchDay(models.Model):
    touranment = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home_team')
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away_team')
    home_score = models.PositiveIntegerField()
    away_score = models.PositiveIntegerField()
    date = models.DateTimeField()

    def __str__(self):
        return f'{self.home_team.name} {self.home_score} - {self.away_team.name} {self.away_score}'


class MatchDayScorer(models.Model):
    match_day = models.ForeignKey(MatchDay, on_delete=models.CASCADE)
    score = models.PositiveIntegerField()
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.team.name} {self.player.first_name} {self.score}'
    



