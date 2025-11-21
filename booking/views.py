from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages  # ¡Faltaba esto!
from django.http import HttpResponse

# Importamos los formularios y modelos
from .forms import NexthoraUserCreationForm, ServiceForm
from .models import Service, ProfessionalProfile

from .forms import BusinessHoursForm # ¡Importa el nuevo form!
from .models import BusinessHours # ¡Importa el modelo!


from .models import Appointment
from django.utils import timezone
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
    # (Usamos timezone.now() para no mostrar citas antiguas, opcional)
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