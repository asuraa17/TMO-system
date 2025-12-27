from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.urls import reverse_lazy
from .models import TMOOfficer
from .forms import PasswordChangeForm, TMOOfficerProfileForm

# Create your views here.

def is_tmo_officer(user):
    """
    Check if user is a TMO Officer
    """
    return user.is_authenticated and user.role == 'tmo_officer'


@login_required(login_url=reverse_lazy('users:all_login'))
@user_passes_test(is_tmo_officer, login_url=reverse_lazy('users:dashboard'))
def tmo_profile(request):
    """Profile page for TMO Officers"""
    try:
        officer = request.user.tmo_officer_profile
    except TMOOfficer.DoesNotExist:
        messages.error(request, 'TMO Officer profile not found.')
        return redirect('tmo:dashboard')
    
    if request.method == 'POST':
        form = TMOOfficerProfileForm(request.POST, instance=officer)
        if form.is_valid():
            officer = form.save(commit=False)
            officer.profile_completed = True
            officer.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('tmo:profile')
    else:
        form = TMOOfficerProfileForm(instance=officer)
    
    context = {
        'officer': officer,
        'form': form,
    }
    
    return render(request, 'tmo/profile.html', context)


@login_required(login_url=reverse_lazy('users:all_login'))
@user_passes_test(is_tmo_officer, login_url=reverse_lazy('tmo:profile'))#dashboard
def change_password(request):
    """
    Password change view for TMO Officers
    """
    try:
        officer = request.user.tmo_officer_profile
    except TMOOfficer.DoesNotExist:
        messages.error(request, 'TMO Officer profile not found.')
        return redirect('tmo:profile')#dashboard
    
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            request.user.set_password(new_password)
            request.user.save()
            
            # Mark password as changed
            officer.has_changed_password = True
            officer.save()
            
            messages.success(
                request, 
                'Password changed successfully! Please login with your new password.'
            )
            return redirect('users:all_login')
    else:
        form = PasswordChangeForm(request.user)
    
    context = {
        'form': form,
        'officer': officer,
    }
    
    return render(request, 'tmo/change_password.html', context)