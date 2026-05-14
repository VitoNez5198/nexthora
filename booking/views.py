from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta, date, time
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm

from .forms import NexthoraUserCreationForm, ServiceForm, BatchScheduleForm, TimeOffForm, ProfessionalProfileForm, AccountSettingsForm, ProScheduleSettingsForm
from .models import Service, ProfessionalProfile, BusinessHours, TimeOff, Appointment

# --- ACTUALIZADO: Ahora muestra la Landing Page en vez de redirigir al Login ---
def index_view(request):
    if request.user.is_authenticated: 
        return redirect('dashboard')
    # Si no está logueado, le mostramos la página de ventas
    return render(request, 'index.html')

def register_view(request):
    if request.method == 'POST':
        form = NexthoraUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = NexthoraUserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, "Usuario o contraseña inválidos.")
        else:
            messages.error(request, "Usuario o contraseña inválidos.")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

@login_required
def profile_setup_view(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfessionalProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "¡Tu perfil ha sido actualizado con éxito!")
            return redirect('profile_setup')
    else:
        form = ProfessionalProfileForm(instance=profile)
    return render(request, 'profile_setup.html', {'form': form})

@login_required
def toggle_profile_visibility(request):
    if request.method == 'POST':
        profile = request.user.profile
        profile.is_active = not profile.is_active
        profile.save()
        return JsonResponse({'success': True, 'is_active': profile.is_active})
    return JsonResponse({'success': False}, status=400)

@login_required
def toggle_plan_view(request):
    profile = request.user.profile
    if request.method == 'POST':
        if profile.plan == 'FREE':
            profile.plan = 'PRO'
        else:
            profile.plan = 'FREE'
        profile.save()
        messages.success(request, f"¡Modo simulación activado! Tu plan actual es {profile.get_plan_display()}")
    referer = request.META.get('HTTP_REFERER', 'dashboard')
    return redirect(referer)

@login_required
def account_settings_view(request):
    if request.method == 'POST':
        if 'update_account' in request.POST:
            account_form = AccountSettingsForm(request.POST, instance=request.user)
            password_form = PasswordChangeForm(user=request.user)
            if account_form.is_valid():
                account_form.save()
                messages.success(request, "Datos de cuenta actualizados correctamente.")
                return redirect('account_settings')
        
        elif 'update_password' in request.POST:
            account_form = AccountSettingsForm(instance=request.user)
            password_form = PasswordChangeForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user) 
                messages.success(request, "¡Tu contraseña ha sido actualizada!")
                return redirect('account_settings')
    else:
        account_form = AccountSettingsForm(instance=request.user)
        password_form = PasswordChangeForm(user=request.user)

    return render(request, 'settings.html', {
        'account_form': account_form,
        'password_form': password_form
    })

@login_required
def dashboard_view(request):
    profile = request.user.profile
    now = timezone.now()
    today = timezone.localtime(now).date()
    tomorrow = today + timedelta(days=1)

    today_appointments = Appointment.objects.filter(
        professional=profile, start_datetime__date=today, status__in=['PENDING', 'CONFIRMED']
    ).order_by('start_datetime')
    
    tomorrow_appointments = Appointment.objects.filter(
        professional=profile, start_datetime__date=tomorrow, status__in=['PENDING', 'CONFIRMED']
    ).order_by('start_datetime')

    next_appointment = today_appointments.filter(start_datetime__gte=now).first()
    
    pending_appointments = Appointment.objects.filter(
        professional=profile, status='PENDING'
    ).order_by('created_at')
    
    pending_count = pending_appointments.count()

    return render(request, 'dashboard.html', {
        'today_appointments': today_appointments,
        'tomorrow_appointments': tomorrow_appointments,
        'next_appointment': next_appointment,
        'pending_appointments': pending_appointments,
        'pending_count': pending_count,
        'today_date': today,
        'tomorrow_date': tomorrow,
        'profile': profile
    })

@login_required
def services_view(request):
    profile = request.user.profile
    services = Service.objects.filter(professional=profile).order_by('name')
    services_count = services.count()
    SERVICE_LIMIT = 2 if profile.plan == 'FREE' else 999

    if request.method == 'POST':
        if services_count >= SERVICE_LIMIT:
            messages.error(request, f"Límite alcanzado ({SERVICE_LIMIT}). Mejora tu plan para crear más servicios.")
            return redirect('services')

        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.professional = profile
            service.save()
            messages.success(request, "¡Servicio creado con éxito!")
            return redirect('services')
        else:
            messages.error(request, "Error al crear el servicio.")
    else:
        form = ServiceForm()

    return render(request, 'services.html', {'form': form, 'services': services, 'services_count': services_count, 'service_limit': SERVICE_LIMIT})

