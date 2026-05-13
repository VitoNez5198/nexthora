import os
from pathlib import Path
from decouple import config # Reemplazamos dotenv por decouple

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# Leemos las variables desde el .env
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)

# Permitimos todos los hosts para hacer las primeras pruebas de despliegue
ALLOWED_HOSTS = ['*'] 


# ---
# CONFIGURACIÓN CLAVE 1: TUS APLICACIONES
# ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic', # Ayuda a que WhiteNoise funcione en modo desarrollo
    'django.contrib.staticfiles',

    # --- Tus Aplicaciones ---
    'booking', 
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # NUEVO: WhiteNoise procesa los archivos estáticos rápido
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Restaurado a tu carpeta original
ROOT_URLCONF = 'nexthora_config.urls'

# ---
# CONFIGURACIÓN CLAVE 2: TEMPLATES (HTML)
# ---
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Restaurado a tu carpeta original
WSGI_APPLICATION = 'nexthora_config.wsgi.application'


# ---
# CONFIGURACIÓN CLAVE 3: LA BASE DE DATOS (PostgreSQL)
# ---
# Usamos config() para leer del .env, y le damos un default por si falla
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='nexthora_db'),
        'USER': config('DB_USER', default='nexthora_user'),
        'PASSWORD': config('DB_PASSWORD', default='Technomax1'),
        'HOST': 'localhost',
        'PORT': '5432',
    }
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# ---
# CONFIGURACIÓN CLAVE 4: OTRAS CONFIGURACIONES
# ---
LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True


# ---
# CONFIGURACIÓN CLAVE 5: STATIC FILES Y MEDIA
# ---
STATIC_URL = 'static/'

# Dónde están tus archivos de desarrollo (CSS, JS, Logo)
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Dónde se guardarán todos compilados cuando subamos a producción
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Activar la compresión y caché de WhiteNoise
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Archivos Multimedia (Las fotos que suben los profesionales)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Direcciones de Autenticación
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'