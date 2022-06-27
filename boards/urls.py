from django.urls import path
from .view import *  #해당 앱의 뷰를 불러온다.
from .views import board_view, humor_view, school_views

app_name = 'boards' #이름공간을 위한, 인덱싱을 위한 변수이다. 이걸 작성하면 인덱스는 '앱이름:인덱스'로 바뀐다.

urlpatterns = [
    path('list/', list, name='list'),
    path('posting/detail/<int:posting_id>', posting_detail, name='detail'),
    path('posting/create/', posting_create, name='create'),
    path('posting/modify/<int:posting_id>/', posting_modify, name='modify'),
    path('posting/delete/<int:posting_id>/', posting_delete, name='delete'),
    path('posting/like/<int:posting_id>/', posting_like, name='posting_like'),
    path('posting/dislike/<int:posting_id>/', posting_dislike, name='posting_dislike'),

    path('humor/list/<int:board_id>', humor_view.list, name='humor_list'),
    path('humor/detail/<int:posting_id>', humor_view.detail, name='humor_detail'),

    path('report/list/<int:board_id>', humor_view.report_list, name='report_list'),
    path('report/detail/<int:posting_id>', humor_view.report_detail, name='report_detail'),
    #path('report/create/<int:board_id>', humor_view.repost_create, name='report_list'),

    path('answer/create/<int:posting_id>/', answer_create, name='answer_create'),
    path('answer/update/<int:answer_id>/', answer_update, name='answer_update'),
    path('answer/delete/<int:answer_id>/', answer_delete, name='answer_delete'),

    path('comment/create/<int:answer_id>/', comment_create, name='comment_create'),
    path('comment/update/<int:comment_id>/', comment_update, name='comment_update'),
    path('comment/delete/<int:comment_id>/', comment_delete, name='comment_delete'),

    path('comment/favorite/<int:posting_id>/', favorite_posting, name='favorite'),
    path('comment/vote/<str:type>/<int:object_id>/', vote, name='vote'),

    path('tag/<str:tag_name>/', tag_info, name='tag_info'),
    path('tag/delete/<int:posting_id>/<str:tag_name>/', tag_delete, name='tag_delete'),

    path('board_list/<int:category_id>', board_view.list, name='board_list'),
    path('board/detail/<int:board_id>', board_view.detail, name='board_detail'),
    path('board/create/', board_view.create, name='board_create'),

    #-school----------------------------------------------------------------------------
    path('school/board_list/',                  school_views.board_list, name='school_board_list'),
    path('school/board_detail/<int:board_id>',  school_views.board_detail, name='school_board_detail'),
    path('school/board_create/',                school_views.board_create, name='school_board_create'),
    path('school/posting_detail/<int:posting_id>', school_views.posting_detail, name='school_posting_detail'),
    path('school/posting_create/<int:board_id>', school_views.posting_create, name='school_posting_create'),
    path('school/posting_modify/<int:posting_id>', school_views.posting_modify, name='school_posting_modify'),

    path('contest/list/<int:category_id>', board_view.contest_list, name='contest_list'),

]