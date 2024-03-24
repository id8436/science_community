from django.shortcuts import render, get_object_or_404, redirect, resolve_url, HttpResponse
from django.http import HttpResponseBadRequest  # 파일 처리 후 요청용.

from .. import models  # 모델 호출.
from custom_account.models import Notification
from ..forms import ClassroomForm, HomeworkForm, AnnouncementForm
from django.contrib import messages
from custom_account.decorator import custom_login_required as login_required
from . import check
import json
import pandas as pd  # 통계용
import math
from datetime import datetime
import openpyxl
## 기본적으로 homeworkbox와 유사.(필요에 따라 조금 바꿈;)
@login_required()
def create(request, announce_box_id):
    '''room 모델 하위에 과제 배치.'''
    context = {}
    if request.method == 'POST':  # 포스트로 요청이 들어온다면... 글을 올리는 기능.
        announce_box = get_object_or_404(models.AnnounceBox, pk=announce_box_id)
        create_base(request, announce_box)
        return announce_box.redirect_to_upper()
    else:  # 포스트 요청이 아니라면.. form으로 넘겨 내용을 작성하게 한다.
        form = HomeworkForm()
    context['form'] = form  # 폼에서 오류가 있으면 오류의 내용을 담아 create.html로 넘긴다.
    return render(request, 'school_report/classroom/homework/create.html', context)
def create_base(request, announce_box):
    '''교과교실에서 작성. .'''  # 과제 제작에 대한 것만 두자.
    # 프로필 모델을 가져오게끔 구성하자. models.Profile.object.filter(admin=request.user, ) # 학교정보와 같이 있으면 괜찮을 듯한데. box에 학교정보가 같이 있게...?
    school = announce_box.get_school_model()
    profile = models.Profile.objects.filter(admin=request.user, school=school).first()  # 나중에 get으로 바꾸자. 프로필은 인당 1개만 만들게 하고.
    form = AnnouncementForm(request.POST)  # 폼을 불러와 내용입력을 받는다.
    if form.is_valid():  # 문제가 없으면 다음으로 진행.
        announcement = form.save(commit=False)  # commit=False는 저장을 잠시 미루기 위함.(입력받는 값이 아닌, view에서 다른 값을 지정하기 위해)
        announcement.author_profile = profile  # 작성자 프로파일 지정.
        announcement.announce_box = announce_box  # 게시판 지정.
        announcement.save()
        ### 자동 과제 분배.
        profiles = announce_box.get_profiles()
        for to_profile in profiles:
            individual, created = models.AnnoIndividual.objects.get_or_create(to_profile=to_profile,
                                                                          base_announcement=announcement)

@login_required()
def modify(request, posting_id):
    announcement = get_object_or_404(models.Announcement, pk=posting_id)
    author = announcement.author_profile.admin  # 유저모델로 비교.
    print(author)
    if request.user != author:
        messages.error(request, '수정권한이 없습니다')
        return redirect('school_report:announcement_detail', posting_id=announcement.id)
    if request.method == "POST":
        form = AnnouncementForm(request.POST, instance=announcement)  # 받은 내용을 객체에 담는다. instance에 제대로 된 걸 넣지 않으면 새로운 인스턴스를 만든다.
        if form.is_valid():
            announcement = form.save(commit=False)  # commit=False는 저장을 잠시 미루기 위함.(입력받는 값이 아닌, view에서 다른 값을 지정하기 위해)
            announcement.save()
            # 개별 확인을 위한 개별과제 체크 해제.(제출상태 취소)
            # submit_list = models.HomeworkSubmit.objects.filter(base_homework=announcement)
            # for submit in submit_list:
            #     submit.check = False
            #     submit.save()
            return redirect('school_report:announcement_detail', posting_id=announcement.id)
    else:  # GET으로 요청된 경우.
        form = AnnouncementForm(instance=announcement)  # 해당 모델의 내용을 가져온다!
        # 태그를 문자열화 하여 form과 함께 담는다.
    context = {'form': form}
    messages.error(request, '수정하면 기존 확인한 학생들의 체크는 "읽지않음"으로 갱신됩니다.')
    return render(request, 'school_report/classroom/homework/create.html', context)
@login_required()
def detail(request, posting_id):
    '''과제 상세페이지와 과제제출 기능.'''
    context = {}
    announcement = get_object_or_404(models.Announcement, pk=posting_id)
    context['posting'] = announcement

    # 학생과 교사 가르기.
    school = announcement.announce_box.get_school_model()
    profile = models.Profile.objects.filter(admin=request.user, school=school).first()  # 나중에 정돈이 되면 filter가 아니라 get으로 바꾸자. 25년엔 괜찮을듯.
    # 교사라면 모든 설문관련 정보를 볼 수 있다.
    if profile.position == 'teacher':
        annoIndividual_list = models.AnnoIndividual.objects.filter(base_announcement=announcement)
        context['annoIndividual_list'] = annoIndividual_list

    # 개인 과제에 대해
    individual_announcement = models.AnnoIndividual.objects.filter(base_announcement=announcement, to_profile=profile)
    context['individual_announcement'] = individual_announcement  # 열람자의 정보 담기.

    return render(request, 'school_report/homeroom/announcement/detail.html', context)
@login_required()
def delete(request, posting_id):
    announcement = get_object_or_404(models.Announcement, pk=posting_id)
    if request.user != announcement.author_profile.admin:
        messages.error(request, '삭제권한이 없습니다. 꼼수쓰지 마라;')
        return redirect('school_report:announcement_detail', posting_id=announcement.id)
    announcement.delete()
    messages.success(request, '삭제 성공~!')
    announce_box = announcement.announce_box
    return announce_box.redirect_to_upper()
