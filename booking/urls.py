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
]