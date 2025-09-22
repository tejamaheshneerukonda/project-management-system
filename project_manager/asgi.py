"""
ASGI config for project_manager project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project_manager.settings")

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
asgi_app = get_asgi_application()

# Import after initializing asgi_app to avoid circular imports
import core.routing

application = ProtocolTypeRouter({
    # Handle HTTP requests with Django's ASGI application
    "http": asgi_app,
    # Handle WebSocket requests with our custom routing
    "websocket": AuthMiddlewareStack(
        URLRouter(
            core.routing.websocket_urlpatterns
        )
    ),
})
