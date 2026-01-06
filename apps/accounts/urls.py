"""
Account URL patterns.
"""
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Web views
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    
    # API endpoints
    path('register/', views.register_api, name='register_api'),
    path('login/', views.login_api, name='login_api'),
    path('logout/', views.logout_api, name='logout_api'),
    path('profile/api/', views.UserProfileAPIView.as_view(), name='profile_api'),
    path('password/change/', views.PasswordChangeAPIView.as_view(), name='password_change_api'),
]