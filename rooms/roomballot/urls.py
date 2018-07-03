from django.urls import path

from . import views

urlpatterns = [
    path('room_details/<str:room_id>', views.show_room, name='detail'),
    path('home', views.get_staircase, name='staircase'),
    path('staircase/<int:staircase_id>/selectroom', views.get_room, name='room'),
    path('survey/<str:room_id>', views.get_survey, name='survey'),
    path('confirmation', views.get_confirmation, name='confirmation')
]