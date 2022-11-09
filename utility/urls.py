from django.urls import path
from . import views #해당 앱의 뷰를 불러온다.
app_name = 'utility'

urlpatterns = [
    path('/', views.main, name='main'),
    path('compound_interest/', views.compound_interest, name='compound_interest'),

]