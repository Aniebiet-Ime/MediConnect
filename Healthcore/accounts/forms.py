from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from .models import User, Profile, ProviderProfile

class UserRegistrationForm(UserCreationForm):
    # Form for user registration
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    user_type = forms.ChoiceField(choices=User.USER_TYPES, required=True)
    phone_number = forms.CharField(max_length=15, required=False)
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    
    
    class Meta:
        model = User
        fields = ('username','email','first_name','last_name','user_type','phone_number','date_of_birth','password1','password2')
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email
    
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.user_type = self.cleaned_data['user_type']
        user.phone_number = self.cleaned_data['phone_number']
        user.date_of_birth = self.cleaned_data['date_of_birth']    
        
        
        if commit:
            user.save()
        return user
    
    
class UserLoginForm(AuthenticationForm):
    #Custom login form using email instead of username
    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )        
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    ) 
    
class ProfileUpdateForm(forms.ModelForm):
    # Form for updating user profile
    
    class Meta:
        model = Profile
        fields = ('bio', 'address', 'city', 'state', 'zip_code', 'emergency_contact_name', 'emergency_contact_phone')
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }
        
class UserUpdateForm(forms.ModelForm):
    # Form for updating user basic information
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone_number', 'date_of_birth', 'profile_picture')
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        } 
             
class ProviderProfileForm(forms.ModelForm):
    # Form for provider-specific profile information
    
    class Meta:
        model = ProviderProfile
        fields = ('license_number', 'specialization', 'years_of_experience', 'hospital_affiliation', 'consultation_fee')
        widgets = {
            'consultation_fee': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }
        
               