from django import forms
from .models import Patient

class PatientRegistrationForm(forms.ModelForm):
    class Meta:
        model = Patient
        exclude = ['user', 'created_at', 'updated_at']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-control'
            }),
            'height': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1234567890'
            }),
            'emergency_contact_name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'emergency_contact_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1234567890'
            }),
            'blood_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'allergies': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'List any allergies...'
            }),
            'medical_conditions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'List any chronic conditions...'
            }),
            'current_medications': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'List current medications...'
            }),
            'medical_history': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Past medical procedures and conditions...'
            }),
            'insurance_provider': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'insurance_policy_number': forms.TextInput(attrs={
                'class': 'form-control'
            }),
        }

    def clean_height(self):
        height = self.cleaned_data.get('height')
        if height and height <= 0:
            raise forms.ValidationError("Height must be a positive number")
        return height

    def clean_weight(self):
        weight = self.cleaned_data.get('weight')
        if weight and weight <= 0:
            raise forms.ValidationError("Weight must be a positive number")
        return weight

class PatientUpdateForm(PatientRegistrationForm):
    class Meta(PatientRegistrationForm.Meta):
        pass
