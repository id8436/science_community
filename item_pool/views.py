from django.contrib.auth.decorators import login_required #로그인이 있어야 가능함

from django.shortcuts import render, get_object_or_404, redirect, resolve_url
from django.utils import timezone  # 시간입력을 위해.
from _datetime import datetime,timedelta  # 시간데이터 활용을 위해
from django.contrib import messages  # 넌필드 오류를 반환하기 위한 것

from .forms import QuestionForm, AnswerForm,CommentForm
from .models import * #모델을 불러온다.
from django.db.models import Q, Count  # 검색을 위함. filter에서 OR조건으로 조회하기 위한 함수.(장고제공)

def list_hidden(request):
    question_list = Question.objects.all()  # 일단 객체 목록을 받아온다.(전부 다~)

    # 정렬 기능.
    ordering = request.GET.get('ordering', 'recent')  # 정렬기준
    if ordering == 'recent':  # 시간순 정렬
        question_list = question_list.order_by('-create_date')
    elif ordering == 'popular':  # 댓글순 정렬
        question_list = question_list.annotate(num_answer=Count('answer')).order_by('-num_answer', '-create_date')
    elif ordering == 'recommend':  # 추천순 정렬
        question_list = question_list.annotate(num_voter=Count('favorite')).order_by('-num_voter', '-create_date')
        print(question_list)
    elif ordering == 'student_code':  # 학번순 정렬
        question_list = question_list.order_by('profile__student_code')
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
        question_list= question_list.filter(create_date__gte= date)  # greater than equal
    if request.GET.get('end'):
        time = request.GET.get('end').split('-')
        end = request.GET.get('end')
        date = datetime(int(time[0]), int(time[1]), int(time[2])) + timedelta(days=1)  # 시간이 00:00:00으로 잡힌다.
        date = datetime.date(date)
        question_list = question_list.filter(create_date__lte=date)

    #-----검색기능
    keyword = request.GET.get('keyword', '')  # 검색어.
    if keyword != '':  # 검색어가 있다면
        result = []  # 검색결과를 담기 위한 리스트를 만든다.
        keywords = keyword.split(' ')  # 공백이 있는 경우 나눈다.
        for kw in keywords:  # 띄어쓰기로 검색을 하는 경우가 많으니까, 다 찾아줘야지.
            result += question_list.filter(  # 검색해서 검색결과에 더한다.
            Q(subject__icontains=kw) |  # 제목검색
            Q(content__icontains=kw) |  # 내용검색
            Q(author__nickname__icontains=kw) |  # # question모델의 상위인 user모델의 nickname에서 검색.
            Q(answer__author__nickname__icontains=kw)  # 하위모델인 answer모델의 참조인 user모델의 속성에서 검색.
            ).distinct()  # 중복된 내용이 있으면 제거하는 함수.
        question_list = result  # 모은 결과를 리스트에 담는다.

    ################## 페이징처리#########
    from django.core.paginator import Paginator  # 장고엔 다 있다!!
    page = request.GET.get('page', '1')  #어떤 페이지를 보고 있을지 전달받는다. 추후 탬플릿에서 구현.
    paginator = Paginator(question_list, 10)  # 페이지당 10개씩 보여주겠다는 의미.
    question_list = paginator.get_page(page)  # 페이징 된 리스트.

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
    for question in question_list:
        question.comment_sum = question.answer_set.count()  # question객체의 새로운 속성을 정의하고 각 댓글의 갯수를 부여한다.
        for answer in question.answer_set.all(): #question 객체 하위의 answer로 돌려가며 대댓글 갯수를 추가한다.
            question.comment_sum += answer.comment_set.count()

    context = {'question_list': question_list,#기존의 리스트 대신 페이지객체를 보낸다.
               'page_list':page_list,  #보여줄 페이지 리스트
               'page': page,  # 현재 페이지
               'keyword': keyword,  # 검색어는 다시 돌려준다.
               'ordering': ordering,  # 선택한 정렬순서는 다시 돌려준다.
               'start': start,  # 시작날짜
               'end': end,  # 끝날짜
               }
    return context

def list(request):
    context=list_hidden(request)
    return render(request, 'item_pool/list_show.html', context)

@login_required(login_url='membership:login')
def detail(request,question_id):
    question = get_object_or_404(Question, pk=question_id)

    if question.wrong != 0:  #아래에서 0으로 나누어지는 것 방지.
        correct = question.correct
        question.correctRate = round(correct / (correct + question.wrong),3) #정답률을 표시하기 위한 새로운 속성 추가.

########list함수와 같은 부분####
    context = list_hidden(request)
    context['question'] = question  # context = { 'question': question}를 추가하기 위함.
    return render(request, 'item_pool/detail.html', context)

