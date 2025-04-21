from django.urls import path
from . import views #해당 앱의 뷰를 불러온다.
from .view import homeroom, classroom, school, subject, homework, announcement
from .view.special import ai_completion
app_name = 'school_report'

urlpatterns = [
    path('', views.main, name='main'),

    # 학교기능 관련.
    path('school/<int:school_id>/', school.main, name='school_main'),
    path('school_create/', school.school_create, name='school_create'),
    path('school_modify/<int:school_id>/', school.school_modify, name='school_modify'),
    path('school/school_list/', school.list, name='school_list'),
    path('meal_info/<int:school_id>/', school.meal_info, name='meal_info'),
    # 과목, 교과 관련
    path('subject_create/<int:school_id>/', subject.create, name='subject_create'),
    path('subject_main/<int:room_id>/', subject.main, name='subject_main'),
    path('create_performance_score/<int:subject_id>/', school.create_performance_score, name='create_performance_score'),
    #path('subject_homework/<int:subject_id>/', subject.subject_homework_create, name='subject_homework_create'),
    path('subject_homework_check/<int:subject_id>/', subject.subject_homework_check, name='subject_homework_check'),
    #path('subject_homework/detail/<int:posting_id>/', homework.detail, name='subject_homework_detail'),

    #교사명단
    path('school/teacher_assignment/<int:school_id>/', school.teacher_assignment, name='teacher_assignment'),
    path('school/download_excel_form/<int:school_id>/', school.download_excel_form, name='school_download_excel_form'),
    path('school/upload_excel_form/<int:school_id>/', school.upload_excel_form, name='school_upload_excel_form'),
    path('school/teacher_code_input/<int:school_id>/', school.teacher_code_input, name='teacher_code_input'),
    path('school/teacher_code_confirm/<int:teacher_id>/', school.teacher_code_confirm, name='teacher_code_confirm'),
    path('school/teacher_delete/<int:teacher_id>/', school.teacher_delete, name='teacher_delete'),

    #학생명단
    path('<str:type>/student_assignment/<int:baseRoom_id>/', school.student_assignment, name='student_assignment'),
    path('<str:type>/student_download_excel_form/<int:baseRoom_id>/', school.student_download_excel_form, name='student_download_excel_form'),
    path('<str:type>/student_upload_student_excel_form/<int:baseRoom_id>/', school.student_upload_excel_form,
         name='student_upload_excel_form'),
    path('student_password_reset/<int:profile_id>/', school.student_password_reset, name='student_password_reset'),
    path('validate_teacher_password/', school.validate_teacher_password, name='validate_teacher_password'),
    path('school/student_code_input/<int:school_id>/', school.student_code_input, name='student_code_input'),
    path('school/student_code_confirm/<int:student_id>/', school.student_code_confirm, name='student_code_confirm'),
    path('school/profile_reset/<int:profile_id>/', school.profile_reset, name='profile_reset'),
    # 프로필 관련.
    path('<str:type>/delete_profile/<int:profile_id>/<int:baseRoom_id>', school.delete_profile, name='delete_profile'),
    #path('school/profile_delete/<int:profile_id>/', school.school_profile_delete, name='school_profile_delete'),
    # 학급 관련.
    path('homeroom/create/<int:school_id>/', homeroom.create, name='homeroom_create'),
    path('homeroom/main/<int:room_id>/', homeroom.main, name='homeroom_main'),
    #path('homeroom/student_assignment/<int:homeroom_id>/', homeroom.assignment, name='homeroom_student_assignment'),
    #path('homeroom/download_excel_form/<int:homeroom_id>/', homeroom.download_excel_form, name='homeroom_download_excel_form'),
    #path('homeroom/upload_excel_form/<int:homeroom_id>/', homeroom.upload_excel_form, name='homeroom_upload_excel_form'),
    path('homeroom/neis_timetable/<int:homeroom_id>/', homeroom.neis_timetable, name='neis_timetable'),
    # 공지
    path('announcement/create/<int:announce_box_id>/', announcement.create, name='announcement_create'),
    path('announcement/detail/<int:posting_id>/', announcement.detail, name='announcement_detail'),
    path('announcement/modify/<int:posting_id>/', announcement.modify, name='announcement_modify'),
    # path('homeroom/posting/modify/<int:posting_id>/', homeroom.announcement_modify, name='announcement_modify'),
    path('announcement/delete/<int:posting_id>/', announcement.delete, name='announcement_delete'),
    # path('homeroom/posting/delete/<int:posting_id>/', homeroom.announcement_delete, name='announcement_delete'),
    path('homeroom/individual_excel_form/<int:announcement_id>/', homeroom.individual_download_excel_from, name='individual_excel_form'),
    path('homeroom/individual_announcement_create/<int:announcement_id>/', homeroom.individual_upload_excel_form,
         name='individual_upload_excel_form'),
    path('homeroom/announcement_check/<int:announcement_id>/', homeroom.announcement_check, name='announcement_check'),

    # 교과교실 관련.
    path('classroom/create/<int:school_id>/', classroom.create, name='classroom_create'),
    path('classroom/main/<int:room_id>/', classroom.main, name='classroom_main'),
    # 과제
    path('homework/create/<int:homework_box_id>/', homework.create, name='homework_create'),
    path('detail/<int:posting_id>/', homework.detail, name='homework_detail'),
    path('homework/modify/<int:posting_id>/', homework.modify, name='homework_modify'),
    path('homework/delete/<int:posting_id>/', homework.delete, name='homework_delete'),
    path('classroom/homework/resubmit/<int:submit_id>/', classroom.homework_resubmit, name='homework_resubmit'),
    #path('classroom/homework/check/<int:classroom_id>/', classroom.homework_check_spreadsheet, name='homework_check_spreadsheet'), 아래로 대체.
    path('classroom/homework/check/<int:homework_box_id>/', subject.homework_check, name='homework_check'),
    path('homework/copy/<int:homework_id>/', homework.copy, name='homework_copy'),
    path('classroom/homework/end_cancel/<int:homework_id>/', classroom.homework_end_cancel, name='homework_end_cancel'),
    path('homework/homework/homework_end/<int:homework_id>/', homework.homework_end, name='homework_end'),
    path('homework/distribution/<int:homework_id>/', homework.distribution, name='homework_distribution'),
    path('homework/below_standard_set/<int:submit_id>/', homework.below_standard_set, name='homework_below_standard_set'),  # 수준미달 지정
    path('homework/below_standard_unset/<int:submit_id>/', homework.below_standard_unset, name='homework_below_standard_unset'),  # 수준미달 해제
    path('homework/reset_pending/<int:homework_id>/', homework.reset_pending,
         name='homework_reset_pending'),  # 수준미달 해제
    path('homework/collect_answers/<int:homework_box_id>/', homework.collect_answer, name='collect_answers'),  # 수준미달 지정

    # 설문 관련.
    path('homework/survey_create/<int:posting_id>/', homework.survey_create, name='homework_survey_create'),
    path('homework/survey_submit/<int:submit_id>/', homework.survey_submit, name='homework_survey_submit'),
    path('homework/survey_temporary_save/<int:submit_id>/', homework.survey_temporary_save, name='homework_survey_temporary_save'),
    path('homework/survey_temp_restore/<int:submit_id>/', homework.survey_temp_restore, name='survey_temp_restore'),
    path('homework/survey_delete/<int:submit_id>/', homework.survey_delete, name='homework_survey_delete'),
    path('homework/survey_statistics/<int:submit_id>/', homework.survey_statistics, name='homework_survey_statistics'),
    path('homework/survey_statistics_for_teacher/<int:homework_id>/', homework.survey_statistics_for_teacher, name='homework_survey_statistics_for_teacher'),
    path('classroom/homework/survey_statistics_spreadsheet/<int:posting_id>/', classroom.homework_survey_statistics_spreadsheet,
         name='homework_survey_statistics_spreadsheet'),
    path('classroom/homework/spreadsheet_to_excel_download/<int:posting_id>/', classroom.spreadsheet_to_excel_download,
         name='spreadsheet_to_excel_download'),
    path('homework/submit_file_download/<int:private_submit_id>/<int:question_id>/', homework.submit_file_download, name='submit_file_download'),  # 제출 파일 다운로드.


    # 특수설문.
    path('classroom/homework/survey_list/<int:posting_id>/', classroom.homework_survey_list,
         name='homework_survey_list'),  # 특수설문 리스트.
    # 동료평가
    path('classroom/homework/peerreview_create/<int:posting_id>/', classroom.peerreview_create, name='peerreview_create'),  # 동료평가할 때 동료평가 대상 지정.
    path('classroom/homework/peerreview_delete/<int:submit_id>/', classroom.peerreview_delete, name='peerreview_delete'),  # 동료평가 대상자에 대한 과제 모두 삭제.
    path('classroom/homework/peerreview_end/<int:posting_id>/', classroom.peerreview_end, name='peerreview_end'),  # 동료평가 마감.
    path('classroom/homework/peerreview_statistics/<int:posting_id>/', classroom.peerreview_statistics,
             name='peerreview_statistics'),  # 동료평가 통계 확인.
    path('classroom/homework/peerreview_select_comment/<int:submit_id>/', classroom.peerreview_select_comment,
             name='peerreview_select_comment'),  # 동료평가 마감 후 학우들의 평가 선택.
    path('classroom/homework/peerreview_who_is_special/<int:posting_id>/', classroom.peerreview_who_is_special,
             name='peerreview_who_is_special'),  # 동료평가. 학우들의 평가 선택 후 카운팅.
    # 세특 자료.
    path('classroom/homework/spreadsheet_upload_excel/<int:posting_id>/', classroom.spreadsheet_upload_excel,
         name='spreadsheet_upload_excel'),  # 세특 자료 엑셀로 올리기.
    path('classroom/homework/info_how_much_point_taken/<int:posting_id>/', ai_completion.info_how_much_point_taken,
         name='info_how_much_point_taken'),  # 소비 포인트 계산.
    path('classroom/homework/spreadsheet_to_ai/<int:posting_id>/', ai_completion.spreadsheet_to_ai,
         name='spreadsheet_to_ai'),  # 세특 자료 ai에 던지기.
    path('classroom/homework/read_response/<int:posting_id>/', ai_completion.read_response,
         name='read_response'),  # ai가 만든 세특 자료 보기.

]