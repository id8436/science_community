from django.urls import path
from . import views  # 해당 앱의 뷰를 불러온다.
from .view import mental_health_chatbot
from .language.translate_ko_en import  translate_ko_en
from .language.korean_spell import korean_spell
app_name = 'utility'

urlpatterns = [
    path('', views.main, name='main'),
    path('compound_interest/', views.compound_interest, name='compound_interest'),

    # 심리상담봇
    path('mental_health_chatbot/', mental_health_chatbot.chatroom, name='mental_health_chatroom'),
    # 번역
    path('translate_ko_en/', translate_ko_en.translate, name='translate_ko_en'),
    # 맞춤법
    path('korean_spell/', korean_spell.main, name='korean_spell'),
    path('korean_spell/upload_excel_form/', korean_spell.upload_excel_form, name='korean_spell_upload_excel_form'),
]