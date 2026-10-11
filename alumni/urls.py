from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.alumni_login, name='alumni_login'),
    path('register/', views.alumni_register, name='alumni_register'),
    path('logout/', views.alumni_logout, name='alumni_logout'),
    path('dashboard/', views.alumni_dashboard, name='alumni_dashboard'),
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/add/', views.add_job, name='add_job'),
    path('events/', views.event_list, name='event_list'),
    path('events/add/', views.add_event, name='add_event'),
    path('events/register/<int:event_id>/', views.register_event, name='register_event'),
    path('directory/', views.alumni_directory, name='alumni_directory'),
    path('students/', views.student_directory, name='student_directory'),
    path('message/send/<int:user_id>/', views.send_message, name='send_message'),
    path('inbox/', views.inbox, name='inbox'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    
    # Faculty Management Routes
    path('approve-student/<int:profile_id>/', views.approve_student, name='approve_student'),
    path('announcement/add/', views.add_announcement, name='add_announcement'),
    path('export-alumni-csv/', views.export_alumni_csv, name='export_alumni_csv'),
]