from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.utils.decorators import method_decorator 
from django.views.decorators.csrf import csrf_protect
from django.utils.crypto import get_random_string
from django.core.mail import send_mail 
from django.conf import settings
from .forms import (UserRegistrationForm, UserLoginForm, ProfileUpdateForm, UserUpdateForm, ProviderProfileForm)
from .models import User, Profile, ProviderProfile 
from functools import wraps
from django.http import HttpResponseForbidden

# Create your views here.
class CustomLoginView(LoginView):
    # Custom login view using email authentication
    form_class = UserLoginForm
    template_name = 'accounts/login.html'
    
    def form_valid(self, form):
        user = form.get_user()
        if not user.is_email_verified:
            messages.error(self.request, 'Please verify your email address before logging in.')
            return redirect('accounts:login')
        return super().form_valid(form)

    def get_success_url(self):
        if self.request.user.user_type == 'patient':
            return reverse_lazy('patient_dashboard')
        elif self.request.user.user_type == 'provider':
            return reverse_lazy('provider_dashboard')
        else:
            return reverse_lazy('admin_dashboard')
        
class RegisterView(CreateView):
    # User Registration View
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')
    
    
    def form_valid(self, form):
        user = form.save()
        
        # Generate email verification token
        token = get_random_string(32)
        user.email_verification_token = token
        user.save()
        
        # Send verification email
        self.send_verification_email(user, token)
        
        messages.success(self.request, 'Account created successfully! Please check your email to verify your account.')
        return super().form_valid(form)
    
    def send_verification_email(self, user, token):
        # Send email verification link
        subject = 'Verify your MediConnect account'
        message = f"""
        Hi {user.first_name},
        
                
        Please click the link below to verify your email address:
        {self.request.build_absolute_uri(f'/accounts/verify/{token}/')}
                
        if you didn't create this account, please ignore this email.
        
        
        Best regards,
        MediConnect Team
        """ 
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False
        )
        
def patient_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.user_type != 'patient':
            return HttpResponseForbidden('You do not have permission to access this page.')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def provider_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.user_type != 'provider':
            return HttpResponseForbidden('You do not have permission to access this page.')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.user_type != 'admin':
            return HttpResponseForbidden('You do not have permission to access this page.')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@login_required
def profile_view(request):
    # View and update user profile
    user = request.user
    
    
    # Get or create profile
    profile, created = Profile.objects.get_or_create(user=user)
    
    
    # Get provider profile if user is a provider
    provider_profile = None
    if user.user_type == 'provider':
        provider_profile, created = ProviderProfile.objects.get_or_create(user=user)
        
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, request.FILES, instance=user)
        profile_form = ProfileUpdateForm(request.POST, instance=profile)
        provider_form = None
        
        if user.user_type == 'provider':
            provider_form = ProviderProfileForm(request.POST, instance=provider_profile)
            
        if user_form.is_valid() and profile_form.is_valid():
            if provider_form is None or provider_form.is_valid():
                user_form.save()
                profile_form.save()
                if provider_form:
                    provider_form.save()
                messages.success(request, 'Your profile has been updated!')
                return redirect('accounts:profile')
    else:
        user_form = UserUpdateForm(instance=user)
        profile_form = ProfileUpdateForm(instance=profile)
        provider_form  = ProviderProfileForm(instance=provider_profile) if provider_profile else None
        
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'provider_form': provider_form,
        'user': user,
        'profile': profile,
        'provider_profile': provider_profile,
    }                                  
    return render(request, 'accounts/profile.html', context)

    
@login_required
def dashboard_view(request):
    # Main dashboard View - redirects based on user type
    user = request.user
    
    if user.user_type == 'patient':
        return redirect('patient_dashboard')
    elif user.user_type == 'provider':
        return redirect('provider_dashboard')
    else:
        return redirect('admin_dashboard')
    
    
def verify_email(request, token):
    # Verify user email address
    try:
        user = User.objects.get(email_verification_token=token)
        user.is_email_verified = True
        user.email_verification_token = ''
        user.save()
        messages.success(request, 'Email verified successfully! You can log in.')
        return redirect('accounts:login')
    except User.DoesNotExist:
        messages.error(request, 'Invalid verification token.')
        return redirect('accounts:login')
    
def logout_view(request):
    # Custom logout view
    logout(request)
    messages.success(request, 'you have been logged out successfully.')
    return redirect('accounts:login')    
              
            
class CustomPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_url = reverse_lazy('accounts:password_reset_done')

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete')

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'    
              
@login_required
@patient_required
def patient_dashboard_view(request):
    return render(request, 'accounts/patient_dashboard.html')

@login_required
@provider_required
def provider_dashboard_view(request):
    return render(request, 'accounts/provider_dashboard.html')

@login_required
@admin_required
def admin_dashboard_view(request):
    return render(request, 'accounts/admin_dashboard.html')    
              
            