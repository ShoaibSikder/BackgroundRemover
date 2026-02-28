from django.urls import path
from .views import RegisterView, LoginView, all_users, google_login

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('all-users/', all_users, name='all-users'),  # Admin only
    path('google-login/<str:backend>/', google_login, name='google-login'),

]