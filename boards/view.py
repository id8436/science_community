from django.contrib.auth.decorators import login_required #로그인이 있어야 가능함

from django.shortcuts import render, get_object_or_404, redirect, resolve_url, HttpResponse
import json
from django.utils import timezone  # 시간입력을 위해.
from _datetime import datetime,timedelta  # 시간데이터 활용을 위해
from django.contrib import messages  # 넌필드 오류를 반환하기 위한 것

from .forms import PostingForm, AnswerForm, CommentForm
from .models import * #모델을 불러온다.
from django.db.models import Q, Count  # 검색을 위함. filter에서 OR조건으로 조회하기 위한 함수.(장고제공)

from custom_account.models import Notification
from custom_account.views import notification_add

def list_hidden(request):
    posting_list = Posting.objects.all()  # 일단 객체 목록을 받아온다.(전부 다~)
    #posting_list = Posting.objects.filter(board=board)

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

def list(request):
    context=list_hidden(request)# board)
    notifications = Notification.objects.filter(to_user=request.user)
    context['notifications'] = notifications
    return render(request, 'boards/list_show.html', context)

def posting_detail(request, posting_id):
    posting = get_object_or_404(Posting, pk=posting_id)
    #----- list함수와 같은 부분 -----
    context = list_hidden(request)
    context['posting'] = posting
    return render(request, 'boards/detail.html', context)

def tag_adding(request, posting):
    tags = request.POST.get('tag').split(',')
    for tag in tags:
        if not tag:
            continue
        else:
            tag = tag.strip()  # 문자열 양쪽에 빈칸이 있을 때 이를 제거한다.
            tag_, created = Tag.objects.get_or_create(name=tag)  # created엔 새로 만들어졌는지 여부가 True로 나오고, tag_엔 그 태그가 담긴다.
            posting.tag.add(tag_)  # 요건 특이하게 save()가 필요 없다.

def tag_info(request, tag_name):
    tag = get_object_or_404(Tag, name=tag_name)
    postings = tag.posting_set.all()
    context = {'tag':tag,
               'boards':postings}
    return render(request, 'boards/tag_info.html', context)
def tag_delete(request, posting_id, tag_name):
    '''게시글에서 태그를 지운다.'''
    posting = get_object_or_404(Posting, pk=posting_id)

    tag = get_object_or_404(Tag, name=tag_name)


@login_required()
def posting_create(request):
    if request.method == 'POST':  #포스트로 요청이 들어온다면... 글을 올리는 기능.
        form = PostingForm(request.POST)  #폼을 불러와 내용입력을 받는다.
        if form.is_valid():  #문제가 없으면 다음으로 진행.
            posting = form.save(commit=False)  #commit=False는 저장을 잠시 미루기 위함.(입력받는 값이 아닌, view에서 다른 값을 지정하기 위해)
            posting.author = request.user  # 추가한 속성 author 적용
            posting.create_date = timezone.now()  #현재 작성일시 자동저장
            posting.save()
            tag_adding(request, posting)  # 태그 추가 함수.
            return redirect('boards:list')  #작성이 끝나면 목록화면으로 보낸다.
    else:  #포스트 요청이 아니라면.. form으로 넘겨 내용을 작성하게 한다.
        form = PostingForm()
    context = {'form': form}  #폼에서 오류가 있으면 오류의 내용을 담아 create.html로 넘긴다.
    #없으면 그냥 form 작성을 위한 객체를 넘긴다.
    return render(request, 'boards/create.html', context)

@login_required()
def posting_modify(request, posting_id):#이름을 update로 해도 괜찮았을 듯하다.
    posting = get_object_or_404(Posting, pk=posting_id)
    if request.user != posting.author:
        messages.error(request, '수정권한이 없습니다')
        return redirect('boards:detail', posting_id=posting.id)

    if request.method == "POST":
        form = PostingForm(request.POST, instance=posting)  # 받은 내용을 객체에 담는다. instance에 제대로 된 걸 넣지 않으면 새로운 인스턴스를 만든다.
        if form.is_valid():
            posting = form.save(commit=False)
            posting.author = request.user
            posting.modify_date = timezone.now()  # 수정일시 자동 저장
            posting.save()
            tag_adding(request, posting)  # 태그 추가 함수.
            return redirect('boards:detail', posting_id=posting.id)
    else:  # GET으로 요청된 경우.
        form = PostingForm(instance=posting)  # 해당 모델의 내용을 가져온다!
    context = {'form': form,
               'posting': posting,}
    return render(request, 'boards/create.html', context)

@login_required()
def posting_delete(request, posting_id):
    posting = get_object_or_404(Posting, pk=posting_id)
    if request.user != posting.author:
        messages.error(request, '삭제권한이 없습니다. 꼼수쓰지 마라;')
        return redirect('boards:detail', posting_id=posting.id)
    posting.delete()
    return redirect('boards:list')
