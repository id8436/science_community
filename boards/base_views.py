from django.contrib.auth.decorators import login_required #로그인이 있어야 가능함

from django.shortcuts import render, get_object_or_404, redirect, resolve_url, HttpResponse
import json
from django.utils import timezone  # 시간입력을 위해.
from _datetime import datetime,timedelta  # 시간데이터 활용을 위해
from django.contrib import messages  # 넌필드 오류를 반환하기 위한 것

from .forms import PostingForm, AnswerForm, CommentForm, BoardForm
from .models import * #모델을 불러온다.
from django.db.models import Q, Count  # 검색을 위함. filter에서 OR조건으로 조회하기 위한 함수.(장고제공)

from custom_account.models import Notification

def board_list_hidden(request, category_id):
    board_list = Board.objects.filter(category=category_id)  # 카테고리에 따라 분류 받아오기.

    # 정렬 기능.
    ordering = request.GET.get('ordering', 'recent')  # 정렬기준
    if ordering == 'recent':  # 시간순 정렬
        board_list = board_list.order_by('-id')  # 생성순서의 반대.

    #-----검색기능
    keyword = request.GET.get('keyword', '')  # 검색어.
    if keyword != '':  # 검색어가 있다면
        result = []  # 검색결과를 담기 위한 리스트를 만든다.
        keywords = keyword.split(' ')  # 공백이 있는 경우 나눈다.
        for kw in keywords:  # 띄어쓰기로 검색을 하는 경우가 많으니까, 다 찾아줘야지.
            result += board_list.filter(  # 검색해서 검색결과에 더한다.
            Q(board_name__name__icontains=kw) |  # 제목검색
            Q(text_1__content__icontains=kw) |  # 텍스트 포린키 안의 content에서 내용검색
            Q(author__nickname__icontains=kw) |  # 모델의 상위인 user모델의 nickname에서 검색.
            Q(text_2__content__icontains=kw)
            ).distinct()  # 중복된 내용이 있으면 제거하는 함수.
        board_list = result  # 모은 결과를 리스트에 담는다.

    ################## 페이징처리#########
    from django.core.paginator import Paginator  # 장고엔 다 있다!!
    page = request.GET.get('board_page', '1')  #어떤 페이지를 보고 있을지 전달받는다. 추후 탬플릿에서 구현.
    paginator = Paginator(board_list, 10)  # 페이지당 10개씩 보여주겠다는 의미.
    board_list = paginator.get_page(page)  # 페이징 된 리스트.

    current_page_num=int(page)  # 현재 페이지는 몇인가?
    first_page=1  # 첫 페이지 넘버
    last_page = int(paginator.num_pages)  # 마지막페이지는 몇인가?
    left_show =current_page_num - 5  # 왼쪽으로 5개까지 나타낸다.
    right_show =current_page_num + 5  # 우측으로 5개까지 나타낸다.

    if current_page_num < 6:
        left_show=first_page
    if current_page_num+5 > last_page:
        right_show = last_page

    page_list = range(left_show, right_show+1)  #보여줄 페이지의 범위.


    context = {'board_list': board_list,#기존의 리스트 대신 페이지객체를 보낸다.
               'board_page_list':page_list,  #보여줄 페이지 리스트
               'board_page': page,  # 현재 페이지
               'keyword': keyword,  # 검색어는 다시 돌려준다.
               }
    return context
def posting_list_hidden(request, board_id):
    board = get_object_or_404(Board, pk=board_id)
    posting_list = board.posting_set.all()

    # 정렬 기능.
    ordering = request.GET.get('ordering', 'recent')  # 정렬기준
    if ordering == 'recent':  # 시간순 정렬
        posting_list = posting_list.order_by('-id')  # 생성순서의 반대.

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
    page = request.GET.get('posting_page', '1')  #어떤 페이지를 보고 있을지 전달받는다. 추후 탬플릿에서 구현.
    paginator = Paginator(posting_list, 10)  # 페이지당 10개씩 보여주겠다는 의미.
    posting_list = paginator.get_page(page)  # 페이징 된 리스트.

    current_page_num=int(page)  #현재 페이지는 몇인가?
    first_page=1 # 첫 페이지 넘버
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
               'posting_page_list':page_list,  #보여줄 페이지 리스트
               'posting_page': page,  # 현재 페이지
               'keyword': keyword,  # 검색어는 다시 돌려준다.
               }
    return context

def board_list(request, category_id, base_dir):
    context = board_list_hidden(request, category_id)
    context = {**context, **base_dir}
    return render(request, base_dir['base_template']+'board_list.html', context)
def board_detail(request, board_id, base_dir):
    board = get_object_or_404(Board, pk=board_id)
    context_posting = posting_list_hidden(request, board_id)  # 하위 포스팅 가져오기.
    category_id = board.category.id
    # ----- list함수와 같은 부분 -----
    context_board = board_list_hidden(request, category_id)
    context_board['board'] = board
    context = {**context_posting, **context_board, **base_dir}
    return render(request, base_dir['base_template']+'board_detail.html', context)
def board_name_adding(request, board):
    instr = request.POST.get('board_name')
    outstr = ''
    for i in range(0, len(instr)):  # 문자열 내 공백 없애기.
        if instr[i] != ' ':
            outstr += instr[i]
    board_name_, created = Board_name.objects.get_or_create(name=outstr)  # created엔 새로 만들어졌는지 여부가 True로 나오고, tag_엔 그 태그가 담긴다.
    board.board_name = board_name_
    board.save()
