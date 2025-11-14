from django.contrib import admin
from django.urls import path, include # ¡Asegúrate de importar 'include'!

urlpatterns = [
    # La ruta para el admin de Django (¡la que ya usaste!)
    path('admin/', admin.site.urls),
    
    # --- ¡NUEVA LÍNEA CLAVE! ---
    # Cuando alguien vaya a la raíz de tu sitio (ej. '.../'),
    # Django cargará todas las rutas que definimos en 'booking/urls.py'.
    path('', include('booking.urls')), 
]