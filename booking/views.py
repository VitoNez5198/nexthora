from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from .forms import NexthoraUserCreationForm # Importa el formulario que acabamos de crear

# --- ¡NUEVA VISTA DE INICIO! ---
def index_view(request):
    """
    Vista para la página de inicio (la raíz '/').
    Por ahora, simplemente redirige a la página de registro.
    """
    return redirect('register') # Redirige a la URL con name='register'

# --- Vista de Registro ---
def register_view(request):
    """
    Maneja la lógica para registrar un nuevo profesional.
    """
    if request.method == 'POST':
        # Si el formulario se envía (POST), procesa los datos
        form = NexthoraUserCreationForm(request.POST)
        
        if form.is_valid():
            # Si los datos son válidos (contraseñas coinciden, etc.):
            user = form.save() # 1. Guarda el nuevo usuario en la BBDD
            login(request, user) # 2. Inicia sesión automáticamente
            # 3. Redirige al profesional a su nuevo Dashboard
            return redirect('dashboard') 
        else:
            # Si el formulario no es válido (ej. usuario ya existe),
            # vuelve a mostrar la página con los errores.
            return render(request, 'register.html', {'form': form})
    
    else:
        # Si es la primera vez que se carga la página (GET):
        # 1. Crea un formulario vacío
        form = NexthoraUserCreationForm()
        # 2. Muestra la plantilla 'register.html'
        return render(request, 'register.html', {'form': form})

# --- Vista de Login (Placeholder) ---
def login_view(request):
    """
    Placeholder para la vista de login.
    (La programaremos después, pero la necesitamos para {% url 'login' %} )
    """
    # Por ahora, solo redirige al registro si intentan ir a /login/
    # TODO: Reemplazar esto con el HTML de login.html
    return redirect('register') 

# --- Vista de Dashboard ---
@login_required
def dashboard_view(request):
    """
    Vista principal del Dashboard del profesional.
    """
    # Aquí renderizamos el archivo HTML real
    return render(request, 'dashboard.html')