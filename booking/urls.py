from django.urls import path
from . import views # ¡Importa la lógica de 'views.py'!

# Este es el "mapa" del departamento de Booking
urlpatterns = [
    # --- ¡NUEVA RUTA DE INICIO! ---
    # Cuando alguien visite la raíz (''), usa la 'index_view'.
    path('', views.index_view, name='index'),
    # --- Rutas del Mundo 2 (Profesional) ---
    
    # Cuando alguien vaya a '.../register/', ejecuta la función 'register_view'.
    # El 'name="register"' es el que usa tu HTML {% url 'register' %}
    path('register/', views.register_view, name='register'),
    
    # Ruta para el Login (para que {% url 'login' %} funcione)
    path('login/', views.login_view, name='login'),
    
    # Ruta para el Dashboard (a donde redirigimos después de registrarse)
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # --- Rutas del Mundo 1 (Cliente) ---
    # (Las crearemos después)
]