from django.urls import path

from . import views

urlpatterns = [
    path('room/<str:room_id>/confirm-selection', views.room_selection_confirm, name='confirm-room-selection'),
    path('room/<str:room_id>', views.room_detail, name='room-detail'),
    path('', views.landing, name='landing'),
    path('dashboard/create-syndicate', views.create_syndicate, name='create-syndicate'),
    path('staircases', views.staircase_list, name='staircases'),
    path('staircase/<int:staircase_id>', views.staircase_detail, name='staircase-detail'),
    path('dashboard', views.student_dashboard, name='dashboard'),
    path('error/<int:code>', views.error, name='error')
]