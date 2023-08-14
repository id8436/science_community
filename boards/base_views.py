from custom_account.decorator import custom_login_required as login_required

from django.shortcuts import render, get_object_or_404, redirect, resolve_url, HttpResponse
import json
from django.utils import timezone  # 시간입력을 위해.
from _datetime import datetime,timedelta  # 시간데이터 활용을 위해
from django.contrib import messages  # 넌필드 오류를 반환하기 위한 것

from .forms import PostingForm, AnswerForm, CommentForm, BoardForm
from .models import * #모델을 불러온다.
from school_report.models import School
from django.db.models import Q, Count  # 검색을 위함. filter에서 OR조건으로 조회하기 위한 함수.(장고제공)
from .view import posting_interest, board_interest
from custom_account.views import notification_add  # 관심 게시판에 게시글을 작성하면 알림을 주기 위함.
from django.core.paginator import Paginator  # 게시판리스트, 게시글리스트, 답변글리스트를 위한 페이지네이터.
from django.contrib.auth import get_user_model  # 유저모델. 유저 신고에서 사용.
from school_report.view import check

def board_list_hidden(request, category):
    '''게시판 객체들을 페이지네이션을 가해 반환한다.'''
    board_list = Board.objects.filter(category=category.id)  # 카테고리에 따라 분류 받아오기.

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
               'category': category,# 게시판 생성 버튼을 위한 카테고리정보 전달.
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

def board_list(request, category_id):
    category = get_object_or_404(Board_category, pk=category_id)
    context = board_list_hidden(request, category)
    context['category'] = category
    get_categroy_name(category=category, context=context)
    return render(request, 'boards/base/board/board_list.html', context)


def board_detail(request, board_id):
    board = get_object_or_404(Board, pk=board_id)
    category = board.category
    # 교사게시판인 경우. 확인 후 리다이렉팅.
    if category.name.split('_')[0] == 'teacher':
        teacher = check.Check_teacher(request, board.school).in_school_and_none()
        if teacher != None:
            pass
        else:
            messages.error(request, '교사만 접근 가능합니다.')
            check.Check_teacher(request, board.school).redirect_to_school()
    context_posting = posting_list_hidden(request, board_id)  # 하위 포스팅 가져오기.
    # ----- list함수와 같은 부분 -----
    context_board = board_list_hidden(request, category)
    context_board['board'] = board
    context_board['category'] = category
    context = {**context_posting, **context_board}
    get_categroy_name(category=category, context=context)
    #template_name = context['base_template'] +
    return render(request, 'boards/base/board/board_detail.html', context)

def board_name_adding(request, board):
    try:
        instr = request.POST['board_name']
    except:  # 게시판 이름 없이 진행된다면...
        instr = request.POST.get('school')
    outstr = ''
    for i in range(0, len(instr)):  # 문자열 내 공백 없애기.
        if instr[i] != ' ':
            outstr += instr[i]
    board_name_, created = Board_name.objects.get_or_create(name=outstr)  # created엔 새로 만들어졌는지 여부가 True로 나오고, tag_엔 그 태그가 담긴다.
    board.board_name = board_name_
    # 뒤에서 board.save()가 나와야 한다.


def school_adding(request, board):
    # try:
    instr = request.POST['school']
    outstr = ''
    for i in range(0, len(instr)):  # 문자열 내 공백 없애기.
        if instr[i] != ' ':
            outstr += instr[i]
    school_name_, created = School.objects.get_or_create(name=outstr, year=request.POST['enter_year'])  # created엔 새로 만들어졌는지 여부가 True로 나오고, tag_엔 그 태그가 담긴다.
    board.school = school_name_
    # 뒤에서 board.save()가 나와야 한다.
