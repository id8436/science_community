from django.shortcuts import render, get_object_or_404, redirect, resolve_url, HttpResponse
from .. import models  # 모델 호출.
from ..forms import HomeroomForm, SchoolForm, SubjectForm
from django.contrib import messages
from custom_account.decorator import custom_login_required as login_required
import openpyxl
from . import check
from django.http import HttpResponse
import random
from boards.models import Board, Board_category, Board_name
from .for_api import SchoolMealsApi
from ..forms import HomeworkForm
from custom_account.models import Notification
import pandas as pd
from school_report.view import homework
from school_report.view import school as school_view
@login_required()
def create(request, school_id):
    '''교과 생성.'''
    context = {}
    school = get_object_or_404(models.School, pk=school_id)
    if request.method == 'POST':  # 포스트로 요청이 들어온다면... 글을 올리는 기능.
        check_teacher = check.Teacher(user=request.user, school=school, request=request)
        profile = check_teacher.in_school()
        if profile == None:
            return check_teacher.redirect_to_school()
        form = SubjectForm(request.POST)  # 폼을 불러와 내용입력을 받는다.
        if form.is_valid():  # 문제가 없으면 다음으로 진행.
            subject = form.save(commit=False)
            subject.school = school
            #teacher = check.Teacher(request, school).in_school_and_none()
            subject.master_profile = profile
            name = school_view.name_trimming(subject.subject_name)  # 이름에서 공백 제거해 적용.
            subject.subject_name = name
            subject.save()
            homework_box, created = models.HomeworkBox.objects.get_or_create(subject=subject)
            announce_box, created = models.AnnounceBox.objects.get_or_create(subject=subject)
            messages.info(request, str(subject.subject_name)+' 생성에 성공하였습니다.')
            return redirect('school_report:school_main', school_id=school.id)
    else:  # 포스트 요청이 아니라면.. form으로 넘겨 내용을 작성하게 한다.
        form = SubjectForm()
    context['form'] = form  # 폼에서 오류가 있으면 오류의 내용을 담아 create.html로 넘긴다.
    return render(request, 'school_report/school/subject/subject_create.html', context)
def main(request, subject_id):
    subject = get_object_or_404(models.Subject, pk=subject_id)
    context = {'subject': subject}
    # 선생님, 혹은 학생객체 가져오기.
    context['student'] = check.Student(user=request.user, school=subject.school).in_school_and_none()
    context['teacher'] = check.Teacher(user=request.user, school=subject.school).in_school_and_none()  # 선생님객체.
    # 교과과제목록.
    homework_box = subject.homeworkbox
    homework_list = homework_box.homework_set.order_by('-create_date')
    # subject_homework_list = classroom.base_subject.homework_set.order_by('-create_date')
    #context['subject_homework_list'] = subject_homework_list
    context['classroom_list'] = subject.classroom_set.all().order_by('homeroom__name')
    context['homework_list'] = homework_list
    return render(request, 'school_report/school/subject/main.html', context)
@login_required()
def subject_homework_create(request, homework_box_id):
    pass  # 없어도 될듯...? classroom도 box_id 지정하면서 넘어가면 좋을듯.
#    subject = get_object_or_404(models.Subject, pk=subject_id)
#    homework_box = models.HomeworkBox.objects.get(subject=subject)
#    return homework.create(request, homework_box_id=homework_box.id)

