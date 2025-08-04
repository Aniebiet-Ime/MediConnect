from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
from dateutil import tz

def send_appointment_notification(appointment, notification_type):
    """
    Send email notifications for different appointment events
    notification_type can be: 'confirmation', 'reminder', 'cancellation', 'rescheduled'
    """
    context = {
        'appointment': appointment,
        'patient_name': appointment.patient.get_full_name() or appointment.patient.email,
        'provider_name': appointment.provider.user.get_full_name(),
        'appointment_time': appointment.time.strftime('%I:%M %p'),
        'appointment_date': appointment.date.strftime('%B %d, %Y'),
    }

    # Configure email based on notification type
    if notification_type == 'confirmation':
        subject = 'Appointment Confirmation'
        template = 'appointments/email/confirmation.html'
    elif notification_type == 'reminder':
        subject = 'Appointment Reminder'
        template = 'appointments/email/reminder.html'
    elif notification_type == 'cancellation':
        subject = 'Appointment Cancellation'
        template = 'appointments/email/cancellation.html'
    elif notification_type == 'rescheduled':
        subject = 'Appointment Rescheduled'
        template = 'appointments/email/rescheduled.html'
    else:
        return  # Invalid notification type

    # Render email content
    html_message = render_to_string(template, context)
    
    # Send to patient
    send_mail(
        subject=subject,
        message='',  # Plain text version
        html_message=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[appointment.patient.email],
        fail_silently=True
    )

    # Send to provider
    send_mail(
        subject=f'Provider: {subject}',
        message='',  # Plain text version
        html_message=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[appointment.provider.user.email],
        fail_silently=True
    )

def generate_ical_event(appointment):
    """Generate iCalendar format string for the appointment"""
    # Convert appointment time to UTC
    local_tz = tz.gettz(settings.TIME_ZONE)
    utc = tz.UTC
    
    # Combine date and time and make it timezone-aware
    local_dt = datetime.combine(appointment.date, appointment.time).replace(tzinfo=local_tz)
    start_time = local_dt.astimezone(utc)
    end_time = start_time + timedelta(minutes=30)  # Assuming 30-minute appointments

    description = f"""
    Appointment Type: {appointment.get_appointment_type_display()}
    Reason: {appointment.reason}
    Provider: {appointment.provider.user.get_full_name()}
    """

    ical_data = f"""BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
DTSTART:{start_time.strftime('%Y%m%dT%H%M%SZ')}
DTEND:{end_time.strftime('%Y%m%dT%H%M%SZ')}
SUMMARY:Medical Appointment - {appointment.get_appointment_type_display()}
DESCRIPTION:{description}
LOCATION:{appointment.provider.office_address if hasattr(appointment.provider, 'office_address') else 'TBD'}
STATUS:CONFIRMED
END:VEVENT
END:VCALENDAR
"""
    return ical_data

def check_appointment_availability(provider, date, time):
    """
    Check if the provider is available at the given date and time
    Returns (bool, str): (is_available, message)
    """
    # Convert time to datetime for comparison
    appointment_datetime = datetime.combine(date, time)
    
    # Check if the time is in the future
    if appointment_datetime <= timezone.now():
        return False, "Cannot book appointments in the past"

    # Check if it's within provider's working hours (assuming 9 AM to 5 PM)
    if time.hour < 9 or time.hour >= 17:
        return False, "Appointments are only available between 9 AM and 5 PM"

    # Check for existing appointments
    existing_appointments = provider.provider_appointments.filter(
        date=date,
        time=time,
        status='SCHEDULED'
    ).exists()

    if existing_appointments:
        return False, "This time slot is already booked"

    return True, "Time slot is available"
