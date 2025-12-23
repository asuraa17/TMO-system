from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import BuyerRegistrationForm
from .models import BuyerProfile
from datetime import date
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import uuid
from django.utils.text import get_valid_filename
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.urls import reverse_lazy


User = get_user_model()

# Create your views here.


def is_tmo_officer(user):
    # check if the user is a TMO Officer
    return user.is_authenticated and user.role == "tmo_officer"


def is_buyer(user):
    # check if the user is a Buyer
    return user.is_authenticated and user.role == "buyer"


@login_required(login_url=reverse_lazy("users:buyer_login"))
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
            return redirect("users:buyer_login")

        except Exception as e:
            messages.error(request, f"Error creating user: {str(e)}")
            return redirect("users:buyer_register")

    return redirect("users:buyer_register")


def buyer_login(request):
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
                        return redirect('tmo:profile') #should go to tmo dashboard but for now since tmo dashboard hasnt been created yet
                    
                except Exception as e: 
                    messages.error(request, "TMO officer profile not found.")
                    return redirect('users:dashboard')

            else:
                #for other role, go to general dashboard
                messages.success(request, f"Welcome, {user.username}!")
                return redirect('users:dashboard')

        else:
            messages.error(request, "Invalid email or password.")

    return render(request, "users/buyer/login.html")


def buyer_logout(request):
    # buyer logout view
    logout(request)

    # Clear existing messages
    list(messages.get_messages(request))

    messages.success(request, "You have been logged out.")
    return redirect("users:buyer_login")


@login_required(login_url=reverse_lazy("users:buyer_login"))
@user_passes_test(is_buyer, login_url=reverse_lazy("users:buyer_login"))
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
