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
        "leagueTeams": [item.toJson() for item in LeagueTeam.objects.all()],
        "players": [item.toJson() for item in Player.objects.all()],
        "newsTags": [item.toJson() for item in NewsTag.objects.all()],
    }
    return JsonResponse(result, safe=False)


def homeIndex(request):
    result = {
        "sliderNewsList": [item.toJson() for item in News.objects.all()],
        "latestNewsList": [item.toJson() for item in News.objects.all()],
        "favouriteNewsList": [item.toJson() for item in News.objects.all()],
        "footballMatchList": {
            "latest": [item.toJson() for item in Match.objects.all()],
            "favourites": [item.toJson() for item in Match.objects.all()],
        },
        "basketballMatchList": {
            "latest": [item.toJson() for item in Match.objects.all()],
            "favourites": [item.toJson() for item in Match.objects.all()],
        },
    }
    return JsonResponse(result, safe=False)


def LeaguesIndex(request):
    result = {
        "upcomingLeagueList": [item.toJson() for item in League.objects.all()],
        "finishedLeagueList": [item.toJson() for item in League.objects.all()],
    }
    return JsonResponse(result, safe=False)


def LeaguesGet(request, leagueId):
    result = {
        "league": League.objects.get(id=leagueId).toJson(),
    }
    return JsonResponse(result, safe=False)


def MatchesGet(request, matchId):
    result = {
        "match": Match.objects.get(id=matchId).toJson(),
        "latestNewsList": [item.toJson() for item in News.objects.all()],
    }
    return JsonResponse(result, safe=False)


def NewsGet(request, newsId):
    result = {
        "news": News.objects.get(id=newsId).toJson(),
        "relatedNewsList": [item.toJson() for item in News.objects.all()],
    }
    return JsonResponse(result, safe=False)


def PlayersGet(request, playerId):
    statisticsTableRowData = []
    for match in Match.objects.all():
        statisticsTableRowData.append({
            "banner": Player.objects.get(id=playerId).toJson(),
            "rowData": [
                "attack",
                3,
                match.date.date(),
                match.stadium.__str__(),
            ],
        })

    detailsTableRowData = []
    for player in Player.objects.all():
        detailsTableRowData.append({
            "banner": Player.objects.get(id=playerId).toJson(),
            "rowData": [
                player.title,
                5,
                player.created_at.date(),
                12,
            ],
        })

    result = {
        "player": Player.objects.get(id=playerId).toJson(),
        "latestNewsList": [item.toJson() for item in News.objects.all()],
        "statisticsTable": {
            "colList": ["STATISTICS", "post", "goals", "acquired", "stadium"],
            "tableRowList": statisticsTableRowData,
        },
        "detailsTable": {
            "colList": ["DETAILS", "title", "goals", "date", "games"],
            "tableRowList": detailsTableRowData,
        },
    }
    return JsonResponse(result, safe=False)


def TeamsGet(request, teamId):
    matchesTableRowData = []
    for match in Match.objects.all():
        matchesTableRowData.append({
            "banner": match.awayTeam.toJson(),
            "rowData": [
                "win",
                3,
                match.date.date(),
                match.stadium.__str__(),
            ],
        })

    playersTableRowData = []
    for player in Player.objects.all():
        playersTableRowData.append({
            "banner": player.toJson(),
            "rowData": [
                player.title,
                5,
                player.created_at.date(),
                12,
            ],
        })

    result = {
        "team": Team.objects.get(id=teamId).toJson(),
        "latestNewsList": [item.toJson() for item in News.objects.all()],
        "matchesTable": {
            "colList": ["MATCHES", "status", "goals", "date", "stadium"],
            "tableRowList": matchesTableRowData,
        },
        "playersTable": {
            "colList": ["PLAYERS", "title", "games", "date", "goals"],
            "tableRowList": playersTableRowData,
        },
    }
    return JsonResponse(result, safe=False)
