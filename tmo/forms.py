from django import forms
from django.contrib.auth import get_user_model
from .models import TMOOfficer

User = get_user_model()

class PasswordChangeForm(forms.Form):
    """
    Form for TMO Officers to change their password
    """
    
    current_password = forms.CharField(
        label='Current Password',
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Enter current password'
            }
        )
    )
    new_password = forms.CharField(
        min_length=8,
        label='New Password',
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Enter new password (min 8 characters)'
            }
        )
    )
    confirm_password = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Confirm new password'
            }
        )
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


class TMOOfficerProfileForm(forms.ModelForm):
    """
    Form for TMO Officers to update their profile
    """
    
    class Meta:
        model = TMOOfficer
        fields = ['full_name', 'phone']
        widgets = {
            'full_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Full Name'
                }
            ),
            'phone': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Phone Number'
                }
            ),
        }
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and not phone.isdigit():
            raise forms.ValidationError('Phone number must contain only digits.')
        if phone and len(phone) != 10:
            raise forms.ValidationError('Phone number must be exactly 10 digits.')
        return phone