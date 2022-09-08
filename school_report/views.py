from django.contrib.auth.decorators import login_required #로그인이 있어야 가능함
from django.shortcuts import render, get_object_or_404, redirect, resolve_url, HttpResponse
import json
from django.utils import timezone  # 시간입력을 위해.
from _datetime import datetime,timedelta  # 시간데이터 활용을 위해
from django.contrib import messages  # 넌필드 오류를 반환하기 위한 것

from django.db.models import Q, Count  # 검색을 위함. filter에서 OR조건으로 조회하기 위한 함수.(장고제공)

from custom_account.models import Notification
from custom_account.views import notification_add
from . import models  # 모델 호출.
@login_required()
def main(request):
    context = {}  # 정보를 담을 사전.
    # 프로필 가져오기.
    teacher = request.user.teacher
    context['teacher'] = teacher
    student = request.user.student
    context['student'] = student
    # 교사 프로필이 등록되어있지 않으면 에러 반환.
    try:
        if teacher.name:
            # 주 소유객체 리스트에 담기.
            maintain_homeroom_list = models.Homeroom.objects.filter(master=teacher)
            context['maintain_homeroom_list'] = maintain_homeroom_list
            maintain_classroom_list = models.Classroom.objects.filter(master=teacher)
            context['maintain_classroom_list'] = maintain_classroom_list
            # 공동 관리자 객체 리스트에 담기.
            context['joint_school'] = teacher.school
            context['joint_homeroom_list'] = teacher.homeroom_have.all()
            context['joint_classroom_list'] = teacher.classroom_have.all()
    except:
        pass
        #messages.info(request, '아직 프로필이 등록되지 않았습니다.')
    # 학생 프로필이 있다면 가져오기.
    try:
        if student.name:
            # 공동 관리자 객체 리스트에 담기.
            context['joint_homeroom'] = student.homeroom
            context['joint_classroom_list'] = student.homeroom.classroom_set.all()

    except:
        pass
    return render(request, 'school_report/main.html', context)



