from django.shortcuts import render, get_object_or_404, redirect, resolve_url, HttpResponse
from django.http import HttpResponseBadRequest  # 파일 처리 후 요청용.

from .. import models  # 모델 호출.
from custom_account.models import Notification
from ..forms import ClassroomForm, HomeworkForm
from django.contrib import messages
from custom_account.decorator import custom_login_required as login_required
from . import check
import json
import pandas as pd  # 통계용
import math
from datetime import datetime
import openpyxl

@login_required()
def create(request, homework_box_id):
    '''room 모델 하위에 과제 배치.'''
    context = {}
    if request.method == 'POST':  # 포스트로 요청이 들어온다면... 글을 올리는 기능.
        homework_box = get_object_or_404(models.HomeworkBox, pk=homework_box_id)
        create_base(request, homework_box)
        return homework_box.redirect_to_upper()
    else:  # 포스트 요청이 아니라면.. form으로 넘겨 내용을 작성하게 한다.
        form = HomeworkForm()
    context['form'] = form  # 폼에서 오류가 있으면 오류의 내용을 담아 create.html로 넘긴다.
    return render(request, 'school_report/classroom/homework/create.html', context)
def create_base(request, homework_box):
    '''교과교실에서 작성. .'''  # 과제 제작에 대한 것만 두자.
    # 프로필 모델을 가져오게끔 구성하자. models.Profile.object.filter(admin=request.user, ) # 학교정보와 같이 있으면 괜찮을 듯한데. box에 학교정보가 같이 있게...?
    school = homework_box.get_school_model()
    profile = models.Profile.objects.filter(admin=request.user, school=school).first()  # 나중에 get으로 바꾸자. 프로필은 인당 1개만 만들게 하고.
    form = HomeworkForm(request.POST)  # 폼을 불러와 내용입력을 받는다.
    if form.is_valid():  # 문제가 없으면 다음으로 진행.
        homework = form.save(commit=False)  # commit=False는 저장을 잠시 미루기 위함.(입력받는 값이 아닌, view에서 다른 값을 지정하기 위해)
        homework.author_profile = profile  # 작성자 프로파일 지정.
        homework.homework_box = homework_box  # 게시판 지정.
        homework.save()
        ### 자동 과제 분배.
        profiles = homework_box.get_profiles()
        for to_profile in profiles:
            individual, created = models.HomeworkSubmit.objects.get_or_create(to_profile=to_profile,
                                                                          base_homework=homework)
@login_required()
def modify(request, posting_id):
    homework = get_object_or_404(models.Homework, pk=posting_id)
    author = homework.author_profile.admin  # 유저모델로 비교.
    if request.user != author:
        messages.error(request, '수정권한이 없습니다')
        return redirect('school_report:homework_detail', posting_id=homework.id)
    if request.method == "POST":
        is_secret = homework.is_secret  # 비밀설문을 다시 공개로 바꿀 수 없게.
        form = HomeworkForm(request.POST, instance=homework)  # 받은 내용을 객체에 담는다. instance에 제대로 된 걸 넣지 않으면 새로운 인스턴스를 만든다.
        if form.is_valid():
            homework = form.save(commit=False)  # commit=False는 저장을 잠시 미루기 위함.(입력받는 값이 아닌, view에서 다른 값을 지정하기 위해)
            if is_secret:
                homework.is_secret = is_secret
            homework.save()
            # 개별 확인을 위한 개별과제 체크 해제.(제출상태 취소)
            submit_list = models.HomeworkSubmit.objects.filter(base_homework=homework)
            for submit in submit_list:
                submit.check = False
                submit.save()
            return redirect('school_report:homework_detail', posting_id=homework.id)
    else:  # GET으로 요청된 경우.
        form = HomeworkForm(instance=homework)  # 해당 모델의 내용을 가져온다!
        # 태그를 문자열화 하여 form과 함께 담는다.
    context = {'form': form}
    messages.error(request, '수정하면 기존 확인한 학생들의 체크는 "읽지않음"으로 갱신됩니다.')
    return render(request, 'school_report/classroom/homework/create.html', context)
