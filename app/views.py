import csv
import json

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout, login, authenticate
from django.contrib import messages
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import Http404, HttpResponse, HttpResponseForbidden, JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.utils.safestring import mark_safe
from django.core.paginator import Paginator
from django.views.generic import TemplateView, View, DetailView
from django.views.generic.edit import FormMixin
from django.urls import reverse
from django.db.models import Q
from django.core import serializers
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Sum, F, Count, Func, Window, Avg, Max, Min
from django.urls import reverse

import pandas as pd

from .models import *
from .forms import *

User = get_user_model()

# Create your views here.

def sample_pages(request):
    context = {}
    template_name = 'sample_pages/payment_page.html'
    return render(request, template_name, context)

def home(request):
    context = {}
    return render(request, 'app/index.html', context)


@login_required
def confirm_plan(request):
    if request.method == "POST":
        plan = request.POST.get('plan')
        price = request.POST.get('price')
        credit_score = request.POST.get('credit_score')
        print(plan, price, credit_score)

        if plan == "standard-monthly":
            credit_score = 10
        elif plan == "premium-monthly":
            credit_score = 50
        elif plan == "enterprise-monthly":
            credit_score = 100

        # Update the user's credit score (you can adjust the user model or use another approach)
        """
        request.user.profile.credit_score = credit_score
        request.user.profile.save()
        """

        request.user.user_credits += int(credit_score)
        request.user.save()

        return JsonResponse({
            "message": f"Plan {plan} selected. Credit score updated to {credit_score}.",
            'plan': plan,
            'price': price,
            'credit_score': credit_score
        })
    else:
        return JsonResponse({"error": "Invalid request."}, status=400)

