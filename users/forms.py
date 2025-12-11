from django import forms
from django.contrib.auth import get_user_model
from .models import BuyerProfile

User = get_user_model()


class BuyerRegistrationForm(forms.Form):
    full_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={"placeholder": "Full Name", "class": "form-control"}
        ),
    )

    address = forms.CharField(
        widget=forms.Textarea(
            attrs={"placeholder": "Address", "class": "form-control", "rows": 3}
        )
    )

    phone = forms.CharField(
        max_length=10,
        widget=forms.TextInput(
            attrs={"placeholder": "e.g. 9800000000", "class": "form-control"}
        ),
    )

    dob = forms.DateField(
        label="Date of Birth",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    )

    citizenship_file = forms.FileField(
        required=False,
        label="Citizenship Document",
        widget=forms.FileInput(
            attrs={"accept": ".pdf,.jpg,.jpeg,.png", "class": "form-control"}
        ),
    )

    nid_file = forms.FileField(
        required=False,
        label="NID Document",
        widget=forms.FileInput(attrs={"accept": ".pdf,.jpg,.jpeg,.png"}),
    )

    passport_photo = forms.ImageField(
        required=False,
        label="Passport Size Photo (required)",
        widget=forms.FileInput(
            attrs={"accept": ".jpg,.jpeg,.png", "class": "form-control"}
        ),
    )

    signature_image = forms.FileField(
        required=False,
        label="Signature",
        widget=forms.FileInput(
            attrs={"accept": ".jpeg,.jpg,.png", "Class": "form-control"}
        ),
    )

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"placeholder": "Email Address", "class": "form-control"}
        )
    )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if not phone.isdigit():
            raise forms.ValidationError("Phone number must contain only digits")
        if len(phone) != 10:
            raise forms.ValidationError("Phone number must be exactly 10 digits long")
        return phone

