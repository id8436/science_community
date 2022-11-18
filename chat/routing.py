from django.urls import re_path

from . import consumers
from utility.mental_health_chatbot import mental_chatbot_consumers

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<room_name>\w+)/$", consumers.ChatConsumer.as_asgi()),
    #re_path("ws/mental_health_chatbot/", mental_chatbot_consumers.ChatConsumer.as_asgi()),
]