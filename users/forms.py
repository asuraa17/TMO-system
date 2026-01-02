from datetime import date
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

    def clean_dob(self):
        dob = self.cleaned_data.get("dob")

        if not dob:
            raise forms.ValidationError("Date of birth is required")
        
        today = date.today()

        if dob > today:
            raise forms.ValidationError("Date of birth cannot be in the future")
        
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

        if age < 18:
            raise forms.ValidationError(f"You must be at least 18 years old to register")
        
        return dob    
    
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

class BuyerProfileUpdateForm(forms.ModelForm):
    """
    Form for updating buyer profile information
    Includes both User and BuyerProfile fields
    """
    # User model fields
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'})
    )
    
    first_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )
    
    last_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
    )
    
    # BuyerProfile model fields
    class Meta:
        model = BuyerProfile
        fields = ['full_name', 'address', 'phone', 'dob', 
                  'citizenship_file', 'nid_file', 'passport_photo', 'signature_image']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Address', 'rows': 3}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'dob': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'citizenship_file': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg,.png'}),
            'nid_file': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg,.png'}),
            'passport_photo': forms.FileInput(attrs={'class': 'form-control', 'accept': '.jpg,.jpeg,.png'}),
            'signature_image': forms.FileInput(attrs={'class': 'form-control', 'accept': '.jpg,.jpeg,.png'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Pre-fill User fields if user is provided
        if self.user:
            self.fields['username'].initial = self.user.username
            self.fields['email'].initial = self.user.email
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
        
        # Make file fields not required for update (only if changing)
        self.fields['citizenship_file'].required = False
        self.fields['nid_file'].required = False
        self.fields['passport_photo'].required = False
        self.fields['signature_image'].required = False
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if self.user and User.objects.filter(username=username).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError('This username is already taken.')
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if self.user and User.objects.filter(email=email).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError('This email is already registered.')
        return email
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone.isdigit():
            raise forms.ValidationError('Phone number must contain only digits.')
        if len(phone) != 10:
            raise forms.ValidationError('Phone number must be exactly 10 digits.')
        return phone
    
    def clean_dob(self):
        dob = self.cleaned_data.get('dob')
        if not dob:
            raise forms.ValidationError('Date of birth is required.')
        
        today = date.today()
        if dob > today:
            raise forms.ValidationError('Date of birth cannot be in the future.')
        
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        if age < 18:
            raise forms.ValidationError('You must be at least 18 years old.')
        
        return dob


class BuyerPasswordChangeForm(forms.Form):
    """
    Form for buyers to change their password
    """
    current_password = forms.CharField(
        label='Current Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter current password'
        })
    )
    
    new_password = forms.CharField(
        min_length=8,
        label='New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new password (min 8 characters)'
        })
    )
    
    confirm_password = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password'
        })
    )
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if not self.user.check_password(current_password):
            raise forms.ValidationError('Current password is incorrect.')
        return current_password
    
    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if new_password and confirm_password:
            if new_password != confirm_password:
                raise forms.ValidationError('New passwords do not match.')
        
        return cleaned_data


class BuyerProfileUpdateFormVerified(forms.ModelForm):
    """
    Limited form for verified buyers - can only update username and User fields
    Profile details are locked
    """
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'})
    )
    
    class Meta:
        model = BuyerProfile
        fields = []  # No BuyerProfile fields for verified users
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            self.fields['username'].initial = self.user.username
            self.fields['email'].initial = self.user.email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if self.user and User.objects.filter(username=username).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError('This username is already taken.')
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if self.user and User.objects.filter(email=email).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError('This email is already registered.')
        return email