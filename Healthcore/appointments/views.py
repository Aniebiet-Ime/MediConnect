from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.db.models import Q
from datetime import datetime, timedelta
from .models import Appointment
from .forms import AppointmentForm
from .utils import send_appointment_notification, generate_ical_event, check_appointment_availability
from accounts.models import ProviderProfile

@login_required
def appointment_list(request):
    today = timezone.now().date()
    if hasattr(request.user, 'providerprofile'):
        upcoming_appointments = Appointment.objects.filter(
            provider=request.user.providerprofile,
            date__gte=today,
            status='SCHEDULED'
        ).order_by('date', 'time')
        past_appointments = Appointment.objects.filter(
            provider=request.user.providerprofile,
            date__lt=today
        ).order_by('-date', '-time')
    else:
        upcoming_appointments = Appointment.objects.filter(
            patient=request.user,
            date__gte=today,
            status='SCHEDULED'
        ).order_by('date', 'time')
        past_appointments = Appointment.objects.filter(
            patient=request.user,
            date__lt=today
        ).order_by('-date', '-time')

    return render(request, 'appointments/appointment_list.html', {
        'upcoming_appointments': upcoming_appointments,
        'past_appointments': past_appointments
    })

@login_required
def book_appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data['date']
            time = form.cleaned_data['time']
            provider = form.cleaned_data['provider']

            # Check availability
            is_available, message = check_appointment_availability(provider, date, time)
            
            if not is_available:
                messages.error(request, message)
                return render(request, 'appointments/book_appointment.html', {
                    'form': form,
                    'providers': ProviderProfile.objects.all()
                })

            appointment = form.save(commit=False)
            appointment.patient = request.user
            appointment.save()

            # Send confirmation email
            send_appointment_notification(appointment, 'confirmation')

            messages.success(request, 'Appointment booked successfully! A confirmation email has been sent.')
            return redirect('appointments:appointment_detail', pk=appointment.pk)
    else:
        form = AppointmentForm()
    
    providers = ProviderProfile.objects.all()
    return render(request, 'appointments/book_appointment.html', {
        'form': form,
        'providers': providers
    })

@login_required
def appointment_detail(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.user != appointment.patient and (not hasattr(request.user, 'providerprofile') or request.user.providerprofile != appointment.provider):
        messages.error(request, 'You do not have permission to view this appointment.')
        return redirect('appointments:appointment_list')

    # Generate iCal file for download
    if request.GET.get('download_ical'):
        ical_data = generate_ical_event(appointment)
        response = HttpResponse(ical_data, content_type='text/calendar')
        response['Content-Disposition'] = f'attachment; filename="appointment_{pk}.ics"'
        return response

    return render(request, 'appointments/appointment_detail.html', {
        'appointment': appointment
    })

@login_required
def cancel_appointment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.user != appointment.patient and (not hasattr(request.user, 'providerprofile') or request.user.providerprofile != appointment.provider):
        messages.error(request, 'You do not have permission to cancel this appointment.')
        return redirect('appointments:appointment_list')
    
    if request.method == 'POST':
        if not appointment.can_be_cancelled():
            messages.error(request, 'This appointment cannot be cancelled.')
            return redirect('appointments:appointment_detail', pk=pk)

        appointment.status = 'CANCELLED'
        appointment.save()

        # Send cancellation notification
        send_appointment_notification(appointment, 'cancellation')

        messages.success(request, 'Appointment cancelled successfully. A notification email has been sent.')
        return redirect('appointments:appointment_list')
    
    return render(request, 'appointments/cancel_appointment.html', {
        'appointment': appointment
    })

@login_required
def provider_schedule(request):
    """View for providers to see their daily/weekly schedule"""
    if not hasattr(request.user, 'providerprofile'):
        messages.error(request, 'Only providers can access the schedule view.')
        return redirect('appointments:appointment_list')

    # Get date range for schedule
    today = timezone.now().date()
    start_date = request.GET.get('start_date')
    start_date = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else today
    end_date = start_date + timedelta(days=7)

    appointments = Appointment.objects.filter(
        provider=request.user.providerprofile,
        date__range=[start_date, end_date],
        status='SCHEDULED'
    ).order_by('date', 'time')

    return render(request, 'appointments/provider_schedule.html', {
        'appointments': appointments,
        'start_date': start_date,
        'end_date': end_date
    })
