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
def posting_interest(request, posting_id):
    posting = get_object_or_404(Posting, pk=posting_id)
    context = {}
    if posting.interest_users.filter(id=request.user.id).exists():
        posting.interest_users.remove(request.user)  # 이미 추가되어 있다면 삭제한다.
        posting.interest_count -= 1
        posting.save()  # save가 있어야 반영된다.
        context['posting_interest_check'] = False
    else:
        posting.interest_users.add(request.user)  # 포스팅의 likeUser에 user를 더한다.
        posting.interest_count += 1
        posting.save()
        context['posting_interest_check'] = True
    return HttpResponse(json.dumps(context), content_type='application/json')
@login_required()
def board_interest(request, board_id):
    board = get_object_or_404(Board, pk=board_id)
    context = {}
    if board.interest_users.filter(id=request.user.id).exists():
        board.interest_users.remove(request.user)  # 이미 추가되어 있다면 삭제한다.
        board.interest_count -= 1
        board.save()  # save가 있어야 반영된다.
        context['board_interest_check'] = False
    else:
        board.interest_users.add(request.user)  # 포스팅의 likeUser에 user를 더한다.
        board.interest_count += 1
        board.save()
        context['board_interest_check'] = True
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
            redirect_url = '{}#answer_{}'.format(request.META.get('HTTP_REFERER','/'), answer.id)
            notification_add(request, type=22, to_users=posting.interest_users.all(), message=posting.subject, url=redirect_url)
            return redirect(redirect_url)

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
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.create_date = timezone.now()
            comment.answer = answer
            comment.save()
            redirect_url = '{}#comment_{}'.format(request.META.get('HTTP_REFERER','/'), comment.id)
            to_users = [answer.author]
            notification_add(request, type=32, to_users=to_users, message=answer.content, url=redirect_url)
            #return HttpResponse(json.dumps(context), content_type='application/json')
            return redirect('{}#answer_{}'.format(
                request.META.get('HTTP_REFERER','/'), answer.id))
            #return render(request, 'boards/comment_create_ajax.html', {'comment':comment})
    else:
        messages.error(request, '제대로 기입하쇼~')
        return redirect('boards:detail', posting_id=answer.posting.id)

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


