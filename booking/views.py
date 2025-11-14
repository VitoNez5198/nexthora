from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages # Para enviar mensajes de éxito o error

# ¡Importante! Usaremos el formulario de creación de usuarios que Django
# ya tiene listo, es más seguro y fácil.
from .forms import NexthoraUserCreationForm # Crearemos este formulario en un momento*

# ---
# VISTA DE REGISTRO (MUNDO 2: PROFESIONAL)
# ---
def register_view(request):
    """
    Maneja la lógica para la página de registro de un nuevo profesional.
    """
    # Si el método es POST, significa que el usuario envió el formulario
    if request.method == 'POST':
        # 1. Crea una instancia del formulario con los datos recibidos (request.POST)
        form = NexthoraUserCreationForm(request.POST)
        
        # 2. Django valida los datos (ej. email válido, contraseñas coinciden)
        if form.is_valid():
            # 3. Si es válido, guarda el nuevo usuario en la BBDD
            user = form.save() 
            
            # 4. (Opcional pero recomendado) Inicia sesión automáticamente
            #    con el usuario que acabamos de crear.
            login(request, user)
            
            # 5. Muestra un mensaje de éxito (lo podemos mostrar en el dashboard)
            messages.success(request, "¡Tu cuenta ha sido creada con éxito!")
            
            # 6. Redirige al usuario a la página de "Dashboard"
            #    (¡Esta URL 'dashboard' la crearemos después!)
            return redirect('dashboard') 
        else:
            # 7. Si el formulario no es válido (ej. email ya existe),
            #    vuelve a mostrar la página de registro CON los errores.
            messages.error(request, "Hubo un error en tu registro. Por favor, revisa los campos.")
            # (El 'form' ahora contiene los mensajes de error que se mostrarán en el HTML)

    # Si el método es GET (el usuario solo está visitando la página)
    else:
        # 1. Crea un formulario vacío
        form = NexthoraUserCreationForm()

    # 2. Muestra la plantilla 'register.html' y le pasa el formulario
    #    (ya sea vacío o con los errores)
    return render(request, 'register.html', {'form': form})

# ---
# VISTA DE LOGIN (MUNDO 2: PROFESIONAL)
# ---
def login_view(request):
    # (Esta la programaremos después, pero necesitamos la URL)
    return render(request, 'login.html') # Asumimos que tienes 'login.html'

# ---
# VISTA DE DASHBOARD (MUNDO 2: PROFESIONAL)
# ---
def dashboard_view(request):
    # (Esta la programaremos después, pero necesitamos la URL)
    return render(request, 'dashboard.html') # Asumimos que tienes 'dashboard.html'