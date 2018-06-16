from django.contrib import admin

from .models import Room, Staircase, SurveyResponse, Review, UserCompletedSurvey

admin.site.register(Room)
admin.site.register(Staircase)
admin.site.register(Review)
admin.site.register(UserCompletedSurvey)