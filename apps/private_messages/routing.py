from django.urls import re_path
from . import consumers

websocket = [
    re_path(r'ws/chats/(?P<chat_id>\d+)/$', consumers.ChatConsumers.as_asgi()),
]