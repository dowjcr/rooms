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
    path('proxy', views.proxy, name='proxy'),
    path('dashboard/create-syndicate', views.create_syndicate, name='create-syndicate'),
    path('dashboard/syndicate', views.syndicate_view, name='syndicate'),
    path('admin', views.admin_dashboard, name='admin'),
    path('admin/manage-student/<str:user_id>', views.manage_student, name='manage-student'),
    path('admin/status', views.status, name='status'),
    path('admin/syndicate/<int:syndicate_id>', views.manage_syndicate, name='manage-syndicate'),
    path('admin/syndicates', views.syndicates_list, name='syndicates-list'),
    path('admin/create-syndicate', views.create_syndicate_admin, name='create-syndicate-admin'),
    path('admin/students', views.students_list, name='students-list'),
    path('admin/rooms', views.rooms_list, name='rooms-list'),
    path('admin/room/<str:room_id>', views.manage_room, name='manage-room'),
    path('admin/rooms/export', views.export_room_data, name='export-room-data'),
    path('admin/students/export', views.export_student_data, name='export-student-data'),
    path('admin/students/ranking', views.ranking_admin, name='ranking-admin'),
    path('admin/analytics', views.analytics, name='analytics'),
    path('admin/change-weights', views.change_weights, name='change-weights'),
    path('ranking', views.ballot_ranking, name='ranking'),
    path('staircases', views.staircase_list, name='staircases'),
    path('staircase/<int:staircase_id>', views.staircase_detail, name='staircase-view'),
    path('room/<str:room_id>/confirm-selection', views.room_selection_confirm, name='confirm-room-selection'),
    path('room/<str:room_id>', views.room_detail, name='room-detail'),
    path('room-pricing/<str:room_id>', views.room_pricing, name='room-pricing'),
    path('error/<int:code>', views.error, name='error'),
    path('student/<str:user_id>', views.student_detail, name='student-detail'),
    path('syndicate/<int:syndicate_id>', views.syndicate_detail, name='syndicate-detail'),
    path('info', views.ballot_info, name='info'),
    path('info/bursary', views.bursary_info, name='bursary-info'),
    path('info/create-syndicate', views.syndicate_info, name='syndicate-info'),
    path('info/individual', views.individual_info, name='individual-info'),
    path('info/select-room', views.select_room_info, name='select-room-info'),
    path('info/pricing', views.pricing_info, name='pricing-info'),
    path('dashboard/review', views.leave_review, name='leave-review'),
    path('admin/currently-picking', views.currently_picking, name='currently-picking'),
    path('about', views.about, name='about'),
]