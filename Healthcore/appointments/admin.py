from django.contrib import admin
from django.utils.html import format_html
from .models import Appointment

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient_name', 'provider_name', 'appointment_datetime', 'appointment_type', 'status_badge')
    list_filter = ('status', 'appointment_type', 'date', 'provider')
    search_fields = ('patient__email', 'patient__first_name', 'patient__last_name',
                    'provider__user__email', 'provider__user__first_name', 'provider__user__last_name')
    date_hierarchy = 'date'
    ordering = ('-date', '-time')

    def patient_name(self, obj):
        return f"{obj.patient.get_full_name()} ({obj.patient.email})"
    patient_name.short_description = 'Patient'

    def provider_name(self, obj):
        return f"Dr. {obj.provider.user.get_full_name()}"
    provider_name.short_description = 'Provider'

    def appointment_datetime(self, obj):
        return format_html('{} at {}', obj.date.strftime('%B %d, %Y'), obj.time.strftime('%I:%M %p'))
    appointment_datetime.short_description = 'Date & Time'

    def status_badge(self, obj):
        colors = {
            'SCHEDULED': 'success',
            'COMPLETED': 'info',
            'CANCELLED': 'danger',
            'NO_SHOW': 'warning'
        }
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            colors.get(obj.status, 'secondary'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    # Add custom admin actions
    actions = ['mark_as_completed', 'mark_as_no_show']

    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='COMPLETED')
        self.message_user(request, f'{updated} appointments marked as completed.')
    mark_as_completed.short_description = "Mark selected appointments as completed"

    def mark_as_no_show(self, request, queryset):
        updated = queryset.update(status='NO_SHOW')
        self.message_user(request, f'{updated} appointments marked as no-show.')
    mark_as_no_show.short_description = "Mark selected appointments as no-show"

    class Media:
        css = {
            'all': ['admin/css/badges.css']
        }
