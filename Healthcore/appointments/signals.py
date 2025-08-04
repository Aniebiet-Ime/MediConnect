from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Appointment
from .utils import send_appointment_notification

@receiver(post_save, sender=Appointment)
def appointment_notification(sender, instance, created, **kwargs):
    """
    Send notifications when an appointment is created or its status changes
    """
    if created:
        # New appointment
        send_appointment_notification(instance, 'confirmation')
    else:
        # Get the old instance from the database
        try:
            old_instance = Appointment.objects.get(pk=instance.pk)
            if old_instance.status != instance.status:
                if instance.status == 'CANCELLED':
                    send_appointment_notification(instance, 'cancellation')
                elif instance.status == 'RESCHEDULED':
                    send_appointment_notification(instance, 'rescheduled')
        except Appointment.DoesNotExist:
            pass
