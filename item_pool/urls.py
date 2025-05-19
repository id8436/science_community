from django.urls import path
from . import views #해당 앱의 뷰를 불러온다.
from .view import profile
app_name = 'item_pool'

urlpatterns = [
    path('', views.list, name='list'),
    path('question/detail/<int:question_id>', views.detail, name='detail'),
    path('question/create/', views.create, name='create'),
    path('question/image_upload/<int:question_id>/<int:order>/', views.image_upload, name='image_upload'),
    path('question/modify/<int:question_id>/', views.modify, name='modify'),
    path('question/delete/<int:question_id>/', views.delete, name='delete'),

    path('question/solve/<int:question_id>/', views.solve, name='solve'),

    path('answer/create/<int:question_id>/', views.answer_create, name='answer_create'),
    path('answer/update/<int:answer_id>/', views.answer_update, name='answer_update'),
    path('answer/delete/<int:answer_id>/', views.answer_delete, name='answer_delete'),

    path('comment/create/<int:answer_id>/', views.comment_create, name='comment_create'),
    path('comment/update/<int:comment_id>/', views.comment_update, name='comment_update'),
    path('comment/delete/<int:comment_id>/', views.comment_delete, name='comment_delete'),

    path('comment/favorite/<int:question_id>/', views.favorite_question, name='favorite'),
    path('comment/vote/<str:type>/<int:object_id>/', views.vote, name='vote'),

    path('profile/create/', profile.create, name='profile_create'),

]