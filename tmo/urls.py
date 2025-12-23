from django.urls import path
from . import views

app_name = 'tmo'

urlpatterns = [

    path('profile/', views.tmo_profile, name='profile'),
    path('change-password/', views.change_password, name='change_password'),
    
]