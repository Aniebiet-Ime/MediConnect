from django.contrib import admin
from .models import Patient

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_full_name', 'phone_number', 'blood_type', 'get_age']
    list_filter = ['blood_type', 'gender', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'phone_number']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'date_of_birth', 'gender')
        }),
        ('Physical Information', {
            'fields': ('height', 'weight')
        }),
        ('Contact Information', {
            'fields': ('address', 'phone_number', 'emergency_contact_name', 'emergency_contact_phone')
        }),
        ('Medical Information', {
            'fields': ('blood_type', 'allergies', 'medical_history', 'medical_conditions', 'current_medications')
        }),
        ('Insurance Information', {
            'fields': ('insurance_provider', 'insurance_policy_number')
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Full Name'
