from django.core.management.base import BaseCommand
from django.utils import timezone
from appointments.models import Appointment
from appointments.utils import send_appointment_notification
from datetime import timedelta

class Command(BaseCommand):
    help = 'Send appointment reminders for upcoming appointments'

    def handle(self, *args, **options):
        # Get tomorrow's appointments
        tomorrow = timezone.now().date() + timedelta(days=1)
        upcoming_appointments = Appointment.objects.filter(
            date=tomorrow,
            status='SCHEDULED'
        )

        reminders_sent = 0
        for appointment in upcoming_appointments:
            try:
                send_appointment_notification(appointment, 'reminder')
                reminders_sent += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully sent reminder for appointment {appointment.id}'
                    )
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'Failed to send reminder for appointment {appointment.id}: {str(e)}'
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully sent {reminders_sent} reminders'
            )
        )
