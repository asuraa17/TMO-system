from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.urls import reverse_lazy
from .models import TMOOfficer
from users.models import BuyerProfile
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
@user_passes_test(is_tmo_officer, login_url=reverse_lazy('tmo:dashboard'))
def change_password(request):
    """
    Password change view for TMO Officers
    """
    try:
        officer = request.user.tmo_officer_profile
    except TMOOfficer.DoesNotExist:
        messages.error(request, 'TMO Officer profile not found.')
        return redirect('tmo:dashboard')
    
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

@login_required(login_url=reverse_lazy('users:all_login'))
@user_passes_test(is_tmo_officer, login_url=reverse_lazy('users:dashboard'))
def tmo_dashboard(request):
    """
    TMO Officer Dashboard
    """
    try:
        officer = request.user.tmo_officer_profile
    except TMOOfficer.DoesNotExist:
        messages.error(request, 'TMO Officer profile not found.')
        return redirect('users:dashboard')
    
    # Get statistics
    pending_buyers = BuyerProfile.objects.filter(verification_status='pending').count()
    verified_buyers = BuyerProfile.objects.filter(verification_status='verified').count()
    rejected_buyers = BuyerProfile.objects.filter(verification_status='rejected').count()
    
    context = {
        'officer': officer,
        'pending_buyers': pending_buyers,
        'verified_buyers': verified_buyers,
        'rejected_buyers': rejected_buyers,
    }
    
    return render(request, 'tmo/dashboard.html', context)

@login_required(login_url=reverse_lazy('users:all_login'))
@user_passes_test(is_tmo_officer, login_url=reverse_lazy('users:dashboard'))
def buyer_verification_list(request):
    """
    List all buyers for verification
    """
    try:
        officer = request.user.tmo_officer_profile
    except TMOOfficer.DoesNotExist:
        messages.error(request, 'TMO Officer profile not found.')
        return redirect('users:dashboard')
    
    # Filter by status if provided
    status = request.GET.get('status', 'pending')
    
    if status == 'all':
        buyers = BuyerProfile.objects.all().order_by('-created_at')
    else:
        buyers = BuyerProfile.objects.filter(verification_status=status).order_by('-created_at')
    
    context = {
        'officer': officer,
        'buyers': buyers,
        'current_status': status,
    }
    
    return render(request, 'tmo/buyer_verification_list.html', context)


@login_required(login_url=reverse_lazy('users:all_login'))
@user_passes_test(is_tmo_officer, login_url=reverse_lazy('users:dashboard'))
def buyer_verification_detail(request, buyer_id):
    """
    View detailed information about a buyer for verification
    """
    try:
        officer = request.user.tmo_officer_profile
    except TMOOfficer.DoesNotExist:
        messages.error(request, 'TMO Officer profile not found.')
        return redirect('users:dashboard')
    
    buyer = get_object_or_404(BuyerProfile, id=buyer_id)
    
    context = {
        'officer': officer,
        'buyer': buyer,
    }
    
    return render(request, 'tmo/buyer_verification_detail.html', context)

@login_required(login_url=reverse_lazy('users:all_login'))
@user_passes_test(is_tmo_officer, login_url=reverse_lazy('users:dashboard'))
def verify_buyer(request, buyer_id):
    """
    Approve a buyer's registration
    Can be done for pending or rejected buyers
    Once verified, cannot be changed unless by admin
    """
    if request.method == 'POST':
        buyer = get_object_or_404(BuyerProfile, id=buyer_id)
        officer = request.user.tmo_officer_profile
        
        # Only allow verification for pending or rejected buyers
        if buyer.verification_status == 'verified':
            messages.error(request, 'This buyer is already verified and cannot be modified.')
            return redirect('tmo:buyer_verification_detail', buyer_id=buyer_id)
        
        buyer.verification_status = 'verified'
        buyer.verified_by = officer
        buyer.verification_remarks = request.POST.get('remarks', '')
        buyer.save()
        
        messages.success(request, f'Buyer {buyer.full_name} has been verified successfully.')
        return redirect('tmo:buyer_verification_list')
    
    return redirect('tmo:buyer_verification_detail', buyer_id=buyer_id)


@login_required(login_url=reverse_lazy('users:all_login'))
@user_passes_test(is_tmo_officer, login_url=reverse_lazy('users:dashboard'))
def reject_buyer(request, buyer_id):
    """
    Reject a buyer's registration
    Buyer can update their details and resubmit for verification
    """
    if request.method == 'POST':
        buyer = get_object_or_404(BuyerProfile, id=buyer_id)
        officer = request.user.tmo_officer_profile
        
        # Only allow rejection for pending or rejected buyers (re-rejection with new remarks)
        if buyer.verification_status == 'verified':
            messages.error(request, 'This buyer is already verified and cannot be rejected.')
            return redirect('tmo:buyer_verification_detail', buyer_id=buyer_id)
        
        remarks = request.POST.get('remarks', '').strip()
        
        if not remarks:
            messages.error(request, 'Rejection remarks are required.')
            return redirect('tmo:buyer_verification_detail', buyer_id=buyer_id)
        
        buyer.verification_status = 'rejected'
        buyer.verified_by = officer
        buyer.verification_remarks = remarks
        buyer.save()
        
        messages.success(request, f'Buyer {buyer.full_name} has been rejected. They can update their details and resubmit.')
        return redirect('tmo:buyer_verification_list')
    
    return redirect('tmo:buyer_verification_detail', buyer_id=buyer_id)