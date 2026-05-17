from pathlib import Path
import dj_database_url

# Ruta base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# CLAVE SECRETA (Mantén esta en secreto en producción más adelante)
SECRET_KEY = 'django-insecure-j%g%zddjne0x!_wrvvx0+ek(@afm+q@cb&e--8h1ufe9c&v04y'

# DEBUG activo por ahora para ver errores si ocurren
DEBUG = True

# Permitir que Render conecte con tu Backend
ALLOWED_HOSTS = ['*']

# Aplicaciones instaladas
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'App_HotelManager',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
    'corsheaders',
]

# Middlewares (CORS debe ir arriba del todo)
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'P_HotelManager.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'P_HotelManager.wsgi.application'

# ─── CONFIGURACIÓN DE BASE DE DATOS NEON (CORREGIDA) ──────────────────
DATABASES = {
    'default': dj_database_url.config(
        default='postgresql://neondb_owner:npg_sT6iewzn9ICk@ep-steep-mud-aqugh9vv-pooler.c-8.us-east-1.aws.neon.tech/neondb?sslmode=require'
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ─── USER MODEL ───────────────────────────────────────
AUTH_USER_MODEL = 'App_HotelManager.Usuario'

# ─── REST FRAMEWORK ───────────────────────────────────
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

# ─── CORS (CORREGIDO Y LIMPIO) ────────────────────────
CORS_ALLOW_ALL_ORIGINS = True