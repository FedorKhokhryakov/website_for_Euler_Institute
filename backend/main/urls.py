from django.urls import path, include
from . import api_views
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import AuthenticationForm
from django.urls import path


urlpatterns = [
    path('api/auth/login/', api_views.login_view, name='login'),
    path('api/get_user_info/', api_views.get_user_info, name='get_user_info'),

    path('api/auth/register/', api_views.register_user, name='register'),

    #path('api/all_publications/', api_views.get_all_publications, name='all-publications'),
    #path('api/my_posts/', api_views.get_user_posts, name='user-publications'),
    path('api/get_post_information/<int:id>/', api_views.get_post_information, name='get_post_information'),
    #path('api/publications/<int:id>/check-owner/', api_views.check_publication_owner, name='check-owner'),
    path('api/create_post/', api_views.create_post, name='create-publication'),
    path('api/update_post/<int:id>/', api_views.update_post, name='update_post'),
    path('api/delete_post/<int:id>/', api_views.delete_post, name='delete_post'),

    #path('api/users/<int:id>/', api_views.get_user_profile, name='user-profile'),
    #path('api/users/', api_views.user_list, name='user-list'),
    #path("api/users_request/", api_views.users_request, name="users-request"),
    path('api/create_user/', api_views.create_user, name='create_user'),
    path('api/update_user/<int:id>/', api_views.update_user, name='update_user'),
    path('api/delete_user/<int:id>/', api_views.delete_user, name='delete_user'),

    path('api/get_all_users/', api_views.get_all_users, name='get_all_users'),

    path('api/impersonate/start/', api_views.impersonate_start, name='impersonate_start'),
    path('api/impersonate/stop/', api_views.impersonate_stop, name='impersonate_stop'),
    path('api/impersonate/status/', api_views.impersonate_status, name='impersonate_status'),

    path('api/get_year_report/<int:year>/', api_views.get_year_report, name='get_year_report'),
    path('api/get_science_report_on_checking/<int:year>/', api_views.submit_science_report_on_checking, name='get_science_report'),
    path('api/set_science_report_new_status/<int:user_id>/<int:year>/', api_views.set_science_report_new_status, name='set_science_report_status'),
    path('api/save_report/<int:year>/', api_views.save_report, name='save_report'),
    path('api/sign_report/<int:year>/', api_views.sign_report, name='sign_report'),
    path('api/admin/send_to_rework/<int:user_id>/<int:year>/', api_views.send_to_rework, name='send_to_rework'),

    path('api/get_db_info/', api_views.get_db_info, name='get_db_info'),

    #path('api/reports/', api_views.create_report, name='create-report'),
    #path('api/reports2/', api_views.list_reports, name='list-reports'),
    #path('api/reports/<int:id>/download/', api_views.download_report, name='download-report'),
    #path('api/reports/download/', api_views.download_report_api, name='download-report-api'),
]