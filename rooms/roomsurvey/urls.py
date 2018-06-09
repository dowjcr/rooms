from django.urls import path

from . import views

urlpatterns = [
    path('room_details/<str:pk>', views.RoomDetailView.as_view(), name='detail'),
    path('home', views.get_staircase, name='staircase'),
    path('staircase/<int:staircase_id>/selectroom', views.get_room, name='room')
]