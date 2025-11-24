from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from datetime import datetime, timedelta, date, time

# Importación de Formularios y Modelos
from .forms import NexthoraUserCreationForm, ServiceForm, BusinessHoursForm, TimeOffForm
from .models import Service, ProfessionalProfile, BusinessHours, TimeOff, Appointment

# --- VISTA DE INICIO ---
def index_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('register')

# --- VISTA DE REGISTRO ---
def register_view(request):
    if request.method == 'POST':
        form = NexthoraUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"¡Bienvenido, {user.username}! Tu cuenta ha sido creada.")
            return redirect('dashboard')
        else:
            messages.error(request, "Hubo un error en el registro. Revisa los campos.")
    else:
        form = NexthoraUserCreationForm()
    
    return render(request, 'register.html', {'form': form})

# --- VISTA DE LOGIN (Placeholder) ---
def login_view(request):
    return redirect('register') 

# --- VISTA DE DASHBOARD ---
@login_required
def dashboard_view(request):
    return render(request, 'dashboard.html')

# --- GESTIÓN DE SERVICIOS ---
@login_required
def services_view(request):
    try:
        profile = request.user.profile
    except ProfessionalProfile.DoesNotExist:
        messages.error(request, "Error: Perfil no encontrado.")
        return redirect('dashboard')

    # Obtener servicios actuales
    services = Service.objects.filter(professional=profile).order_by('name')
    services_count = services.count()
    SERVICE_LIMIT = 2 # Límite Freemium

    if request.method == 'POST':
        # VALIDACIÓN FREEMIUM: Impedir crear si ya tiene 2
        if services_count >= SERVICE_LIMIT:
            messages.error(request, f"Plan Gratuito: Límite alcanzado ({SERVICE_LIMIT} servicios). Edita o elimina uno existente.")
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

    return render(request, 'services.html', {
        'form': form, 
        'services': services,
        'services_count': services_count,
        'service_limit': SERVICE_LIMIT
    })

# --- NUEVO: EDITAR SERVICIO ---
@login_required
def edit_service_view(request, service_id):
    service = get_object_or_404(Service, id=service_id, professional=request.user.profile)
    
    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, "Servicio actualizado correctamente.")
            return redirect('services')
    else:
        form = ServiceForm(instance=service)
    
    return render(request, 'service_edit.html', {'form': form, 'service': service})

# --- NUEVO: ACTIVAR/DESACTIVAR (VISIBILIDAD) ---
@login_required
def toggle_service_view(request, service_id):
    service = get_object_or_404(Service, id=service_id, professional=request.user.profile)
    # Invertir estado
    service.is_active = not service.is_active
    service.save()
    
    estado = "visible" if service.is_active else "oculto"
    messages.success(request, f"El servicio '{service.name}' ahora está {estado}.")
    return redirect('services')

@login_required
def delete_service_view(request, service_id):
    service = get_object_or_404(Service, id=service_id, professional=request.user.profile)
    if request.method == 'POST':
        service.delete()
        messages.success(request, "Servicio eliminado.")
    return redirect('services')

# --- GESTIÓN DE HORARIOS ---
@login_required
def schedule_view(request):
    try:
        profile = request.user.profile
    except:
        return redirect('dashboard')

    # Instanciamos ambos formularios
    hours_form = BusinessHoursForm(prefix='hours')
    timeoff_form = TimeOffForm(prefix='off')

    if request.method == 'POST':
        if 'submit_hours' in request.POST:
            hours_form = BusinessHoursForm(request.POST, prefix='hours')
            if hours_form.is_valid():
                hours = hours_form.save(commit=False)
                hours.professional = profile
                try:
                    hours.save()
                    messages.success(request, "Horario recurrente añadido.")
                    return redirect('schedule')
                except:
                    messages.error(request, "Error: Horario duplicado.")
        
        elif 'submit_off' in request.POST:
            timeoff_form = TimeOffForm(request.POST, prefix='off')
            if timeoff_form.is_valid():
                off = timeoff_form.save(commit=False)
                off.professional = profile
                off.save()
                messages.success(request, "Días bloqueados correctamente.")
                return redirect('schedule')

    schedule = BusinessHours.objects.filter(professional=profile).order_by('weekday', 'start_time')
    time_off_list = TimeOff.objects.filter(professional=profile).order_by('start_date')

    return render(request, 'schedule.html', {
        'hours_form': hours_form,
        'timeoff_form': timeoff_form,
        'schedule': schedule,
        'time_off_list': time_off_list
    })

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

# --- VER AGENDA ---
@login_required
def appointments_view(request):
    try:
        profile = request.user.profile
    except:
        return redirect('dashboard')

    upcoming_appointments = Appointment.objects.filter(
        professional=profile,
        start_datetime__gte=timezone.now()
    ).order_by('start_datetime')

    past_appointments = Appointment.objects.filter(
        professional=profile,
        start_datetime__lt=timezone.now()
    ).order_by('-start_datetime')

    return render(request, 'appointments.html', {
        'upcoming_appointments': upcoming_appointments,
        'past_appointments': past_appointments
    })