@login_required()
def board_create(request, category_id):
    category = get_object_or_404(Board_category, pk=category_id)
    context = {}
    get_categroy_name(category=category, context=context)
    if request.method == 'POST':  # 포스트로 요청이 들어온다면... 글을 올리는 기능.
        form = BoardForm(request.POST)  # 폼을 불러와 내용입력을 받는다.
        if form.is_valid():  # 문제가 없으면 다음으로 진행.
            board = form.save(commit=False)  # commit=False는 저장을 잠시 미루기 위함.(입력받는 값이 아닌, view에서 다른 값을 지정하기 위해)
            board.author = request.user  # 추가한 속성 author 적용
            board.category = category
            try:
                board_name_adding(request, board)  # 태그 추가 함수.
                school_adding(request, board)  # 위와 동일.
                board.save()
                board_interest(request, board.id)  # 저장 이후에 가능한 명령. 순서 바뀌면 404 뜬다.
            except:
                messages.error(request, '이미 등록된 학교와 연도 조합입니다.')
        return redirect('boards:board_list', category_id)  # 작성이 끝나면 목록화면으로 보낸다.
    else:  # 포스트 요청이 아니라면.. form으로 넘겨 내용을 작성하게 한다.
        form = BoardForm(request.POST)
    context['form'] = form  # 폼에서 오류가 있으면 오류의 내용을 담아 create.html로 넘긴다.
    # 없으면 그냥 form 작성을 위한 객체를 넘긴다.

    return render(request, 'boards/base/board/board_create.html', context)

def tag_adding_on_posting(request, posting):
    replace_text = [';', '#']  # 치환할 문자열. 이 문자열들을 , 로 바꾼다.
    tags_str = request.POST.get('tag')
    if tags_str:  # 태그가 있을 경우에만 진행.
        for text in replace_text:
            tags_str = tags_str.replace(text, ',')  # 각종 문자들을 ,로 바꾼다.
        tags = tags_str.split(',')  # ,로 구분된 태그 분할.
        for tag in tags:
            if not tag:  # tags가 없어서 tag가 없다면
                continue
            if tag == '':  # 공백이라면
                continue
            else:
                tag = tag.strip()  # 문자열 양쪽에 빈칸이 있을 때 이를 제거한다.
                tag_, created = Tag.objects.get_or_create(name=tag)  # created엔 새로 만들어졌는지 여부가 True로 나오고, tag_엔 그 태그가 담긴다.
                posting.tag.add(tag_)  # 요건 특이하게 save()가 필요 없다.

def pagenation_answer(request, posting):
    answer_list = posting.answer_set.all()
    ################## 페이징처리#########
    paginator = Paginator(answer_list, 10)  # 페이지당 10개씩 보여주겠다는 의미.
    last_page = int(paginator.num_pages)  #마지막페이지는 몇인가?
    page = request.GET.get('answer_page', last_page)  # 아무런 입력이 없으면 마지막 페이지를 보여주기 위해.

    answer_list = paginator.get_page(page)  # 페이징 된 리스트.

    current_page_num=int(page)  #현재 페이지는 몇인가?
    first_page=1 # 첫 페이지 넘버
    left_show = current_page_num - 5  #왼쪽으로 5개까지 나타낸다.
    right_show = current_page_num + 5  #우측으로 5개까지 나타낸다.
    if current_page_num < 6:
        left_show = first_page
    if current_page_num+5 > last_page:
        right_show = last_page
    page_list = range(left_show, right_show+1)  #보여줄 페이지의 범위.
    return {'answer_list': answer_list, 'answer_page_list': page_list, 'answer_page': page}

def get_categroy_name(category, context):
    '''context에 필요한 속성을 추가한다.'''
    category_name = category.name.split('_')[0]
    context['base_template'] = 'boards/' + category_name + "/"
    context['base_url'] = 'boards:' + category_name + '_'
