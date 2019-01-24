from django.urls import path
from . import views

urlpatterns = [
    path('test', views.test, name='test'),
    path('home', views.homeIndex, name='homeIndex'),
    path('leagues', views.LeaguesIndex, name='LeaguesIndex'),
    path('leagues/<int:leagueId>', views.LeaguesGet, name='LeaguesGet'),
    path('matches/<int:matchId>', views.MatchesGet, name='MatchesGet'),
    path('news/<int:newsId>', views.NewsGet, name='NewsGet'),
    path('players/<int:playerId>', views.PlayersGet, name='PlayersGet'),
    path('teams/<int:teamId>', views.TeamsGet, name='TeamsGet'),
]
