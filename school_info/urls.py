from django.urls import path
from .views import *  #해당 앱의 뷰를 불러온다.

app_name = 'school_info' #이름공간을 위한, 인덱싱을 위한 변수이다. 이걸 작성하면 인덱스는 '앱이름:인덱스'로 바뀐다.

urlpatterns = [
    path('list/', list, name='list'),
    path('posting/detail/<int:posting_id>', posting_detail, name='detail'),
    path('posting/create/', posting_create, name='create'),
    path('posting/modify/<int:posting_id>/', posting_modify, name='modify'),
    path('posting/delete/<int:posting_id>/', posting_delete, name='delete'),
    path('posting/like/<int:posting_id>/', posting_like, name='posting_like'),
    path('posting/dislike/<int:posting_id>/', posting_dislike, name='posting_dislike'),

    path('answer/create/<int:posting_id>/', answer_create, name='answer_create'),
    path('answer/update/<int:answer_id>/', answer_update, name='answer_update'),
    path('answer/delete/<int:answer_id>/', answer_delete, name='answer_delete'),

]