from django import forms
from django.contrib.auth import get_user_model
from users.models import ShowroomProfile, Vehicle, BuyerProfile

User = get_user_model()


class ShowroomRegistrationForm(forms.Form):
    """Form for showroom registration"""
    
    # Business Information
    showroom_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Showroom Name'
        })
    )
    
    registration_number = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Business Registration Number'
        })
    )
    
    pan_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'PAN Number'
        })
    )
    
    # Contact Information
    address = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Showroom Address',
            'rows': 3
        })
    )
    
    phone = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Primary Phone Number'
        })
    )
    
    alternative_phone = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Alternative Phone Number (Optional)'
        })
    )
    
    # Owner Information
    owner_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Owner Full Name'
        })
    )
    
    owner_citizenship = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Owner Citizenship Number'
        })
    )
    
    # Documents
    registration_certificate = forms.FileField(
        required=False,
        label="Business Registration Certificate",
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf,.jpg,.jpeg,.png'
        })
    )
    
    pan_certificate = forms.FileField(
        required=False,
        label="PAN Registration Certificate",
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf,.jpg,.jpeg,.png'
        })
    )
    
    owner_citizenship_file = forms.FileField(
        required=False,
        label="Owner's Citizenship Document",
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf,.jpg,.jpeg,.png'
        })
    )
    
    showroom_photo = forms.ImageField(
        required=False,
        label="Showroom Photo",
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.jpg,.jpeg,.png'
        })
    )
    
    # Account Information
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address'
        })
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone.isdigit():
            raise forms.ValidationError('Phone number must contain only digits.')
        if len(phone) != 10:
            raise forms.ValidationError('Phone number must be exactly 10 digits.')
        return phone
    
    def clean_registration_number(self):
        reg_num = self.cleaned_data.get('registration_number')
        if ShowroomProfile.objects.filter(registration_number=reg_num).exists():
            raise forms.ValidationError('This registration number is already registered.')
        return reg_num


class ShowroomProfileUpdateForm(forms.ModelForm):
    """
    Form for updating showroom profile information
    Includes both User and ShowroomProfile fields
    """
    # User model fields
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'})
    )
    
    
    class Meta:
        model = ShowroomProfile
        fields = [
            'showroom_name', 'registration_number', 'pan_number',
            'address', 'phone', 'alternative_phone',
            'owner_name', 'owner_citizenship',
            'registration_certificate', 'pan_certificate',
            'owner_citizenship_file', 'showroom_photo'
        ]
        widgets = {
            'showroom_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Showroom Name'}),
            'registration_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Registration Number'}),
            'pan_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'PAN Number'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Address', 'rows': 3}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'alternative_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Alternative Phone'}),
            'owner_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Owner Name'}),
            'owner_citizenship': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Citizenship Number'}),
            'registration_certificate': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg,.png'}),
            'pan_certificate': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg,.png'}),
            'owner_citizenship_file': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg,.png'}),
            'showroom_photo': forms.FileInput(attrs={'class': 'form-control', 'accept': '.jpg,.jpeg,.png'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Pre-fill User fields if user is provided
        if self.user:
            self.fields['username'].initial = self.user.username
            self.fields['email'].initial = self.user.email
        
        # Make file fields not required for update
        self.fields['registration_certificate'].required = False
        self.fields['pan_certificate'].required = False
        self.fields['owner_citizenship_file'].required = False
        self.fields['showroom_photo'].required = False
    
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
    
    def clean_registration_number(self):
        reg_num = self.cleaned_data.get('registration_number')
        if self.instance and ShowroomProfile.objects.filter(
            registration_number=reg_num
        ).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('This registration number is already registered.')
        return reg_num


class ShowroomProfileUpdateFormVerified(forms.ModelForm):
    """
    Limited form for verified showrooms - can only update username and User fields
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
        model = ShowroomProfile
        fields = []  # No ShowroomProfile fields for verified users
    
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


class VehicleRegistrationForm(forms.ModelForm):
    """Form for vehicle registration by showroom"""
    
    # Buyer selection
    buyer_email = forms.EmailField(
        label="Buyer Email",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter buyer email address'
        }),
        help_text="Enter the email of the verified buyer purchasing this vehicle"
    )
    
    class Meta:
        model = Vehicle
        fields = [
            'chassis_number', 'engine_number', 'make', 'model', 'year',
            'color', 'vehicle_type', 'fuel_type', 'engine_cc', 'seating_capacity',
            'photo_front', 'photo_back', 'photo_left', 'photo_right',
            'price', 'payment_receipt'
        ]
        widgets = {
            'chassis_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Chassis Number'}),
            'engine_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Engine Number'}),
            'make': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Toyota'}),
            'model': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Corolla'}),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '2024'}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., White'}),
            'vehicle_type': forms.Select(attrs={'class': 'form-control'}),
            'fuel_type': forms.Select(attrs={'class': 'form-control'}),
            'engine_cc': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 1500'}),
            'seating_capacity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 5'}),
            'photo_front': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'photo_back': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'photo_left': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'photo_right': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'}),
            'payment_receipt': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg,.png'}),
        }
    
    def clean_buyer_email(self):
        email = self.cleaned_data.get('buyer_email')
        try:
            user = User.objects.get(email=email, role='buyer')
            buyer_profile = user.buyer_profile
            
            if buyer_profile.verification_status != 'verified':
                raise forms.ValidationError(
                    f'Buyer is not verified. Current status: {buyer_profile.get_verification_status_display()}'
                )
            
            return buyer_profile
        except User.DoesNotExist:
            raise forms.ValidationError('No buyer found with this email.')
        except BuyerProfile.DoesNotExist:
            raise forms.ValidationError('Buyer profile not found for this email.')
    
    def clean_chassis_number(self):
        chassis = self.cleaned_data.get('chassis_number')
        if Vehicle.objects.filter(chassis_number=chassis).exists():
            raise forms.ValidationError('This chassis number is already registered.')
        return chassis
    
    def clean_year(self):
        from datetime import date
        year = self.cleaned_data.get('year')
        current_year = date.today().year
        if year < 1900 or year > current_year + 1:
            raise forms.ValidationError(f'Year must be between 1900 and {current_year + 1}.')
        return year


class ShowroomPasswordChangeForm(forms.Form):
    """Form for showroom to change password"""
    
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