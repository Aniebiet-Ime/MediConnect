from django.urls import path
from . import views

app_name = 'patients'

urlpatterns = [
    path('register/', views.patient_registration, name='register'),
    path('profile/', views.patient_profile, name='profile'),
    path('medical-history/', views.patient_medical_history, name='medical_history'),
]
