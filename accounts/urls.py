
from django.urls import path
from django.contrib.auth import views as auth_views
from .views import EmailLoginView, RegistrationView, profile_view

app_name = 'accounts'

urlpatterns = [
    path('login/',  EmailLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'), 
    path('register', RegistrationView.as_view(), name='register'),
    path('profile/', profile_view, name='profile'),
]