def posting_detail_on_board(request, posting_id):
    posting = get_object_or_404(Posting, pk=posting_id)
    category = posting.board.category
    # 교사게시판인 경우. 확인 후 리다이렉팅.
    if category.name.split('_')[0] == 'teacher':
        teacher = check.Check_teacher(request, posting.board.school).in_school_and_none()
        if teacher != None:
            pass
        else:
            messages.error(request, '교사만 접근 가능합니다.')
            check.Check_teacher(request, posting.board.school).redirect_to_school()
    # ----- board_detail 함수와 같은 부분 -----
    board = posting.board
    context_posting = posting_list_hidden(request, board.id)
    context_board = board_list_hidden(request, category)  # 포스팅이 속한 게시판 list를 얻기 위함.
    context_board['board'] = board
    context_answer = pagenation_answer(request, posting)  # 포스팅에 속한 답글 list를 얻기 위함.
    context = {**context_posting, **context_board, **context_answer}
    # 포스팅 정보 추가.
    context['posting'] = posting
    get_categroy_name(category, context)
    return render(request, 'boards/base/posting/posting_detail.html', context)

def check_boolean(request, posting):  # 생성된 포스팅을 받는다.
    value_list = []
    html_fiedl_list = ['boolean_1', 'boolean_2']
    for bools in html_fiedl_list:
        check = request.POST.get(bools)
        value_list.append(check)
    if value_list[0] == 'true':
        posting.boolean_1 = True
    else:
        posting.boolean_1 = False
    if value_list[1] == 'true':
        posting.boolean_2 = True
    else:
        posting.boolean_2 = False

@login_required()
def posting_create_on_board(request, board_id):
    board = get_object_or_404(Board, pk=board_id)
    context = {}
    if request.method == 'POST':  # 포스트로 요청이 들어온다면... 글을 올리는 기능.
        form = PostingForm(request.POST)  # 폼을 불러와 내용입력을 받는다.
        if form.is_valid():  # 문제가 없으면 다음으로 진행.
            posting = form.save(commit=False)  # commit=False는 저장을 잠시 미루기 위함.(입력받는 값이 아닌, view에서 다른 값을 지정하기 위해)
            posting.author = request.user  # 추가한 속성 author 적용
            posting.board = board  # 게시판 지정.
            check_boolean(request, posting)
            posting.save()
            posting_interest(request, posting.id)
            notification_add(request, type=12, to_users=board.interest_users.all(),
                             message=str(board.board_name)+str(board.enter_year), url=resolve_url('boards:posting_detail', posting.id))
            tag_adding_on_posting(request, posting)  # 태그 추가 함수.
            return posting_detail_on_board(request, posting.id)  # 작성이 끝나면 작성한 글로 보낸다.
    else:  # 포스트 요청이 아니라면.. form으로 넘겨 내용을 작성하게 한다.
        form = PostingForm()
    context['form'] = form  # 폼에서 오류가 있으면 오류의 내용을 담아 create.html로 넘긴다.
    get_categroy_name(category=board.category, context=context)
    return render(request, 'boards/base/posting/posting_create.html', context)

@login_required()
def posting_modify_on_board(request, posting_id):
    posting = get_object_or_404(Posting, pk=posting_id)
    if request.user != posting.author:
        messages.error(request, '수정권한이 없습니다')
        return redirect('boards:detail', posting_id=posting.id)
    if request.method == "POST":
        form = PostingForm(request.POST, instance=posting)  # 받은 내용을 객체에 담는다. instance에 제대로 된 걸 넣지 않으면 새로운 인스턴스를 만든다.
        if form.is_valid():
            posting = form.save(commit=False)
            posting.author = request.user
            posting.tag.clear()  # 수정화면에서 문자열로 다루기 위해 지웠다가 다시 등록하는 방법을 사용한다.
            tag_adding_on_posting(request, posting)  # 태그 추가 함수.
            check_boolean(request, posting)
            posting.save()
            return posting_detail_on_board(request, posting.id)
    else:  # GET으로 요청된 경우.
        form = PostingForm(instance=posting)  # 해당 모델의 내용을 가져온다!
        # 태그를 문자열화 하여 form과 함께 담는다.
        tags = posting.tag.all()
        tags_str = ''
        for tag in tags:
            tags_str += tag.name + ', '
    context = {'form': form,
               'tags_str': tags_str}
    get_categroy_name(category=posting.board.category, context=context)
    return render(request, 'boards/base/posting/posting_create.html', context)

