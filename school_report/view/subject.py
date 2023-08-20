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

def homework_distribution(homework, user):
    '''과제 분배.'''
    individual, created = models.HomeworkSubmit.objects.get_or_create(to_user=user,
                                                                      base_homework=homework)
@login_required()
def subject_homework_create(request, subject_id):
    subject = get_object_or_404(models.Subject, pk=subject_id)
    '''교과교실에서 작성. 원본은 classroom에서 작성된 것..'''
    #classroom = get_object_or_404(models.Subject, pk=subject_id)
    context = {}
    if request.method == 'POST':  # 포스트로 요청이 들어온다면... 글을 올리는 기능.
        form = HomeworkForm(request.POST)  # 폼을 불러와 내용입력을 받는다.
        if form.is_valid():  # 문제가 없으면 다음으로 진행.
            homework = form.save(commit=False)  # commit=False는 저장을 잠시 미루기 위함.(입력받는 값이 아닌, view에서 다른 값을 지정하기 위해)
            homework.author = request.user  # 추가한 속성 author 적용
            homework.subject_object = subject  # 게시판 지정.
            homework.save()
            # 개별 확인을 위한 개별과제 생성.
            userlist = request.POST.getlist('user')
            if userlist:  # 특정 방법으로 유저리스트가 전달된 경우.
                pass  # 나중에 짜자. 들어오는 방법에 대한 논의가 필요하겠네.
            else:  # 유저리스트가 없으면 class, 교과에서 작성한 것으로 판단하고,
                student_id_list = []
                classrooms = subject.classroom_set.all()
                # 연결된 homeroom의 학생을 가져온다.
                for classroom in classrooms:
                    homeroom_students = models.Student.objects.filter(homeroom=classroom.homeroom)
                    for student in homeroom_students:
                        student_id_list.append(student.id)
                # student_list = before_query_sets[0]  # 쿼리셋 집단으로 만들기.
                # try:
                #     for query in before_query_sets[1:]:  # 다음 쿼리셋부터 합치기.
                #         student_list = student_list.union(query)
                # except:
                #     pass  # 반이 1개인 경우엔 에러남.
                # print(before_query_sets)
                print(student_id_list)
                student_list = models.Student.objects.filter(id__in=student_id_list)
                print(student_list)
                ordered_list = student_list.order_by('student_code')
                print(ordered_list)
                for student in ordered_list:
                    homework_distribution(homework, student.admin)  # 유저모델을 대응시킨다.
                    try:
                        Notification.objects.create(to_user=student.admin, official=True, classification=12, type=2,
                                                    from_user=request.user, message=classroom,
                                                    url=resolve_url("school_report:homework_detail", homework.id))
                    except Exception as e:
                        print(e)  # 학생 중 등록이 안한 학생은 to_user에서 에러가 난다.
                homework_distribution(homework, request.user)  # 작성자도 대응시킨다.

            return redirect('school_report:subject_main', subject.id)  # 작성이 끝나면 작성한 글로 보낸다.
    else:  # 포스트 요청이 아니라면.. form으로 넘겨 내용을 작성하게 한다.
        form = HomeworkForm()
    context['form'] = form  # 폼에서 오류가 있으면 오류의 내용을 담아 create.html로 넘긴다.
    return render(request, 'school_report/classroom/homework/create.html', context)

def subject_homework_detail(request, posting_id):
    '''classroom 안의 함수가 원본..'''
    context = {}
    posting = get_object_or_404(models.Homework, pk=posting_id)
    context['posting'] = posting
    subject_object = posting.subject_object

    if request.method == 'POST':  # 과제를 제출한 경우.
        homework_submit = get_object_or_404(models.HomeworkSubmit, base_homework=posting, to_user=request.user)
        content = request.POST.get('content')
        homework_submit.content = content
        homework_submit.check = True  # 제출표시
        homework_submit.save()
        return redirect('school_report:homework_detail', posting.id)  # 작성이 끝나면 작성한 글로 보낸다.

    individual_announcement = []  # 주어진 과제를 담을 공간.
    try:  # 과제 하위가 하나일 경우.
        # 새로운 학생이 훗날 추가되었다면 접속했을 때 개별과제 하나가 늘게끔.
        individual_announcement, created = models.HomeworkSubmit.objects.get_or_create(to_user=request.user,
                                                                                       base_homework=posting)
        individual_announcement.read = True
        individual_announcement.save()
    except:
        sumbits = models.HomeworkSubmit.objects.filter(to_user=request.user, base_homework=posting)
        for submit in sumbits:
            submit.read = True
            submit.save()
            individual_announcement.append(submit)
    context['individual_announcement'] = individual_announcement
    # 학생과 교사 가르기.
    student = check.Check_student(request, subject_object.school).in_school_and_none()
    teacher = check.Check_teacher(request, subject_object.school).check_in_school()
    if teacher:
        school = subject_object.school  # 학생 객체를 찾아 배정하기 위해.
        submit_list = models.HomeworkSubmit.objects.filter(base_homework=posting)
        for submit in submit_list:
            try:
                student_check = models.Student.objects.get(admin=submit.to_user, school=school)
                submit.who = student_check  # 설문자 정보를 담기.
            except:
                teacher_check = models.Teacher.objects.get(admin=submit.to_user, school=school)
                submit.who = teacher_check
    context['survey'] = posting.homeworkquestion_set.exists()  # 설문객체 여부.

    private_submit = models.HomeworkSubmit.objects.get(base_homework=posting, to_user=request.user)
    if student != None:
        private_submit.who = student
    elif teacher != None:
        private_submit.who = teacher
    context['private_submit'] = private_submit  # 열람자의 정보 담기.

    context['submit_list'] = submit_list  # 여기 수정해야 함. 일반인들이 본인의 설문을 볼 수 있게!
    return render(request, 'school_report/classroom/homework/detail.html', context)