@login_required()
def posting_like(request, posting_id):
    posting = get_object_or_404(Posting, pk=posting_id)
    context = {}
    if posting.like_users.filter(id=request.user.id).exists():
        posting.like_users.remove(request.user)  # 이미 추가되어 있다면 삭제한다.
        posting.like_count -= 1
        posting.save()  # save가 있어야 반영된다.
        context['like_check'] = False
    else:
        posting.like_users.add(request.user)  # 포스팅의 likeUser에 user를 더한다.
        posting.like_count += 1
        posting.save()
        context['like_check'] = True
    return HttpResponse(json.dumps(context), content_type='application/json')
@login_required()
def posting_dislike(request, posting_id):
    posting = get_object_or_404(Posting, pk=posting_id)
    context = {}
    if posting.dislike_users.filter(id=request.user.id).exists():
        posting.dislike_users.remove(request.user)  # 이미 추가되어 있다면 삭제한다.
        posting.dislike_count -= 1
        posting.save()  # save가 있어야 반영된다.
        context['like_check'] = False
    else:
        posting.dislike_users.add(request.user)  # 포스팅의 likeUser에 user를 더한다.
        posting.dislike_count += 1
        posting.save()
        context['like_check'] = True
    return HttpResponse(json.dumps(context), content_type='application/json')

@login_required()
def answer_create(request, posting_id):
    posting = get_object_or_404(Posting, pk=posting_id)
    if request.method == "POST":
        form = AnswerForm(request.POST)  # post를 통해 받은 폼.
        if form.is_valid():
            answer = form.save(commit=False)
            answer.posting = posting  # 상위 객체 연결.
            answer.author = request.user  # 추가한 속성 author 적용
            answer.create_date = timezone.now()
            answer.save()
            notification_add(request, type=22, to_user=posting.author, message=posting.subject)
            return redirect('{}#answer_{}'.format(
            request.META.get('HTTP_REFERER','/'), answer.id))
            #request.GET.get('next'), answer.id))  # 글을 올렸던 곳에 대한 정보를 get으로 받아 되돌려준다.
    #resolve_url('boards:detail', posting_id=posting.id), answer.id))
            #redirect('boards:detail', posting_id=posting.id)
    form = AnswerForm()
    context = {'posting': posting, 'form': form}
    return render(request, 'boards/detail.html', context)
    #폼이 적절하지 않다면 에러메시지와 함께 detail로 보낸다.

@login_required()
def answer_update(request, answer_id):
    answer = get_object_or_404(Answer, pk=answer_id)
    if request.user != answer.author:
        messages.error(request, '수정권한이 없습니다')
        return redirect('boards:detail', posting_id=answer.posting.id)

    if request.method == "POST":
        form = AnswerForm(request.POST, instance=answer)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.author = request.user
            answer.modify_date = timezone.now()
            answer.save()
            return redirect('boards:detail', posting_id=answer.posting.id)
        else:
            form = AnswerForm(instance=answer)
        context = {'answer': answer, 'form': form}
    return render(request, 'answer_form.html', context)

@login_required()
def answer_delete(request, answer_id):
    answer = get_object_or_404(Answer, pk=answer_id)
    if request.user != answer.author:
        messages.error(request, '댓글삭제권한이 없습니다. 꼼수쓰지 마라;')
    else:
        answer.delete()
    return redirect('boards:detail', posting_id=answer.posting.id)

##############################################대댓글 관련 뷰##
@login_required()
def comment_create(request, answer_id):
    answer = get_object_or_404(Answer, pk=answer_id)
    posting = answer.posting  # 답글과 연결된 포스팅.
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.create_date = timezone.now()
            comment.answer = answer
            comment.save()
            context = {"content" : comment.content}
            #return HttpResponse(json.dumps(context), content_type='application/json')
            return redirect('{}#answer_{}'.format(
                request.META.get('HTTP_REFERER','/'), answer.id))
            #return render(request, 'boards/comment_create_ajax.html', {'comment':comment})
    return redirect('boards:detail', posting_id=answer.posting.id)
    #else:
    #    form = CommentForm()
    #context = {'form': form}
    #return render(request, 'comment_form.html', context)

@login_required()
def comment_update(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user != comment.author:
        messages.error(request, '댓글수정권한이 없습니다')
        return redirect('boards:detail', posting_id=comment.answer.posting.id)

    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.modify_date = timezone.now()
            comment.save()
            return redirect('boards:detail', posting_id=comment.answer.posting.id)
    else:
        form = CommentForm(instance=comment)
    context = {'form': form}
    return render(request, 'comment_form.html', context)

@login_required()
def comment_delete(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user != comment.author:
        messages.error(request, '댓글삭제권한이 없습니다. 꼼수쓰지 마라;')
        return redirect('boards:detail', posting_id=comment.answer.posting.id)
    else:
        comment.delete()
    #return HttpResponse(json.dumps({}))
    #return redirect('boards:detail', posting_id=comment.answer.posting.id)


############추천, 즐겨찾기 추가기능##########
@login_required()
def favorite_posting(request, posting_id):
    posting = get_object_or_404(Posting, pk=posting_id)
    posting.favorite.add(request.user)
    return redirect('boards:detail', posting_id=posting.id)

@login_required()  # 추천할 것 타입을 지정해 추천을 주게 하면 좋겠는데?
def vote(request, type, object_id):
    object = get_object_or_404(type, pk=object_id)
    object.voter.add(request.user)
    return redirect('boards:detail', posting_id= posting.id)



