"""
PythonAnywhere Production Settings (No WebSocket)
Optimized for PythonAnywhere free tier without real-time features
"""

from .settings import *
import os

# Security settings for production
DEBUG = False
ALLOWED_HOSTS = ['tejamaheshneerukonda.pythonanywhere.com', 'www.tejamaheshneerukonda.pythonanywhere.com']

# Database configuration for PythonAnywhere
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Static files configuration
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Session settings
SESSION_COOKIE_SECURE = False  # Set to True if using HTTPS
CSRF_COOKIE_SECURE = False    # Set to True if using HTTPS

# Email configuration (optional - for contact forms)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'django.log'),
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}

# Cache configuration (using dummy cache for free tier)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Remove channels from INSTALLED_APPS for PythonAnywhere free tier
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != 'channels']

# Remove channels middleware
MIDDLEWARE = [middleware for middleware in MIDDLEWARE if middleware != 'channels.middleware.WebSocketMiddleware']

# Disable ASGI application (use WSGI only)
# ASGI_APPLICATION = None

# Remove channel layers configuration
# CHANNEL_LAYERS = None
