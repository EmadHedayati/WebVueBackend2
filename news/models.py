import datetime

from django.db import models
from django.contrib.auth.models import User


# Create your models here.


class NewsUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    token = models.CharField(max_length=200, unique=True)
    image = models.ImageField()

    def __str__(self):
        return "{}".format(self.user.username)

    def toJson(self):
        return dict(
            id=self.user.id,
            title=self.user.username,
            fullname=self.user.get_full_name(),
            username=self.user.username,
            email=self.user.email,
            image=self.image.url,
        )

    class Meta:
        verbose_name_plural = "Users"


class Account(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    image = models.ImageField()
    backgroundImage = models.ImageField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{}".format(self.title)

    def toJson(self):
        return dict(
            id=self.id,
            title=self.title,
            description=self.description,
            image=self.image.url,
            backgroundImage=self.backgroundImage.url,
            dateCreated=self.created_at.timestamp(),
        )

    class Meta:
        abstract = True


class Team(Account):
    shortTitle = models.CharField(max_length=10)

    def __str__(self):
        return "{} also known as {}".format(self.title, self.shortTitle)

    def toJson(self):
        playerList = [player.toJson() for player in self.playerList.all()]
        superDict = super(Team, self).toJson()
        superDict['shortTitle'] = self.shortTitle
        superDict['playerList'] = playerList
        superDict['type'] = 'Team'
        return superDict

    class Meta:
        verbose_name_plural = "Teams"


class Player(Account):
    bornDate = models.DateTimeField()
    post = models.CharField(max_length=100)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='playerList', null=True)

    def __str__(self):
        return "{}".format(self.title)

    def toJson(self):
        naive = self.bornDate.replace(tzinfo=None)
        superDict = super(Player, self).toJson()
        superDict['type'] = 'Player'
        superDict['age'] = (datetime.datetime.today() - naive).days / 365
        superDict['post'] = self.post
        superDict['teamId'] = self.team.id
        return superDict

    class Meta:
        verbose_name_plural = "Players"


class League(Account):
    startDate = models.DateTimeField()
    finished = models.BooleanField(default=False)

    def __str__(self):
        return "{}".format(self.title)

    def toJson(self):
        matchList = Match.objects.all().filter(league=self)

        teamList = []
        for match in matchList:
            if match.awayTeam not in teamList:
                teamList.append(match.awayTeam)
            if match.homeTeam not in teamList:
                teamList.append(match.homeTeam)

        leagueTeamTableRowList = []
        for team in teamList:
            points = 0
            games = 0
            goalFor = 0
            goalAgainst = 0
            for match in Match.objects.all().filter(league=self):
                if match.homeTeam == team:
                    games += 1
                    points += match.homePoints
                    goalFor += match.homeScore
                    goalAgainst += match.awayScore
                if match.awayTeam == team:
                    games += 1
                    points += match.awayPoints
                    goalFor += match.awayScore
                    goalAgainst += match.homeScore

            leagueTeamTableRowList.append({
                "banner": team.toJson(),
                "rowData": [
                    points,
                    games,
                    goalFor,
                    goalAgainst,
                    goalFor - goalAgainst,
                ],
            })

        matchList = [match.toJson() for match in self.matchList.all()]
        superDict = super(League, self).toJson()
        superDict['matchList'] = matchList
        superDict['nextMatch'] = self.matchList.all()[0].toJson()
        superDict['leagueTeamTable'] = {
            'colList': ["LEAGUE TABLE", "points", "games", "score for", "score against", "score difference"],
            'tableRowList': leagueTeamTableRowList,
        }
        superDict['type'] = 'League'
        return superDict

    class Meta:
        verbose_name_plural = "Leagues"


class MatchStatistic(models.Model):
    title = models.CharField(max_length=100)

    def __str__(self):
        return "{} ({})".format(self.title, self.id)

    def toJson(self):
        return dict(
            id=self.id,
            title=self.title,
            statisticsList=[statistic.toJson() for statistic in self.statisticList.all()]
        )

    class Meta:
        verbose_name_plural = "MatchStatistics"


class Statistic(models.Model):
    title = models.CharField(max_length=100)
    homeValue = models.IntegerField()
    awayValue = models.IntegerField()
    matchStatistic = models.ForeignKey(MatchStatistic, on_delete=models.CASCADE, related_name='statisticList')

    def __str__(self):
        return "{} for ({})".format(self.title, self.matchStatistic.id)

    def toJson(self):
        return dict(
            id=self.id,
            title=self.title,
            homeValue=self.homeValue,
            awayValue=self.awayValue,
            matchStatisticId=self.matchStatistic.id,
        )

    class Meta:
        verbose_name_plural = "Statistics"


