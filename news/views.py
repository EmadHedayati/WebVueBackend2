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
            'activationUrl': 'http://127.0.0.1:8000/api/activate/' + urlsafe_base64_encode(
                force_bytes(user.pk)).decode() + '/' +
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
def Activate(request, uidb64, token):
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


@csrf_exempt
def ForgetPassword(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    result = {}
    return JsonResponse(result, safe=False)


def getUser(request):
    try:
        user = authenticate(username=request.META['HTTP_USERNAME'], password=request.META['HTTP_PASSWORD'])
        return NewsUser.objects.filter(user=user).first()
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


def getSliderNews():
    return News.objects.all()[:5]


def getLatestNews():
    return News.objects.all()[:10]


def getRelatedNews(news):
    newsList = []
    newsList.extend(News.objects.all().filter(author=news.author).exclude(id=news.id))
    for tag in news.tagList.all():
        newsList.extend([newsTag.news for newsTag in NewsTag.objects.filter(tag=tag).exclude(id=news.id)])
    newsList = list(set(newsList))
    return newsList


def getUserNews(user):
    newsList = []
    subscriptionList = Subscription.objects.filter(newsUser=user)
    for subscription in subscriptionList:
        if subscription.accountType == 'Match':
            newsList.extend(getModelNews(Match.objects.filter(id=subscription.accountId).first()))
        elif subscription.accountType == 'League':
            newsList.extend(getModelNews(League.objects.filter(id=subscription.accountId).first()))
        elif subscription.accountType == 'Team':
            newsList.extend(getModelNews(Team.objects.filter(id=subscription.accountId).first()))
        elif subscription.accountType == 'Player':
            newsList.extend(getModelNews(Player.objects.filter(id=subscription.accountId).first()))
        elif subscription.accountType == 'Stadium':
            newsList.extend(getModelNews(Stadium.objects.filter(id=subscription.accountId).first()))
    return newsList[:3]


def getModelNews(model):
    type = ''
    if isinstance(model, Match):
        type = 'Match'
    elif isinstance(model, League):
        type = 'League'
    elif isinstance(model, Team):
        type = 'Team'
    elif isinstance(model, Player):
        type = 'Player'
    elif isinstance(model, Stadium):
        type = 'Stadium'
    else:
        return []

    tagList = Tag.objects.all().filter(accountType=type, accountId=model.id)
    newsList = [newsTag.news for newsTag in NewsTag.objects.all().filter(tag__in=tagList)[:3]]
    return newsList


def isSubscribed(user, accountType, accountId):
    if Subscription.objects.all().filter(newsUser=user, accountType=accountType, accountId=accountId).count() > 0:
        return True
    else:
        return False


@csrf_exempt
def Subscribe(request):
    body = json.loads(request.body)
    if not isSubscribed(getUser(request), body['accountType'], body['accountId']):
        Subscription.objects.create(newsUser=getUser(request), accountType=body['accountType'], accountId=body['accountId'])
    result = {
        "subscribed": True
    }
    return JsonResponse(result, safe=False)


@csrf_exempt
def Unsubscribe(request):
    body = json.loads(request.body)
    if isSubscribed(getUser(request), body['accountType'], body['accountId']):
        Subscription.objects.filter(newsUser=getUser(request), accountType=body['accountType'], accountId=body['accountId']).delete()
    result = {
        "subscribed": False
    }
    return JsonResponse(result, safe=False)


@csrf_exempt
def NewsComment(request):
    body = json.loads(request.body)
    news = News.objects.filter(id=int(body['newsId'])).first()
    if getUser(request) is not None:
        comment = Comment.objects.create(author=getUser(request), body=body['body'], news=news)
        result = {
            "comment": comment.toJson()
        }
    else:
        result = {
            "error": 'Not registered'
        }
    return JsonResponse(result, safe=False)


def getModelJsonWithSubscription(user, model):
    json = model.toJson()
    if isinstance(model, Match):
        type = 'Match'
    elif isinstance(model, League):
        type = 'League'
    elif isinstance(model, Team):
        type = 'Team'
    elif isinstance(model, Player):
        type = 'Player'
    elif isinstance(model, Stadium):
        type = 'Stadium'
    json['subscribed'] = isSubscribed(user, type, model.id)
    return json


def getDateWithDeltaDays(delta):
    today = datetime.date.today()
    deltaDays = datetime.timedelta(days=abs(delta))
    if delta > 0:
        return today + deltaDays
    else:
        return today - deltaDays

def homeIndex(request):
    result = {
        "sliderNewsList": [item.toJson() for item in getSliderNews()],
        "latestNewsList": [item.toJson() for item in getLatestNews()],
        "footballMatchList": {
            "latest": [item.toJson() for item in Match.objects.all().filter(type='Football')[:6]],
        },
        "basketballMatchList": {
            "latest": [item.toJson() for item in Match.objects.all().filter(type='Basketball')[:6]],
        },
    }
    user = getUser(request)
    if user is not None:
        result['favouriteNewsList'] = [item.toJson() for item in getUserNews(user)]

        matchList = []
        subscriptionList = Subscription.objects.filter(newsUser=user, accountType='Team')
        for subscription in subscriptionList:
            team = Team.objects.filter(id=subscription.accountId).first()
            matchList.extend(Match.objects.filter(type='Football', homeTeam=team, date__gt=getDateWithDeltaDays(-1), date__lt=getDateWithDeltaDays(1)))
            matchList.extend(Match.objects.filter(type='Football', awayTeam=team, date__gt=getDateWithDeltaDays(-1), date__lt=getDateWithDeltaDays(1)))
        result['footballMatchList']['favourites'] = [item.toJson() for item in matchList[:6]]

        matchList = []
        subscriptionList = Subscription.objects.filter(newsUser=user, accountType='Team')
        for subscription in subscriptionList:
            team = Team.objects.filter(id=subscription.accountId).first()
            matchList.extend(Match.objects.filter(type='Basketball', homeTeam=team, date__gt=getDateWithDeltaDays(-1), date__lt=getDateWithDeltaDays(1)))
            matchList.extend(Match.objects.filter(type='Basketball', awayTeam=team, date__gt=getDateWithDeltaDays(-1), date__lt=getDateWithDeltaDays(1)))
        result['basketballMatchList']['favourites'] = [item.toJson() for item in matchList[:6]]
    return JsonResponse(result, safe=False)


def LeaguesIndex(request):
    result = {}
    if request.GET.get('q'):
        search = request.GET.get('q')
        parts = search.split(' ')
        date = datetime.date.today()
        if parts[-1].isnumeric():
            newSearch = ' '.join(parts[:-1])
            startDate = date.replace(year=int(parts[-1]), month=1, day=1)
            finishDate = date.replace(year=int(parts[-1]) + 1, month=1, day=1)
            result = {
                "upcomingLeagueList": [item.toJson() for item in League.objects.all().filter(
                    startDate__gt=datetime.date.today(), title__exact=newSearch, startDate__lt=finishDate)],
                "finishedLeagueList": [item.toJson() for item in League.objects.all().filter(
                    startDate__gt=startDate, finished=True, title__exact=newSearch, startDate__lt=finishDate)],
            }
        else:
            result = {
                "upcomingLeagueList": [item.toJson() for item in League.objects.all().filter(
                    startDate__gt=datetime.date.today(), title__exact=search)],
                "finishedLeagueList": [item.toJson() for item in League.objects.all().filter(
                    finished=True, title__exact=search)],
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
        "league": getModelJsonWithSubscription(getUser(request), league),
    }
    return JsonResponse(result, safe=False)


def MatchesGet(request, matchId):
    match = Match.objects.get(id=matchId)
    result = {
        "match": getModelJsonWithSubscription(getUser(request), match),
        "latestNewsList": [item.toJson() for item in getModelNews(match)],
    }
    return JsonResponse(result, safe=False)


def NewsGet(request, newsId):
    news = News.objects.get(id=newsId)
    result = {
        "news": news.toJson(),
        "relatedNewsList": [item.toJson() for item in getRelatedNews(news)],
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
        "banner": getModelJsonWithSubscription(getUser(request), player),
        "rowData": [value for value in eventListDict.values()],
    }]

    naive = player.bornDate.replace(tzinfo=None)
    detailsTableRowList = [{
        "banner": getModelJsonWithSubscription(getUser(request), player),
        "rowData": [
            int((datetime.datetime.today() - naive).days / 365),
            player.post,
            player.height,
            player.weight,
            player.nationality,
            player.team.title,
        ],
    }]

    result = {
        "player": getModelJsonWithSubscription(getUser(request), player),
        "latestNewsList": [item.toJson() for item in getModelNews(player)],
        "statisticsTable": {
            "colList": ['STATISTICS'] + [key for key in eventListDict.keys()],
            "tableRowList": statisticsTableRowList,
        },
        "detailsTable": {
            "colList": ["DETAILS", "age", "post", "height", "weight", "nationality", "team"],
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
        "team": getModelJsonWithSubscription(getUser(request), team),
        "latestNewsList": [item.toJson() for item in getModelNews(team)],
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
