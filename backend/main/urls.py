from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import AuthenticationForm

urlpatterns = [
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