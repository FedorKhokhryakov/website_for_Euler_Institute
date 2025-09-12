from django.urls import path, include
from . import views, api_views
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import AuthenticationForm
from django.urls import path


urlpatterns = [
    path('api/auth/login/', api_views.login_view, name='login'),
    path('api/auth/user/', api_views.get_current_user, name='current-user'),

    path('api/auth/register/', api_views.register_user, name='register'),

    path('api/all_publications/', api_views.get_all_publications, name='all-publications'),
    path('api/my_publications/', api_views.get_user_publications, name='user-publications'),
    path('api/publications/<int:id>/', api_views.get_publication_detail, name='publication-detail'),
    path('api/publications/<int:id>/check-owner/', api_views.check_publication_owner, name='check-owner'),
    path('api/publications/', api_views.create_publication, name='create-publication'),

    path('api/users/<int:id>/', api_views.get_user_profile, name='user-profile'),
    path('api/users/', api_views.user_list, name='user-list'),
    path("api/users_request/", api_views.users_request, name="users-request"),

    path('api/reports/', api_views.create_report, name='create-report'),
    path('api/reports2/', api_views.list_reports, name='list-reports'),
    path('api/reports/<int:id>/download/', api_views.download_report, name='download-report'),
    path('api/reports/download/', api_views.download_report_api, name='download-report-api'),

    path('', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    path('add-publication/', views.add_post, name='add_post'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(
        template_name='registration/login.html',
        authentication_form=AuthenticationForm,
        redirect_authenticated_user=True
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    path('publications/', views.all_posts, name='all_posts'),
    path('publications/<int:pk>/', views.post_detail, name='post_detail'),
    path('users/', views.all_users, name='all_users'),
    path('users/<int:user_id>/publications/', views.user_posts, name='user_posts'),
    path('search/', views.search, name='search'),

    path("reports/", views.report_page, name="report_page"),
    path("reports/admin/", views.report_page, name="admin_reports"),
    path("reports/generate/", views.generate_user_report, name="generate_user_report"),
]