@login_required()
def homework_check(request, homework_box_id):
    '''학교, 교실, 교과 등 박스정보를 받아 과제 했나 여부를 체크.'''
    homework_box = get_object_or_404(models.HomeworkBox, pk=homework_box_id)
    context = {}
    school = homework_box.get_school_model()
    # 관련자만 접근하게끔.
    student = check.Student(usser=request.user, school=school).in_school_and_none()
    teacher = check.Teacher(usser=request.user, school=school).in_school_and_none()
    if teacher:
        student_list = homework_box.get_profiles()
        homework_list = homework_box.homework_set().all()
        info_dic = {'student': student_list}
        for homework in homework_list:
            info_dic[homework.subject] = []  # 과제명으로 사전key, 리스트 만들기.
            for student in student_list:
                try:  # 동료평가 등 특수설문에서 에러.(과제 부여가 안된 경우에도)
                    submit = models.HomeworkSubmit.objects.get(base_homework=homework, to_profile=student)
                    if submit.check:
                        info_dic[homework.subject].append("제출")
                    elif submit.read:
                        info_dic[homework.subject].append("읽음")
                    else:
                        info_dic[homework.subject].append("미열람")
                except:
                    info_dic[homework.subject].append("특수상황")
        print(info_dic)
        df = pd.DataFrame(info_dic)
        df_dict = df.to_dict(orient='records')
    elif student:  # 학생인 경우.
        homework_list = homework_box.homework_set.all()
        info_dic = {'student': student}
        for homework in homework_list:
            info_dic[homework.subject] = []  # 과제명으로 사전key, 리스트 만들기.
            try:
                submit = models.HomeworkSubmit.objects.get(base_homework=homework, to_profile=student)
                if submit.check:
                    info_dic[homework.subject].append("제출")
                elif submit.read:
                    info_dic[homework.subject].append("읽음")
                else:
                    info_dic[homework.subject].append("미열람")
            except:  # 동료평가 등 특수설문에서 에러.(과제 부여가 안된 경우에도)
                info_dic[homework.subject].append("특수상황")
        df = pd.DataFrame(info_dic)
        df_dict = df.to_dict(orient='records')
    else:
        messages.info(request, "이 학교에 소속된 인원이 아닙니다.")

    context['data_list'] = df_dict
    return render(request, 'school_report/classroom/homework/check_spreadsheet.html', context)
@login_required()  ## 위로 대체되어서 버려질 코드.
def subject_homework_check(request, subject_id):
    '''homework_check_spreadsheet 에서 약간 변형함.'''
    subject = get_object_or_404(models.Subject, id=subject_id)
    context = {}
    # 관련자만 접근하게끔.
    school = subject.school
    student = check.Student(usser=request.user, school=school).in_school_and_none()
    teacher = check.Teacher(usser=request.user, school=school).in_school_and_none()
    if teacher:
        student_list = []
        classrooms = subject.classroom_set.all()
        # 연결된 homeroom의 학생을 가져온다.
        for classroom in classrooms:
            homeroom_students = models.Student.objects.filter(homeroom=classroom.homeroom)
            for student in homeroom_students:
                student_list.append(student)

        student_list = list(student_list)
        homework_list = models.Homework.objects.filter(subject_object=subject)
        info_dic = {'student': student_list}
        for homework in homework_list:
            info_dic[homework.subject] = []  # 과제명으로 사전key, 리스트 만들기.
            for student in student_list:
                try:  # 동료평가 등 특수설문에서 에러.(과제 부여가 안된 경우에도)
                    submit = models.HomeworkSubmit.objects.get(base_homework=homework, to_user=student.admin)
                    if submit.check:
                        info_dic[homework.subject].append("제출")
                    elif submit.read:
                        info_dic[homework.subject].append("읽음")
                    else:
                        info_dic[homework.subject].append("미열람")
                except:
                    info_dic[homework.subject].append("특수상황")
        print(info_dic)
        df = pd.DataFrame(info_dic)
        df_dict = df.to_dict(orient='records')
        # print(df)
    elif student:  # 학생인 경우.
        homework_list = models.Homework.objects.filter(subject_object=subject)
        info_dic = {'student': student}
        for homework in homework_list:
            info_dic[homework.subject] = []  # 과제명으로 사전key, 리스트 만들기.
            try:
                submit = models.HomeworkSubmit.objects.get(base_homework=homework, to_user=student.admin)
                if submit.check:
                    info_dic[homework.subject].append("제출")
                elif submit.read:
                    info_dic[homework.subject].append("읽음")
            except:  # 동료평가 등 특수설문에서 에러.(과제 부여가 안된 경우에도)
                info_dic[homework.subject].append("특수상황")
        df = pd.DataFrame(info_dic)
        df_dict = df.to_dict(orient='records')

    context['data_list'] = df_dict
    return render(request, 'school_report/classroom/homework/check_spreadsheet.html', context)
