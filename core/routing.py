from django.urls import re_path
from . import consumers
from . import leave_consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/room/(?P<room_id>\w+)/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/leave-requests/$', leave_consumers.LeaveRequestConsumer.as_asgi()),
]