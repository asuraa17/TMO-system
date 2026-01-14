from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    # General dashboard
    path("dashboard/", views.dashboard, name="dashboard"),
    # Buyer registration paths
    path("buyer/register/", views.buyer_register, name="buyer_register"),
    path(
        "buyer/register/preview/",
        views.buyer_register_preview,
        name="buyer_register_preview",
    ),
    path(
        "buyer/register/submit/",
        views.buyer_register_submit,
        name="buyer_register_submit",
    ),
    # Buyer authentication paths
    path("login/", views.all_login, name="all_login"),
    path("logout/", views.all_logout, name="all_logout"),
    # Buyer home path
    path("buyer/home/", views.buyer_home, name="buyer_home"),

    # Buyer profile update paths
    path("buyer/profile/update/", views.buyer_profile_update, name="buyer_profile_update"),
    path("buyer/password/change/", views.buyer_change_password, name="buyer_change_password"),
    # Buyer vehicles paths (NEW)
    path("buyer/vehicles/", views.buyer_vehicles, name="buyer_vehicles"),
    path("buyer/vehicles/<int:vehicle_id>/", views.buyer_vehicle_detail, name="buyer_vehicle_detail"),
]