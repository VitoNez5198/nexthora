from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from datetime import datetime, timedelta, date, time
# Importación necesaria para el login
from django.contrib.auth.forms import AuthenticationForm

# Importación de Formularios y Modelos locales
from .forms import NexthoraUserCreationForm, ServiceForm, BatchScheduleForm, TimeOffForm
from .models import Service, ProfessionalProfile, BusinessHours, TimeOff, Appointment



# ... (Tus vistas index, register, login, dashboard SE QUEDAN IGUAL) ...
def index_view(request):
    if request.user.is_authenticated: 
        return redirect('dashboard')
    return redirect('login')

def register_view(request):
    if request.method == 'POST':
        form = NexthoraUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"¡Bienvenido, {user.username}!")
            return redirect('dashboard')
    else:
        form = NexthoraUserCreationForm()
    return render(request, 'register.html', {'form': form})

# --- VISTA DE LOGIN ---
def login_view(request):
    """
    Maneja el inicio de sesión de los profesionales.
    """
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"¡Hola de nuevo, {username}!")
                return redirect('dashboard')
            else:
                messages.error(request, "Usuario o contraseña inválidos.")
        else:
            messages.error(request, "Usuario o contraseña inválidos.")
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})

@login_required
def dashboard_view(request):
    profile = request.user.profile
    
    # Obtener fecha y hora actual en la zona horaria correcta
    now = timezone.localtime(timezone.now())
    today = now.date()
    tomorrow = today + timedelta(days=1)

    # 1. Citas de HOY (Ordenadas por hora)
    today_appointments = Appointment.objects.filter(
        professional=profile,
        start_datetime__date=today,
        status='CONFIRMED'
    ).order_by('start_datetime')

    # 2. Citas de MAÑANA
    tomorrow_appointments = Appointment.objects.filter(
        professional=profile,
        start_datetime__date=tomorrow,
        status='CONFIRMED'
    ).order_by('start_datetime')

    # (Opcional) Próximas citas después de mañana
    future_appointments = Appointment.objects.filter(
        professional=profile,
        start_datetime__date__gt=tomorrow,
        status='CONFIRMED'
    ).order_by('start_datetime')[:5]

    return render(request, 'dashboard.html', {
        'today_appointments': today_appointments,
        'tomorrow_appointments': tomorrow_appointments,
        'today_date': today,
        'tomorrow_date': tomorrow
    })

# --- GESTIÓN DE SERVICIOS (AQUÍ ESTÁ LA LÓGICA DEL LÍMITE) ---
@login_required
def services_view(request):
    try:
        profile = request.user.profile
    except ProfessionalProfile.DoesNotExist:
        return redirect('dashboard')

    services = Service.objects.filter(professional=profile).order_by('name')
    services_count = services.count()
    SERVICE_LIMIT = 2  # <--- ¡AQUÍ ESTÁ EL LÍMITE! CÁMBIALO A 10 SI QUIERES PROBAR MÁS

    if request.method == 'POST':
        # Si ya alcanzó el límite, mostramos error y NO guardamos
        if services_count >= SERVICE_LIMIT:
            messages.error(request, f"Límite alcanzado ({SERVICE_LIMIT}). Elimina un servicio para crear otro.")
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

# ... (MANTÉN EL RESTO DE TUS VISTAS IGUAL: edit, toggle, delete, schedule...) ...
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

# --- GESTIÓN DE HORARIOS (ACTUALIZADO) ---
@login_required
def schedule_view(request):
    try:
        profile = request.user.profile
    except:
        return redirect('dashboard')

    # Instanciamos ambos formularios
    hours_form = BatchScheduleForm(prefix='hours')
    timeoff_form = TimeOffForm(prefix='off')

    if request.method == 'POST':
        # --- PROCESAR HORARIO SEMANAL ---
        if 'submit_hours' in request.POST:
            hours_form = BatchScheduleForm(request.POST, prefix='hours')
            if hours_form.is_valid():
                selected_days = hours_form.cleaned_data['days'] # Lista ['0', '1', '2'...]
                start = hours_form.cleaned_data['start_time']
                end = hours_form.cleaned_data['end_time']
                
                count = 0
                for day_code in selected_days:
                    # 1. BORRAR PREVIOS: Eliminamos cualquier horario existente para este día
                    # Esto garantiza que solo haya UN horario por día (Lógica MVP)
                    BusinessHours.objects.filter(
                        professional=profile, 
                        weekday=int(day_code)
                    ).delete()
                    
                    # 2. CREAR NUEVO:
                    BusinessHours.objects.create(
                        professional=profile,
                        weekday=int(day_code),
                        start_time=start,
                        end_time=end
                    )
                    count += 1
                
                if count > 0:
                    messages.success(request, f"Horario actualizado para {count} días.")
                else:
                    messages.warning(request, "No seleccionaste ningún día.")
                
                return redirect('schedule')
        
        # --- PROCESAR DÍAS BLOQUEADOS ---
        elif 'submit_off' in request.POST:
            timeoff_form = TimeOffForm(request.POST, prefix='off')
            if timeoff_form.is_valid():
                off = timeoff_form.save(commit=False)
                off.professional = profile
                off.save()
                messages.success(request, "Días bloqueados correctamente.")
                return redirect('schedule')

    # Obtener datos para mostrar
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