@login_required(login_url='membership:login')
def solve(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    answer = '123a'  # 사용자의 대답을 담기 위한 변수.
    feedback = '112s'  # 정답여부에 따라 달라지는 피드백.
    if request.method == 'POST':  # 정답정보는 포스트로 보내자.
        answer = request.POST.get('answer')
        if answer == question.solution:  # 대답이 정답과 일치한다면..
            question.correct = question.correct+1
            question.save()
            feedback = '정답입니다~'
        else:
            question.wrong = question.wrong+1
            question.save()
            feedback = '틀렸습니다;;'
    correct = question.correct
    question.correctRate = round(correct / (correct + question.wrong),3)
    ###list 가져오기####
    context = list_hidden(request)
    #context['question'] = question  # context = { 'question': question}를 추가하기 위함.
    context2 = {'question': question, 'answer': answer, 'feedback': feedback}
    context.update(context2)  # 딕셔너리 합치기!
    return render(request, 'item_pool/detail.html', context)

@login_required()
def create(request):
    if request.method == 'POST':  #포스트로 요청이 들어온다면... 글을 올리는 기능.
        form = QuestionForm(request.POST)  #폼을 불러와 내용입력을 받는다.
        if form.is_valid():  #문제가 없으면 다음으로 진행.
            question = form.save(commit=False)  #commit=False는 저장을 잠시 미루기 위함.(입력받는 값이 아닌, view에서 다른 값을 지정하기 위해)
            question.author = request.user  # 추가한 속성 author 적용
            question.create_date = timezone.now()  #현재 작성일시 자동저장
            question.save()
            return redirect('item_pool:list')  #작성이 끝나면 목록화면으로 보낸다.
    else:  #포스트 요청이 아니라면.. form으로 넘겨 내용을 작성하게 한다.
        form = QuestionForm()
    context = {'form': form}  #폼에서 오류가 있으면 오류의 내용을 담아 create.html로 넘긴다.
    #없으면 그냥 form 작성을 위한 객체를 넘긴다.
    return render(request, 'item_pool/create.html', context)

@login_required()
def modify(request, question_id):#이름을 update로 해도 괜찮았을 듯하다.
    question = get_object_or_404(Question, pk=question_id)
    if request.user != question.author:
        messages.error(request, '수정권한이 없습니다')
        return redirect('item_pool:detail', question_id=question.id)

    if request.method == "POST":
        form = QuestionForm(request.POST, instance=question)  # 받은 내용을 객체에 담는다. instance에 제대로 된 걸 넣지 않으면 새로운 인스턴스를 만든다.
        if form.is_valid():
            question = form.save(commit=False)
            question.author = request.user
            question.modify_date = timezone.now()  # 수정일시 자동 저장
            question.save()
            return redirect('item_pool:detail', question_id=question.id)
    else:#GET으로 요청된 경우.
        form = QuestionForm(instance=question)#해당 모델의 내용을 가져온다!
    context = {'form': form}
    return render(request, 'item_pool/create.html', context)

@login_required()
def delete(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if request.user != question.author:
        messages.error(request, '삭제권한이 없습니다. 꼼수쓰지 마라;')
        return redirect('item_pool:detail', question_id=question.id)
    question.delete()
    return redirect('item_pool:list')

@login_required()
def answer_create(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if request.method == "POST":
        form = AnswerForm(request.POST)  # post를 통해 받은 폼.
        if form.is_valid():
            answer = form.save(commit=False)
            answer.question = question  # question객체 연결.
            answer.author = request.user  # 추가한 속성 author 적용
            answer.create_date = timezone.now()
            answer.save()
            return redirect('{}#answer_{}'.format(
    resolve_url('item_pool:detail', question_id=question.id), answer.id))
            #redirect('item_pool:detail', question_id=question.id)
    else:
        form = AnswerForm()
    context = {'question': question, 'form': form}
    return render(request, 'item_pool/detail.html', context)
    #폼이 적절하지 않다면 에러메시지와 함께 detail로 보낸다.

@login_required(login_url='membership:login')
def answer_update(request, answer_id):
    answer = get_object_or_404(Answer, pk=answer_id)
    if request.user != answer.author:
        messages.error(request, '수정권한이 없습니다')
        return redirect('item_pool:detail', question_id=answer.question.id)

    if request.method == "POST":
        form = AnswerForm(request.POST, instance=answer)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.author = request.user
            answer.modify_date = timezone.now()
            answer.save()
            return redirect('item_pool:detail', question_id=answer.question.id)
    else:
        form = AnswerForm(instance=answer)
    context = {'answer': answer, 'form': form}
    return render(request, 'item_pool/answer_form.html', context)

@login_required(login_url='membership:login')
def answer_delete(request, answer_id):
    answer = get_object_or_404(Answer, pk=answer_id)
    if request.user != answer.author:
        messages.error(request, '댓글삭제권한이 없습니다. 꼼수쓰지 마라;')
    else:
        answer.delete()
    return redirect('item_pool:detail', question_id=answer.question.id)

##############################################대댓글 관련 뷰##
@login_required(login_url='membership:login')
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
            return redirect('item_pool:detail', question_id=comment.answer.question.id)
    else:
        form = CommentForm()
    context = {'form': form}
    return render(request, 'item_pool/comment_form.html', context)

@login_required(login_url='membership:login')
def comment_update(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user != comment.author:
        messages.error(request, '댓글수정권한이 없습니다')
        return redirect('item_pool:detail', question_id=comment.answer.question.id)

    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.modify_date = timezone.now()
            comment.save()
            return redirect('item_pool:detail', question_id=comment.answer.question.id)
    else:
        form = CommentForm(instance=comment)
    context = {'form': form}
    return render(request, 'item_pool/comment_form.html', context)

@login_required(login_url='membership:login')
def comment_delete(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user != comment.author:
        messages.error(request, '댓글삭제권한이 없습니다. 꼼수쓰지 마라;')
        return redirect('item_pool:detail', question_id=comment.answer.question.id)
    else:
        comment.delete()
    return redirect('item_pool:detail', question_id=comment.answer.question.id)


############추천, 즐겨찾기 추가기능##########
@login_required(login_url='membership:login')
def favorite_question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    question.favorite.add(request.user)
    return redirect('item_pool:detail', question_id=question.id)

@login_required(login_url='membership:login')  # 추천할 것 타입을 지정해 추천을 주게 하면 좋겠는데?
def vote(request, type, object_id):
    object = get_object_or_404(type, pk=object_id)
    object.voter.add(request.user)
    return redirect('item_pool:detail', question_id= object.id)



