import datetime
import json

from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from news.models import *

from django.contrib.auth import login, authenticate
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .tokens import account_activation_token
from django.contrib.auth.models import User


# Create your views here.


@csrf_exempt
def signup(request):
    #         current_site = get_current_site(request)
    #         mail_subject = 'Activate your blog account.'
    #         message = render_to_string('acc_activate_email.html', {
    #             'user': user,
    #             'domain': current_site.domain,
    #             'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
    #             'token': account_activation_token.make_token(user),
    #         })
    #         to_email = form.cleaned_data.get('email')
    #         email = EmailMessage(
    #                     mail_subject, message, to=[to_email]
    #         )
    #         # email.send()

    body = json.loads(request.body)
    if User.objects.all().filter(username=body['username']).count() > 0 is not None:
        result = {
            "error": "This Username Already Exist"
        }
    else:
        user = User.objects.create_user(body['username'], body['email'], body['password'])
        user.is_active = False
        user.save()
        newsUser = NewsUser.objects.create(user=user, token=uuid.uuid4())
        newsUser.save()
        result = {
            'activationUrl': 'http://127.0.0.1:8000/api/activate/' + urlsafe_base64_encode(force_bytes(user.pk)).decode() + '/' +
                             account_activation_token.make_token(user),
        }
    return JsonResponse(result, safe=False)


@csrf_exempt
def login(request):
    body = json.loads(request.body)
    user = authenticate(username=body['username'], password=body['password'])
    if user is not None:
        if user.is_active:
            result = {
                "user": NewsUser.objects.all().filter(user=user).first().toJson()
            }
        else:
            result = {
                "error": 'Please Activate Your Account'
            }
    else:
        result = {
            "error": "Login Failed"
        }
    return JsonResponse(result, safe=False)


@csrf_exempt
def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        result = {
            "activation": True
        }
    else:
        result = {
            "activation": False
        }
    return JsonResponse(result, safe=False)


def getUser(request):
    try:
        user = authenticate(username=request.META['HTTP_USERNAME'], password=request.META['HTTP_PASSWORD'])
        return user
    except:
        return None


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
    type = ''
    if isinstance(model, Match):
        type = 'Match'
    if isinstance(model, League):
        type = 'League'
    if isinstance(model, Team):
        type = 'Team'
    if isinstance(model, Player):
        type = 'Player'
    if isinstance(model, Stadium):
        type = 'Stadium'

    tagList = Tag.objects.all().filter(accountType=type, accountId=model.id)
    newsList = [newsTag.news for newsTag in NewsTag.objects.all().filter(tag__in=tagList)[:3]]
    return [item.toJson() for item in newsList]


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
        "footballMatchList": {
            "latest": [item.toJson() for item in Match.objects.all().filter(type='Football')[:6]],
        },
        "basketballMatchList": {
            "latest": [item.toJson() for item in Match.objects.all().filter(type='Basketball')[:6]],
        },
    }
    user = getUser(request)
    if user is not None:
        result['favouriteNewsList'] = getNews(user)
        result['footballMatchList']['favourites'] = [item.toJson() for item in Match.objects.all().filter(type='Football')[:2]]
        result['basketballMatchList']['favourites'] = [item.toJson() for item in Match.objects.all().filter(type='Basketball')[:2]]

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
        "latestNewsList": getNews(player),
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
        "latestNewsList": getNews(team),
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
