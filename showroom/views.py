from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from users.models import ShowroomProfile, Vehicle, VehicleOwnershipHistory
from .forms import ShowroomRegistrationForm, VehicleRegistrationForm, ShowroomProfileUpdateForm, ShowroomProfileUpdateFormVerified, ShowroomPasswordChangeForm
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils.text import get_valid_filename
from django.conf import settings
import uuid
from datetime import date

# Create your views here.


User = get_user_model()


def is_showroom(user):
    """Check if user is a showroom"""
    return user.is_authenticated and user.role == 'showroom'


def showroom_register(request):
    """Showroom registration view"""
    preview_data = request.session.get("from_preview", False)

    if request.method == "POST":
        form = ShowroomRegistrationForm(request.POST, request.FILES)

        if form.is_valid():
            request.session["from_preview"] = True

            # Store form data in session
            request.session["showroom_registration_data"] = {
                "showroom_name": form.cleaned_data["showroom_name"],
                "registration_number": form.cleaned_data["registration_number"],
                "pan_number": form.cleaned_data["pan_number"],
                "address": form.cleaned_data["address"],
                "phone": form.cleaned_data["phone"],
                "alternative_phone": form.cleaned_data.get("alternative_phone", ""),
                "owner_name": form.cleaned_data["owner_name"],
                "owner_citizenship": form.cleaned_data["owner_citizenship"],
                "email": form.cleaned_data["email"],
            }

            # Handle file uploads
            temp_files = request.session.get("showroom_temp_files", {})
            file_names = request.session.get("showroom_file_names", {})

            for field in [
                "registration_certificate",
                "pan_certificate",
                "owner_citizenship_file",
                "showroom_photo",
            ]:
                file = form.cleaned_data.get(field)
                if file:
                    if temp_files.get(field):
                        default_storage.delete(temp_files[field])

                    safe_name = get_valid_filename(file.name)
                    unique_name = f"{uuid.uuid4()}_{safe_name}"
                    temp_path = default_storage.save(f"temp/{unique_name}", file)

                    temp_files[field] = temp_path
                    file_names[field] = file.name

            request.session["showroom_temp_files"] = temp_files
            request.session["showroom_file_names"] = file_names

            return redirect("showroom:register_preview")
    else:
        registration_data = request.session.get("showroom_registration_data")

        if registration_data and preview_data:
            form = ShowroomRegistrationForm(initial=registration_data)
        else:
            request.session.pop("showroom_registration_data", None)
            request.session.pop("showroom_temp_files", None)
            request.session.pop("showroom_file_names", None)
            form = ShowroomRegistrationForm()

    request.session.pop("from_preview", None)

    return render(
        request,
        "showroom/register.html",
        {"form": form, "MEDIA_URL": settings.MEDIA_URL},
    )


def showroom_register_preview(request):
    """Preview showroom registration"""
    registration_data = request.session.get("showroom_registration_data")
    file_names = request.session.get("showroom_file_names")

    if not registration_data:
        messages.error(request, "No registration data found. Please fill the form.")
        return redirect("showroom:register")

    request.session["from_preview"] = True

    context = {"data": registration_data, "files": file_names}
    return render(request, "showroom/register_preview.html", context)


