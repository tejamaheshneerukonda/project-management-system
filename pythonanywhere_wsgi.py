# PythonAnywhere WSGI Configuration File
# This file is used by PythonAnywhere to serve your Django app

import os
import sys

# Add your project directory to the Python path
path = '/home/tejamaheshneerukonda/project-management-system'
if path not in sys.path:
    sys.path.append(path)

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_manager.settings_pythonanywhere')

# Import Django's WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
