from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('tmo/', views.tmo_officer, name='tmo_officer_dashboard'),
]