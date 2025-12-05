from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    # General dashboard
    path("dashboard/", views.dashboard, name="dashboard"),
    path("tmo/", views.tmo_officer, name="tmo_officer_dashboard"),
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
    path("buyer/login/", views.buyer_login, name="buyer_login"),
    path("buyer/logout/", views.buyer_logout, name="buyer_logout"),
    # Buyer home path
    path("buyer/home/", views.buyer_home, name="buyer_home"),
]
