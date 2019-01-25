import datetime

from django.db.models import Q
from django.http import JsonResponse
from news.models import *


# Create your views here.


def test(request):
    result = {
        "users": [item.toJson() for item in NewsUser.objects.all()],
        "teams": [item.toJson() for item in Team.objects.all()],
        "leagues": [item.toJson() for item in League.objects.all()],
        "matchStatistics": [item.toJson() for item in MatchStatistic.objects.all()],
        "statistics": [item.toJson() for item in Statistic.objects.all()],
        "stadiums": [item.toJson() for item in Stadium.objects.all()],
        "matches": [item.toJson() for item in Match.objects.all()],
        "events": [item.toJson() for item in Event.objects.all()],
        "tags": [item.toJson() for item in Tag.objects.all()],
        "news": [item.toJson() for item in News.objects.all()],
        "comments": [item.toJson() for item in Comment.objects.all()],
        "players": [item.toJson() for item in Player.objects.all()],
        "newsTags": [item.toJson() for item in NewsTag.objects.all()],
    }
    return JsonResponse(result, safe=False)


def getNewsRelatedToAccount(model):
    # todo: implement this
    return [item.toJson() for item in News.objects.all()[:3]]


def getSliderNews():
    # todo: implement this
    return [item.toJson() for item in News.objects.all()[:5]]


def getLatestNews():
    return [item.toJson() for item in News.objects.all()[:3]]


def getNews(model):
    if isinstance(model, News):
        return [item.toJson() for item in News.objects.all().filter(author=model.author)[:3]]
    if isinstance(model, User):
        # todo: query favourite news for user
        return [item.toJson() for item in News.objects.all()[:3]]
    return getNewsRelatedToAccount(model)


def homeIndex(request):
    result = {
        "sliderNewsList": getSliderNews(),
        "latestNewsList": getLatestNews(),
        "favouriteNewsList": getLatestNews(),  # todo: find user from request
        "footballMatchList": {
            "latest": [item.toJson() for item in Match.objects.all().filter(type='Football')[:6]],
            "favourites": [item.toJson() for item in Match.objects.all().filter(type='Football')[:6]],
            # todo: find user from request
        },
        "basketballMatchList": {
            "latest": [item.toJson() for item in Match.objects.all().filter(type='Basketball')[:6]],
            "favourites": [item.toJson() for item in Match.objects.all().filter(type='Basketball')[:6]],
            # todo: find user from request
        },
    }
    return JsonResponse(result, safe=False)


def LeaguesIndex(request):
    result = {}
    if request.GET.get('q'):
        result = {
            "upcomingLeagueList": [item.toJson() for item in League.objects.all().filter(
                    startDate__gt=datetime.date.today(), title__exact=request.GET.get('q'))],
            "finishedLeagueList": [item.toJson() for item in League.objects.all().filter(
                    finished=True, title__exact=request.GET.get('q'))],
        }
    else:
        result = {
            "upcomingLeagueList": [item.toJson() for item in
                                   League.objects.all().filter(startDate__gt=datetime.date.today())],
            "finishedLeagueList": [item.toJson() for item in League.objects.all().filter(finished=True)],
        }
    return JsonResponse(result, safe=False)


def LeaguesGet(request, leagueId):
    league = League.objects.get(id=leagueId)
    result = {
        "league": league.toJson(),
    }
    return JsonResponse(result, safe=False)


def MatchesGet(request, matchId):
    match = Match.objects.get(id=matchId)
    result = {
        "match": match.toJson(),
        "latestNewsList": getNews(match),
    }
    return JsonResponse(result, safe=False)


def NewsGet(request, newsId):
    news = News.objects.get(id=newsId)
    result = {
        "news": news.toJson(),
        "relatedNewsList": getNews(news),
    }
    return JsonResponse(result, safe=False)


def PlayersGet(request, playerId):
    player = Player.objects.get(id=playerId)

    eventListDict = dict()
    for event in Event.objects.all().filter(player=player):
        if event.title in eventListDict:
            eventListDict[event.title] += 1
        else:
            eventListDict[event.title] = 1

    statisticsTableRowList = [{
        "banner": player.toJson(),
        "rowData": [value for value in eventListDict.values()],
    }]

    naive = player.bornDate.replace(tzinfo=None)
    detailsTableRowList = [{
        "banner": player.toJson(),
        "rowData": [
            (datetime.datetime.today() - naive).days / 365,
            player.post,
            player.team.title,
        ],
    }]

    result = {
        "player": player.toJson(),
        "latestNewsList": [item.toJson() for item in News.objects.all()],
        "statisticsTable": {
            "colList": ['STATISTICS'] + [key for key in eventListDict.keys()],
            "tableRowList": statisticsTableRowList,
        },
        "detailsTable": {
            "colList": ["DETAILS", "age", "post", "team"],
            "tableRowList": detailsTableRowList,
        },
    }
    return JsonResponse(result, safe=False)


def TeamsGet(request, teamId):
    team = Team.objects.get(id=teamId)

    matchList = Match.objects.all().filter(Q(homeTeam=team) | Q(awayTeam=team))

    matchesTableRowList = []
    for match in matchList:
        otherTeam = {}
        goals = 0
        if match.awayTeam.id == team.id:
            otherTeam = match.homeTeam
            goals = match.awayScore
        else:
            otherTeam = match.awayTeam
            goals = match.homeScore

        status = "win"
        if (match.homeTeam.id == team.id and match.homeScore < match.awayScore) or (
                match.awayTeam.id == team.id and match.homeScore > match.awayScore):
            status = "lost"
        if match.homeScore == match.awayScore:
            status = "tied"

        matchesTableRowList.append({
            "banner": otherTeam.toJson(),
            "rowData": [
                status,
                goals,
                match.date.date(),
                match.stadium.__str__(),
            ],
        })

    playerList = [player for player in team.playerList.all()]

    playersTableRowList = []
    for player in playerList:
        playersTableRowList.append({
            "banner": player.toJson(),
            "rowData": [
                player.post,
            ],
        })

    result = {
        "team": team.toJson(),
        "latestNewsList": [item.toJson() for item in News.objects.all()],
        "matchesTable": {
            "colList": ["MATCHES", "status", "goals", "date", "stadium"],
            "tableRowList": matchesTableRowList,
        },
        "playersTable": {
            "colList": ["PLAYERS", "post"],
            "tableRowList": playersTableRowList,
        },
    }
    return JsonResponse(result, safe=False)
