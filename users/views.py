from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from showroom.forms import ShowroomPasswordChangeForm
from showroom.views import is_showroom
from tmo.forms import PasswordChangeForm
from tmo.models import TMOOfficer
from .forms import BuyerPasswordChangeForm, BuyerProfileUpdateForm, BuyerProfileUpdateFormVerified, BuyerRegistrationForm
from .models import BuyerProfile, ShowroomProfile
from datetime import date
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import uuid
from django.utils.text import get_valid_filename
from django.conf import settings
from django.urls import reverse_lazy


User = get_user_model()

# Create your views here.


def is_tmo_officer(user):
    # check if the user is a TMO Officer
    return user.is_authenticated and user.role == "tmo_officer"


def is_buyer(user):
    # check if the user is a Buyer
    return user.is_authenticated and user.role == "buyer"


@login_required(login_url=reverse_lazy("users:all_login"))
def dashboard(request):
    # dashbaord view for all authenticated users
    context = {
        "user": request.user,
        "role": request.user.get_role_display(),
    }
    return render(request, "users/dashboard.html", context)

def buyer_register(request):
    # view for buyer registration

    preview_data = request.session.get("from_preview", False)

    if request.method == "POST":
        form = BuyerRegistrationForm(request.POST, request.FILES)


        if form.is_valid():

            request.session["from_preview"] = True

            # store form data in session for preview (text data only, no password)
            request.session["registration_data"] = {
                "full_name": form.cleaned_data["full_name"],
                "address": form.cleaned_data["address"],
                "phone": form.cleaned_data["phone"],
                "dob": form.cleaned_data["dob"].isoformat(),
                "email": form.cleaned_data["email"],
            }

            # TEMPORARY FILE STORAGE
            temp_files = request.session.get("temp_files", {})
            file_names = request.session.get("file_names", {})

            for field in [
                "citizenship_file",
                "nid_file",
                "passport_photo",
                "signature_image",
            ]:
                file = form.cleaned_data.get(field)
                if file:
                    if temp_files.get(field):
                        # delete old temp file
                        default_storage.delete(temp_files[field])

                    # save temp file with safe unique filename
                    safe_name = get_valid_filename(file.name)
                    unique_name = f"{uuid.uuid4()}_{safe_name}"
                    temp_path = default_storage.save(f"temp/{unique_name}", file)

                    temp_files[field] = temp_path
                    file_names[field] = file.name  # keep original name for preview

            request.session["temp_files"] = temp_files
            request.session["file_names"] = file_names

            return redirect("users:buyer_register_preview")
    else:
        registration_data = request.session.get("registration_data")

        if registration_data and preview_data:
            # pre-fill form with session data
            dob_str = registration_data.get("dob")
            dob_obj = date.fromisoformat(dob_str) if dob_str else None

            form = BuyerRegistrationForm(
                initial={
                    "full_name": registration_data.get("full_name"),
                    "address": registration_data.get("address"),
                    "phone": registration_data.get("phone"),
                    "dob": dob_obj,
                    "email": registration_data.get("email"),
                }
            )
        else:
            request.session.pop("registration_data", None)
            request.session.pop("temp_files", None) 
            request.session.pop("file_names", None)

            form = BuyerRegistrationForm()

    request.session.pop("from_preview", None)

    return render(
        request,
        "users/buyer/registration_form.html",
        {
            "form": form,
            "MEDIA_URL": settings.MEDIA_URL,  # pass MEDIA_URL to template
        },
    )


def buyer_register_preview(request):
    # preview page before final submission of buyer registration
    registration_data = request.session.get("registration_data")
    file_names = request.session.get("file_names")

    if not registration_data:
        messages.error(
            request, "No registration data found. Please fill the registration form."
        )
        return redirect("users:buyer_register")
    
    request.session["from_preview"] = True

    context = {
        "data": registration_data,
        "files": file_names,
    }
    return render(request, "users/buyer/registration_preview.html", context)


def buyer_register_submit(request):

    if request.method == "POST":
        registration_data = request.session.get("registration_data")
        temp_files = request.session.get("temp_files")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if not registration_data or not temp_files:
            messages.error(request, "Session expired. Please register again.")
            return redirect("users:buyer_register")
        
        if not password or not confirm_password or password != confirm_password:
            context = {
                "data": registration_data,
                "files": request.session.get("file_names"),
                "error": "Password do not match. Please try again"
            }
            return render(request,"users/buyer/registration_preview.html", context)
        
        try:
            # create user
            user = User.objects.create_user(
                username=registration_data["email"],
                email=registration_data["email"],
                password=password,
                role=User.Role.Buyer,
            )

            # create buyer profile
            buyer_profile = BuyerProfile.objects.create(
                user=user,
                full_name=registration_data["full_name"],
                address=registration_data["address"],
                phone=registration_data["phone"],
                dob=date.fromisoformat(registration_data["dob"]),
            )

            # MOVE FILES FROM temp/ TO buyer_docs/
            for field, temp_path in temp_files.items():
                if temp_path:
                    filename = temp_path.split("/")[-1]
                    with default_storage.open(temp_path, "rb") as f:
                        getattr(buyer_profile, field).save(
                            filename, ContentFile(f.read())
                        )

            buyer_profile.save()

            # remove temp files
            for path in temp_files.values():
                if path:
                    default_storage.delete(path)

            # clear session
            del request.session["registration_data"]
            del request.session["temp_files"]
            del request.session["file_names"]

            messages.success(request, "Registration successful! You can now log in.")
            return redirect("users:all_login")

        except Exception as e:
            messages.error(request, f"Error creating user: {str(e)}")
            return redirect("users:buyer_register")

    return redirect("users:buyer_register")