def showroom_register_submit(request):
    """Submit showroom registration"""
    if request.method == "POST":
        registration_data = request.session.get("showroom_registration_data")
        temp_files = request.session.get("showroom_temp_files")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if not registration_data or not temp_files:
            messages.error(request, "Session expired. Please register again.")
            return redirect("showroom:register")

        if not password or not confirm_password or password != confirm_password:
            context = {
                "data": registration_data,
                "files": request.session.get("showroom_file_names"),
                "error": "Passwords do not match. Please try again.",
            }
            return render(request, "showroom/register_preview.html", context)

        try:
            # Create user
            user = User.objects.create_user(
                username=registration_data["email"],
                email=registration_data["email"],
                password=password,
                role=User.Role.Showroom,
            )

            # Create showroom profile
            showroom_profile = ShowroomProfile.objects.create(
                user=user,
                showroom_name=registration_data["showroom_name"],
                registration_number=registration_data["registration_number"],
                pan_number=registration_data["pan_number"],
                address=registration_data["address"],
                phone=registration_data["phone"],
                alternative_phone=registration_data.get("alternative_phone", ""),
                owner_name=registration_data["owner_name"],
                owner_citizenship=registration_data["owner_citizenship"],
            )

            # Move files from temp to showroom_docs
            for field, temp_path in temp_files.items():
                if temp_path:
                    filename = temp_path.split("/")[-1]
                    with default_storage.open(temp_path, "rb") as f:
                        getattr(showroom_profile, field).save(filename, ContentFile(f.read()))

            showroom_profile.save()

            # Clean up temp files
            for path in temp_files.values():
                if path:
                    default_storage.delete(path)

            # Clear session
            del request.session["showroom_registration_data"]
            del request.session["showroom_temp_files"]
            del request.session["showroom_file_names"]

            messages.success(request, "Registration successful! You can now log in.")
            return redirect("users:all_login")

        except Exception as e:
            messages.error(request, f"Error creating showroom: {str(e)}")
            return redirect("showroom:register")

    return redirect("showroom:register")


@login_required(login_url=reverse_lazy("users:all_login"))
@user_passes_test(is_showroom, login_url=reverse_lazy("users:dashboard"))
def showroom_dashboard(request):
    """Showroom dashboard"""
    try:
        showroom = request.user.showroom_profile
    except ShowroomProfile.DoesNotExist:
        messages.error(request, "Showroom profile not found.")
        return redirect("users:dashboard")

    # Get statistics
    total_vehicles = Vehicle.objects.filter(showroom=showroom).count()
    pending_vehicles = Vehicle.objects.filter(verification_status='pending').count()
    verified_vehicles = Vehicle.objects.filter(verification_status='verified').count()
    rejected_vehicles = Vehicle.objects.filter(verification_status='rejected').count()

    context = {
        "showroom": showroom,
        "total_vehicles": total_vehicles,
        "pending_vehicles": pending_vehicles,
        "verified_vehicles": verified_vehicles,
        "rejected_vehicles": rejected_vehicles,
    }

    return render(request, "showroom/dashboard.html", context)


@login_required(login_url=reverse_lazy("users:all_login"))
@user_passes_test(is_showroom, login_url=reverse_lazy("users:dashboard"))
def showroom_profile(request):
    """Showroom profile view and update"""
    try:
        showroom = request.user.showroom_profile
    except ShowroomProfile.DoesNotExist:
        messages.error(request, "Showroom profile not found.")
        return redirect("showroom:dashboard")
    
    is_verified = showroom.verification_status == 'verified'
    
    if request.method == 'POST':
        if is_verified:
            # Use limited form for verified showrooms
            form = ShowroomProfileUpdateFormVerified(
                request.POST,
                instance=showroom,
                user=request.user
            )
        else:
            # Use full form for pending/rejected showrooms
            form = ShowroomProfileUpdateForm(
                request.POST,
                request.FILES,
                instance=showroom,
                user=request.user
            )
        
        if form.is_valid():
            # Update User model fields
            request.user.username = form.cleaned_data['username']
            request.user.email = form.cleaned_data['email']
            request.user.first_name = form.cleaned_data.get('first_name', '')
            request.user.last_name = form.cleaned_data.get('last_name', '')
            request.user.save()
            
            # Save ShowroomProfile
            form.save()
            
            if showroom.verification_status == 'rejected':
                messages.success(
                    request,
                    'Profile updated successfully! Your profile has been resubmitted for verification.'
                )
            else:
                messages.success(request, 'Profile updated successfully!')
            
            return redirect('showroom:profile')
    else:
        if is_verified:
            form = ShowroomProfileUpdateFormVerified(
                instance=showroom,
                user=request.user
            )
        else:
            form = ShowroomProfileUpdateForm(
                instance=showroom,
                user=request.user
            )
    
    context = {
        'form': form,
        'showroom': showroom,
        'is_verified': is_verified,
    }
    
    return render(request, 'showroom/profile.html', context)


