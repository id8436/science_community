from django.urls import path
from . import views  # 해당 앱의 뷰를 불러온다.
from .view import mental_health_chatbot
from .language.translate_ko_en import  translate_ko_en
from .language.korean_spell import korean_spell
from utility.data_analysis import data_analysis
app_name = 'utility'

urlpatterns = [
    path('', views.main, name='main'),
    path('do_DB/', views.do_DB, name='do_DB'),  # 변동사항이 생겨 데이터베이스에 반영이 필요할 때.

    path('compound_interest/', views.compound_interest, name='compound_interest'),

    # 심리상담봇
    path('mental_health_chatbot/', mental_health_chatbot.chatroom, name='mental_health_chatroom'),
    # 번역
    path('translate_ko_en/', translate_ko_en.translate, name='translate_ko_en'),
    # 맞춤법
    path('korean_spell/', korean_spell.main, name='korean_spell'),
    path('korean_spell/upload_excel_form/', korean_spell.upload_excel_form, name='korean_spell_upload_excel_form'),
    # 데이터분석
    path('data_analysis/', data_analysis.main, name='data_analysis_main'),
    path('data_analysis/upload_excel/', data_analysis.upload_excel, name='data_analysis_upload_excel'),
    path('data_analysis/correlation/', data_analysis.correlation, name='data_analysis_correlation'),
    path('data_analysis/linearRegression/', data_analysis.linearRegression, name='data_analysis_linearRegression'),
    path('data_analysis/draw_graph_table/', data_analysis.draw_graph_table, name='data_analysis_draw_graph_table'),
    path('data_analysis/draw_graph/', data_analysis.draw_graph, name='data_analysis_draw_graph'),



]