@login_required()
def report_user(request):
    user_nickname = request.POST.get('report_user')
    reported_user = get_object_or_404(get_user_model(), nickname=user_nickname)
    '''기본적으로 posting_create와 동일.'''  # + usernickname으로 추가하는 것 추가.
    print('---------------테스트용')
    board = get_object_or_404(Board, id=23)  # 건의 게시판 pk는 23.
    context = {}
    if request.method == 'POST':  # 포스트로 요청이 들어온다면... 글을 올리는 기능.
        form = PostingForm(request.POST)  # 폼을 불러와 내용입력을 받는다.\
        print(form.is_valid())
        if form.is_valid():  # 문제가 없으면 다음으로 진행.
            print('되나')
            posting = form.save(commit=False)  # commit=False는 저장을 잠시 미루기 위함.(입력받는 값이 아닌, view에서 다른 값을 지정하기 위해)
            posting.author = request.user  # 추가한 속성 author 적용
            posting.board = board  # 게시판 지정.
            check_boolean(request, posting)
            # 요거 추가함.
            posting.report_user = reported_user
            posting.save()
            posting_interest(request, posting.id)
            notification_add(request, type=12, to_users=board.interest_users.all(),
                             message=str(board.board_name) + str(board.enter_year),
                             url=resolve_url('boards:posting_detail', posting.id))
            tag_adding_on_posting(request, posting)  # 태그 추가 함수.
            return posting_detail_on_board(request, posting.id)  # 작성이 끝나면 작성한 글로 보낸다.
    else:  # 포스트 요청이 아니라면.. form으로 넘겨 내용을 작성하게 한다.
        print('폼이 안맞나')
        form = PostingForm()
    context['form'] = form  # 폼에서 오류가 있으면 오류의 내용을 담아 create.html로 넘긴다.
    get_categroy_name(category=board.category, context=context)
    ## 요부분만 create와 다르다.
    user_id = request.GET.get('user_id')
    context['report_user'] = reported_user
    return render(request, 'boards/base/posting/posting_create.html', context)

@login_required()
def posting_delete(request, posting_id):
    posting = get_object_or_404(Posting, pk=posting_id)
    board = posting.board  # 지울거니까 미리 받아놓자.
    if request.user != posting.author:
        messages.error(request, '삭제권한이 없습니다. 꼼수쓰지 마라;')
        return redirect('boards:detail', posting_id=posting.id)
    elif posting.answer_set.count() >= 1:
        messages.error(request, '하위에 작성된 댓글이 있으면 삭제 불가능합니다.')
        return redirect(request.META.get('HTTP_REFERER','/'))
    messages.success(request, '삭제 성공~!')
    posting.delete()
    # 메인화면으로 돌리자.
    return redirect('boards:posting_list', board.id)
@login_required()
def board_delete(request, board_id):
    board = get_object_or_404(Board, pk=board_id)
    category = board.category  # 삭제될 거니까, 미리 받아놓는다.
    if request.user != board.author:
        messages.error(request, '삭제권한이 없습니다. 꼼수쓰지 마라;')
        return redirect('boards:detail', board_id=board.id)
    elif board.posting_set.count() >= 1:
        messages.error(request, '하위에 작성된 게시글이 있으면 삭제 불가능합니다.')
        return redirect(request.META.get('HTTP_REFERER','/'))
    messages.success(request, '삭제 성공~!')
    board.delete()
    # 게시판으로 돌리자.
    return redirect('boards:board_list', category.id)