def all_login(request):
    #login view for both buyer and tmo
    if request.method == "POST":
        email_or_username = request.POST.get("email")
        password = request.POST.get("password")

        # authenticate using email as username
        user = authenticate(request, username=email_or_username, password=password)

        if user is not None:
            login(request, user)

            #redirect based on role
            if user.role == "buyer":
                messages.success(request, f"Welcome, {user.username}!")
                # go to next page if there is after login, else go to buyer home
                next_url = request.GET.get('next', reverse_lazy("users:buyer_home"))
                return redirect(next_url)
            
            elif user.role == "tmo_officer":
                messages.success(request, f"Welcome, {user.username}!")

                #check for tmo officer profile
                try:
                    officer = user.tmo_officer_profile
                    
                    #if password not changed, redirect to change password
                    if not officer.has_changed_password:
                        return redirect('tmo:change_password')
                    else:
                        return redirect('tmo:dashboard') #should go to tmo dashboard but for now since tmo dashboard hasnt been created yet
                    
                except Exception: 
                    messages.error(request, "TMO officer profile not found.")
                    return redirect('users:dashboard')
                
            elif user.role == "showroom":
                messages.success(request, f"Welcome, {user.username}!")
                return redirect('showroom:dashboard')
                    
            else:
                #for other role, go to general dashboard
                messages.success(request, f"Welcome, {user.username}!")
                return redirect('users:dashboard')

        else:
            messages.error(request, "Invalid email or password.")

    return render(request, "users/buyer/login.html")


def all_logout(request):
    # logout view for both buyer and tmo
    logout(request)

    # Clear existing messages
    list(messages.get_messages(request))

    messages.success(request, "You have been logged out.")
    return redirect("users:all_login")


@login_required(login_url=reverse_lazy("users:all_login"))
@user_passes_test(is_buyer, login_url=reverse_lazy("users:dashboard"))
def buyer_home(request):
    # buyer home/dashboard view
    try:
        buyer_profile = request.user.buyer_profile
    except BuyerProfile.DoesNotExist:
        buyer_profile = None

    context = {
        "user": request.user,
        "profile": buyer_profile,
    }
    return render(request, "users/buyer/home.html", context)


@login_required(login_url=reverse_lazy("users:all_login"))
@user_passes_test(is_buyer, login_url=reverse_lazy("users:dashboard"))
def buyer_profile_update(request):
    """
    View for buyer to update profile information
    Verified buyers can only update User fields (username, email)
    Pending/Rejected buyers can update all fields
    """
    try:
        buyer_profile = request.user.buyer_profile
    except BuyerProfile.DoesNotExist:
        messages.error(request, "Buyer profile not found.")
        return redirect("users:buyer_home")
    
    is_verified = buyer_profile.verification_status == 'verified'
    
    if request.method == 'POST':
        if is_verified:
            # Use limited form for verified users
            form = BuyerProfileUpdateFormVerified(
                request.POST, 
                instance=buyer_profile,
                user=request.user
            )
        else:
            # Use full form for pending/rejected users
            form = BuyerProfileUpdateForm(
                request.POST, 
                request.FILES,
                instance=buyer_profile,
                user=request.user
            )
        
        if form.is_valid():
            # Update User model fields
            request.user.username = form.cleaned_data['username']
            request.user.email = form.cleaned_data['email']
            request.user.first_name = form.cleaned_data.get('first_name', '')
            request.user.last_name = form.cleaned_data.get('last_name', '')
            request.user.save()
            
            # Save BuyerProfile
            form.save()
            
            if buyer_profile.verification_status == 'rejected':
                messages.success(
                    request, 
                    'Profile updated successfully! Your profile has been resubmitted for verification.'
                )
            else:
                messages.success(request, 'Profile updated successfully!')
            
            return redirect('users:buyer_home')
    else:
        if is_verified:
            form = BuyerProfileUpdateFormVerified(
                instance=buyer_profile,
                user=request.user
            )
        else:
            form = BuyerProfileUpdateForm(
                instance=buyer_profile,
                user=request.user
            )
    
    context = {
        'form': form,
        'profile': buyer_profile,
        'is_verified': is_verified,
    }
    
    return render(request, 'users/buyer/profile_update.html', context)

