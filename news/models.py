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
        superDict = super(Team, self).toJson()
        superDict['shortTitle'] = self.shortTitle
        superDict['type'] = 'Team'
        return superDict

    class Meta:
        verbose_name_plural = "Teams"


class Player(Account):

    def __str__(self):
        return "{}".format(self.title)

    def toJson(self):
        superDict = super(Player, self).toJson()
        superDict['type'] = 'Player'
        return superDict

    class Meta:
        verbose_name_plural = "Players"


class League(Account):
    teamList = models.ManyToManyField(Team, through='LeagueTeam')

    def __str__(self):
        return "{}".format(self.title)

    def toJson(self):
        # todo: add teamList
        leagueTeamTableRowData = []
        for team in self.teamList.all():
            leagueTeamTableRowData.append({
                "banner": team.toJson(),
                "rowData": [
                    "rank1",
                    3,
                    team.created_at.date(),
                ],
            })

        teamList = [team.toJson() for team in self.teamList.all()]
        matchList = [match.toJson() for match in self.matchList.all()]
        superDict = super(League, self).toJson()
        superDict['teamList'] = teamList
        superDict['matchList'] = matchList
        superDict['nextMatch'] = self.matchList.all()[0].toJson()
        superDict['leagueTeamTable'] = {
            'colList': ["STATISTICS", "rank", "points", "last game"],
            'tableRowList': leagueTeamTableRowData,
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
    homeTeam = models.OneToOneField(Team, related_name='homeTeam', on_delete=models.CASCADE)
    awayTeam = models.OneToOneField(Team, related_name='awayTeam', on_delete=models.CASCADE)
    homeScore = models.IntegerField()
    awayScore = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
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
            homeTeam=self.homeTeam.toJson(),
            homeEventList=homeEventList,
            awayTeam=self.awayTeam.toJson(),
            awayEventList=awayEventList,
            homeScore=self.homeScore,
            awayScore=self.awayScore,
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

    def __str__(self):
        return "{}".format(self.title)

    def toJson(self):
        return dict(
            id=self.id,
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


class LeagueTeam(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    rank = models.IntegerField()
    points = models.IntegerField()
    played = models.IntegerField()
    goalDifference = models.IntegerField()

    def __str__(self):
        return "{} team in {} league".format(self.team.title, self.league.title)

    def toJson(self):
        return dict(
            id=self.id,
            teamId=self.team.id,
            leagueId=self.league.id,
            rank=self.rank,
            points=self.points,
            played=self.played,
            goalDifference=self.goalDifference,
        )

    class Meta:
        verbose_name_plural = "LeagueTeams"


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
