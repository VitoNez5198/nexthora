"""
Configuración principal de Django para el proyecto Nexthora.
"""

from pathlib import Path
import os # ¡Importante! Necesitamos 'os' para unir rutas

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-tu-secret-key-aqui' # ¡Cambia esto!

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# ---
# CONFIGURACIÓN CLAVE 1: TUS APLICACIONES
# ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # --- Aplicaciones de Terceros (las instalarás después) ---
    # 'rest_framework',  # Para crear tu API (DRF)
    # 'corsheaders',   # Para permitir que tu JS hable con tu API

    # --- Tus Aplicaciones (La Magia) ---
    'booking',         # ¡Tu app principal! (donde está models.py)
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # 'corsheaders.middleware.CorsMiddleware', # (Para la API)
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'nexthora_config.urls'

# ---
# CONFIGURACIÓN CLAVE 2: TEMPLATES (HTML)
# ---
# Le decimos a Django dónde encontrar tu carpeta 'templates' en la raíz.
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')], # ¡Línea clave!
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

WSGI_APPLICATION = 'nexthora_config.wsgi.application'


# ---
# CONFIGURACIÓN CLAVE 3: LA BASE DE DATOS (PostgreSQL)
# ---
# Así le dices a Django que use PostgreSQL.
# Necesitarás instalar: pip install psycopg2-binary
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'nexthora_db',          # El nombre de tu BBDD en PostgreSQL
        'USER': 'nexthora_user',       # Tu usuario de PostgreSQL
        'PASSWORD': 'Trevor1995',
        'HOST': 'localhost',             # O la dirección de tu BBDD
        'PORT': '5432',                  # Puerto por defecto de PostgreSQL
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    # ... (Se quedan los validadores por defecto) ...
]


# ---
# CONFIGURACIÓN CLAVE 4: OTRAS CONFIGURACIONES
# ---
LANGUAGE_CODE = 'es-cl'  # Para que el admin esté en español chileno
TIME_ZONE = 'America/Santiago' # ¡Crítico para tu app de agenda!
USE_I18N = True
USE_TZ = True # ¡Crítico! Guarda todo en UTC en la BBDD.

# ---
# CONFIGURACIÓN CLAVE 5: STATIC FILES (CSS, JS)
# ---
# La URL para acceder a los archivos estáticos
STATIC_URL = '/static/'

# ¡Línea clave! Le decimos a Django dónde encontrar tu carpeta 'static' en la raíz.
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'