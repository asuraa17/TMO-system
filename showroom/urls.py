from django.urls import path
from . import views

app_name = 'showroom'

urlpatterns = [
    # Registration
    path('register/', views.showroom_register, name='register'),
    path('register/preview/', views.showroom_register_preview, name='register_preview'),
    path('register/submit/', views.showroom_register_submit, name='register_submit'),
    
    # Dashboard
    path('dashboard/', views.showroom_dashboard, name='dashboard'),
    
    # Profile
    path('profile/', views.showroom_profile, name='profile'),
    path('password/change/', views.showroom_change_password, name='change_password'),

    # Vehicle Management
    path('vehicle/register/', views.vehicle_register, name='vehicle_register'),
    path('vehicle/list/', views.vehicle_list, name='vehicle_list'),
    path('vehicle/<int:vehicle_id>/', views.vehicle_detail, name='vehicle_detail'),
    
]