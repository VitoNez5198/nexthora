from django.urls import path
from django.contrib.auth.views import LogoutView 
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.index_view, name='index'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),

    path('dashboard/profile/', views.profile_setup_view, name='profile_setup'),
    path('dashboard/profile/toggle/', views.toggle_profile_visibility, name='toggle_profile_visibility'),
    path('dashboard/settings/', views.account_settings_view, name='account_settings'), 

    path('dashboard/services/', views.services_view, name='services'), 
    path('dashboard/services/edit/<int:service_id>/', views.edit_service_view, name='edit_service'),
    path('dashboard/services/toggle/<int:service_id>/', views.toggle_service_view, name='toggle_service'),
    path('dashboard/services/delete/<int:service_id>/', views.delete_service_view, name='delete_service'),
    
    path('dashboard/schedule/', views.schedule_view, name='schedule'),
    path('dashboard/schedule/delete/<int:schedule_id>/', views.delete_schedule_view, name='delete_schedule'),
    path('dashboard/schedule/delete-off/<int:timeoff_id>/', views.delete_timeoff_view, name='delete_timeoff'),

    path('dashboard/appointments/', views.appointments_view, name='appointments'),
    path('dashboard/appointments/<int:appt_id>/status/<str:new_status>/', views.update_appointment_status, name='update_appointment_status'),
    
    path('<slug:profile_slug>/book/<int:service_id>/', views.booking_view, name='booking_step1'),
    path('<slug:profile_slug>/book/<int:service_id>/confirm/', views.booking_confirm_view, name='booking_step2'),
    
    # --- NUEVA RUTA PARA EL ÉXITO ---
    path('<slug:profile_slug>/book/success/<int:appointment_id>/', views.booking_success_view, name='booking_success'),
    
    path('<slug:profile_slug>/', views.profile_view, name='public_profile'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)