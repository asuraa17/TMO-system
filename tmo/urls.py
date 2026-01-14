from django.urls import path
from . import views

app_name = 'tmo'

urlpatterns = [
    #dashboard
    path('dashboard/', views.tmo_dashboard, name='dashboard'),

    #profile and password change
    path('profile/', views.tmo_profile, name='profile'),
    path('change-password/', views.change_password, name='change_password'),

    #buyer verification
    path('buyer-verification/', views.buyer_verification_list, name='buyer_verification_list'),
    path('buyer-verification/<int:buyer_id>/', views.buyer_verification_detail, name='buyer_verification_detail'),
    path('buyer-verification/<int:buyer_id>/verify/', views.verify_buyer, name='verify_buyer'),
    path('buyer-verification/<int:buyer_id>/reject/', views.reject_buyer, name='reject_buyer'),

    # Showroom verification
    path('showroom-verification/', views.showroom_verification_list, name='showroom_verification_list'),
    path('showroom-verification/<int:showroom_id>/', views.showroom_verification_detail, name='showroom_verification_detail'),
    path('showroom-verification/<int:showroom_id>/verify/', views.verify_showroom, name='verify_showroom'),
    path('showroom-verification/<int:showroom_id>/reject/', views.reject_showroom, name='reject_showroom'),

    # Vehicle verification
    path('vehicle-verification/', views.vehicle_verification_list, name='vehicle_verification_list'),
    path('vehicle-verification/<int:vehicle_id>/', views.vehicle_verification_detail, name='vehicle_verification_detail'),
    path('vehicle-verification/<int:vehicle_id>/verify/', views.verify_vehicle, name='verify_vehicle'),
    path('vehicle-verification/<int:vehicle_id>/reject/', views.reject_vehicle, name='reject_vehicle'),  # Added
]