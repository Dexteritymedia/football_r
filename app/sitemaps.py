from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.db.models import Q

from .models import Team, ClubPoint


class TeamListSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8
    #protocol = 'http'

    def items(self):
     #return Team.objects.all()
     return ['pl-team-list-page']

    def location(self, item):
        return reverse(item)


class TeamSitemap(Sitemap):

    changefreq = "daily"
    priority = 0.8

    def items(self):
        # Assuming you have a method to fetch episodes
        #return ClubPoint.objects.all()
        contents = ClubPoint.objects.filter(Q(club__league__name='Premier League')).values_list('club', flat=True).order_by('club').distinct()
        print(contents)
        print(len(ClubPoint.objects.filter(Q(club__league__name='Premier League'))))
        return ClubPoint.objects.filter(Q(club__league__name='Premier League'))


class StaticSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8
    #protocol = 'https'

    def items(self):
        return ['match-search', 'team-goal-search', 'home', 'dist-goal-search', 'pl-team-list-page', 'match-goal-search']

    def location(self, item):
        return reverse(item)


"""
import itertools

class TeamSitemap(Sitemap):
    # List method names from your objects that return the absolute URLs here
    FIELDS = ("get_absolute_url", "get_about_url", "get_teachers_url")

    changefreq = "weekly"
    priority = 0.6

    def items(self):
        # This will return you all possible ("method_name", object) tuples instead of the
        # objects from the query set. The documentation says that this should be a list 
        # rather than an iterator, hence the list() wrapper.
        return list(itertools.product(TeamSitemap.FIELDS,
                                      ClubPoint.objects.filter(Q(club__league__name='Premier League'))
                                      )
                    )

    def location(self, item):
        # Call method_name on the object and return its output
        return getattr(item[1], item[0])()
"""