class Stadium(Account):

    def __str__(self):
        return "{}".format(self.title)

    def toJson(self):
        superDict = super(Stadium, self).toJson()
        superDict['type'] = 'Stadium'
        return superDict

    class Meta:
        verbose_name_plural = "Stadiums"


class Match(models.Model):
    TYPE_LIST = (
        ('Football', 'Football'),
        ('Basketball', 'Basketball'),
    )

    type = models.CharField(max_length=100, choices=TYPE_LIST)
    homeTeam = models.ForeignKey(Team, related_name='homeTeam', on_delete=models.CASCADE)
    awayTeam = models.ForeignKey(Team, related_name='awayTeam', on_delete=models.CASCADE)
    homeScore = models.IntegerField()
    awayScore = models.IntegerField()
    homePoints = models.IntegerField()
    awayPoints = models.IntegerField()
    date = models.DateTimeField()
    stadium = models.ForeignKey(Stadium, on_delete=models.CASCADE)
    matchStatistic = models.ForeignKey(MatchStatistic, on_delete=models.CASCADE)
    time = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name='matchList')

    def __str__(self):
        return "{} vs {} in {}".format(self.homeTeam.shortTitle, self.awayTeam.shortTitle, self.date.date())

    def toJson(self):
        homeEventList = [event.toJson() for event in Event.objects.all().filter(team=self.homeTeam, match=self)]
        awayEventList = [event.toJson() for event in Event.objects.all().filter(team=self.awayTeam, match=self)]
        return dict(
            id=self.id,
            type=self.type,
            homeTeam=self.homeTeam.toJson(),
            homeEventList=homeEventList,
            awayTeam=self.awayTeam.toJson(),
            awayEventList=awayEventList,
            homeScore=self.homeScore,
            awayScore=self.awayScore,
            homePoints=self.homePoints,
            awayPoints=self.awayPoints,
            date=self.date.timestamp(),
            stadium=self.stadium.toJson(),
            matchStatistics=self.matchStatistic.toJson(),
            time=self.time,
            dateCreated=self.created_at.timestamp(),
            leagueId=self.league.id,
        )

    class Meta:
        verbose_name_plural = "Matches"


class Event(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    time = models.IntegerField()
    image = models.ImageField()
    important = models.BooleanField()
    player = models.ForeignKey(Player, on_delete=models.CASCADE, null=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)

    def __str__(self):
        return "{} in {}".format(self.title, self.match.__str__())

    def toJson(self):
        return dict(
            id=self.id,
            title=self.title,
            description=self.description,
            time=self.time,
            image=self.image.url,
            important=self.important,
            player=self.player.toJson(),
            teamId=self.team.id,
            matchId=self.match.id,
        )

    class Meta:
        verbose_name_plural = "Events"


class Tag(models.Model):
    title = models.CharField(max_length=100)
    accountId = models.IntegerField(null=True)
    accountType = models.CharField(max_length=100, null=True)

    def __str__(self):
        return "{}".format(self.title)

    def toJson(self):
        return dict(
            id=self.id,
            accountId=self.accountId,
            accountType=self.accountType,
            title=self.title,
        )

    class Meta:
        verbose_name_plural = "Tags"


class News(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    body = models.CharField(max_length=50000)
    image = models.ImageField()
    author = models.ForeignKey(NewsUser, on_delete=models.CASCADE)
    tagList = models.ManyToManyField(Tag, through='NewsTag')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{}".format(self.title)

    def toJson(self):
        tagList = [tag.toJson() for tag in self.tagList.all()]
        commentList = [comment.toJson() for comment in self.commentList.all()]
        return dict(
            id=self.id,
            title=self.title,
            description=self.description,
            body=self.body,
            image=self.image.url,
            author=self.author.toJson(),
            tagList=tagList,
            commentList=commentList,
            dateCreated=self.created_at.timestamp(),
        )

    class Meta:
        verbose_name_plural = "News"


class Comment(models.Model):
    body = models.CharField(max_length=500)
    author = models.ForeignKey(NewsUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    news = models.ForeignKey(News, on_delete=models.CASCADE, null=False, related_name='commentList')

    def __str__(self):
        return "{} by {}".format(self.body, self.author.username)

    def toJson(self):
        return dict(
            id=self.id,
            body=self.body,
            dateCreated=self.created_at.timestamp(),
            author=self.author.toJson(),
            newsId=self.news.id,
        )

    class Meta:
        verbose_name_plural = "Comments"


class NewsTag(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    def __str__(self):
        return "{} tag in {} news".format(self.tag.title, self.news.title)

    def toJson(self):
        return dict(
            id=self.id,
            newsId=self.news.id,
            tagId=self.tag.id,
        )

    class Meta:
        verbose_name_plural = "NewsTags"
