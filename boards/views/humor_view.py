from django.contrib.auth.decorators import login_required #로그인이 있어야 가능함

from django.shortcuts import render, get_object_or_404, redirect, resolve_url, HttpResponse
import json
from django.utils import timezone  # 시간입력을 위해.
from _datetime import datetime,timedelta  # 시간데이터 활용을 위해
from django.contrib import messages  # 넌필드 오류를 반환하기 위한 것

from ..forms import PostingForm, AnswerForm, CommentForm
from ..models import * #모델을 불러온다.
from django.db.models import Q, Count  # 검색을 위함. filter에서 OR조건으로 조회하기 위한 함수.(장고제공)

def list_hidden(request, board_id):
    #posting_list = Posting.objects.all()  # 일단 객체 목록을 받아온다.(전부 다~)
    posting_list = Posting.objects.filter(board=board_id)

    # 정렬 기능.
    ordering = request.GET.get('ordering', 'recent')  # 정렬기준
    if ordering == 'recent':  # 시간순 정렬
        posting_list = posting_list.order_by('-create_date')
    elif ordering == 'popular':  # 댓글순 정렬
        posting_list = posting_list.annotate(num_answer=Count('answer')).order_by('-num_answer', '-create_date')
    elif ordering == 'recommend':  # 추천순 정렬
        posting_list = posting_list.annotate(num_voter=Count('favorite')).order_by('-num_voter', '-create_date')
        print(posting_list)
    elif ordering == 'student_code':  # 학번순 정렬
        posting_list = posting_list.order_by('profile__student_code')
    else:  # recent
        pass

    # 날짜 필터
    start = None
    end = None
    if request.GET.get('start'):
        time = request.GET.get('start').split('-')
        start = request.GET.get('start')  # 받은 걸 되돌려서 탬플릿에 보여주기 위한 변수
        date = datetime(int(time[0]), int(time[1]), int(time[2]))
        date = datetime.date(date)  # 인수에 datetime이 들어가야 해서 굳이 이렇게 씀;;
        posting_list= posting_list.filter(create_date__gte= date)  # greater than equal
    if request.GET.get('end'):
        time = request.GET.get('end').split('-')
        end = request.GET.get('end')
        date = datetime(int(time[0]), int(time[1]), int(time[2])) + timedelta(days=1)  # 시간이 00:00:00으로 잡힌다.
        date = datetime.date(date)
        posting_list = posting_list.filter(create_date__lte=date)

    #-----검색기능
    keyword = request.GET.get('keyword', '')  # 검색어.
    if keyword != '':  # 검색어가 있다면
        result = []  # 검색결과를 담기 위한 리스트를 만든다.
        keywords = keyword.split(' ')  # 공백이 있는 경우 나눈다.
        for kw in keywords:  # 띄어쓰기로 검색을 하는 경우가 많으니까, 다 찾아줘야지.
            result += posting_list.filter(  # 검색해서 검색결과에 더한다.
            Q(subject__icontains=kw) |  # 제목검색
            Q(content__icontains=kw) |  # 내용검색
            Q(author__nickname__icontains=kw) |  # 모델의 상위인 user모델의 nickname에서 검색.
            Q(answer__author__nickname__icontains=kw)  # 하위모델인 answer모델의 참조인 user모델의 속성에서 검색.
            ).distinct()  # 중복된 내용이 있으면 제거하는 함수.
        posting_list = result  # 모은 결과를 리스트에 담는다.

    ################## 페이징처리#########
    from django.core.paginator import Paginator  # 장고엔 다 있다!!
    page = request.GET.get('page', '1')  #어떤 페이지를 보고 있을지 전달받는다. 추후 탬플릿에서 구현.
    paginator = Paginator(posting_list, 10)  # 페이지당 10개씩 보여주겠다는 의미.
    posting_list = paginator.get_page(page)  # 페이징 된 리스트.

    current_page_num=int(page)  #현재 페이지는 몇인가?
    first_page=1#첫 페이지 넘버
    last_page = int(paginator.num_pages)  #마지막페이지는 몇인가?
    left_show =current_page_num - 5  #왼쪽으로 5개까지 나타낸다.
    right_show =current_page_num + 5  #우측으로 5개까지 나타낸다.

    if current_page_num < 6:
        left_show=first_page
    if current_page_num+5 > last_page:
        right_show = last_page

    page_list = range(left_show, right_show+1)  #보여줄 페이지의 범위.

    ####댓글 갯수 세기
    for posting in posting_list:
        posting.comment_sum = posting.answer_set.count()  # 객체의 새로운 속성을 정의하고 각 댓글의 갯수를 부여한다.
        for answer in posting.answer_set.all(): # posting 객체 하위의 answer로 돌려가며 대댓글 갯수를 추가한다.
            posting.comment_sum += answer.comment_set.count()

    context = {'posting_list': posting_list,#기존의 리스트 대신 페이지객체를 보낸다.
               'page_list':page_list,  #보여줄 페이지 리스트
               'page': page,  # 현재 페이지
               'keyword': keyword,  # 검색어는 다시 돌려준다.
               'ordering': ordering,  # 선택한 정렬순서는 다시 돌려준다.
               'start': start,  # 시작날짜
               'end': end,  # 끝날짜
               }
    return context

def list(request, board_id):
    context = list_hidden(request, board_id)
    return render(request, 'boards/humor_list.html', context)

def detail(request, posting_id):
    posting = get_object_or_404(Posting, pk=posting_id)
    board = posting.board
    #----- list함수와 같은 부분 -----
    context = list_hidden(request, board.id)  # 해당 보드에 해당하는 것만 담기 위해.
    context['posting'] = posting
    return render(request, 'boards/humor_detail.html', context)

def report_list(request, board_id):
    context = list_hidden(request, board_id)
    return render(request, 'boards/report_list.html', context)

def report_detail(request, posting_id):
    posting = get_object_or_404(Posting, pk=posting_id)
    board = posting.board
    #----- list함수와 같은 부분 -----
    context = list_hidden(request, board.id)  # 해당 보드에 해당하는 것만 담기 위해.
    context['posting'] = posting
    return render(request, 'boards/report_detail.html', context)
