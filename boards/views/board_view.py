from django.contrib.auth.decorators import login_required #로그인이 있어야 가능함

from django.shortcuts import render, get_object_or_404, redirect, resolve_url, HttpResponse
import json
from django.utils import timezone  # 시간입력을 위해.
from _datetime import datetime,timedelta  # 시간데이터 활용을 위해
from django.contrib import messages  # 넌필드 오류를 반환하기 위한 것

from ..models import Board, Board_name, Posting #모델을 불러온다
from ..forms import BoardForm
from django.db.models import Q, Count  # 검색을 위함. filter에서 OR조건으로 조회하기 위한 함수.(장고제공)

category_id = 2

from ..base_views import board_list_hidden


def list(request, category_id):
    context=board_list_hidden(request, category_id)
    return render(request, 'boards/board_list_show.html', context)


def detail(request, board_id):
    board = get_object_or_404(Board, pk=board_id)
    context = posting_list_hidden(request, board_id)
    category_id = board.category.id
    #----- list함수와 같은 부분 -----
    context_board = board_list_hidden(request, category_id)
    context['board'] = board
    context = {**context, **context_board}
    return render(request, 'boards/board_detail.html', context)




@login_required()
def create(request):
    if request.method == 'POST':  # 포스트로 요청이 들어온다면... 글을 올리는 기능.
        form = BoardForm(request.POST)  # 폼을 불러와 내용입력을 받는다.
        if form.is_valid():  # 문제가 없으면 다음으로 진행.
            board = form.save(commit=False)  # commit=False는 저장을 잠시 미루기 위함.(입력받는 값이 아닌, view에서 다른 값을 지정하기 위해)
            board.author = request.user  # 추가한 속성 author 적용
            board.save()
            board_name_adding(request, board)  # 태그 추가 함수.
            return redirect('boards:board_list')  # 작성이 끝나면 목록화면으로 보낸다.
    else:  # 포스트 요청이 아니라면.. form으로 넘겨 내용을 작성하게 한다.
        form = BoardForm()
    context = {'form': form}  # 폼에서 오류가 있으면 오류의 내용을 담아 create.html로 넘긴다.
    # 없으면 그냥 form 작성을 위한 객체를 넘긴다.
    return render(request, 'boards/board_create.html', context)


from ..forms import PostingForm
@login_required()
def school_posting_create(request, board_id):
    if request.method == 'POST':  # 포스트로 요청이 들어온다면... 글을 올리는 기능.
        form = PostingForm(request.POST)  # 폼을 불러와 내용입력을 받는다.
        if form.is_valid():  # 문제가 없으면 다음으로 진행.
            board = get_object_or_404(Board, pk=board_id)  # 넣을 보드를 찾는다.
            posting = form.save(commit=False)  # commit=False는 저장을 잠시 미루기 위함.(입력받는 값이 아닌, view에서 다른 값을 지정하기 위해)
            posting.author = request.user  # 추가한 속성 author 적용
            posting.create_date = timezone.now()  # 현재 작성일시 자동저장
            posting.board = board  # 보드 지정.
            posting.save()
            print('---------')
            return detail(request, board_id)  # 디테일로 처리를 넘긴다.
    else:  # 포스트 요청이 아니라면.. form으로 넘겨 내용을 작성하게 한다.
        form = PostingForm()
    context = {'form': form,}  # 폼에서 오류가 있으면 오류의 내용을 담아 create.html로 넘긴다.
    # 없으면 그냥 form 작성을 위한 객체를 넘긴다.
    return render(request, 'boards/school_posting_create.html', context)

def school_posting_detail(request, posting_id):
    posting = get_object_or_404(Posting, pk=posting_id)
    category_id = posting.board.category.id
    # ----- board_detail 함수와 같은 부분 -----
    board = posting.board
    context = posting_list_hidden(request, board.id)
    context_board = board_list_hidden(request, category_id)
    context['board'] = board
    context = {**context, **context_board}
    # 포스팅 정보 추가.
    context['posting'] = posting
    return render(request, 'boards/school_posting_detail.html', context)

def contest_list(request, category_id):
    context = board_list_hidden(request, category_id)
    return render(request, 'boards/contest_list.html', context)


