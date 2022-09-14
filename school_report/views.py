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

    return render(request, 'school_report/main.html', context)



