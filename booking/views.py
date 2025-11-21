from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages  # ¡Faltaba esto!
from django.http import HttpResponse

from .forms import NexthoraUserCreationForm, ServiceForm
from .models import Service, ProfessionalProfile

from .forms import BusinessHoursForm # ¡Importa el nuevo form!
from .models import BusinessHours # ¡Importa el modelo!


from .models import Appointment
from django.utils import timezone

from datetime import datetime, timedelta, date, time

# --- VISTA DE INICIO ---
def index_view(request):
    """
    Vista para la página de inicio (la raíz '/').
    Por ahora, simplemente redirige a la página de registro o dashboard.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('register')

# --- VISTA DE REGISTRO ---
def register_view(request):
    """
    Maneja la lógica para registrar un nuevo profesional.
    """
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
    """
    Placeholder para login. Redirige a registro por ahora.
    """
    return redirect('register') 

# --- VISTA DE DASHBOARD ---
@login_required
def dashboard_view(request):
    """
    Vista principal del Dashboard.
    """
    return render(request, 'dashboard.html')

# --- VISTA: GESTIONAR SERVICIOS ---
@login_required
def services_view(request):
    # Intentamos obtener el perfil. Si falla, redirigimos (seguridad).
    try:
        profile = request.user.profile
    except ProfessionalProfile.DoesNotExist:
        messages.error(request, "Error: Tu usuario no tiene un perfil profesional asociado.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.professional = profile # Asignamos el servicio al profesional actual
            service.save()
            messages.success(request, "¡Servicio creado con éxito!")
            return redirect('services')
        else:
            messages.error(request, "Error al crear el servicio. Revisa el formulario.")
    else:
        form = ServiceForm()

    # Listar solo los servicios de ESTE profesional
    services = Service.objects.filter(professional=profile)

    return render(request, 'services.html', {
        'form': form,
        'services': services
    })

# --- VISTA: ELIMINAR SERVICIO ---
@login_required
def delete_service_view(request, service_id):
    # Obtenemos el servicio solo si pertenece al usuario actual (seguridad)
    service = get_object_or_404(Service, id=service_id, professional=request.user.profile)
    
    if request.method == 'POST':
        service.delete()
        messages.success(request, "Servicio eliminado correctamente.")
        
    return redirect('services')

# --- VISTA: GESTIONAR HORARIOS ---
@login_required
def schedule_view(request):
    try:
        profile = request.user.profile
    except:
        return redirect('dashboard')

    if request.method == 'POST':
        form = BusinessHoursForm(request.POST)
        if form.is_valid():
            hours = form.save(commit=False)
            hours.professional = profile
            try:
                hours.save()
                messages.success(request, "¡Horario añadido correctamente!")
                return redirect('schedule')
            except Exception as e:
                # Captura error de duplicados (unique_together en models.py)
                messages.error(request, "Error: Ya existe un horario idéntico para este día.")
        else:
            messages.error(request, "Error en el horario. Revisa que la hora fin sea mayor a la inicio.")
    else:
        form = BusinessHoursForm()

    # Obtener horarios ordenados por día y hora
    schedule = BusinessHours.objects.filter(professional=profile).order_by('weekday', 'start_time')

    return render(request, 'schedule.html', {
        'form': form,
        'schedule': schedule
    })

# --- VISTA: ELIMINAR HORARIO ---
@login_required
def delete_schedule_view(request, schedule_id):
    hours = get_object_or_404(BusinessHours, id=schedule_id, professional=request.user.profile)
    
    if request.method == 'POST':
        hours.delete()
        messages.success(request, "Bloque de horario eliminado.")
        
    return redirect('schedule')

# --- VISTA: VER AGENDA ---
@login_required
def appointments_view(request):
    try:
        profile = request.user.profile
    except:
        return redirect('dashboard')

    # Obtener citas futuras ordenadas por fecha
    upcoming_appointments = Appointment.objects.filter(
        professional=profile,
        start_datetime__gte=timezone.now()
    ).order_by('start_datetime')

    # Obtener citas pasadas (opcional, para historial)
    past_appointments = Appointment.objects.filter(
        professional=profile,
        start_datetime__lt=timezone.now()
    ).order_by('-start_datetime')

    return render(request, 'appointments.html', {
        'upcoming_appointments': upcoming_appointments,
        'past_appointments': past_appointments
    })


# --- VISTA PÚBLICA: PERFIL DEL PROFESIONAL ---
# Nota: ¡No usamos @login_required aquí! Es pública.
def profile_view(request, profile_slug):
    # 1. Buscar al profesional por su URL personalizada (slug)
    # Si no existe, muestra un error 404 automáticamente.
    profile = get_object_or_404(ProfessionalProfile, slug=profile_slug)
    
    # 2. Obtener sus servicios ACTIVOS
    services = Service.objects.filter(professional=profile, is_active=True)
    
    # 3. Renderizar la plantilla pública
    return render(request, 'profile.html', {
        'profile': profile,
        'services': services
    })

# --- VISTA PÚBLICA: PERFIL DEL PROFESIONAL ---
# Nota: ¡No usamos @login_required aquí! Es pública.
def profile_view(request, profile_slug):
    # 1. Buscar al profesional por su URL personalizada (slug)
    # Si no existe, Django mostrará automáticamente un error 404.
    profile = get_object_or_404(ProfessionalProfile, slug=profile_slug)
    
    # 2. Obtener sus servicios ACTIVOS
    services = Service.objects.filter(professional=profile, is_active=True)
    
    # 3. Renderizar la plantilla pública
    return render(request, 'profile.html', {
        'profile': profile,
        'services': services
    })
    
# --- HELPER: CALCULAR SLOTS DISPONIBLES ---
def get_available_slots(profile, service, check_date):
    """
    Genera una lista de horas disponibles para un día específico.
    """
    # 1. Obtener el horario de trabajo para ese día de la semana (0=Lunes, 6=Domingo)
    weekday = check_date.weekday()
    try:
        work_hours = BusinessHours.objects.get(professional=profile, weekday=weekday)
    except BusinessHours.DoesNotExist:
        return [] # No trabaja este día

    # 2. Obtener todas las citas YA agendadas para ese día
    existing_appointments = Appointment.objects.filter(
        professional=profile,
        start_datetime__date=check_date
    )

    # 3. Generar slots
    slots = []
    current_time = datetime.combine(check_date, work_hours.start_time)
    end_work_time = datetime.combine(check_date, work_hours.end_time)
    
    duration = timedelta(minutes=service.duration_minutes)

    while current_time + duration <= end_work_time:
        slot_end = current_time + duration
        
        # Verificar colisiones
        is_taken = False
        for appt in existing_appointments:
            # Lógica de superposición simple
            # Si el slot empieza antes de que termine la cita Y termina después de que empiece la cita
            appt_start = appt.start_datetime.replace(tzinfo=None) # Quitamos zona horaria para comparar simple
            appt_end = appt.end_datetime.replace(tzinfo=None)
            
            if current_time < appt_end and slot_end > appt_start:
                is_taken = True
                break
        
        if not is_taken:
            slots.append(current_time.time()) # Guardamos solo la hora

        # Avanzamos al siguiente bloque (ej. cada 30 min o duración del servicio)
        # Para simplificar MVP, avanzamos según la duración del servicio
        current_time += duration 

    return slots

# --- VISTA PASO 1: ELEGIR FECHA Y HORA ---
def booking_view(request, profile_slug, service_id):
    profile = get_object_or_404(ProfessionalProfile, slug=profile_slug)
    service = get_object_or_404(Service, id=service_id, professional=profile)
    
    # Obtener fecha seleccionada (o hoy por defecto)
    date_str = request.GET.get('date')
    if date_str:
        selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    else:
        selected_date = date.today()

    # Calcular slots
    available_slots = get_available_slots(profile, service, selected_date)

    return render(request, 'booking.html', {
        'profile': profile,
        'service': service,
        'selected_date': selected_date,
        'available_slots': available_slots
    })

# --- VISTA PASO 2: CONFIRMAR Y GUARDAR ---
def booking_confirm_view(request, profile_slug, service_id):
    profile = get_object_or_404(ProfessionalProfile, slug=profile_slug)
    service = get_object_or_404(Service, id=service_id, professional=profile)
    
    # Obtener datos de la URL (fecha y hora elegida)
    date_str = request.GET.get('date')
    time_str = request.GET.get('time')
    
    if request.method == 'POST':
        # Crear la cita
        client_name = request.POST.get('client_name')
        client_email = request.POST.get('client_email')
        client_phone = request.POST.get('client_phone')
        
        # Construir el datetime final
        start_datetime_str = f"{date_str} {time_str}"
        start_datetime = datetime.strptime(start_datetime_str, '%Y-%m-%d %H:%M')
        
        # Guardar en BBDD (Capturamos el objeto en una variable 'appointment')
        appointment = Appointment.objects.create(
            professional=profile,
            service=service,
            client_name=client_name,
            client_email=client_email,
            client_phone=client_phone,
            start_datetime=start_datetime
        )
        
        # Pasamos 'appointment' a la plantilla en lugar de solo 'service'
        return render(request, 'success.html', {
            'service': service, 
            'appointment': appointment
        })

    return render(request, 'booking_confirm.html', {
        'profile': profile,
        'service': service,
        'date_str': date_str,
        'time_str': time_str
    })