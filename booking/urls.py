from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='index'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # --- NUEVAS RUTAS (Placeholders para que el dashboard no falle) ---
    # Usaremos 'dashboard_view' temporalmente hasta que creemos las vistas reales
    path('services/', views.dashboard_view, name='services'), 
    path('schedule/', views.dashboard_view, name='schedule'),
    path('appointments/', views.dashboard_view, name='appointments'),
    
    # --- GESTIÓN DE SERVICIOS ---
    # Esta es la ruta real para "Mis Servicios"
    path('dashboard/services/', views.services_view, name='services'), 
    
     # NUEVAS RUTAS:
    path('dashboard/services/edit/<int:service_id>/', views.edit_service_view, name='edit_service'),
    path('dashboard/services/toggle/<int:service_id>/', views.toggle_service_view, name='toggle_service'),
    path('dashboard/services/delete/<int:service_id>/', views.delete_service_view, name='delete_service'),
    # --- GESTIÓN DE HORARIOS ---
    # Esta es la ruta real para "Mi Horario"
    path('dashboard/schedule/', views.schedule_view, name='schedule'),
    
    # Ruta para eliminar un horario
    path('dashboard/schedule/delete/<int:schedule_id>/', views.delete_schedule_view, name='delete_schedule'),

    # --- GESTIÓN DE CITAS (AGENDA) ---
    # CAMBIO: Ahora apunta a 'views.appointments_view' en vez de 'dashboard_view'
    path('dashboard/appointments/', views.appointments_view, name='appointments'),
    
    # --- FLUJO DE RESERVA (CLIENTE) ---
    # Paso 1: Elegir Fecha y Hora
    path('<slug:profile_slug>/book/<int:service_id>/', views.booking_view, name='booking_step1'),
    
    # Paso 2: Confirmar y Pagar (o solo Datos)
    path('<slug:profile_slug>/book/<int:service_id>/confirm/', views.booking_confirm_view, name='booking_step2'),
    
    # --- RUTA PÚBLICA (¡SIEMPRE AL FINAL!) ---
    # Captura cualquier texto (slug) y busca un perfil.
    # Ej: nexthora.com/peluqueria-cool -> profile_slug="peluqueria-cool"
    path('<slug:profile_slug>/', views.profile_view, name='public_profile'),
    
    path('dashboard/schedule/delete-off/<int:timeoff_id>/', views.delete_timeoff_view, name='delete_timeoff'),
]