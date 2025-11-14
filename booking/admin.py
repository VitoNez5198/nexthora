from django.contrib import admin
from .models import ProfessionalProfile, BusinessHours, Service, Appointment

# ---
# Personalización del Admin (Opcional pero recomendado)
# ---

# Esto permite ver los "Servicios" y "Horarios" DENTRO de la página del Profesional
class ServiceInline(admin.TabularInline):
    model = Service
    extra = 1 # Muestra 1 campo de servicio vacío por defecto

class BusinessHoursInline(admin.TabularInline):
    model = BusinessHours
    extra = 1 # Muestra 1 campo de horario vacío

# Personaliza cómo se ve el ProfessionalProfile en el admin
@admin.register(ProfessionalProfile)
class ProfessionalProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'display_name', 'slug') # Columnas a mostrar
    search_fields = ('display_name', 'user__username') # Barra de búsqueda
    inlines = [BusinessHoursInline, ServiceInline] # ¡La magia!

# Personaliza cómo se ven las Citas
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'professional', 'service', 'start_datetime', 'status')
    list_filter = ('status', 'professional', 'start_datetime') # Filtros al costado
    search_fields = ('client_name', 'professional__display_name')

# Registra los modelos que no necesitan tanta personalización (aún)
# admin.site.register(Service) # Ya no es necesario, está en el Inline
# admin.site.register(BusinessHours) # Ya no es necesario, está en el Inline
