from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
import datetime

# ---
# MODELO 1: El Profesional (Tu Usuario)
# ---
# Usamos el sistema de Usuarios de Django, pero lo extendemos
# para guardar su info "pública" de Nexthora.
class ProfessionalProfile(models.Model):
    """
    Guarda la información pública del profesional (tu cliente).
    Se crea automáticamente cuando un 'User' de Django se registra.
    """
    # Conexión 1-a-1 con el usuario de Django (el que tiene email/contraseña)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    
    # Este es el link público: nexthora.com/[slug]
    # Ej: nexthora.com/la-mejor-manicurista
    slug = models.SlugField(max_length=100, unique=True, blank=True, 
                            help_text="La URL pública de tu perfil. Ej: 'la-mejor-manicurista'")
    
    # El nombre que se muestra en el perfil público
    display_name = models.CharField(max_length=100, help_text="El nombre de tu negocio. Ej: 'Manicure Express'")
    
    # Una pequeña biografía que se muestra en la página
    bio = models.TextField(max_length=500, blank=True, null=True, help_text="Describe brevemente tus servicios.")

    def __str__(self):
        return self.user.username
    
    # Lógica para crear el 'slug' automáticamente basado en el nombre de usuario
    def save(self, *args, **kwargs):
        if not self.slug:
            # Crea un slug único basado en el username
            base_slug = slugify(self.user.username) if self.user.username else "perfil"
            new_slug = base_slug
            counter = 1
            # Asegura que el slug sea único
            while ProfessionalProfile.objects.filter(slug=new_slug).exists():
                new_slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = new_slug
        super().save(*args, **kwargs)

# ---
# SEÑAL: Crear Perfil Automáticamente
# ---
# Esta función "escucha" cuando un 'User' se crea
# y automáticamente crea un 'ProfessionalProfile' vacío para él.
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Crea un ProfessionalProfile cuando se crea un User.
    """
    if created:
        ProfessionalProfile.objects.create(user=instance)
    instance.profile.save()


# ---
# MODELO 2: El Horario del Profesional (BusinessHours)
# ---
# Define los bloques de tiempo en que el profesional TRABAJA.
# Ej: "Lunes de 9:00 a 17:00", "Miércoles de 10:00 a 14:00"
class BusinessHours(models.Model):
    """
    Define los bloques de horario laboral del profesional.
    El profesional puede tener varios (ej. Lunes en la mañana y Lunes en la tarde).
    """
    WEEKDAYS = [
        (0, "Lunes"),
        (1, "Martes"),
        (2, "Miércoles"),
        (3, "Jueves"),
        (4, "Viernes"),
        (5, "Sábado"),
        (6, "Domingo"),
    ]

    professional = models.ForeignKey(ProfessionalProfile, on_delete=models.CASCADE, related_name="business_hours")
    weekday = models.IntegerField(choices=WEEKDAYS, help_text="Día de la semana")
    start_time = models.TimeField(help_text="Hora de inicio (formato 24h, ej: 09:00)")
    end_time = models.TimeField(help_text="Hora de fin (formato 24h, ej: 17:00)")

    def __str__(self):
        return f"{self.professional.display_name} - {self.get_weekday_display()}: {self.start_time} a {self.end_time}"
    
    class Meta:
        ordering = ['weekday', 'start_time'] # Ordena los horarios
        unique_together = ('professional', 'weekday', 'start_time', 'end_time') # Evita duplicados

# ---
# MODELO 3: El Servicio (El Corazón del MVP Flexible)
# ---
# Aquí está la flexibilidad que hablaste para el tatuador y la manicurista.
class Service(models.Model):
    """
    Cada servicio que ofrece el profesional.
    La clave es la 'duration_minutes' para la flexibilidad del MVP.
    """
    professional = models.ForeignKey(ProfessionalProfile, on_delete=models.CASCADE, related_name="services")
    
    # Nombre del servicio: "Tatuaje (Sesión Larga)" o "Uñas Acrílicas"
    name = models.CharField(max_length=150)
    
    # Descripción que verá el cliente
    description = models.TextField(blank=True, null=True)
    
    # ¡La flexibilidad del MVP!
    # Tatuaje 4 horas = 240 minutos
    # Corte Pelo = 45 minutos
    duration_minutes = models.IntegerField(help_text="Duración total del servicio en minutos. Ej: 45")
    
    # Precio que se muestra en la página (Plan Gratuito)
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Precio a mostrar (ej: 15000.00)", blank=True, null=True)

    is_active = models.BooleanField(default=True, help_text="Marca si el servicio está activo y se puede agendar")

    def __str__(self):
        return f"{self.name} ({self.professional.display_name})"

# ---
# MODELO 4: La Cita (La Reserva)
# ---
# La cita confirmada. Conecta al Profesional, el Servicio y el Cliente.
class Appointment(models.Model):
    """
    La cita agendada. Es el registro que bloquea el tiempo.
    """
    STATUS_CHOICES = [
        ('CONFIRMED', 'Confirmada'),
        ('CANCELLED_BY_CLIENT', 'Cancelada por Cliente'),
        ('CANCELLED_BY_PRO', 'Cancelada por Profesional'),
        ('COMPLETED', 'Completada'),
    ]

    # A qué profesional pertenece
    professional = models.ForeignKey(ProfessionalProfile, on_delete=models.SET_NULL, null=True, related_name="appointments")
    
    # Qué servicio se agendó
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, related_name="appointments")
    
    # Datos del cliente final
    client_name = models.CharField(max_length=200)
    client_email = models.EmailField()
    client_phone = models.CharField(max_length=20, blank=True, null=True) # Opcional
    
    # La hora de inicio (¡La clave!)
    start_datetime = models.DateTimeField(help_text="Fecha y hora de inicio de la cita")
    
    # La hora de fin (la calculamos automáticamente)
    end_datetime = models.DateTimeField(help_text="Fecha y hora de fin de la cita (calculada automáticamente)")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='CONFIRMED')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cita para {self.client_name} - {self.service.name} el {self.start_datetime}"

    # Lógica automática: Cuando guardes la cita, calcula la hora de fin.
    def save(self, *args, **kwargs):
        if self.start_datetime and self.service:
            # Calcula la hora de fin sumando los minutos del servicio
            self.end_datetime = self.start_datetime + datetime.timedelta(minutes=self.service.duration_minutes)
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['start_datetime']

class TimeOff(models.Model):
    """
    Representa días o rangos de fechas en los que el profesional NO trabaja,
    independientemente de su horario recurrente.
    """
    professional = models.ForeignKey(ProfessionalProfile, on_delete=models.CASCADE, related_name="time_off")
    start_date = models.DateField(help_text="Fecha de inicio del bloqueo")
    end_date = models.DateField(help_text="Fecha de fin del bloqueo (puede ser la misma que inicio)")
    description = models.CharField(max_length=100, blank=True, help_text="Ej: Vacaciones, Médico, Feriado")

    def __str__(self):
        return f"{self.professional} off: {self.start_date} - {self.end_date}"