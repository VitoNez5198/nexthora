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
    
    # Ruta para eliminar un servicio específico
    path('dashboard/services/delete/<int:service_id>/', views.delete_service_view, name='delete_service'),
    
    # --- GESTIÓN DE HORARIOS ---
    # Esta es la ruta real para "Mi Horario"
    path('dashboard/schedule/', views.schedule_view, name='schedule'),
    
    # Ruta para eliminar un horario
    path('dashboard/schedule/delete/<int:schedule_id>/', views.delete_schedule_view, name='delete_schedule'),

    # --- GESTIÓN DE CITAS (AGENDA) ---
    # CAMBIO: Ahora apunta a 'views.appointments_view' en vez de 'dashboard_view'
    path('dashboard/appointments/', views.appointments_view, name='appointments'),
]