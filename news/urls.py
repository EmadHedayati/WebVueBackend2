from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    path('test', views.test, name='test'),
    path('home', views.homeIndex, name='homeIndex'),
    path('leagues', views.LeaguesIndex, name='LeaguesIndex'),
    path('leagues/<int:leagueId>', views.LeaguesGet, name='LeaguesGet'),
    path('matches/<int:matchId>', views.MatchesGet, name='MatchesGet'),
    path('news/<int:newsId>', views.NewsGet, name='NewsGet'),
    path('news/comment', views.NewsComment, name='NewsComment'),
    path('players/<int:playerId>', views.PlayersGet, name='PlayersGet'),
    path('teams/<int:teamId>', views.TeamsGet, name='TeamsGet'),
    path('account/subscribe', views.Subscribe, name='Subscribe'),
    path('account/unsubscribe', views.Unsubscribe, name='Unsubscribe'),

    url('signup', views.signup, name='signup'),
    url('login', views.login, name='login'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.Activate, name='Activate'),
    url(r'^forget-password/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.ForgetPassword, name='ForgetPassword'),
]
