from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test

# Create your views here.

def is_tmo_officer(user):
    #check if the user is a TMO Officer
    return user.is_authenticated and user.role == 'tmo_officer'

@login_required
def dashboard(request):
    #dashbaord view for all authenticated users
    context = {
        'user': request.user,
        'role': request.user.get_role_display(),
    }
    return render(request, 'users/dashboard.html', context)

@login_required
@user_passes_test(is_tmo_officer, login_url='/users/dashboard/')
def tmo_officer(request):
    #dashboard only for tmo officers
    context = {
        'user': request.user,
    }
    return render(request, 'users/tmo_dashboard.html', context)
