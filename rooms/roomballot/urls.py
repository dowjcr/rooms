"""
URLS
Defines URL paths which match to Django views.
Author Cameron O'Connor
"""

from django.urls import path
from . import views


urlpatterns = [
    path('welcome', views.landing, name='landing'),
    path('dashboard', views.student_dashboard, name='dashboard'),
    path('dashboard/create-syndicate', views.create_syndicate, name='create-syndicate'),
    path('dashboard/syndicate', views.syndicate_detail, name='syndicate'),
    path('admin', views.admin_dashboard, name='admin'),
    path('admin/manage-student/<str:user_id>', views.manage_student, name='manage-student'),
    path('admin/status', views.status, name='status'),
    path('admin/syndicate/<int:syndicate_id>', views.manage_syndicate, name='manage-syndicate'),
    path('admin/syndicates', views.syndicates_list, name='syndicates-list'),
    path('admin/students', views.students_list, name='students-list'),
    path('admin/rooms', views.rooms_list, name='rooms-list'),
    path('admin/room/<str:room_id>', views.manage_room, name='manage-room'),
    path('admin/rooms/export', views.export_room_data, name='export-room-data'),
    path('admin/students/export', views.export_student_data, name='export-student-data'),
    path('ranking', views.ballot_ranking, name='ranking'),
    path('staircases', views.staircase_list, name='staircases'),
    path('staircase/<int:staircase_id>', views.staircase_detail, name='staircase-detail'),
    path('room/<str:room_id>/confirm-selection', views.room_selection_confirm, name='confirm-room-selection'),
    path('room/<str:room_id>', views.room_detail, name='room-detail'),
    path('error/<int:code>', views.error, name='error'),
    path('student/<str:user_id>', views.student_detail, name='student-detail'),
    path('info', views.ballot_info, name='info'),
    path('info/create-syndicate', views.syndicate_info, name='syndicate-info'),
    path('info/individual', views.individual_info, name='individual-info'),
    path('info/select-room', views.select_room_info, name='select-room-info'),
    path('dashboard/review', views.leave_review, name='leave-review'),
    path('about', views.about, name='about'),
]