# --- HELPER: CALCULAR SLOTS DISPONIBLES ---
def get_available_slots(profile, service, check_date):
    """
    Calcula horas disponibles validando:
    1. Días bloqueados (TimeOff)
    2. Horario laboral (BusinessHours)
    3. Citas existentes (Appointment)
    4. Horas pasadas (si es hoy)
    """
    
    # 1. VALIDACIÓN TimeOff (Días Bloqueados)
    is_blocked = TimeOff.objects.filter(
        professional=profile,
        start_date__lte=check_date, 
        end_date__gte=check_date
    ).exists()
    
    if is_blocked:
        return [] # Día bloqueado por vacaciones/excepción

    # 2. Obtener horario laboral
    weekday = check_date.weekday()
    try:
        work_hours = BusinessHours.objects.get(professional=profile, weekday=weekday)
    except BusinessHours.DoesNotExist:
        return [] # No trabaja este día de la semana

    # 3. Obtener citas existentes
    existing_appointments = Appointment.objects.filter(
        professional=profile,
        start_datetime__date=check_date
    )

    # 4. Generar slots
    slots = []
    current_time = datetime.combine(check_date, work_hours.start_time)
    end_work_time = datetime.combine(check_date, work_hours.end_time)
    now = timezone.localtime(timezone.now())
    duration = timedelta(minutes=service.duration_minutes)

    while current_time + duration <= end_work_time:
        slot_start = current_time
        slot_end = current_time + duration
        
        # Validar hora pasada (si es hoy)
        if check_date == now.date() and slot_start.time() < now.time():
            current_time += duration
            continue

        # Validar colisión con citas
        is_taken = False
        for appt in existing_appointments:
            appt_start = timezone.localtime(appt.start_datetime).replace(tzinfo=None)
            appt_end = timezone.localtime(appt.end_datetime).replace(tzinfo=None)
            
            if slot_start < appt_end and slot_end > appt_start:
                is_taken = True
                break
        
        if not is_taken:
            slots.append(current_time.time())

        current_time += duration 

    return slots

# --- VISTA PÚBLICA: PERFIL ---
def profile_view(request, profile_slug):
    profile = get_object_or_404(ProfessionalProfile, slug=profile_slug)
    services = Service.objects.filter(professional=profile, is_active=True)
    return render(request, 'profile.html', {'profile': profile, 'services': services})

# --- VISTA PÚBLICA: RESERVAR ---
def booking_view(request, profile_slug, service_id):
    profile = get_object_or_404(ProfessionalProfile, slug=profile_slug)
    service = get_object_or_404(Service, id=service_id, professional=profile)
    
    date_str = request.GET.get('date')
    if date_str:
        selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    else:
        selected_date = date.today()

    available_slots = get_available_slots(profile, service, selected_date)

    return render(request, 'booking.html', {
        'profile': profile,
        'service': service,
        'selected_date': selected_date,
        'available_slots': available_slots
    })

# --- VISTA PÚBLICA: CONFIRMAR ---
# --- VISTA PASO 2: CONFIRMAR Y GUARDAR ---
def booking_confirm_view(request, profile_slug, service_id):
    profile = get_object_or_404(ProfessionalProfile, slug=profile_slug)
    service = get_object_or_404(Service, id=service_id, professional=profile)
    
    # IMPORTANTE: Obtener fecha y hora de la URL
    date_str = request.GET.get('date')
    time_str = request.GET.get('time')
    
    if request.method == 'POST':
        print("--- INICIANDO PROCESO DE RESERVA ---") # Debug
        
        # 1. Obtener datos del formulario
        client_name = request.POST.get('client_name')
        client_last_name = request.POST.get('client_last_name')
        client_rut = request.POST.get('client_rut')
        client_email = request.POST.get('client_email')
        client_whatsapp = request.POST.get('client_whatsapp')
        
        print(f"Datos recibidos: {client_name}, {client_last_name}, {client_rut}, {client_email}, {client_whatsapp}") # Debug

        # Validar campos vacíos
        if not all([client_name, client_last_name, client_rut, client_email, client_whatsapp]):
            print("ERROR: Faltan campos") # Debug
            messages.error(request, "Por favor completa todos los campos.")
            return render(request, 'booking_confirm.html', {
                'profile': profile, 'service': service, 'date_str': date_str, 'time_str': time_str
            })

        try:
            # Reconstruir fecha
            start_datetime_str = f"{date_str} {time_str}"
            start_datetime = datetime.strptime(start_datetime_str, '%Y-%m-%d %H:%M')
            
            print(f"Intentando crear cita para: {start_datetime}") # Debug

            # 2. Crear la cita
            appointment = Appointment.objects.create(
                professional=profile,
                service=service,
                client_name=client_name,
                client_last_name=client_last_name,
                client_rut=client_rut,
                client_email=client_email,
                client_whatsapp=client_whatsapp,
                start_datetime=start_datetime
            )
            
            print("¡CITA CREADA CON ÉXITO!") # Debug
            
            # Redirigir al éxito
            return render(request, 'success.html', {
                'service': service, 
                'appointment': appointment,
                'profile': profile
            })
            
        except Exception as e:
            print(f"ERROR CRÍTICO AL GUARDAR: {e}") # Debug
            messages.error(request, f"Error al agendar: {e}")

    # GET Request
    return render(request, 'booking_confirm.html', {
        'profile': profile,
        'service': service,
        'date_str': date_str,
        'time_str': time_str
    })