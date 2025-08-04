from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .models import Patient
from .forms import PatientRegistrationForm, PatientUpdateForm

@login_required
def patient_registration(request):
    """Handle new patient registration"""
    # Check if patient profile already exists
    if Patient.objects.filter(user=request.user).exists():
        messages.info(request, 'You already have a patient profile.')
        return redirect('patients:profile')

    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            patient = form.save(commit=False)
            patient.user = request.user
            patient.save()
            messages.success(request, 'Your patient profile has been created successfully.')
            return redirect('patients:profile')
    else:
        form = PatientRegistrationForm()
    
    return render(request, 'patients/registration.html', {
        'form': form,
        'title': 'Patient Registration'
    })

@login_required
def patient_profile(request):
    """Display and update patient profile"""
    patient = get_object_or_404(Patient, user=request.user)
    
    if request.method == 'POST':
        form = PatientUpdateForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('patients:profile')
    else:
        form = PatientUpdateForm(instance=patient)
    
    return render(request, 'patients/profile.html', {
        'patient': patient,
        'form': form,
        'title': 'Patient Profile',
        'age': patient.get_age(),
        'bmi': patient.get_bmi()
    })

@login_required
def patient_medical_history(request):
    """Display patient medical history"""
    patient = get_object_or_404(Patient, user=request.user)
    
    return render(request, 'patients/medical_history.html', {
        'patient': patient,
        'title': 'Medical History'
    })
