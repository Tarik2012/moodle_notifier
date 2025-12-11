from pathlib import Path
import os
from dotenv import load_dotenv

# ======================
# LOAD .ENV
# ======================
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# ======================
# SECURITY / DEBUG
# ======================
SECRET_KEY = os.getenv("SECRET_KEY", "dev-key")
DEBUG = os.getenv("DEBUG", "True") == "True"

# En desarrollo lo dejamos abierto
ALLOWED_HOSTS = ["*"]  
# En producción: ALLOWED_HOSTS = ["tu-dominio.com"]


# ======================
# INSTALLED APPS
# ======================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Apps del proyecto
    'core',
    'moodle_app',
    'whatsapp_app',
    'notifier',
    'dashboard',
]


# ======================
# MIDDLEWARE
# ======================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# ======================
# ROOT & URLS
# ======================
ROOT_URLCONF = 'notifier_backend.urls'


# ======================
# TEMPLATES
# ======================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / "templates",   # carpeta global de templates
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# ======================
# WSGI
# ======================
WSGI_APPLICATION = 'notifier_backend.wsgi.application'


# ======================
# DATABASE (POSTGRESQL)
# ======================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv("DB_NAME"),
        'USER': os.getenv("DB_USER"),
        'PASSWORD': os.getenv("DB_PASSWORD"),
        'HOST': os.getenv("DB_HOST", "localhost"),
        'PORT': os.getenv("DB_PORT", "5432"),
    }
}


# ======================
# AUTH / LOGIN
# ======================

# Después de login → Admin
LOGIN_REDIRECT_URL = '/'

# Después de logout → Login
LOGOUT_REDIRECT_URL = '/login/'

# URL del formulario de login
LOGIN_URL = 'login'


# ======================
# PASSWORD VALIDATION
# ======================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ======================
# INTERNATIONALIZATION
# ======================
LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'Europe/Madrid'
USE_I18N = True
USE_TZ = True


# ======================
# STATIC FILES
# ======================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = []


# ======================
# DEFAULT PRIMARY KEY
# ======================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ======================
# MOODLE SETTINGS
# ======================
MOODLE_URL = os.getenv("MOODLE_URL")
MOODLE_TOKEN = os.getenv("MOODLE_TOKEN")


# ======================
# WHATSAPP SETTINGS
# ======================
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID")
WHATSAPP_BUSINESS_ID = os.getenv("WHATSAPP_BUSINESS_ID")