@login_required()
def detail(request, posting_id):
    '''과제 상세페이지와 과제제출 기능.'''
    context = {}
    homework = get_object_or_404(models.Homework, pk=posting_id)
    context['posting'] = homework

    # 주어진 과제 보여지기. 아마 과거의 흔적인듯.
    # individual_announcement = []  # 주어진 과제를 담을 공간.
    # sumbits = models.HomeworkSubmit.objects.filter(to_user=request.user, base_homework=homework)
    # for submit in sumbits:
    #     submit.read = True
    #     submit.save()
    #     individual_announcement.append(submit)
    # context['individual_announcement'] = individual_announcement

    # 학생과 교사 가르기.
    school = homework.homework_box.get_school_model()
    profile = models.Profile.objects.filter(admin=request.user, school=school).first()  # 나중에 정돈이 되면 filter가 아니라 get으로 바꾸자. 25년엔 괜찮을듯.
    #student = check.Check_student(request, school).in_school_and_none()
    #teacher = check.Check_teacher(request, school).in_school_and_none()
    # 교사라면 모든 설문관련 정보를 볼 수 있다.
    if profile.position == 'teacher':
        submit_list = models.HomeworkSubmit.objects.filter(base_homework=homework)
        context['submit_list'] = submit_list

    context['survey'] = homework.homeworkquestion_set.exists()  # 설문객체 여부.

    # 개인 과제에 대해
    private_submits = models.HomeworkSubmit.objects.filter(base_homework=homework, to_profile=profile)
    context['private_submits'] = private_submits  # 열람자의 정보 담기.

    # 동료평가에서의 기능.
    if homework.is_special == 'peerReview':  # 동료평가의 경우, 지금 부여한 평균 보여주기.
        # 평가 관련 데이터.
        try:  # 평가한 게 없으면 df가 None이 됨.
            question = models.HomeworkQuestion.objects.get(homework=homework, ordering=1)  # 동료평가의 첫번째 질문.
            answers = models.HomeworkAnswer.objects.filter(respondent=request.user, question=question)  # 내가 부여한 것.
            df = pd.DataFrame.from_records(answers.values('contents'))
            df['contents'] = pd.to_numeric(df['contents'], errors='coerce')
            score_mean = df['contents'].mean()
            variance = df['contents'].organization()
            context['score_mean'] = score_mean
            context['variance'] = variance
        except:
            pass
        # score_sum = 0
        # for answer in answers:
        #     score_sum += float(answer.contents)
        #     count += 1
        # try:  # 아무 평가도 안한 상태에선 count0이라 에러 발생.
        #     score_mean = score_sum/count
        #     context['score_mean'] = score_mean
        # except:
        #     pass
    return render(request, 'school_report/classroom/homework/detail.html', context)
@login_required()
def delete(request, posting_id):
    homework = get_object_or_404(models.Homework, pk=posting_id)
    if request.user != homework.author_profile.admin:
        messages.error(request, '삭제권한이 없습니다. 꼼수쓰지 마라;')
        return redirect(request.META.get('HTTP_REFERER', None))  # 이전 화면으로 되돌아가기.
    homework.delete()
    messages.success(request, '삭제 성공~!')
    homework_box = homework.homework_box
    return homework_box.redirect_to_upper()  # box를 소유한 상위객체로 리다이렉트.
def distribution(homework, user):  # [profile로 바꾸자.]
    # 개별 확인을 위한 개별과제 생성.
    # 개별 부여할 사람을 탬플릿에서 받는 것도 괜찮을듯...? 흠... []
    userlist = request.POST.getlist('user')
    if userlist:  # 특정 방법으로 유저리스트가 전달된 경우.
        pass  # 나중에 짜자. 들어오는 방법에 대한 논의가 필요하겠네.
    else:  # 유저리스트가 없으면 class에서 작성한 것으로 판단하고,
        student_list = models.Student.objects.filter(homeroom=classroom.homeroom)  # 정상 작동하면 추후 지우자.
        for student in student_list:
            homework_distribution(homework, student.admin)  # 유저모델을 대응시킨다.
            try:
                Notification.objects.create(to_user=student.admin, official=True, classification=12, type=2,
                                            from_user=request.user, message=classroom,
                                            url=resolve_url("school_report:homework_detail", homework.id))
            except Exception as e:
                print(e)  # 학생 중 등록이 안한 학생은 to_user에서 에러가 난다.
        homework_distribution(homework, request.user)  # 작성자도 대응시킨다.
    '''과제 분배.'''  # 과제 지정하기..
    individual, created = models.HomeworkSubmit.objects.get_or_create(to_user=user,
                                                                      base_homework=homework)