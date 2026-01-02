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
]