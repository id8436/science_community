from django.urls import path
from .view import *  #해당 앱의 뷰를 불러온다.
from . import base_views
from .views import score_share

app_name = 'boards' #이름공간을 위한, 인덱싱을 위한 변수이다. 이걸 작성하면 인덱스는 '앱이름:인덱스'로 바뀐다.
urlpatterns = [
    # Checks 일반적으로 Ajax로 구현.
    path('posting/like/<int:posting_id>/', posting_like, name='posting_like'),
    path('posting/dislike/<int:posting_id>/', posting_dislike, name='posting_dislike'),
    path('posting/interest/<int:posting_id>/', posting_interest, name='posting_interest'),
    path('board/interest/<int:board_id>/', board_interest, name='board_interest'),
    # Answer CRUD. 일반적으로 Ajax로 구현.
    path('answer/create/<int:posting_id>/', answer_create, name='answer_create'),
    path('answer/update/<int:answer_id>/', answer_update, name='answer_update'),
    path('answer/delete/<int:answer_id>/', answer_delete, name='answer_delete'),
    # Comment CRUD. 일반적으로 Ajax로 구현.
    path('comment/create/<int:answer_id>/', comment_create, name='comment_create'),
    path('comment/update/<int:comment_id>/', comment_update, name='comment_update'),
    path('comment/delete/<int:comment_id>/', comment_delete, name='comment_delete'),

    path('tag/<str:tag_name>/', tag_info, name='tag_info'),
    path('tag/delete/<int:posting_id>/<str:tag_name>/', tag_delete, name='tag_delete'),

    # Board CRUD
    path('board/list/<int:category_id>/', base_views.board_list, name='board_list'),
    path('board/detail/<int:board_id>/', base_views.board_detail, name='board_detail'),
    path('board/create/<int:category_id>', base_views.board_create, name='board_create'),
    path('board/delete/<int:board_id>/', base_views.board_delete, name='board_delete'),
    # Posting CRUD
    path('posting/list/<int:board_id>/', base_views.board_detail, name='posting_list'),  # 위 게시판 보기와 동일.
    path('posting/detail/<int:posting_id>', base_views.posting_detail_on_board, name='posting_detail'),
    path('posting/create/<int:board_id>', base_views.posting_create_on_board, name='posting_create'),
    path('posting/modify/<int:posting_id>', base_views.posting_modify_on_board, name='posting_modify'),
    path('posting/delete/<int:posting_id>/', base_views.posting_delete, name='posting_delete'),

    # report
    path('report_user/', base_views.report_user, name='report_user'),

    # score_share
    path('score/profile_create/<int:board_id>/', score_share.profile_create, name='profile_create'),
    path('score/subject_create/<int:board_id>/', subject_create, name='subject_create'),
    path('score/subject_register/<int:board_id>/', subject_register, name='subject_register'),
    path('score/subject_download_excel_form/<int:board_id>/', subject_download_excel_form, name='subject_download_excel_form'),
    path('score/subject_upload_excel_form/<int:board_id>/', subject_upload_excel_form, name='subject_upload_excel_form'),
    path('score/subject_answer_info_form_download/<int:subject_id>/', score_share.subject_answer_info_form_download,
         name='subject_answer_info_form_download'),
    path('score/subject_answer_info_form_upload/<int:subject_id>/', score_share.subject_answer_info_form_upload,
         name='subject_answer_info_form_upload'),

    # result
    path('score/result/<int:board_id>/', score_share.result_main, name='exam_result'),
    path('score/result_for_teacher/<int:subject_id>/', score_share.result_for_teacher, name='result_for_teacher'),
    path('score/show_answer/<int:score_id>/', score_share.show_answer, name='show_answer'),
    path('score/show_answer_for_teacher/<int:subject_id>/', score_share.show_answer_for_teacher, name='show_answer_for_teacher'),


]

