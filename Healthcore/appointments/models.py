from django.db import models
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from accounts.models import ProviderProfile

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('NO_SHOW', 'No Show'),
    ]

    APPOINTMENT_TYPES = [
        ('ROUTINE', 'Routine Checkup'),
        ('FOLLOW_UP', 'Follow-up'),
        ('CONSULTATION', 'Consultation'),
        ('EMERGENCY', 'Emergency'),
    ]

    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='patient_appointments')
    provider = models.ForeignKey(ProviderProfile, on_delete=models.CASCADE, related_name='provider_appointments')
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')
    appointment_type = models.CharField(max_length=20, choices=APPOINTMENT_TYPES, default='CONSULTATION')
    reason = models.TextField(max_length=500)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-time']

    def __str__(self):
        return f"{self.patient.username} - {self.provider.user.username} - {self.date} {self.time}"

    def save(self, *args, **kwargs):
        # Check if this is a new appointment or status has changed
        is_new = not self.pk
        if not is_new:
            old_instance = Appointment.objects.get(pk=self.pk)
            status_changed = old_instance.status != self.status
        else:
            status_changed = False

        # Save the instance
        super().save(*args, **kwargs)

        # Send notifications
        if is_new:
            self.send_confirmation_emails()
        elif status_changed:
            self.send_status_update_emails()

    def send_confirmation_emails(self):
        # Send to patient
        subject = 'Appointment Confirmation'
        patient_message = render_to_string('appointments/email/patient_confirmation.html', {
            'appointment': self,
            'calendar_link': self.get_calendar_link()
        })
        send_mail(
            subject,
            patient_message,
            settings.DEFAULT_FROM_EMAIL,
            [self.patient.email],
            fail_silently=True,
        )

        # Send to provider
        provider_message = render_to_string('appointments/email/provider_confirmation.html', {
            'appointment': self,
            'calendar_link': self.get_calendar_link()
        })
        send_mail(
            subject,
            provider_message,
            settings.DEFAULT_FROM_EMAIL,
            [self.provider.user.email],
            fail_silently=True,
        )

    def send_status_update_emails(self):
        subject = f'Appointment Status Update: {self.get_status_display()}'
        message = render_to_string('appointments/email/status_update.html', {
            'appointment': self,
        })
        # Send to both patient and provider
        recipients = [self.patient.email, self.provider.user.email]
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            recipients,
            fail_silently=True,
        )

    def get_calendar_link(self):
        """Generate iCalendar link for the appointment"""
        datetime_start = timezone.make_aware(
            timezone.datetime.combine(self.date, self.time)
        )
        datetime_end = datetime_start + timezone.timedelta(minutes=30)
        
        # Basic iCal format
        ical_data = f"""
BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
DTSTART:{datetime_start.strftime('%Y%m%dT%H%M%SZ')}
DTEND:{datetime_end.strftime('%Y%m%dT%H%M%SZ')}
SUMMARY:Medical Appointment with {self.provider.user.get_full_name()}
DESCRIPTION:{self.reason}
LOCATION:{self.provider.office_address}
END:VEVENT
END:VCALENDAR
"""
        return ical_data

    def is_upcoming(self):
        """Check if the appointment is upcoming"""
        now = timezone.now()
        appointment_datetime = timezone.make_aware(
            timezone.datetime.combine(self.date, self.time)
        )
        return appointment_datetime > now

    def can_be_cancelled(self):
        """Check if the appointment can be cancelled"""
        return self.is_upcoming() and self.status == 'SCHEDULED'

    def get_absolute_url(self):
        """Get the absolute URL for this appointment"""
        return reverse('appointments:appointment_detail', kwargs={'pk': self.pk})