@login_required
def edit_service_view(request, service_id):
    service = get_object_or_404(Service, id=service_id, professional=request.user.profile)
    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, "Servicio actualizado.")
            return redirect('services')
    else:
        form = ServiceForm(instance=service)
    return render(request, 'service_edit.html', {'form': form, 'service': service})

@login_required
def toggle_service_view(request, service_id):
    service = get_object_or_404(Service, id=service_id, professional=request.user.profile)
    service.is_active = not service.is_active
    service.save()
    estado = "visible" if service.is_active else "oculto"
    messages.success(request, f"Servicio {estado}.")
    return redirect('services')

@login_required
def delete_service_view(request, service_id):
    service = get_object_or_404(Service, id=service_id, professional=request.user.profile)
    if request.method == 'POST':
        service.delete()
        messages.success(request, "Servicio eliminado.")
    return redirect('services')

@login_required
def schedule_view(request):
    profile = request.user.profile
    hours_form = BatchScheduleForm(prefix='hours')
    timeoff_form = TimeOffForm(prefix='off')
    pro_form = ProScheduleSettingsForm(instance=profile, prefix='pro')

    if request.method == 'POST':
        if 'submit_hours' in request.POST:
            hours_form = BatchScheduleForm(request.POST, prefix='hours')
            if hours_form.is_valid():
                selected_days = hours_form.cleaned_data['days']
                start = hours_form.cleaned_data['start_time']
                end = hours_form.cleaned_data['end_time']
                count = 0
                for day_code in selected_days:
                    BusinessHours.objects.filter(professional=profile, weekday=int(day_code)).delete()
                    BusinessHours.objects.create(professional=profile, weekday=int(day_code), start_time=start, end_time=end)
                    count += 1
                messages.success(request, f"Horario actualizado para {count} días.")
                return redirect('schedule')
        
        elif 'submit_off' in request.POST:
            timeoff_form = TimeOffForm(request.POST, prefix='off')
            if timeoff_form.is_valid():
                off = timeoff_form.save(commit=False)
                off.professional = profile
                off.save()
                messages.success(request, "Días bloqueados correctamente.")
                return redirect('schedule')
                
        elif 'submit_pro' in request.POST:
            if profile.plan == 'FREE':
                messages.error(request, "Las opciones avanzadas son exclusivas de los planes PRO.")
                return redirect('schedule')
            pro_form = ProScheduleSettingsForm(request.POST, instance=profile, prefix='pro')
            if pro_form.is_valid():
                pro_form.save()
                messages.success(request, "Configuración avanzada guardada con éxito.")
                return redirect('schedule')

    schedule = BusinessHours.objects.filter(professional=profile).order_by('weekday', 'start_time')
    time_off_list = TimeOff.objects.filter(professional=profile).order_by('start_date')
    return render(request, 'schedule.html', {'hours_form': hours_form, 'timeoff_form': timeoff_form, 'pro_form': pro_form, 'schedule': schedule, 'time_off_list': time_off_list})

@login_required
def delete_schedule_view(request, schedule_id):
    hours = get_object_or_404(BusinessHours, id=schedule_id, professional=request.user.profile)
    if request.method == 'POST':
        hours.delete()
        messages.success(request, "Bloque de horario eliminado.")
    return redirect('schedule')

@login_required
def delete_timeoff_view(request, timeoff_id):
    off = get_object_or_404(TimeOff, id=timeoff_id, professional=request.user.profile)
    if request.method == 'POST':
        off.delete()
        messages.success(request, "Bloqueo eliminado.")
    return redirect('schedule')

@login_required
def appointments_view(request):
    profile = request.user.profile
    now = timezone.now()
    
    pending_appointments = Appointment.objects.filter(professional=profile, start_datetime__gte=now, status='PENDING').order_by('start_datetime')
    upcoming_appointments = Appointment.objects.filter(professional=profile, start_datetime__gte=now, status='CONFIRMED').order_by('start_datetime')
    past_appointments = Appointment.objects.filter(professional=profile, start_datetime__lt=now, status__in=['CONFIRMED', 'COMPLETED']).order_by('-start_datetime')
    cancelled_appointments = Appointment.objects.filter(professional=profile, status__in=['CANCELLED_BY_PRO', 'CANCELLED_BY_CLIENT']).order_by('-start_datetime')
    
    pending_count = pending_appointments.count()

    return render(request, 'appointments.html', {
        'pending_appointments': pending_appointments,
        'upcoming_appointments': upcoming_appointments,
        'past_appointments': past_appointments,
        'cancelled_appointments': cancelled_appointments,
        'pending_count': pending_count
    })

@login_required
def update_appointment_status(request, appt_id, new_status):
    if request.method == 'POST':
        appt = get_object_or_404(Appointment, id=appt_id, professional=request.user.profile)
        valid_statuses = [choice[0] for choice in Appointment.STATUS_CHOICES]
        
        if new_status in valid_statuses:
            appt.status = new_status
            appt.save()
            
            if new_status == 'CONFIRMED': messages.success(request, f"¡Cita con {appt.client_name} confirmada!")
            elif new_status == 'CANCELLED_BY_PRO': messages.warning(request, f"Cita con {appt.client_name} rechazada/cancelada.")
            
    referer = request.META.get('HTTP_REFERER', 'dashboard')
    return redirect(referer)