@login_required()
def board_create(request, category_id, base_dir):
    if request.method == 'POST':  # 포스트로 요청이 들어온다면... 글을 올리는 기능.
        form = BoardForm(request.POST)  # 폼을 불러와 내용입력을 받는다.
        if form.is_valid():  # 문제가 없으면 다음으로 진행.
            category = get_object_or_404(Board_category, pk=category_id)
            board = form.save(commit=False)  # commit=False는 저장을 잠시 미루기 위함.(입력받는 값이 아닌, view에서 다른 값을 지정하기 위해)
            board.author = request.user  # 추가한 속성 author 적용
            board.category = category
            board.save()
            board_name_adding(request, board)  # 태그 추가 함수.
            return redirect(base_dir['base_url']+'board_list')  # 작성이 끝나면 목록화면으로 보낸다.
    else:  # 포스트 요청이 아니라면.. form으로 넘겨 내용을 작성하게 한다.
        form = BoardForm()
    context = {'form': form}  # 폼에서 오류가 있으면 오류의 내용을 담아 create.html로 넘긴다.
    # 없으면 그냥 form 작성을 위한 객체를 넘긴다.
    context = {**context, **base_dir}
    return render(request, base_dir['base_template']+'board_create.html', context)

def tag_adding_on_posting(request, posting):
    replace_text = [';', '#']  # 치환할 문자열
    tags_str = request.POST.get('tag')
    for text in replace_text:
        tags_str = tags_str.replace(text, ',')  # 각종 문자들을 ,로 바꾼다.
    tags = tags_str.split(',')
    for tag in tags:
        if not tag:
            continue
        else:
            tag = tag.strip()  # 문자열 양쪽에 빈칸이 있을 때 이를 제거한다.
            tag_, created = Tag.objects.get_or_create(name=tag)  # created엔 새로 만들어졌는지 여부가 True로 나오고, tag_엔 그 태그가 담긴다.
            posting.tag.add(tag_)  # 요건 특이하게 save()가 필요 없다.

def posting_detail_on_board(request, posting_id, base_dir):
    posting = get_object_or_404(Posting, pk=posting_id)
    category_id = posting.board.category.id
    # ----- board_detail 함수와 같은 부분 -----
    board = posting.board
    context_posting = posting_list_hidden(request, board.id)
    context_board = board_list_hidden(request, category_id)
    context_board['board'] = board
    context = {**context_posting, **context_board}
    # 포스팅 정보 추가.
    context['posting'] = posting
    context = {**context, **base_dir}
    return render(request, base_dir['base_template']+'posting_detail.html', context)
@login_required()
def posting_create_on_board(request, board_id, base_dir):
    if request.method == 'POST':  # 포스트로 요청이 들어온다면... 글을 올리는 기능.
        form = PostingForm(request.POST)  # 폼을 불러와 내용입력을 받는다.
        if form.is_valid():  # 문제가 없으면 다음으로 진행.
            board = get_object_or_404(Board, pk=board_id)
            posting = form.save(commit=False)  # commit=False는 저장을 잠시 미루기 위함.(입력받는 값이 아닌, view에서 다른 값을 지정하기 위해)
            posting.author = request.user  # 추가한 속성 author 적용
            #posting.create_date = timezone.now()  # 현재 작성일시 자동저장. 모델에서 처리하면 없어도 될듯.
            posting.board = board  # 게시판 지정.
            posting.save()
            tag_adding_on_posting(request, posting)  # 태그 추가 함수.
            return posting_detail_on_board(request, posting.id, base_dir)  # 작성이 끝나면 작성한 글로 보낸다.
    else:  # 포스트 요청이 아니라면.. form으로 넘겨 내용을 작성하게 한다.
        form = PostingForm()
    context = {'form': form}  # 폼에서 오류가 있으면 오류의 내용을 담아 create.html로 넘긴다.
    context = {**context, **base_dir}
    return render(request, base_dir['base_template']+'posting_create.html', context)
@login_required()
def posting_modify_on_board(request, posting_id, base_dir):
    posting = get_object_or_404(Posting, pk=posting_id)
    if request.user != posting.author:
        messages.error(request, '수정권한이 없습니다')
        return redirect('boards:detail', posting_id=posting.id)
    if request.method == "POST":
        form = PostingForm(request.POST, instance=posting)  # 받은 내용을 객체에 담는다. instance에 제대로 된 걸 넣지 않으면 새로운 인스턴스를 만든다.
        if form.is_valid():
            posting = form.save(commit=False)
            posting.author = request.user
            #posting.modify_date = timezone.now()  # 수정일시 자동 저장, 모델에서 처리하면 없어도 되지 않나?
            posting.tag.clear()  # 수정화면에서 문자열로 다루기 위해 지웠다가 다시 등록하는 방법을 사용한다.
            tag_adding_on_posting(request, posting)  # 태그 추가 함수.
            posting.save()
            return posting_detail_on_board(request, posting.id, base_dir)
    else:  # GET으로 요청된 경우.
        form = PostingForm(instance=posting)  # 해당 모델의 내용을 가져온다!
        # 태그를 문자열화 하여 form과 함께 담는다.
        tags = posting.tag.all()
        tags_str = ''
        for tag in tags:
            tags_str += tag.name + ', '
    context = {'form': form,
               'tags_str': tags_str}
    context = {**context, **base_dir}
    return render(request, base_dir['base_template']+'posting_create.html', context)