@login_required(login_url=reverse_lazy("users:all_login"))
@user_passes_test(is_showroom, login_url=reverse_lazy("users:dashboard"))
def vehicle_register(request):
    """Register a new vehicle"""
    try:
        showroom = request.user.showroom_profile
    except ShowroomProfile.DoesNotExist:
        messages.error(request, "Showroom profile not found.")
        return redirect("users:dashboard")

    # Check if showroom is verified
    if showroom.verification_status != 'verified':
        messages.error(
            request,
            f"Your showroom is not verified yet. Current status: {showroom.get_verification_status_display()}"
        )
        return redirect("showroom:dashboard")

    if request.method == "POST":
        form = VehicleRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            vehicle = form.save(commit=False)
            vehicle.showroom = showroom
            
            # Get buyer from cleaned data
            buyer_profile = form.cleaned_data['buyer_email']
            vehicle.current_owner = buyer_profile
            
            # Generate temporary plate number
            vehicle.temporary_plate_number = f"TEMP-{uuid.uuid4().hex[:8].upper()}"
            
            vehicle.save()

            # Create ownership history
            VehicleOwnershipHistory.objects.create(
                vehicle=vehicle,
                owner=buyer_profile,
                is_current_owner=True,
                purchase_date=date.today(),
                purchase_price=vehicle.price,
            )

            messages.success(
                request,
                f"Vehicle registered successfully! Temporary plate: {vehicle.temporary_plate_number}"
            )
            return redirect("showroom:vehicle_list")
    else:
        form = VehicleRegistrationForm()

    context = {"form": form, "showroom": showroom}
    return render(request, "showroom/vehicle_register.html", context)

# showroom/views.py - Fixed vehicle_list to use verification_status

@login_required(login_url=reverse_lazy("users:all_login"))
@user_passes_test(is_showroom, login_url=reverse_lazy("users:dashboard"))
def vehicle_list(request):
    """List all vehicles registered by this showroom"""
    try:
        showroom = request.user.showroom_profile
    except ShowroomProfile.DoesNotExist:
        messages.error(request, "Showroom profile not found.")
        return redirect("users:dashboard")

    # Filter by verification status if provided
    status = request.GET.get('status', 'all')
    
    # FIXED: Use verification_status instead of is_verified
    if status == 'verified':
        vehicles = Vehicle.objects.filter(
            showroom=showroom, 
            verification_status='verified'
        ).order_by('-created_at')
    elif status == 'pending':
        vehicles = Vehicle.objects.filter(
            showroom=showroom, 
            verification_status='pending'
        ).order_by('-created_at')
    elif status == 'rejected':
        vehicles = Vehicle.objects.filter(
            showroom=showroom, 
            verification_status='rejected'
        ).order_by('-created_at')
    else:
        vehicles = Vehicle.objects.filter(showroom=showroom).order_by('-created_at')

    context = {
        "showroom": showroom,
        "vehicles": vehicles,
        "current_status": status,
    }

    return render(request, "showroom/vehicle_list.html", context)

@login_required(login_url=reverse_lazy("users:all_login"))
@user_passes_test(is_showroom, login_url=reverse_lazy("users:dashboard"))
def vehicle_detail(request, vehicle_id):
    """View vehicle details"""
    try:
        showroom = request.user.showroom_profile
    except ShowroomProfile.DoesNotExist:
        messages.error(request, "Showroom profile not found.")
        return redirect("users:dashboard")

    vehicle = get_object_or_404(Vehicle, id=vehicle_id, showroom=showroom)

    # Get ownership history
    ownership_history = vehicle.ownership_history.all().order_by('-purchase_date')

    context = {
        "showroom": showroom,
        "vehicle": vehicle,
        "ownership_history": ownership_history,
    }

    return render(request, "showroom/vehicle_detail.html", context)


@login_required(login_url=reverse_lazy("users:all_login"))
@user_passes_test(is_showroom, login_url=reverse_lazy("users:dashboard"))
def showroom_change_password(request):
    """Change showroom password"""
    try:
        showroom = request.user.showroom_profile
    except ShowroomProfile.DoesNotExist:
        messages.error(request, "Showroom profile not found.")
        return redirect("users:dashboard")

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