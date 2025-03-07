import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beacon_project.settings')
django.setup()

def get_application():
    from channels.auth import AuthMiddlewareStack
    from channels.routing import URLRouter
    from Realtime.routing import websocket_urlpatterns
    return ProtocolTypeRouter({
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(
            URLRouter(
                websocket_urlpatterns
            )
        ),
    })

application = get_application()