@login_required(login_url=reverse_lazy("users:all_login"))
@user_passes_test(is_buyer, login_url=reverse_lazy("users:dashboard"))
def buyer_change_password(request):
    """View for buyer to change password"""
    try:
        buyer_profile = request.user.buyer_profile
    except BuyerProfile.DoesNotExist:
        messages.error(request, "Buyer profile not found.")
        return redirect("users:buyer_home")
    
    if request.method == 'POST':
        form = BuyerPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            request.user.set_password(new_password)
            request.user.save()
            
            messages.success(
                request,
                'Password changed successfully! Please login with your new password.'
            )
            return redirect('users:all_login')
    else:
        form = BuyerPasswordChangeForm(request.user)
    
    context = {
        'form': form,
        'profile': buyer_profile,
    }
    
    return render(request, 'users/buyer/change_password.html', context)

@login_required(login_url=reverse_lazy("users:all_login"))
@user_passes_test(is_showroom, login_url=reverse_lazy("users:dashboard"))
def showroom_change_password(request):
    """Change showroom password"""
    try:
        showroom = request.user.showroom_profile
    except ShowroomProfile.DoesNotExist:
        messages.error(request, "Showroom profile not found.")
        return redirect("showroom:dashboard")  # Fixed: was users:dashboard

    if request.method == 'POST':
        form = ShowroomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            request.user.set_password(new_password)
            request.user.save()

            messages.success(
                request,
                'Password changed successfully! Please login with your new password.'
            )
            return redirect('users:all_login')
    else:
        form = ShowroomPasswordChangeForm(request.user)

    context = {'form': form, 'showroom': showroom}
    return render(request, 'showroom/change_password.html', context)


@login_required(login_url=reverse_lazy('users:all_login'))
@user_passes_test(is_tmo_officer, login_url=reverse_lazy('users:dashboard'))
def change_password(request):
    """Password change view for TMO Officers"""
    try:
        officer = request.user.tmo_officer_profile
    except TMOOfficer.DoesNotExist:
        messages.error(request, 'TMO Officer profile not found.')
        return redirect('tmo:dashboard')  # Fixed: was users:dashboard
    
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

@login_required(login_url=reverse_lazy("users:all_login"))
@user_passes_test(is_buyer, login_url=reverse_lazy("users:dashboard"))
def buyer_vehicles(request):
    """
    View for buyer to see their registered vehicles
    Only shows vehicles owned by the current buyer
    """
    try:
        buyer_profile = request.user.buyer_profile
    except BuyerProfile.DoesNotExist:
        messages.error(request, "Buyer profile not found.")
        return redirect("users:buyer_home")
    
    # Check if buyer is verified
    if buyer_profile.verification_status != 'verified':
        messages.warning(
            request,
            f"Your profile must be verified to view vehicles. Current status: {buyer_profile.get_verification_status_display()}"
        )
        return redirect("users:buyer_home")
    
    # Get all vehicles owned by this buyer
    from users.models import Vehicle
    vehicles = Vehicle.objects.filter(current_owner=buyer_profile).order_by('-created_at')
    
    # Get statistics
    total_vehicles = vehicles.count()
    verified_vehicles = vehicles.filter(verification_status='verified').count()
    pending_vehicles = vehicles.filter(verification_status='pending').count()
    
    context = {
        'buyer_profile': buyer_profile,
        'vehicles': vehicles,
        'total_vehicles': total_vehicles,
        'verified_vehicles': verified_vehicles,
        'pending_vehicles': pending_vehicles,
    }
    
    return render(request, 'users/buyer/my_vehicles.html', context)


@login_required(login_url=reverse_lazy("users:all_login"))
@user_passes_test(is_buyer, login_url=reverse_lazy("users:dashboard"))
def buyer_vehicle_detail(request, vehicle_id):
    """
    View for buyer to see detailed information about their vehicle
    """
    try:
        buyer_profile = request.user.buyer_profile
    except BuyerProfile.DoesNotExist:
        messages.error(request, "Buyer profile not found.")
        return redirect("users:buyer_home")
    
    # Get vehicle and ensure it belongs to this buyer
    from users.models import Vehicle
    vehicle = get_object_or_404(
        Vehicle, 
        id=vehicle_id, 
        current_owner=buyer_profile
    )
    
    # Get ownership history
    ownership_history = vehicle.ownership_history.all().order_by('-purchase_date')
    
    context = {
        'buyer_profile': buyer_profile,
        'vehicle': vehicle,
        'ownership_history': ownership_history,
    }
    
    return render(request, 'users/buyer/vehicle_detail.html', context)