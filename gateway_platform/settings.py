"""
Django settings for gateway_platform project.
Production-grade configuration with security and scalability in mind.
"""

import os
import environ
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Environment variables
env = environ.Env(
    DEBUG=(bool, False),
    SECRET_KEY=(str, ''),
    DATABASE_URL=(str, ''),
    REDIS_URL=(str, 'redis://localhost:6379/0'),
    ALLOWED_HOSTS=(list, []),
    ENCRYPTION_KEY=(str, ''),
)

# Read .env file if it exists
environ.Env.read_env(BASE_DIR / '.env')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

ALLOWED_HOSTS = env('ALLOWED_HOSTS') + ['192.168.1.75', 'scan2talk.in', 'www.scan2talk.in', '68.183.91.15']

# CSRF Trusted Origins (for production domain)
CSRF_TRUSTED_ORIGINS = [
    'https://scan2talk.in',
    'http://scan2talk.in',
    'https://www.scan2talk.in',
    'http://www.scan2talk.in',
]

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'corsheaders',
    # 'django_ratelimit',  # Disabled - requires Redis
]

LOCAL_APPS = [
    'apps.core',
    'apps.accounts',
    'apps.gateways',
    'apps.routing',
    'apps.interactions',
    'apps.communications',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.core.middleware.SecurityHeadersMiddleware',
    'apps.core.middleware.RateLimitMiddleware',
]

ROOT_URLCONF = 'gateway_platform.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.accounts.context_processors.wallet_visibility',
            ],
        },
    },
]

WSGI_APPLICATION = 'gateway_platform.wsgi.application'

# Database
if env('DATABASE_URL', default='').startswith('postgresql'):
    DATABASES = {
        'default': env.db()
    }
else:
    # Use SQLite for development
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Redis Configuration
REDIS_URL = env('REDIS_URL', default='')

# Cache Configuration - Use in-memory cache for development without Redis
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Session Configuration - Use database sessions for reliability
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'  # Changed from Strict to Lax for admin
SESSION_SAVE_EVERY_REQUEST = True

# Celery Configuration
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

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

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    },
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20
}

# Security Settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# CORS Settings
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[])

# Encryption Key for sensitive data
ENCRYPTION_KEY = env('ENCRYPTION_KEY').encode() if env('ENCRYPTION_KEY') else None

# Rate Limiting - Disabled for development without Redis
RATELIMIT_ENABLE = False
RATELIMIT_USE_CACHE = 'default'

# Logging
if DEBUG:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
            },
        },
        'root': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    }
else:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
                'style': '{',
            },
        },
        'handlers': {
            'file': {
                'level': 'INFO',
                'class': 'logging.FileHandler',
                'filename': BASE_DIR / 'logs' / 'django.log',
                'formatter': 'verbose',
            },
            'console': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'verbose',
            },
        },
        'root': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
    }

# Communication Service Settings
TWILIO_ACCOUNT_SID = env('TWILIO_ACCOUNT_SID', default='')
TWILIO_AUTH_TOKEN = env('TWILIO_AUTH_TOKEN', default='')
TWILIO_PHONE_NUMBER = env('TWILIO_PHONE_NUMBER', default='')

WHATSAPP_BUSINESS_API_TOKEN = env('WHATSAPP_BUSINESS_API_TOKEN', default='')
WHATSAPP_BUSINESS_PHONE_ID = env('WHATSAPP_BUSINESS_PHONE_ID', default='')

# SparkTG Call Masking Settings
SPARKTG_USERNAME = env('SPARKTG_USERNAME', default='')
SPARKTG_PASSWORD = env('SPARKTG_PASSWORD', default='')
SPARKTG_DID_NUMBER = env('SPARKTG_DID_NUMBER', default='01205019042')
SPARKTG_SID = env('SPARKTG_SID', default='')

# SMSCountry OTP Settings (AuthKey-based, NO SID)
SMSCOUNTRY_AUTH_KEY = env('SMSCOUNTRY_AUTH_KEY', default='')
SMSCOUNTRY_AUTH_TOKEN = env('SMSCOUNTRY_AUTH_TOKEN', default='')

# Platform Settings
PLATFORM_NAME = 'Gateway Platform'
PLATFORM_DOMAIN = env('PLATFORM_DOMAIN', default='localhost:8000')
GATEWAY_SESSION_TIMEOUT = 600  # 10 minutes
MAX_GATEWAYS_PER_USER = env('MAX_GATEWAYS_PER_USER', default=100)

# Wallet & Recharge Settings
# PhonePe Payment Gateway (Production)
PHONEPE_MERCHANT_ID = env('PHONEPE_MERCHANT_ID', default='M227BOU8BBNV7')  # Your merchant ID
PHONEPE_SALT_KEY = env('PHONEPE_SALT_KEY', default='5fb67f81-c6d6-4989-9bf4-e10c6db8ae8d')  # Your salt key
PHONEPE_SALT_INDEX = env('PHONEPE_SALT_INDEX', default=1)  # Usually 1 for production
PHONEPE_PRODUCTION = env('PHONEPE_PRODUCTION', default=False)  # Set True for production

# Legacy settings (kept for backward compatibility)
RECHARGE_API_KEY = '5fb67f81-c6d6-4989-9bf4-e10c6db8ae8d'
RECHARGE_CLIENT_ID = 'SU2504042021229572318914'
RECHARGE_TEST_MODE = env('RECHARGE_TEST_MODE', default=True)
RECHARGE_GATEWAY_URL = env('RECHARGE_GATEWAY_URL', default='https://api.rechargegateway.in')