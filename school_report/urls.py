from django.urls import path
from . import views #해당 앱의 뷰를 불러온다.
from .view import homeroom, classroom, school
app_name = 'school_report'

urlpatterns = [
    path('', views.main, name='main'),

    # 학교기능 관련.
    path('school/<int:school_id>/', school.main, name='school_main'),
    path('school/school_list/', school.list, name='school_list'),
    #교사명단
    path('school/teacher_assignment/<int:school_id>/', school.assignment, name='teacher_assignment'),
    path('school/download_excel_form/', school.download_excel_form, name='school_download_excel_form'),
    path('school/upload_excel_form/<int:school_id>/', school.upload_excel_form, name='school_upload_excel_form'),
    path('school/teacher_code_input/<int:school_id>/', school.teacher_code_input, name='teacher_code_input'),
    path('school/teacher_code_confirm/<int:teacher_id>/', school.teacher_code_confirm, name='teacher_code_confirm'),

    # 학급 관련.
    path('homeroom/create/<int:school_id>/', homeroom.create, name='homeroom_create'),
    path('homeroom/main/<int:homeroom_id>/', homeroom.main, name='homeroom_main'),
    path('homeroom/student_assignment/<int:homeroom_id>/', homeroom.assignment, name='student_assignment'),
    path('homeroom/download_excel_form/', homeroom.download_excel_form, name='homeroom_download_excel_form'),
    path('homeroom/upload_excel_form/<int:homeroom_id>/', homeroom.upload_excel_form, name='homeroom_upload_excel_form'),
    path('homeroom/student_code_input/<int:homeroom_id>/', homeroom.student_code_input, name='student_code_input'),
    path('homeroom/student_code_confirm/<int:student_id>/', homeroom.student_code_confirm, name='student_code_confirm'),
    # 공지
    path('homeroom/announcement/create/<int:homeroom_id>/', homeroom.announcement_create, name='announcement_create'),
    path('homeroom/posting/detail/<int:posting_id>/', homeroom.announcement_detail, name='announcement_detail'),
    path('homeroom/posting/modify/<int:posting_id>/', homeroom.announcement_modify, name='announcement_modify'),
    path('homeroom/posting/delete/<int:posting_id>/', homeroom.announcement_delete, name='announcement_delete'),
    path('homeroom/individual_excel_form/<int:homeroom_id>/', homeroom.individual_download_excel_from, name='individual_excel_form'),
    path('homeroom/individual_announcement_create/<int:announcement_id>/', homeroom.individual_announcement_create,
         name='individual_announcement_create'),
    path('homeroom/announcement_check/<int:announcement_id>/', homeroom.announcement_check, name='announcement_check'),

    # 교과교실 관련.
    path('classroom/create/<int:school_id>/', classroom.create, name='classroom_create'),
    path('classroom/main/<int:classroom_id>/', classroom.main, name='classroom_main'),
    # 과제
    path('classroom/homework/create/<int:classroom_id>/', classroom.homework_create, name='homework_create'),
    path('classroom/homework/detail/<int:posting_id>/', classroom.homework_detail, name='homework_detail'),
    path('classroom/homework/modify/<int:posting_id>/', classroom.homework_modify, name='homework_modify'),
    path('classroom/homework/delete/<int:posting_id>/', classroom.homework_delete, name='homework_delete'),
    path('classroom/homework/resubmit/<int:submit_id>/', classroom.homework_resubmit, name='homework_resubmit'),

]