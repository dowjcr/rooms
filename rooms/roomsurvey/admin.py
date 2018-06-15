from django.contrib import admin

from .models import Room, Staircase, SurveyResponse

admin.site.register(Room)
admin.site.register(Staircase)
admin.site.register(SurveyResponse)