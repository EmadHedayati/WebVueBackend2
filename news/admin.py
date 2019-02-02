from django.contrib import admin

# Register your models here.
from . import models

admin.site.register(models.NewsUser)
admin.site.register(models.Team)
admin.site.register(models.League)
admin.site.register(models.MatchStatistic)
admin.site.register(models.Statistic)
admin.site.register(models.Stadium)
admin.site.register(models.Match)
admin.site.register(models.Event)
admin.site.register(models.Tag)
admin.site.register(models.News)
admin.site.register(models.Comment)
admin.site.register(models.Player)
admin.site.register(models.NewsTag)
admin.site.register(models.Subscription)