# ... (El resto de vistas appointments_view, profile_view, booking_view... SE QUEDAN IGUAL) ...
@login_required
def appointments_view(request):
    try:
        profile = request.user.profile
    except:
        return redirect('dashboard')
    upcoming_appointments = Appointment.objects.filter(professional=profile, start_datetime__gte=timezone.now()).order_by('start_datetime')
    past_appointments = Appointment.objects.filter(professional=profile, start_datetime__lt=timezone.now()).order_by('-start_datetime')
    return render(request, 'appointments.html', {'upcoming_appointments': upcoming_appointments, 'past_appointments': past_appointments})

def get_available_slots(profile, service, check_date):
    is_blocked = TimeOff.objects.filter(professional=profile, start_date__lte=check_date, end_date__gte=check_date).exists()
    if is_blocked: return []
    
    weekday = check_date.weekday()
    try:
        work_hours = BusinessHours.objects.get(professional=profile, weekday=weekday)
    except BusinessHours.DoesNotExist:
        return []

    existing_appointments = Appointment.objects.filter(professional=profile, start_datetime__date=check_date)
    slots = []
    current_time = datetime.combine(check_date, work_hours.start_time)
    end_work_time = datetime.combine(check_date, work_hours.end_time)
    now = timezone.localtime(timezone.now())
    duration = timedelta(minutes=service.duration_minutes)

    while current_time + duration <= end_work_time:
        slot_start = current_time
        slot_end = current_time + duration
        if check_date == now.date() and slot_start.time() < now.time():
            current_time += duration
            continue
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

def profile_view(request, profile_slug):
    profile = get_object_or_404(ProfessionalProfile, slug=profile_slug)
    services = Service.objects.filter(professional=profile, is_active=True)
    return render(request, 'profile.html', {'profile': profile, 'services': services})

def booking_view(request, profile_slug, service_id):
    profile = get_object_or_404(ProfessionalProfile, slug=profile_slug)
    service = get_object_or_404(Service, id=service_id, professional=profile)
    date_str = request.GET.get('date')
    if date_str:
        selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    else:
        selected_date = date.today()
    available_slots = get_available_slots(profile, service, selected_date)
    return render(request, 'booking.html', {'profile': profile, 'service': service, 'selected_date': selected_date, 'available_slots': available_slots})

def booking_confirm_view(request, profile_slug, service_id):
    profile = get_object_or_404(ProfessionalProfile, slug=profile_slug)
    service = get_object_or_404(Service, id=service_id, professional=profile)
    
    date_str = request.GET.get('date')
    time_str = request.GET.get('time')
    
    if request.method == 'POST':
        client_name = request.POST.get('client_name')
        client_last_name = request.POST.get('client_last_name')
        client_rut = request.POST.get('client_rut')
        client_email = request.POST.get('client_email')
        client_whatsapp = request.POST.get('client_whatsapp')
        
        if not all([client_name, client_last_name, client_rut, client_email, client_whatsapp]):
             messages.error(request, "Por favor completa todos los campos.")
             return render(request, 'booking_confirm.html', {
                'profile': profile, 'service': service, 'date_str': date_str, 'time_str': time_str
            })

        try:
            # 1. Crear datetime "naive" (sin zona horaria)
            start_datetime_naive = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M')
            
            # 2. Convertirlo a "aware" (con zona horaria actual del proyecto)
            # Esto le pega la etiqueta "America/Santiago" (o la que tengas en settings)
            current_tz = timezone.get_current_timezone()
            start_datetime = current_tz.localize(start_datetime_naive)
            
            # 3. Crear la cita
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
            
            return render(request, 'success.html', {
                'service': service, 
                'appointment': appointment,
                'profile': profile
            })
            
        except Exception as e:
            # Imprimimos el error en la consola para verlo claro si falla
            print(f"ERROR AL AGENDAR: {e}")
            messages.error(request, f"Error al agendar. Inténtalo de nuevo. ({e})")

    return render(request, 'booking_confirm.html', {
        'profile': profile,
        'service': service,
        'date_str': date_str,
        'time_str': time_str
    })