def get_available_slots(profile, service, check_date):
    is_blocked = TimeOff.objects.filter(professional=profile, start_date__lte=check_date, end_date__gte=check_date).exists()
    if is_blocked: return []
    
    weekday = check_date.weekday()
    try:
        work_hours = BusinessHours.objects.get(professional=profile, weekday=weekday)
    except BusinessHours.DoesNotExist:
        return []

    existing_appointments = Appointment.objects.filter(professional=profile, start_datetime__date=check_date, status__in=['PENDING', 'CONFIRMED'])
    
    slots = []
    current_time = datetime.combine(check_date, work_hours.start_time)
    end_work_time = datetime.combine(check_date, work_hours.end_time)
    now = timezone.localtime(timezone.now())
    duration = timedelta(minutes=service.duration_minutes)
    
    buffer = timedelta(minutes=profile.buffer_time_minutes) if profile.plan != 'FREE' else timedelta(minutes=0)
    
    has_lunch = False
    if profile.plan != 'FREE' and profile.lunch_start_time and profile.lunch_end_time:
        lunch_start = datetime.combine(check_date, profile.lunch_start_time)
        lunch_end = datetime.combine(check_date, profile.lunch_end_time)
        has_lunch = True

    while current_time + duration <= end_work_time:
        slot_start = current_time
        slot_end = current_time + duration
        
        if has_lunch and (slot_start < lunch_end and slot_end > lunch_start):
            current_time = lunch_end
            continue

        if check_date == now.date() and slot_start.time() < now.time():
            current_time += duration + buffer
            continue
            
        is_taken = False
        for appt in existing_appointments:
            appt_start = timezone.localtime(appt.start_datetime).replace(tzinfo=None)
            appt_end_with_buffer = timezone.localtime(appt.end_datetime).replace(tzinfo=None) + buffer
            if slot_start < appt_end_with_buffer and slot_end > appt_start:
                is_taken = True
                break
                
        if not is_taken:
            slots.append(current_time.time())
        current_time += duration + buffer 
    return slots

def profile_view(request, profile_slug):
    profile = get_object_or_404(ProfessionalProfile, slug=profile_slug)
    services = Service.objects.filter(professional=profile, is_active=True)
    return render(request, 'profile.html', {'profile': profile, 'services': services})

def booking_view(request, profile_slug, service_id):
    profile = get_object_or_404(ProfessionalProfile, slug=profile_slug)
    if not profile.is_active: return redirect('public_profile', profile_slug=profile.slug)
    
    service = get_object_or_404(Service, id=service_id, professional=profile)
    date_str = request.GET.get('date')
    selected_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else date.today()
    available_slots = get_available_slots(profile, service, selected_date)
    return render(request, 'booking.html', {'profile': profile, 'service': service, 'selected_date': selected_date, 'available_slots': available_slots})

def booking_confirm_view(request, profile_slug, service_id):
    profile = get_object_or_404(ProfessionalProfile, slug=profile_slug)
    if not profile.is_active: return redirect('public_profile', profile_slug=profile.slug)
        
    service = get_object_or_404(Service, id=service_id, professional=profile)
    date_str = request.GET.get('date')
    time_str = request.GET.get('time')
    
    if request.method == 'POST':
        client_name = request.POST.get('client_name')
        client_last_name = request.POST.get('client_last_name')
        client_rut = request.POST.get('client_rut')
        client_email = request.POST.get('client_email')
        client_whatsapp = request.POST.get('client_whatsapp')

        try:
            start_datetime_naive = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M')
            start_datetime = timezone.make_aware(start_datetime_naive)
            
            appointment = Appointment.objects.create(
                professional=profile, service=service, client_name=client_name,
                client_last_name=client_last_name, client_rut=client_rut,
                client_email=client_email, client_whatsapp=client_whatsapp,
                start_datetime=start_datetime
            )
            return redirect('booking_success', profile_slug=profile.slug, appointment_id=appointment.id)
            
        except Exception as e:
            messages.error(request, f"Error al agendar. Inténtalo de nuevo. ({e})")

    return render(request, 'booking_confirm.html', {'profile': profile, 'service': service, 'date_str': date_str, 'time_str': time_str})

def booking_success_view(request, profile_slug, appointment_id):
    profile = get_object_or_404(ProfessionalProfile, slug=profile_slug)
    appointment = get_object_or_404(Appointment, id=appointment_id, professional=profile)
    return render(request, 'success.html', {
        'service': appointment.service, 
        'appointment': appointment, 
        'profile': profile
    })