@login_required(login_url="account_login")
def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    print(user)
    if user != request.user:
        return HttpResponseForbidden()
    saved_urls = SavedUrl.objects.filter(user=user).order_by('-created_at')
    
    paginator = Paginator(saved_urls, 2)  # Show 10 items per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    """
    if request.htmx:  # Check if the request is an HTMX request
        return render(request, 'partials/user_page.html', {'contents': page_obj})
    return render(request, 'app/user_page.html', {'user':user, 'contents': page_obj})
    """
    return render(request, 'partials/user_page_infinite_scroll.html', {'user':user, 'contents':page_obj})


def payment_page(request):
    context = {}
    #return render(request, 'payments/payment_page.html', context)
    return render(request, 'app/payment_page.html', context)

def success(request):
    return render(request, 'payments/success.html')

def error(request):
    return render(request, 'payments/error.html')


def team_list_page(request):
    #teams = Team.objects.all()
    teams = Team.objects.filter(Q(league__name='Premier League'))
    #teams = Team.objects.filter(Q(league__name='Premier League')| Q(league__name='La Liga')| Q(league__name='Bundesliga'))
    latest_season = Season.objects.last()
    context = {'teams': teams, 'season':latest_season}
    return render(request, 'app/team_list.html', context)


def brazilian_league_team_list_page(request):
    teams = Team.objects.filter(Q(league__name='Premier League')| Q(league__name='La Liga')| Q(league__name='Bundesliga'))
    latest_season = Season.objects.last()
    context = {'teams': teams, 'season':latest_season}
    return render(request, 'app/brazilian_league_team_list.html', context)


def team_goal_chart(request, team, season):
    labels = []
    data = []

    goal_diff_labels = []
    goal_diff_data = []

    queryset = ClubPoint.objects.filter(
        club__name=team.title(),
        season__name=season,
        tournament__name='Premier League',
        ).annotate(
            cumbalance=Window(Sum('goals_scored'), order_by=F('matchweek').asc())
            ).order_by('matchweek').distinct()


    goal_diff = ClubPoint.objects.filter(
        club__name=team.title(), tournament__name='Premier League', season__name=season,).annotate(
            gd=Sum(F('goals_scored')-F('goals_against')), order_by=F('matchweek')
        )
    

    #print(goal_diff)

    """
    for entry in queryset:
        labels.append(entry.matchweek)
        data.append(entry.cumbalance)

    """

    try:
        for entry in goal_diff:
            labels.append(entry.matchweek)
            data.append(entry.gd)

        
        dat={
            'labels': labels,
            'data': data,
        }

        combined = list(zip(dat['labels'], dat['data']))
        sorted_combined = sorted(combined, key=lambda item: item[0], reverse=True)
        sorted_labels, sorted_data = zip(*sorted_combined)
        sorted_dict = {"labels": list(sorted_labels), "data": list(sorted_data)}
        print(sorted_dict)
        
        print('LABELS', labels, 'DATA', data)
        
        return JsonResponse(data={
            'labels': list(sorted_labels),
            'data': list(sorted_data),
        })
    except:
        return JsonResponse(data={})


def team_goal_analysis_page(request, team, slug, season):
    team = get_object_or_404(Team, name=team, slug=slug)
    #season = Season.objects.get(name=season, year=2024)
    current_season = season
    #print(current_season)
    all_seasons = Season.objects.all().exclude(name=season).values_list('name', flat=True).order_by('-name').distinct()
    #print(list(all_seasons))
    #last_five_seasons = all_seasons[:5]

    all_seasons_ = list(Season.objects.all().values_list('name', flat=True).order_by('-name').distinct())
    print(all_seasons_)
    selected_season = all_seasons_.index(current_season)
    print(selected_season)
    start_index = max(0, selected_season - 5)
    end_index = min(len(all_seasons_), selected_season + 6)
    print(start_index)
    print(end_index)
    next_five_years = all_seasons_[selected_season + 1:end_index]
    previous_five_years = all_seasons_[start_index:selected_season]
    print(previous_five_years)
    print(next_five_years)
    


    last_five_seasons_goals = []
    for prev_season in previous_five_years:
        total_goals = ClubPoint.objects.filter(club__name=team, tournament__name='Premier League', season__name=prev_season).aggregate(gs=Sum('goals_scored'), gc=Sum('goals_against'))
        last_five_seasons_goals.append(total_goals)
        
    prev_seasons_results = zip(previous_five_years, last_five_seasons_goals)


    next_five_seasons_goals = []
    for next_season in next_five_years:
        total_goals = ClubPoint.objects.filter(club__name=team, tournament__name='Premier League', season__name=next_season).aggregate(gs=Sum('goals_scored'), gc=Sum('goals_against'))
        next_five_seasons_goals.append(total_goals)
        
    next_seasons_results = zip(next_five_years, next_five_seasons_goals)
    
    team_data = ClubPoint.objects.filter(club__name=team, tournament__name='Premier League', season__name=season)
    team_season = team_data.values_list('date__year', flat=True).order_by('date__year').distinct()
    #print(team_season)
    
    queryset = Q()
    #queryset = Q(tournament__name='Premier League')| Q(tournament__name='La Liga')
    
    total_goals_scored = ClubPoint.objects.filter(club__name=team, tournament__name='Premier League', season__name=season).aggregate(gs=Sum('goals_scored'), gc=Sum('goals_against'))
    total_home_goals_scored = ClubPoint.objects.filter(club__name=team, tournament__name='Premier League', ground='Home', season__name=season).aggregate(gs=Sum('goals_scored'), gc=Sum('goals_against'))
    total_away_goals_scored = ClubPoint.objects.filter(club__name=team, tournament__name='Premier League', ground='Away', season__name=season).aggregate(gs=Sum('goals_scored'), gc=Sum('goals_against'))
    total_clean_sheet = ClubPoint.objects.filter(club__name=team, tournament__name='Premier League', season__name=season, goals_against=0).aggregate(gc=Count('goals_against'))
    max_min_goal = ClubPoint.objects.filter(club__name=team, tournament__name='Premier League', season__name=season).aggregate(gs=Max('goals_scored'), gc=Max('goals_against'))
    average_goal = ClubPoint.objects.filter(club__name=team, tournament__name='Premier League', season__name=season).aggregate(gs=Avg('goals_scored'), gc=Avg('goals_against'))
    print('Avg', average_goal)
    
    goal_diff = ClubPoint.objects.filter(
        club__name=team, tournament__name='Premier League', season__name=season,).annotate(
            gd=Sum(F('goals_scored')-F('goals_against')), order_by=F('matchweek')
        )
    total_goal_diff = goal_diff.aggregate(total=Sum('gd'))
    #print(total_goal_diff)
    
    cumulative_goals = ClubPoint.objects.filter(
        club__name=team,
        season__name=season,
        tournament__name='Premier League',
        ).annotate(
            cumbalance=Window(Sum('goals_scored'), order_by=F('matchweek').asc())
            ).order_by('matchweek')
    """
    annotate(
        cumsum=Func(
        Sum('goals_scored'),
        template='%(expressions)s OVER (ORDER BY %(order_by)s)',
        order_by="matchweek"
        )
    ).values('matchweek', 'cumsum').order_by('matchweek', 'cumsum')
    """
    
    value_list = ClubPoint.objects.filter(
        club__name=team,
        season__name=season,
        tournament__name="Premier League"
        ).values_list('club_against__name', flat=True).order_by('club_against').distinct()

    #print(value_list)
    group_by_value = {}
    for value in value_list:
        group_by_value[value] = team_data.filter(club_against__name=value).order_by('ground').distinct()

    #team_groupby = team_data.values('outcome').annotate(match_outcome=Count('outcome'))

    #print('Team', group_by_value)

    team_value_list = team_data.values_list('outcome', flat=True).order_by('outcome').distinct()

    group_by_team_value = {}
    for value in team_value_list:
        group_by_team_value[value] = team_data.filter(outcome=value)

    data = ClubPoint.objects.filter(Q(club__league__name='Premier League')).order_by('club').distinct()
    

    team_home_games = team_data.filter(ground='Home').values_list('outcome', flat=True).order_by('outcome').distinct()

    group_by_team_home_games = {}
    for value in team_home_games:
        group_by_team_home_games[value] = team_data.filter(ground='Home').filter(outcome=value)


    team_away_games = team_data.filter(ground='Away').values_list('outcome', flat=True).order_by('outcome').distinct()

    group_by_team_away_games = {}
    for value in team_away_games:
        group_by_team_away_games[value] = team_data.filter(ground='Away').filter(outcome=value)


    df = pd.DataFrame(
        ClubPoint.objects.filter(
        club__name=team,
        season__name=season,
        tournament__name="Premier League"
        ).values_list('club_against__name','outcome','goals_scored','goals_against','matchweek','ground', 'club_against__slug').order_by('club_against'),

        columns=['Opponent','Outcome','Goals Scored','Goals Against','MatchWeek','Ground', 'Slug']
    )

    print(df)

    df_h = df.groupby([df['Opponent'], df['Slug']])[['Goals Against','Goals Scored']].agg(['sum'])
    print(df_h)

    print(df_h.values.tolist())
    df_h.reset_index(inplace=True)

    df_h['GA%'] = (df_h['Goals Against','sum']/df_h['Goals Against','sum'].sum()).round(3)*100
    df_h['GS%'] = (df_h['Goals Scored','sum']/df_h['Goals Scored','sum'].sum()).round(3)*100
    
    print(df_h)
    print(df_h.values.tolist())
    print(df_h.info())

    print(df[['Goals Against','Goals Scored']].describe())
    print(df_h['Goals Scored','sum'].mean())
    print(df_h['Goals Against','sum'].mean())
    print(df['Goals Scored'].mean())
    print(df['Goals Against'].mean())
    print('Avg', average_goal)
    print(df['Slug'].unique())

    context = {
        'team_goal_analysis': df_h.values.tolist(),
        'average_goal_scored': df['Goals Scored'].mean(),
        'average_goal_conceded': df['Goals Against'].mean(),
        'team_data':team_data,
        'team':team,
        'current_season': current_season,
        'season':team_season,
        'clean_sheet': total_clean_sheet,
        'max_min_goal': max_min_goal,
        'seasons': all_seasons,
        'prev_seasons': previous_five_years,
        'prev_five_seasons_goals': last_five_seasons_goals,
        'prev_seasons_results': prev_seasons_results,
        'next_five_years': next_seasons_results,
        
        'goals_scored':total_goals_scored,
        'home_goals_scored': total_home_goals_scored,
        'away_goals_scored': total_away_goals_scored,
        'goal_diff':goal_diff,
        'c_goals':cumulative_goals,
        
        'group_by_value':group_by_value,
        'value_list':value_list,
        
        #'team_groupby': team_groupby,
        
        'team_value_list': team_value_list,
        'group_by_team_value': group_by_team_value,

        'group_by_team_home_games': group_by_team_home_games,
        'group_by_team_away_games': group_by_team_away_games,
        
        #'goals_conceded':goals_conceded
    }

    return render(request, 'app/goal_analysis.html', context)


def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="data.csv"'

    writer = csv.writer(response)
    writer.writerow(['Matchweek', 'Outcome', 'Date', 'Point', 'Total point',
        'Goals against', 'Goals scored', 'Club against', 'Ground',
        'Club','Season', 'Tournament'])

    data = ClubPoint.objects.all().values_list(
        'matchweek', 'outcome', 'date', 'point', 'total_point',
        'goals_against', 'goals_scored', 'club_against__name', 'ground',
        'club__name','season__name', 'tournament__name'
    )
    for obj in data:
        writer.writerow(obj)

    return response


class GoalDistView(View):
    query = None
    results = []
    form_class = GoalDistForm

    def get(self, request):
        form = self.form_class(request.GET)
        save_url = SavedUrlForm(url=request.build_absolute_uri())
        if form.is_valid():
            club = form.cleaned_data.get('club', None)
            ground = form.cleaned_data['ground']
            date = form.cleaned_data['date']
            tournament = form.cleaned_data['tournament']
            print(ground)
            print(request.build_absolute_uri())

            query = Q()

            query &= Q(club=club)

            if tournament and tournament != "null":
                query &= Q(tournament=tournament)

            if ground and ground != "null":
                query &= Q(ground=ground)

            if date and date != "null":
                query &= Q(date__gte=date)

            print('Username:', request.user.username)
            try:
                user = User.objects.get(username=request.user.username)
                
                #user.user_credits = 100
                #user.save()
                
                if user.user_credits <= 0:
                    payment_url = reverse('payment-page')
                    messages.warning(request, mark_safe(
                        f'You are out of credit today! Please come back tomorrow to receive free 10 credits or you can get unlimited credits by making a payment <a href="{payment_url}" target="_blank">here</a>'
                    ))
                    return redirect('dist-goal-search')
                else:
                    user.user_credits -= 1
                    user.save()
            except User.DoesNotExist:
                login_url = reverse('account_login')
                messages.warning(request, mark_safe(
                    f'You need to <a href="{login_url}">login</a> to use this!'
                ))
                return redirect('dist-goal-search')
    

            df = pd.DataFrame(
                ClubPoint.objects.filter(query).all().
                values_list('season__name', 'club_against__name','outcome','goals_scored','goals_against','matchweek','ground').order_by('club_against'),
                columns=['Season', 'Opponent','Outcome','Goals Scored','Goals Against','MatchWeek','Ground']
            )

            print(df)

            df_h = df.groupby(df['Opponent'])[['Goals Against','Goals Scored']].agg(['sum'])
            df_h['GA%'] = (df_h['Goals Against','sum']/df_h['Goals Against','sum'].sum()).round(3)*100
            df_h['GS%'] = (df_h['Goals Scored','sum']/df_h['Goals Scored','sum'].sum()).round(3)*100
            df_h['GD'] = (df_h['Goals Scored','sum'] - df_h['Goals Against','sum'])

            df_h.reset_index(inplace=True)
            #df_h.sort_values(by=[, 'col2'], ascending=False, inplace=True)

            print(df_h)
            print(df_h.values.tolist())

            context = {
                'club': club,
                'ground': ground,
                'date': date,
                'tournament': tournament,
                'no_of_teams': df_h['Opponent'].count(),
                'total_goals_conceded': df_h['Goals Against','sum'].sum(),
                'total_goals_scored': df_h['Goals Scored','sum'].sum(),
                'results': df_h.values.tolist(),
                'save_url': save_url,
            }

            return render(request, 'app/goal_distribution_result_page.html', context)
        else:
            return render(request, 'app/goal_distribution_page.html', {'form':form})

        return render(request, 'app/goal_distribution_page.html', {'form': form})

    def post(self, request):
        url = request.POST.get('url')
        name = request.POST.get('name', None)

        if url:
            saved_url = SavedUrl()
            saved_url.user = request.user
            saved_url.url = url
            saved_url.name = name
            saved_url.save()
        
            user_account_url = reverse('user_profile', kwargs={'username':saved_url.user.username})
            print(user_account_url)
            #return redirect('user_profile', saved_url.user.username)
            messages.info(request, mark_safe(
                'You have successfully saved this! <a href="{user_account_url}" target="_blank">Profile</a>'
            ))
            return HttpResponseRedirect(request.get_full_path())
        else:
            messages.info(request, mark_safe(
                f"You can't save this! because"
            ))
        return self.get(request)

class SearchGoalMatchView(View):
    query = None
    results = []
    form_class = SearchGoalMatchForm

    def get(self, request):
        form = self.form_class(request.GET)
        if form.is_valid():
            club = form.cleaned_data.get('club', None)
            no_of_goals = form.cleaned_data['no_of_goals']
            goals = form.cleaned_data['goals']
            ground = form.cleaned_data['ground']

            print(goals)

            query = Q()

            query &= Q(club=club)

            if ground and ground != "null":
                query &= Q(ground=ground)

            if goals == 'GF':
                df = pd.DataFrame(
                    ClubPoint.objects.filter(query).filter(tournament__name='Premier League').all().
                    values_list('season__name', 'club_against__name','outcome','goals_scored','matchweek','ground').order_by('club_against'),
                    columns=['Season', 'Opponent','Outcome','Goals Scored','MatchWeek','Ground']
                )

                df.sort_values(['Season','MatchWeek'], ascending=True, inplace=True)

                df_h = df.groupby(df['Season'])['Goals Scored'].agg(['sum'])

                df_matchweek = df.groupby(df['Season'])['MatchWeek'].count()

                print(df_h)
                print(df_matchweek)

                dff = df.groupby("Season").apply(
                    lambda x: x.assign(
                        cumu=(
                            val := 0,
                            *(
                                val := val + v if val < int(no_of_goals) else (val := 0)
                                for v in x["Goals Scored"][1:]
                            ),
                        )
                    ),
                )
            else:
                df = pd.DataFrame(
                    ClubPoint.objects.filter(query).filter(tournament__name='Premier League').all().
                    values_list('season__name', 'club_against__name','outcome','goals_against','matchweek','ground').order_by('club_against'),
                    columns=['Season', 'Opponent','Outcome','Goals Against','MatchWeek','Ground']
                )
                df.sort_values(['Season','MatchWeek'], ascending=True, inplace=True)
                print(df)

                df_h = df.groupby(df['Season'])['Goals Against'].agg(['sum'])

                df_matchweek = df.groupby(df['Season'])['MatchWeek'].count()

                print(df_h)
                print(df_matchweek)

                dff = df.groupby("Season").apply(
                    lambda x: x.assign(
                        cumu=(
                            val := 0,
                            *(
                                val := val + v if val < int(no_of_goals) else (val := 0)
                                for v in x["Goals Against"][1:]
                            ),
                        )
                    ),
                )

                
            print(dff)
            df_k = dff.groupby([dff['cumu'] == int(no_of_goals), dff['Season']])
            results = pd.DataFrame(df_k.size().reset_index(name = "Group_Count"))
            print(results)
            data = results.loc[(results['cumu'] == True )]
            
            #dff = dff.groupby(dff['Season'])['cumu'].sum()
            #print(dff)
            #df.groupby([(df['Date'].dt.year)])[' Close'].agg(['first','last','count'])

            df_h.reset_index(inplace=True)

    
            
            context = {
                'club': club,
                'goals': goals,
                'no_of_goals': no_of_goals,
                'ground': ground,
                'table': data.values.tolist(),
                'results': dff.values.tolist(),
            }

            return render(request, 'app/goal_match_result_page.html', context)
            
        else:
            return render(request, 'app/goal_match_page.html', {'form':form})

        return render(request, 'app/goal_match_page.html', {'form': form})



class MatchDayToReachGoals(View):
    query = None
    results = []
    form_class = SearchGoalMatchForm

    def get(self, request):
        form = self.form_class(request.GET)
        if form.is_valid():
            club = form.cleaned_data.get('club', None)
            no_of_goals = form.cleaned_data['no_of_goals']
            goals = form.cleaned_data['goals']
            ground = form.cleaned_data['ground']

            print(goals)

            query = Q()

            query &= Q(club=club)

            if ground and ground != "null":
                query &= Q(ground=ground)

            if goals == 'GF':
                df = pd.DataFrame(
                    ClubPoint.objects.filter(query).filter(tournament__name='Premier League').all().
                    values_list('season__name', 'club_against__name','outcome','goals_scored','matchweek','ground').order_by('club_against'),
                    columns=['Season', 'Opponent','Outcome','Goals Scored','MatchWeek','Ground']
                )

                df.sort_values(['Season','MatchWeek'], ascending=True, inplace=True)

                df['CumulativeGoals'] = df.groupby('Season')['Goals Scored'].cumsum()
                df_results = df[df['CumulativeGoals'] >= int(no_of_goals)].groupby('Season').first().reset_index()
                df_results = df_results[['Season','MatchWeek']].rename(columns={'Matchday': f'MatchdayToReach {no_of_goals} Goals'})
                
            else:
                df = pd.DataFrame(
                    ClubPoint.objects.filter(query).filter(tournament__name='Premier League').all().
                    values_list('season__name', 'club_against__name','outcome','goals_against','matchweek','ground').order_by('club_against'),
                    columns=['Season', 'Opponent','Outcome','Goals Against','MatchWeek','Ground']
                )
                df.sort_values(['Season','MatchWeek'], ascending=True, inplace=True)


                df['CumulativeGoals'] = df.groupby('Season')['Goals Against'].cumsum()
                df_results = df[df['CumulativeGoals'] >= int(no_of_goals)].groupby('Season').first().reset_index()
                df_results = df_results[['Season','MatchWeek']].rename(columns={'MatchWeek': f'MatchdayToConcede {no_of_goals} Goals'})

            print(df_results)
            
            context = {
                'club': club,
                'goals': goals,
                'no_of_goals': no_of_goals,
                'ground': ground,
                'table': df_results.values.tolist(),
                #'results': df_results.values.tolist(),
            }

            return render(request, 'app/match-reach-goal-result-page.html', context)
            
        else:
            return render(request, 'app/match-reach-goal.html', {'form':form})

        return render(request, 'app/match-reach-goal.html', {'form': form})



class TeamSearchGoalView(View):
    query = None
    results = []
    form_class = TeamGoalForm

    def get(self, request):
        form = self.form_class(request.GET)
        if form.is_valid():
            club = form.cleaned_data.get('club', None)
            no_of_goals = form.cleaned_data['no_of_goals']
            goals = form.cleaned_data['goals']
            date = form.cleaned_data['date']
            print(goals)

            print(club)
            
            query = Q()

            if date and date != "null":
                query &= Q(date__gte=date)

                

            #value_list = ClubPoint.objects.filter(club=club, goals_scored=int(no_of_goals)).filter(query).values_list('outcome', flat=True).order_by('outcome').distinct()
            group_by_value = {}
            if goals == 'GF':
                value_list = ClubPoint.objects.filter(club=club, goals_scored=int(no_of_goals)).filter(query).values_list('outcome', flat=True).order_by('outcome').distinct()
                for value in value_list:
                    group_by_value[value] = ClubPoint.objects.filter(club=club, goals_scored=int(no_of_goals), outcome=value).filter(query)
            else:
                value_list = ClubPoint.objects.filter(club=club, goals_against=int(no_of_goals)).filter(query).values_list('outcome', flat=True).order_by('outcome').distinct()
                for value in value_list:
                    group_by_value[value] = ClubPoint.objects.filter(club=club, goals_against=int(no_of_goals), outcome=value).filter(query)
            print('value', value_list)
            """
            if goals == 'GF':
                for value in value_list:
                    group_by_value[value] = ClubPoint.objects.filter(club=club, goals_scored=int(no_of_goals), outcome=value).filter(query)
            else:
                for value in value_list:
                    group_by_value[value] = ClubPoint.objects.filter(club=club, goals_against=int(no_of_goals), outcome=value).filter(query)
            """   

            print(group_by_value)

            return render(request, 'app/team_goals_result_page.html', {'results': group_by_value, 'club':club, 'goals':no_of_goals, 'goal_type':goals, 'date':date})
            
        else:
            return render(request, 'app/team_search_goal.html', {'form':form})

        return render(request, 'app/team_search_goal.html', {'form': form})


class SearchMatchView(View):
    query = None
    results = []
    form_class = MatchForm

    def get(self, request):
        form = self.form_class(request.GET)
        form.fields['outcome'].initial = None
        if form.is_valid():
            club = form.cleaned_data.get('club', None)
            matchweek = form.cleaned_data['matchweek']
            outcome = form.cleaned_data['outcome']
            ground = form.cleaned_data.get('ground', None)
            opponent = form.cleaned_data.get('opponent', None)
            tournament = form.cleaned_data['tournament']
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']

            print(club)
            print(matchweek)
            print(outcome)
            print(start_date)
            print(end_date)
            print(ground)
            print(opponent)
            print(tournament)

            query = Q()

            query &= Q(date__range=(start_date, end_date))

            if club and club != "null":
                query &= Q(club=club)
            
            if matchweek and matchweek != "null":
                query &= Q(matchweek=matchweek)

            if outcome and outcome != "null":
                query &= Q(outcome=outcome)

            if tournament and tournament != "null":
                query &= Q(tournament=tournament)

            if opponent and opponent != "null":
                query &= Q(club_against__name=opponent)
                print('Opponent', query)

            if ground and ground != "null":
                query &= Q(ground=ground)

            print(query)

            results = ClubPoint.objects.filter(query).all()
            #print(results)
            #print(str(results.query))

            groupby = ClubPoint.objects.filter(query).values('outcome').annotate(match_outcome=Count('outcome'))
            print(groupby)

            value_list = ClubPoint.objects.filter(query).values_list('outcome', flat=True).order_by('outcome').distinct()
            print(value_list)

            group_by_value = {}
            for value in value_list:
                group_by_value[value] = ClubPoint.objects.filter(query).filter(outcome=value)

            print(type(group_by_value))

            """
            qs = (
                ClubPoint.objects.filter(query)
                .select_related("b", "c", "d")  # This is the join. You'll need to use the reverse-lookups, forward-lookups
                .values("b__name", "d__id") # This will produce a group by
                .annotate(Sum(all_data="all_data"), Sum(today_data="today_data")  # This is the aggregation part
                          .values("standard_name")  # Here put all the other fields
                          .order_by("b__type", "b__name")  # finally the order by
                          )
                )
            """

            paginator = Paginator(results, 10)

            page = request.GET.get('page')
            page_obj = paginator.get_page(page)
            try:
                posts = paginator.page(page)
            except PageNotAnInteger:
                posts = paginator.page(1)
            except EmptyPage:
                posts = paginator.page(paginator.num_pages)

            return render(request, 'app/match_result_page.html', {
                'results': group_by_value, 'page_obj': page_obj, 'club':club,
                'opponent':opponent, 'tournament':tournament, 'start_date': start_date, 'end_date':end_date,
                })
            """
            if request.user.is_authenticated:
                return render(request, 'app/match_result_page.html', {'results': results})
            else:
                request.session['results'] = serializers.serialize('json', list(results))
                return redirect('result-page')
            """
        else:
            return render(request, 'app/match_search.html', {'form':form})

        return render(request, 'app/match_search.html', {'form': form})


def result_page(request):
    if 'results' in request.session:
        context = {}
        context['results'] = request.session['results']
        print(context['results'])
        return render(request, 'app/match_result_page.html', context)
    
    return render(request, 'app/match_result_page.html')


def update_data(request):
    #update_club = ClubPoint.objects.filter(club__name='Chelsea').update(club=Team.objects.get_or_create(name='Tottenham')[0])

    #update_all = ClubPoint.objects.filter(club_against__name='Eng Arsenal').update(club_against=Team.objects.get_or_create(name='Arsenal')[0])

    return export_csv(request)

def filter_data(request):
    start_date = '2000-08-19'
    end_date = '2005-05-15'
    filter_club = ClubPoint.objects.filter(club__name='Chelsea', date__range=(start_date, end_date))
    print(filter_club.count())
    print(len(filter_club))

    season = Season.objects.all().values()
    print(season.count())

    #club_season = ClubPoint.objects.filter(club__name='Chelsea', )

    return HttpResponse("Done")


def delete_certain_data(request):
    start_date = '2000-08-19'
    end_date = '2005-05-15'
    filter_club = ClubPoint.objects.all()
    #filter_club = ClubPoint.objects.filter(club__name='Manchester City').all()
    print(filter_club.count())
    print(len(filter_club))

    #filter_club.delete()

    return HttpResponse("Done")


#####
def searchform(request):
    if request.method == "POST":
        form = MatchForm(request.POST)
        if form.is_valid():
            club = form.cleaned_data['club']
            matchweek = form.cleaned_data['matchweek']
            outcome = form.cleaned_data['outcome']
            print(outcome)
            results = ClubPoint.objects.filter(club__name=club, matchweek=int(matchweek), outcome=outcome)
            print(results)
            return render(request, 'app/match_search_page.html', {'results': results})
    else:
        form = MatchForm()
            
    return render(request, 'app/match_search_page.html', {'form': form})

def search_page(request):
    form = AllClubForm()
    #url = reverse('')
    #url_with_params = 
    #return HttpResponseRedirect(url_with_params)
    return render(request, 'app/search_page.html', {'form': form})

class ClubDetailView(FormMixin, DetailView):
    model = Team
    slug_field = "slug"
    context_object_name = 'club'
    template_name = 'app/club_detail.html'
    pk_url_kwarg = "pk"
    slug_url_kwarg = 'slug'
    query_pk_and_slug = True
    form = MatchForm

    def get_context_data(self, **kwargs):
        context = super(ClubDetailView, self).get_context_data(**kwargs)
        #context['form'] = MatchForm(request.GET)
        return context

    """
    def get(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            try:
                club = form.cleaned_data['club']
                matchweek = form.cleaned_data['matchweek']
                outcome = form.cleaned_data['outcome']
                results = ClubPoint.objects.filter(club__name=club[0], matchweek=int(matchweek), outcome=outcome).order_by('-total_point')
                print(results)
                return render(request, 'app/match_search.html', {'form': form, 'results':results})
            except:
                
                return HttpResponse("None")

        return render(request, 'app/match_search.html', {'form': form})
    """
class SearchView(View):
    query = None
    results = []
    form_class = ClubPointForm

    def get(self, request):
        form = self.form_class(request.GET)
        if form.is_valid():
            try:
                season = form.cleaned_data['season']
                matchweek = form.cleaned_data['matchweek']
                results = ClubPoint.objects.filter(season__name=season[0], matchweek=int(matchweek)).order_by('-total_point')
                print(results)
                return render(request, 'app/search.html', {'form': form, 'results':results})
            except:
                return HttpResponse("None")

        return render(request, 'app/search.html', {'form': form})
