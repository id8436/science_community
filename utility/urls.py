from django.urls import path
from . import views  # 해당 앱의 뷰를 불러온다.
from .view import mental_health_chatbot
app_name = 'utility'

urlpatterns = [
    path('', views.main, name='main'),
    path('compound_interest/', views.compound_interest, name='compound_interest'),

    # 심리상담봇
    path('mental_health_chatbot/', mental_health_chatbot.chatroom, name='mental_health_chatroom'),

]