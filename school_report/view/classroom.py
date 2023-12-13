from django.shortcuts import render, get_object_or_404, redirect, resolve_url, HttpResponse
from django.http import HttpResponseBadRequest  # 파일 처리 후 요청용.

from .. import models  # 모델 호출.
from custom_account.models import Notification
from ..forms import ClassroomForm, HomeworkForm
from django.contrib import messages
from custom_account.decorator import custom_login_required as login_required
from . import check
import json
import pandas as pd  # 통계용
import math
from datetime import datetime
import openpyxl

@login_required()
def create(request, school_id):
    subject = get_object_or_404(models.Subject, pk=school_id)  # 학교로 되어있지만... shcool_id가 아니라 교과아이디.
    school = subject.school
    context = {'subject': subject, 'school': school}
    homeroom_list = list(school.homeroom_set.all()) # 학교 하위의 학급들.
    context['homeroom_list'] = homeroom_list
    obtained_classroom_list = subject.classroom_set.all()  # 현재 과목의 하위 교실들.
    obtained_list = []  # 클래스룸 상위의 홈룸을 담을 리스트.
    for classroom in obtained_classroom_list:
        obtained_list.append(classroom.homeroom)
    for homeroom in obtained_list:  # 기존에 만들어진 홈룸은 지우고 제공한다.
        homeroom_list.remove(homeroom)

    if request.method == 'POST':  # 포스트로 요청이 들어온다면... 글을 올리는 기능.
        teacher = check.Check_teacher(request, school).in_school_and_none()
        if teacher == None:
            messages.error(request, "학교에 등록된 교사가 아닙니다.")
            context['form'] = ClassroomForm(request.POST)
            return render(request, 'school_report/classroom/create.html', context)
        #form = ClassroomForm(request.POST)  # 폼을 불러와 내용입력을 받는다.
        #if form.is_valid():  # 문제가 없으면 다음으로 진행.
        homeroom_list = request.POST.getlist('homeroom_list')
        for homeroom_id in homeroom_list:  # 받은 데이터에 해당하는 걸 넣는다.
            homeroom = get_object_or_404(models.Homeroom, pk=homeroom_id)
            classroom, _ = models.Classroom.objects.get_or_create(base_subject=subject, master=teacher, school=school, homeroom=homeroom)
        return redirect('school_report:subject_main', subject_id=subject.id)  # 작성이 끝나면 작성한 글로 보낸다.
    else:  # 포스트 요청이 아니라면.. form으로 넘겨 내용을 작성하게 한다.
        #form = ClassroomForm()
        pass
    #context['form'] = form  # 폼에서 오류가 있으면 오류의 내용을 담아 create.html로 넘긴다.
    return render(request, 'school_report/classroom/create.html', context)

def main(request, classroom_id):
    classroom = get_object_or_404(models.Classroom, pk=classroom_id)
    context ={'classroom': classroom}

    subject_homework_list = classroom.base_subject.homework_set.order_by('-create_date')
    context['subject_homework_list'] = subject_homework_list
    homework_list = classroom.homework_set.order_by('-create_date')
    context['homework_list'] = homework_list
    return render(request, 'school_report/classroom/main.html', context)

@login_required()
def homework_create(request, classroom_id):
    '''교과교실에서 작성. .'''
    classroom = get_object_or_404(models.Classroom, pk=classroom_id)
    context = {}
    if request.method == 'POST':  # 포스트로 요청이 들어온다면... 글을 올리는 기능.
        form = HomeworkForm(request.POST)  # 폼을 불러와 내용입력을 받는다.
        if form.is_valid():  # 문제가 없으면 다음으로 진행.
            homework = form.save(commit=False)  # commit=False는 저장을 잠시 미루기 위함.(입력받는 값이 아닌, view에서 다른 값을 지정하기 위해)
            homework.author = request.user  # 추가한 속성 author 적용
            homework.classroom = classroom  # 게시판 지정.
            homework.save()

            # 개별 확인을 위한 개별과제 생성.
            # 개별 부여할 사람을 탬플릿에서 받는 것도 괜찮을듯...? 흠... []
            userlist = request.POST.getlist('user')
            if userlist:  # 특정 방법으로 유저리스트가 전달된 경우.
                pass # 나중에 짜자. 들어오는 방법에 대한 논의가 필요하겠네.
            else:  # 유저리스트가 없으면 class에서 작성한 것으로 판단하고,
                student_list = models.Student.objects.filter(homeroom=classroom.homeroom)
                for student in student_list:
                    homework_distribution(homework, student.admin)  # 유저모델을 대응시킨다.
                    try:
                        Notification.objects.create(to_user=student.admin, official=True, classification=12, type=2, from_user=request.user, message=classroom, url=resolve_url("school_report:homework_detail", homework.id))
                    except Exception as e:
                        print(e)  # 학생 중 등록이 안한 학생은 to_user에서 에러가 난다.
                homework_distribution(homework, request.user)  # 작성자도 대응시킨다.

            return redirect('school_report:classroom_main', classroom.id)  # 작성이 끝나면 작성한 글로 보낸다.
    else:  # 포스트 요청이 아니라면.. form으로 넘겨 내용을 작성하게 한다.
        form = HomeworkForm()
    context['form'] = form  # 폼에서 오류가 있으면 오류의 내용을 담아 create.html로 넘긴다.
    return render(request, 'school_report/classroom/homework/create.html', context)
def homework_distribution(homework, user):
    '''과제 분배.'''
    individual, created = models.HomeworkSubmit.objects.get_or_create(to_user=user,
                                                                      base_homework=homework)
def homework_modify(request, posting_id):
    posting = get_object_or_404(models.Homework, pk=posting_id)
    if request.user != posting.author:
        messages.error(request, '수정권한이 없습니다')
        return redirect('school_report:homework_detail', posting_id=posting.id)
    if request.method == "POST":
        is_secret = posting.is_secret  # 비밀설문을 다시 공개로 바꿀 수 없게.
        form = HomeworkForm(request.POST, instance=posting)  # 받은 내용을 객체에 담는다. instance에 제대로 된 걸 넣지 않으면 새로운 인스턴스를 만든다.
        if form.is_valid():
            posting = form.save(commit=False)  # commit=False는 저장을 잠시 미루기 위함.(입력받는 값이 아닌, view에서 다른 값을 지정하기 위해)
            if is_secret:
                posting.is_secret = is_secret
            posting.save()
            # 개별 확인을 위한 개별과제 체크 해제.
            submit_list = models.HomeworkSubmit.objects.filter(base_homework=posting)
            for submit in submit_list:
                submit.check = False
                submit.save()
                toward = ''
                if posting.classroom:
                    toward = posting.classroom
                elif posting.subject_object:
                    toward = posting.subject_object
                Notification.objects.create(to_user=submit.to_user, official=True, classification=12,
                                                              type=3, from_user=request.user, message=toward,
                                                              url=resolve_url("school_report:homework_detail",
                                                                              posting_id))

            return redirect('school_report:homework_detail', posting_id=posting.id)
    else:  # GET으로 요청된 경우.
        form = HomeworkForm(instance=posting)  # 해당 모델의 내용을 가져온다!
        # 태그를 문자열화 하여 form과 함께 담는다.
    context = {'form': form}
    messages.error(request, '수정하면 기존 확인한 학생들의 체크는 "읽지않음"으로 갱신됩니다.')
    return render(request, 'school_report/classroom/homework/create.html', context)
def homework_delete(request, posting_id):
    posting = get_object_or_404(models.Homework, pk=posting_id)
    if request.user != posting.author:
        messages.error(request, '삭제권한이 없습니다. 꼼수쓰지 마라;')
        return redirect('school_report:homework_detail', posting_id=posting.id)
    messages.success(request, '삭제 성공~!')
    posting.delete()
    if posting.classroom:
        classroom = posting.classroom
        return redirect('school_report:classroom_main', classroom_id=classroom.id)
    if posting.subject_object:
        subject_object = posting.subject_object
        return redirect('school_report:subject_main', subject_object.id)
@login_required()
def homework_detail(request, posting_id):
    '''과제 상세페이지와 과제제출 기능.'''
    context = {}
    posting = get_object_or_404(models.Homework, pk=posting_id)
    context['posting'] = posting
    if posting.subject_object:
        school = posting.subject_object.school
    else:
        classroom = posting.classroom
        school = classroom.school

    if request.method == 'POST':  # 과제를 제출한 경우.
        homework_submit = get_object_or_404(models.HomeworkSubmit, base_homework=posting, to_user=request.user)
        content = request.POST.get('content')
        homework_submit.content = content
        homework_submit.submit_date = datetime.now()
        homework_submit.check = True  # 제출표시
        homework_submit.save()
        return redirect('school_report:homework_detail', posting.id)  # 작성이 끝나면 작성한 글로 보낸다.

    # 위 작동에 문제 없으면 아래 지우자.
    #student = get_object_or_404(models.Student, admin=request.user, homeroom=classroom.homeroom)  # 학생객체 가져와서...

    individual_announcement = []  # 주어진 과제를 담을 공간.
    try:  # 과제 하위가 하나일 경우.
        # 새로운 학생이 훗날 추가되었다면 접속했을 때 개별과제 하나가 늘게끔.
        individual_announcement, created = models.HomeworkSubmit.objects.get_or_create(to_user=request.user,
                                                                                       base_homework=posting)
        individual_announcement.read = True
        individual_announcement.save()
    except:
        sumbits = models.HomeworkSubmit.objects.filter(to_user=request.user, base_homework=posting)
        for submit in sumbits:
            submit.read = True
            submit.save()
            individual_announcement.append(submit)
    context['individual_announcement'] = individual_announcement
    # 학생과 교사 가르기.
    student = check.Check_student(request, school).in_school_and_none()
    teacher = check.Check_teacher(request, school).in_school_and_none()
    # 아래 작성자에 대한 건 빼도 괜찮지 않을까?
    # if posting.author == request.user:  # 과제의 제출자라면...
    #     submit_list = models.HomeworkSubmit.objects.filter(base_homework=posting)
    #     for submit in submit_list:
    #         #student = models.Student.objects.get(admin=submit.to_user, school=classroom.school)
    #         submit.who = 'QHS'  #student  # 설문자 정보를 담기.
    if teacher:
        submit_list = models.HomeworkSubmit.objects.filter(base_homework=posting)
        for submit in submit_list:
            try:
                student_check = models.Student.objects.get(admin=submit.to_user, school=school)
                submit.who = student_check  # 설문자 정보를 담기.
            except:
                try:
                    teacher_check = models.Teacher.objects.get(admin=submit.to_user, school=school)
                    submit.who = teacher_check
                except:
                    pass  # 어떤 이유에서인지 모르겠지만, 학생과 교사 양 쪽 다 에러가 뜨곤 함.
        context['submit_list'] = submit_list
    context['survey'] = posting.homeworkquestion_set.exists()  # 설문객체 여부.

    private_submits = models.HomeworkSubmit.objects.filter(base_homework=posting, to_user=request.user)
    for private_submit in private_submits:
        if student != None:
            private_submit.who = student
        elif teacher != None:
            private_submit.who = teacher
    context['private_submits'] = private_submits  # 열람자의 정보 담기.
    # 동료평가에서의 기능.
    if posting.is_special == 'peerReview':  # 동료평가의 경우, 지금 부여한 평균 보여주기.
        question = models.HomeworkQuestion.objects.get(homework=posting, ordering=1)  # 동료평가의 첫번째 질문.
        answers = models.HomeworkAnswer.objects.filter(respondent=request.user, question=question)  # 내가 부여한 것.
        df = pd.DataFrame.from_records(answers.values('contents'))
        try:  # 평가한 게 없으면 df가 None이 됨.
            df['contents'] = pd.to_numeric(df['contents'], errors='coerce')
            score_mean = df['contents'].mean()
            variance = df['contents'].var()
            context['score_mean'] = score_mean
            context['variance'] = variance
        except:
            pass
        # score_sum = 0
        # for answer in answers:
        #     score_sum += float(answer.contents)
        #     count += 1
        # try:  # 아무 평가도 안한 상태에선 count0이라 에러 발생.
        #     score_mean = score_sum/count
        #     context['score_mean'] = score_mean
        # except:
        #     pass
    return render(request, 'school_report/classroom/homework/detail.html', context)

def homework_resubmit(request, submit_id):
    submit = get_object_or_404(models.HomeworkSubmit, pk=submit_id)
    submit.check = False
    submit.save()
    return redirect('school_report:homework_detail', posting_id=submit.base_homework.id)
def homework_copy(request, homework_id):
    homework = models.Homework.objects.get(id=homework_id)
    context = {}
    admin = homework.author
    if request.method == 'POST':
        print('포스트 들어옴.')
        classroom_list = request.POST.getlist('classroom_list')
        subject_list = request.POST.getlist('subject_list')
        print(classroom_list)
        print(subject_list)
        # 여기부터 복사과정
        copied = homework.copy_create(classroom_list=classroom_list, subject_list=subject_list)
        return redirect('school_report:homework_detail', copied.id)
    # 사용자가 관리하는 객체를 보이기 위한 사전작업.
    if homework.school:
        school = homework.school
    elif homework.subject_object:
        school = homework.subject_object.school
    elif homework.classroom:
        school = homework.classroom.school
    # 사용자가 관리하는 객체들을 보여준다.
    admin_teacher = models.Teacher.objects.get(admin=admin, school=school)
    classroom_list = models.Classroom.objects.filter(master=admin_teacher, school=school)
    subject_list = models.Subject.objects.filter(master=admin_teacher, school=school)
    context['classroom_list'] = classroom_list
    context['subject_list'] = subject_list

    return render(request, 'school_report/classroom/homework/copy.html', context)
#    return redirect('school_report:homework_detail', posting_id=submit.base_homework.id)
def homework_survey_create(request, posting_id):
    '''설문의 수정도 이곳에서 처리.'''
    posting = get_object_or_404(models.Homework, pk=posting_id)  # 과제 찾아오기.
    context = {'posting': posting}
    if request.method == 'POST':  # 포스트로 요청이 들어온다면... 글을 올리는 기능.
        print(request.POST)
        if posting.author == request.user:  # 과제의 주인인 경우에만 가능.
            previous_question = list(posting.homeworkquestion_set.all())  # 기존에 등록되어 있던 질문들. list로 불러야 현재 상황 반영.
            question_type = request.POST.getlist('question_type')
            is_essential = request.POST.getlist('is_essential')
            is_special = request.POST.getlist('is_special')
            question_title = request.POST.getlist('question_title')
            question_id = request.POST.getlist('question_id')
            for i in range(len(question_type)):  # 질문 갯수만큼 순회.
                j = i+1
                try:  # 만들어진 것 같다면 불러와본다.
                    question = models.HomeworkQuestion.objects.get(pk=question_id[i])
                    if question.homework != posting:  # 기존 질문이 상위과제와 일치하지 않는다면 부정접근.
                        messages.error(request,'부정접근')
                        return redirect('school_report:homework_detail', posting_id=posting.id)
                    if question in previous_question:  # 기존 질문에 있던 거라면
                        previous_question.remove(question)  # 리스트에서 제거.
                    question.question_title = question_title[i]
                except:  # 없다면 새로 만들기.
                    question = models.HomeworkQuestion.objects.create(homework=posting, question_title=question_title[i])
                # 일단 생성 후 단순 정보 담기.
                question.question_type = question_type[i]
                question.ordering = j  # 순서정렬용 인덱스를 설정한다.
                # 데이터형 변경 후 넣기.
                if is_essential[i] == 'True':
                    is_essential[i] = True
                else:
                    is_essential[i] = False
                question.is_essential = is_essential[i]
                if is_special[i] == 'True':
                    is_special[i] = True
                else:
                    is_special[i] = False
                question.is_special = is_special[i]

                # 기능 저장.
                if request.POST.getlist('option'+str(j)):  # 문항 하위의 옵션 여부.
                    question.options = json.dumps(request.POST.getlist('option'+str(j)))  # 옵션 저장.
                if request.POST.get('upper_lim'+str(j)):  # 문항 하위의 옵션 여부.
                    question.upper_lim = float(request.POST.get('upper_lim'+str(j)))  # 옵션 저장.
                if request.POST.get('lower_lim' + str(j)):  # 문항 하위의 옵션 여부.
                    question.lower_lim = float(request.POST.get('lower_lim' + str(j)))  # 옵션 저장.
                question.save()
        for remain in previous_question:  # 남겨진 녀석들은 지운다.
            remain.delete()
        return redirect('school_report:homework_detail', posting_id=posting.id)
    question_list = posting.homeworkquestion_set.all()
    question_list = question_list.order_by('ordering')  # 주어진 순서대로 정렬.
    context['question_list'] = question_list
    for question in question_list:  # option값을 탬플릿에 전달하기 위함.
        if question.options:
            question.options = json.loads(question.options)  # 리스트화+저장하지 않고 옵션에 리스트 부여.(이게 되네?!)
    return render(request, 'school_report/classroom/homework/survey/create.html', context)



def homework_survey_list(request, posting_id):
    '''특수설문 지정.'''
    posting = get_object_or_404(models.Homework, pk=posting_id)  # 과제 찾아오기.
    context = {'posting': posting}  # 어떤 과제의 하위로 만들지 전달하기 위해.
    if request.method == 'POST':  # 포스트로 요청이 들어온다면... 글을 올리는 기능.
        surveyType = request.POST.get('surveyType')
        posting.is_special = surveyType
        posting.save()  # 특수설문 타입 저장.
        context['surveyType'] = surveyType  # 폼의 hidden에 담기 위해 전달.
        address = 'school_report/classroom/homework/survey/special/' + str(surveyType) + '.html'
        return render(request, address, context)
    return render(request, 'school_report/classroom/homework/survey/special/list.html', context)

@login_required()
def homework_survey_submit(request, submit_id):
    '''submit_id는 개별 아이디니... 설문 자체에 접근하게끔 하는 방략을 생각해야 할듯. 설문 ID를 주고..?
    설문 자체에 대한 링크는 주지 않는 게 좋을듯.'''
    '''사용자의 설문 제출.'''
    submit = get_object_or_404(models.HomeworkSubmit, pk=submit_id)  # 과제 찾아오기.
    posting = submit.base_homework
    # 제출기한이 지났다면 제출되지 않도록.
    if posting.deadline:
        import pytz  # 타임존이 안맞아 if에서 대소비교가 안되어 처리.
        deadline = posting.deadline.astimezone(pytz.UTC)
        if deadline < datetime.now(pytz.UTC) or posting.is_end:  # 데드라인이 지났다면... 안되지.
            messages.error(request, "이미 제출기한이 지난 과제입니다.")
            return redirect(request.META.get('HTTP_REFERER', None))  # 이전 화면으로 되돌아가기.

    context = {'posting': posting, 'submit':submit}
    # 설문 정보 불러오기.
    question_list = posting.homeworkquestion_set.all().order_by('ordering')
    for question in question_list:  # option값을 탬플릿에 전달하기 위함.
        if question.options:
            question.options = json.loads(question.options)  # 리스트화+저장하지 않고 옵션에 리스트 부여.(이게 되네?!)

    if request.method == 'POST':  # 포스트로 요청이 들어온다면... 글을 올리는 기능.
        if posting.classroom:  # 지금은 어쩔 수 없이 학교..로 해뒀는데, 나중엔 교실에 속한 경우에도 할 수 있도록... 구성하자.
            school = posting.classroom.school
        if posting.subject_object:
            school = posting.subject_object.school
        # 본인의 설문인지 검사.
        if submit.to_user == request.user:
            student = check.Check_student(request, school).in_school_and_none()
            if student == None:  # 학급에 속한 경우에만 가능.
                teacher = check.Check_teacher(request, school).in_school_and_none()
                if teacher == None:
                    return redirect('school_report:homework_detail', posting_id=posting.id)
        else:
            messages.error(request, '다른 사람의 응답을 할 수는 없어요~')
            return redirect('school_report:homework_detail', posting_id=posting.id)

        for question_id in request.POST.getlist('question'):
            question = models.HomeworkQuestion.objects.get(pk=question_id)
            if question.homework != posting:  # 부정접근 방지.
                return redirect('school_report:homework_detail', posting_id=posting.id)
            answer,_ = models.HomeworkAnswer.objects.get_or_create(respondent=request.user, question=question, to_student=submit.to_student)
            # response 태그가 있는 경우.
            response = request.POST.get('response'+question_id)
            if response:
                answer.contents = response
                question.respond = response  # 표시를 위해 담기.
            # option이 있는 경우. json으로 담는다.(객관식 선택의 경우임.)
            option = request.POST.getlist('option_for'+question_id)
            if option:
                answer.contents = json.dumps(option, ensure_ascii=False)
            # file이 있는 경우.
            file = request.FILES.get('response' + question_id)
            if file:
                answer.file.delete()  # 기존 파일 삭제.
                # 여기서 파일에 대한 검사를 수행합니다.
                # 예를 들어, 파일 크기가 10MB를 초과하는지 검사할 수 있습니다.
                if file.size > 10 * 1024 * 1024:
                    return HttpResponseBadRequest("10MB를 초과합니다.")
                # 파일을 모델에 저장합니다.
                answer.file = file  # 업로드.
            answer.save()

        submit.check = True
        submit.submit_date =datetime.now()
        submit.save()
        return redirect('school_report:homework_detail', posting_id=posting.id)

    for question in question_list:
        try:  # 연동된 제출의 응답 가져오기.
            answer = models.HomeworkAnswer.objects.get(respondent=request.user,
                                                       question=question, to_student=submit.to_student)
            question.response = answer.contents  # 기존 답변을 추가하기 위한 과정.
            # 파일이 있다면 반영.
            if answer.file:
                question.response = answer.file
            if question.options:  # 객관식, 드롭다운의 경우 선택지를 담기 위함.
                question.answer_list = json.loads(answer.contents)  # 선택지와 비교하기 위해.
        except Exception as e:
            # 에러가 났다는 건 json을 만들 수 없는 단일데이터라는 것.
            print(e)
    context['question_list'] = question_list

    return render(request, 'school_report/classroom/homework/survey/submit.html', context)

def question_list_statistics(question_list, submit):
    '''question_list를 받아 통계를 내고 다시 반환.'''
    for question in question_list:
        answers = models.HomeworkAnswer.objects.filter(question=question, to_student=submit.to_student)
        question.answer_count = answers.count()  # 갯수 따로 저장.
        origin_type = question.question_type  # 탬플릿 불러오기를 위해 원 타입으로 되돌려야 함.
        match question.question_type:  # 중복되는 작동을 짧게 줄이기 위해.
            case 'long':
                question.question_type = 'short'
            case 'dropdown':
                question.question_type = 'multiple-choice'
        match question.question_type:
            case 'short':
                df = pd.DataFrame.from_records(answers.values('contents'))  # 콘텐츠행만.
                # value_counts를 쓰면 인덱스가 꼬이기 때문에 중간과정을 거친다.
                contents_count = df['contents'].value_counts()
                contents_percentage = df['contents'].value_counts(normalize=True) * 100
                df['count'] = df['contents'].map(contents_count)
                df['percentage'] = df['contents'].map(contents_percentage)
                df = df.drop_duplicates(subset='contents')  # 답변이 중복된 행 삭제.
                # contents를 인덱스로 사용하여 새로운 값을 할당합니다.
                # df.set_index('contents', inplace=True)  # 인덱스 설정 하면 값이 안나와.
                #df = df.sort_values('count', ascending=False).reset_index(drop=False)  # 정렬은 필요 없지;
                df_dict = df.to_dict('records')  # 편하게 쓰기 위해 사전의 리스트로 반환!
                question.answers = df_dict
            case 'numeric':
                ## 숫자는 내 성적사이트 참고해서 다시;
                if question.answer_count < 1:
                    continue  # 등록된 정보가 없으면 에러가 나니, 패스.
                df = pd.DataFrame.from_records(answers.values('contents'))
                df = df.rename(columns={'contents': 'score'})  # 행이름 바꿔주기.(아래에서 그대로 써먹기 위해)
                df = df.astype({'score':float})
                # 통계데이터와 인터벌 지정하기.
                max = df['score'].max()
                min = df['score'].min()
                question.info = {}  # 사전에 담아두면 편하겠지.
                interval_size = 10
                n = (max - min) / interval_size
                data_dict = {}
                for i in range(interval_size):
                    if i == 0:  # 최하점을 담기 위해. else 아래 것이 본체.
                        ceriterion_min = round(min + n * i, 2)
                        ceriterion_max = round(min + n * (i + 1), 2)
                        interval_count = \
                        df.loc[(df['score'] >= ceriterion_min) & (df['score'] <= ceriterion_max)].shape[
                            0]  # 해당구간 데이터 세기.
                        key_text = '{}이상, {}이하'.format(ceriterion_min, ceriterion_max)
                        data_dict[key_text] = interval_count
                    else:
                        ceriterion_min = round(min + n * i, 2)
                        ceriterion_max = round(min + n * (i + 1), 2)
                        interval_count = df.loc[(df['score'] > ceriterion_min) & (df['score'] <= ceriterion_max)].shape[
                            0]  # 해당구간 데이터 세기.
                        key_text = '{}초과, {}이하'.format(ceriterion_min, ceriterion_max)
                        data_dict[key_text] = interval_count
                question.data_dict = data_dict  # context에 직접 담으면 다른 것들이랑 겹치니까.
                # 통계데이터 계산
                question.info['mean'] = df.mean(axis=0)[0]
                question.info['var']= df.var(axis=0)[0]
                question.info['std'] = df.std(axis=0)[0]
                question.info['mode'] = df.mode(axis=0).iloc[0][0]  # 최빈값.
                question.info['median'] = df.median(axis=0)[0]
                question.info['skew'] = df.skew(axis=0)[0]  # 왜도.
                question.info['kurtosis'] = df.kurtosis(axis=0)[0]  # 첨도.
                question.info['max'] = max
                question.info['min'] = min
            case 'multiple-choice':  # 2개 이상 동시 선택을 위해 json으로 저장한다.
                df = pd.DataFrame({})  # 빈 df 제작.
                for answer in answers:
                    selects = json.loads(answer.contents)  # 리스트로 받는다. json.loads를 안해도 된다고...??
                    if not isinstance(selects, list):  # 숫자형이거나, 다른 데이터 1개인 경우.
                        df = df.append({'contents': selects}, ignore_index=True)  # 대답을 담는다.
                    else:
                        for select in selects:
                            df = df.append({'contents':select}, ignore_index=True)  # 대답을 담는다.
                # value_counts를 쓰면 인덱스가 꼬이기 때문에 중간과정을 거친다.
                contents_count = df['contents'].value_counts()
                contents_percentage = df['contents'].value_counts(normalize=True) * 100
                df = df.drop_duplicates(subset='contents')  # 답변이 중복된 행 삭제.
                # contents를 인덱스로 사용하여 새로운 값을 할당합니다.
                df.set_index('contents', inplace=True)
                df['count'] = contents_count
                df['percentage'] = contents_percentage
                df = df.sort_values('count', ascending=False).reset_index(drop=False)
                df_dict = df.to_dict('records')  # 편하게 쓰기 위해 사전의 리스트로 반환!
                question.data_dict = df_dict
        question.question_type = origin_type  # 원래 타입으로 되돌리기.(탬플릿 불러오기에 문제)
    return question_list
def homework_survey_statistics(request, submit_id):  # 나중에 submit id로 바꾸는 게 좋을듯.
    submit = models.HomeworkSubmit.objects.get(id=submit_id)
    homework = submit.base_homework
    question_list = homework.homeworkquestion_set.order_by('ordering')
    context = {}
    # 아래를 어떻게 축약해야 적절하게 될까;;; 흠, 그냥 함수화 해서...? 모델 바꾸려면 힘드니까?
    if homework.school:
        school = homework.school
    elif homework.subject_object:
        school = homework.subject_object.school
    elif homework.classroom:
        school = homework.classroom.school
    teacher = check.Check_teacher(request, school).in_school_and_none()  # 교사라면 교사객체가 반환됨. 교과 뿐 아니라 학교, 학급 등에서도 일관적으로 작동할 수 있게 해야 할텐데...
    try:
        to_admin = submit.to_student.admin
    except:
        to_admin =None
    if to_admin == request.user or teacher or submit.to_student == None:  # 설문대상학생이거나 교사. 자기만 볼 수 있게.
        question_list = question_list_statistics(question_list, submit)  # question_list 의 info에 정보를 담아 반환한다.
        context['question_list'] = question_list
        context['submit'] = submit  # 동료평가에서 특별한 댓글 선택하기에서.
        return render(request, 'school_report/classroom/homework/survey/statistics.html', context)
    else:
        messages.error(request, "설문대상자 혹은 교사만 열람이 가능합니다.")
        return redirect(request.META.get('HTTP_REFERER', None))
def make_spreadsheet_df(request, posting_id):
    '''응답에 대한 df를 제작.'''
    homework = get_object_or_404(models.Homework, id=posting_id)
    question_list = homework.homeworkquestion_set.order_by('ordering')
    if homework.classroom:  # 지금은 어쩔 수 없이 학교..로 해뒀는데, 나중엔 교실에 속한 경우에도 할 수 있도록... 구성하자.
        school = homework.classroom.school
    elif homework.subject_object:
        school = homework.subject_object.school
    # 제출자 명단.
    submit_list = homework.homeworksubmit_set.all()
    submit_user_list = []
    user_name_list = []
    student_code_list = []
    user_pk_list = []  # ai에 보낼 학생을 선택하기 위해.
    for submit in submit_list:
        try:  # 교사계정도 제출자에 포함하기 위해.
            res_user = models.Student.objects.get(admin=submit.to_user, school=school)
            student_code = res_user.student_code
            user_pk = res_user.admin.id
        except:
            try:
                res_user = models.Teacher.objects.get(admin=submit.to_user, school=school)
                student_code = None
                user_pk = res_user.admin.id
            except:
                continue
        submit_user_list.append(submit.to_user)  # 인덱스가 될 유저.
        try:  # 등록을 안한 학생계정 등이 있을 때 res_user가 None이다.
            user_name_list.append(res_user.name)  # 학생계정 및 선생계정 이름.
            user_pk_list.append(user_pk)  # ai 세특 저장용.
        except:
            user_name_list.append(None)
            user_pk_list.append(None)
        student_code_list.append(student_code)
    # 초기 df 만들기.
    df = pd.DataFrame({'계정': submit_user_list, '제출자': user_name_list, '학번': student_code_list})
    df = df.set_index('계정')  # 인덱스로 만든다.
    df = df[~df.index.duplicated(keep='first')]  # 제출자가 여럿 나와서, 중복자를 제거한다.

    # 질문에 대한 응답 담기.
    for question in question_list:
        answer_list = []
        user_list = []
        answers = models.HomeworkAnswer.objects.filter(question=question,
                                                       to_student=submit.to_student)  # 해당 질문에 대한 답변들 모음.
        for answer in answers:
            answer_list.append(answer.contents)
            user_list.append(answer.respondent)
        df_answers = pd.DataFrame({'계정': user_list, question.question_title: answer_list})
        df_answers = df_answers.set_index('계정')  # 합칠 기준이 될 인덱스 지정.
        df_answers = df_answers[~df_answers.index.duplicated(keep='first')]  # 중복을 제거해보는데.. 이거 언젠가 문제가 될지도;;
        # 행을 df로 만들기.  질문에 따라 하나의 행씩 합치기.
        df = pd.concat([df, df_answers], join='outer', axis=1)
    # df = df.set_index('제출자')
    # df = df.drop('계정', axis=1)
    return df, user_pk_list
@login_required()
def homework_check_spreadsheet(request, classroom_id):
    '''classroom 과제 제출 여부를 한 df로 확인하기 위한 함수.'''
    classroom = get_object_or_404(models.Classroom, id=classroom_id)
    context = {}
    # 관련자만 접근하게끔.
    school = classroom.homeroom.school
    student = check.Check_student(request, school).in_school_and_none()
    teacher = check.Check_teacher(request, school).in_school_and_none()
    if teacher:
        homeroom = classroom.homeroom
        student_list = models.Student.objects.filter(homeroom=homeroom)  # 홈룸에 등록된 학생목록.
        student_list = list(student_list)
        homework_list = models.Homework.objects.filter(classroom=classroom)
        info_dic = {'student':student_list}
        for homework in homework_list:
            info_dic[homework.subject] = []  # 과제명으로 사전key, 리스트 만들기.
            for student in student_list:
                try:  # 동료평가 등 특수설문에서 에러.(과제 부여가 안된 경우에도)
                    submit = models.HomeworkSubmit.objects.get(base_homework=homework, to_user=student.admin)
                    if submit.check:
                        info_dic[homework.subject].append("제출")
                    elif submit.read:
                        info_dic[homework.subject].append("읽음")
                    else:
                        info_dic[homework.subject].append("미열람")
                except:
                    info_dic[homework.subject].append("특수상황")
        print(info_dic)
        df = pd.DataFrame(info_dic)
        df_dict = df.to_dict(orient='records')
        #print(df)
    elif student:  # 학생인 경우.
        homework_list = models.Homework.objects.filter(classroom=classroom)
        info_dic = {'student': student}
        for homework in homework_list:
            info_dic[homework.subject] = []  # 과제명으로 사전key, 리스트 만들기.
            try:
                submit = models.HomeworkSubmit.objects.get(base_homework=homework, to_user=student.admin)
                if submit.check:
                    info_dic[homework.subject].append("제출")
                elif submit.read:
                    info_dic[homework.subject].append("읽음")
            except:  # 동료평가 등 특수설문에서 에러.(과제 부여가 안된 경우에도)
                info_dic[homework.subject].append("특수상황")
        df = pd.DataFrame(info_dic)
        df_dict = df.to_dict(orient='records')

    context['data_list'] = df_dict
    return render(request, 'school_report/classroom/homework/check_spreadsheet.html', context)

@login_required()
def homework_survey_statistics_spreadsheet(request, posting_id):
    # 과거유산. 문제없음 버리자. submit = get_object_or_404(models.HomeworkSubmit, id=submit_id)
    homework = get_object_or_404(models.Homework, id=posting_id)
    context = {'posting':homework}

    df, user_pk_list = make_spreadsheet_df(request, posting_id)
    df = df.to_dict(orient='records')
    if homework.is_special == 'TalentEval':
        question_title = df[0]  # 기존 df의 첫번째 행을 가져온다.
        context['columns'] = question_title
        df = zip(user_pk_list, df)
    context['data_list'] = df

    return render(request, 'school_report/classroom/homework/survey/statistics_spreadsheet.html', context)

@login_required()
def spreadsheet_to_excel_download(request, posting_id):
    df = make_spreadsheet_df(request, posting_id)
    from main.view import df_funcs
    response = df_funcs.df_to_excel_download(df, '설문결과')
    return response
@login_required()
def spreadsheet_upload_excel(request, posting_id):
    homework = get_object_or_404(models.Homework, id=posting_id)
    if request.user == homework.author:
        pass
    else:
        messages.error(request, '과제 작성자만 올릴 수 있습니다.')
        return redirect(request.META.get('HTTP_REFERER', None))

    from main.view import df_funcs
    df = df_funcs.upload_to_df(request.FILES["uploadedFile"])
    if homework.classroom:  # 지금은 어쩔 수 없이 학교..로 해뒀는데, 나중엔 교실에 속한 경우에도 할 수 있도록... 구성하자.
        school = homework.classroom.school
    if homework.subject_object:
        school = homework.subject_object.school

    # 1단계. 질문 목록 호출.
    question_list = []
    for question in df.columns[2:]:
        question = models.HomeworkQuestion.objects.get(homework=homework, question_title=question)
        question_list.append(question)

    # 2단계. df를 읽으며 학생 목록 호출. 및 넣기.
    for index in df.index:
        row = df.loc[index]
        try:
            student = models.Student.objects.get(school=school, student_code=int(row['학번']))
        except:
            messages.error(request, '적절하지 않은 학번의 경우 건너뜁니다. ' + str(row[0]))
            continue
        for question in question_list:
            answer, _ = models.HomeworkAnswer.objects.get_or_create(question=question, respondent=student.admin)
            answer.contents = row[question.question_title]  # 질문의 열에 있는 정보를 담는다.
            answer.save()

    messages.success(request, '업로드 완료!')
    return redirect(request.META.get('HTTP_REFERER', None))



from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
def summit_file_download(request, pk):
    hw_answer = get_object_or_404(models.HomeworkAnswer, pk=pk)
    if hw_answer.file:
        return FileResponse(hw_answer.file, as_attachment=True)
    else:
        raise Http404("File doesn't exist")

def peerreview_create(request, posting_id):
    posting = get_object_or_404(models.Homework, pk=posting_id)  # 과제 찾아오기.
    context = {'posting': posting}  # 어떤 과제의 하위로 만들지 전달하기 위해.
    homeroom = posting.classroom.homeroom  # 학급.
    student_list = models.Student.objects.filter(homeroom=homeroom)
    if request.method == 'POST':
        user_list = request.POST.getlist('user_list')
        try:  # 기존의 설문은 제거한다.
            origin = models.HomeworkSubmit.objects.get(base_homework=posting,
                        to_student=None)
            origin.delete()
        except:  # 없으면 패스.
            pass
        for user in user_list:
            to_student = models.Student.objects.get(pk=user)
            # 학급의 학생들에게 배정.
            for student in student_list:
                submit, _ = models.HomeworkSubmit.objects.get_or_create(base_homework=posting,
                to_student=to_student, to_user=student.admin, title=to_student)
            # 작성자도 대응시킨다.
            submit, _ = models.HomeworkSubmit.objects.get_or_create(base_homework=posting,
            to_student=to_student, to_user=request.user, title=to_student)
        return redirect('school_report:homework_detail', posting_id=posting.id)
    for to_student in student_list:  # 동료평가를 만들 수 있는 학생 목록.
        submit = models.HomeworkSubmit.objects.filter(base_homework=posting ,to_student=to_student).exists()  # 있나 여부만 파악.
        to_student.submit = submit  # 있으면 True
    context['student_list'] = student_list
    return render(request, 'school_report/classroom/homework/survey/special/peerReview_create.html', context)


def peerreview_end(request, posting_id):
    homework = get_object_or_404(models.Homework, pk=posting_id)  # 과제 찾아오기.
    context = {}
    # 과제 제출자인 경우에만 진행한다.
    if request.user == homework.author:
        homework.deadline = datetime.now()  # 현재 시간으로 마감.
        homework.is_end = True
        homework.save()
        question = models.HomeworkQuestion.objects.get(homework=homework, ordering=1)  # 동료평가의 첫번째 질문.

        # 설문자와, 대상자 목록.
        delete_list = models.HomeworkSubmit.objects.filter(base_homework=homework, to_student=None)  # 연습용이라 만들어졌던 설문.
        delete_list.delete()
        # 어째서인지... DB 관련해 뭔가 문제가 있는 듯한데, 연동된 answer가 안지워져.
        # 아.. submit과 answer의 연동을 끊고 answer에서 바로 대상자를 지정해서 그래.
        delete_list = models.HomeworkAnswer.objects.filter(question=question, to_student=None)
        delete_list.delete()

        homework_submits = models.HomeworkSubmit.objects.filter(base_homework=homework)
        to_list = []  # 동료평가 대상자의 목록.
        for submit in homework_submits:
            to_list.append(submit.to_student)
        to_list = set(to_list)  # 중복값 제거.
        user_list = []  # 설문 참여자의 목록.
        for submit in homework_submits:
            user_list.append(submit.to_user)
        user_list = set(user_list)  # 중복값 제거.

        # 필요없을지도. student_mean = {}  # 학생명에 평균을 담을 사전.
        for to_student in to_list:
            # 이건 왜...? question_list = homework.homeworkquestion_set.filter('ordering')
            answers = models.HomeworkAnswer.objects.filter(to_student=to_student, question=question)
            df = pd.DataFrame.from_records(answers.values('contents'))
            if df.empty:
                continue  # df가 비었다면 패스.
            df = df.rename(columns={'contents': 'score'})  # 행이름 바꿔주기.(아래에서 그대로 써먹기 위해)
            df = df.astype({'score': float})
            mean = df.mean(axis=0)[0]  # 평균 구하기.
            for respondent in user_list:  # 평가자 돌며 평균에서 차 담기.
                try:  # 응답 안한 사람이 있으면 answer객체가 없기도 하다.
                    answer = models.HomeworkAnswer.objects.get(respondent=respondent, to_student=to_student, question=question)
                    answer.memo = (float(answer.contents) - mean)**2  # 평균에서의 차, 제곱 담기.
                    answer.save()
                except:
                    pass
        messages.success(request, "계산 완료.")
    return redirect(request.META.get('HTTP_REFERER', None))  # 이전 화면으로 되돌아가기.
        # to_student에 따라 평균 구하고... 사전으로 정리??
def homework_end_cancel(request, homework_id):
    homework = get_object_or_404(models.Homework, pk=homework_id)  # 과제 찾아오기.
    context = {}
    # 과제 제출자인 경우에만 진행한다.
    if request.user == homework.author:
        homework.deadline = None
        homework.is_end = False
        homework.save()
        messages.success(request, "과제 마감을 취소하였습니다.")
    return redirect(request.META.get('HTTP_REFERER', None))  # 이전 화면으로 되돌아가기.
def peerreview_statistics(request, posting_id):
    '''표 형식으로 제시. 최종 통계.'''
    homework = get_object_or_404(models.Homework, pk=posting_id)  # 과제 찾아오기.
    context = {}
    question = models.HomeworkQuestion.objects.get(homework=homework, ordering=1)  # 동료평가용.
    if homework.classroom:  # 지금은 어쩔 수 없이 학교..로 해뒀는데, 나중엔 교실에 속한 경우에도 할 수 있도록... 구성하자.
        school = homework.classroom.school
    elif homework.subject_object:
        school = homework.subject_object.school
    teacher = check.Check_teacher(request, school).in_school_and_none()
    # 제출자 명단.
    submit_list = homework.homeworksubmit_set.all()
    submit_user_list = []  # 설문 참여자.
    user_name_list = []  # 계정이 아니라 학생명, 교사명을 담을 리스트.
    to_list = []  # 동료평가 대상자.

    if teacher:
        for submit in submit_list:
            try:
                res_user = models.Student.objects.get(admin=submit.to_user, school=school)
            except:
                try:
                    res_user = models.Teacher.objects.get(admin=submit.to_user, school=school)
                except:
                    res_user = None
            submit_user_list.append(submit.to_user)  # 인덱스가 될 유저.
            user_name_list.append(res_user)  # 학생계정 및 선생계정 이름. 평가자 목록.
            to_list.append(submit.to_student)  # 동료평가 대상자에 추가.
    else:  # 학생이라면 자기의 결과만 볼 수 있게.
        res_user = models.Student.objects.get(admin=request.user, school=school)
        submit_user_list.append(request.user)
        user_name_list.append(res_user)
        for submit in submit_list:
            to_list.append(submit.to_student)  # 평가대상리스트 만들기.

    given_mean_list = []  # 평가 대상자가 받은 평균값을 담을 리스트.
    mean_list = []  # 각 응답자가 받은 평균값을 담을 리스트.
    var_list = []  # 각 응답자의 평균 오차(분산)를 담을 리스트.
    given_var_list = []  # 평가자가 얼마나 점수를 많이 분포시켰느냐.(무지성으로 한 점수만 찍는 아이들 대비)
    not_res_list = []  # 응답자들이 평가하지 않은 횟수를 담을 리스트.
    to_list = set(to_list)  # 중복값 제거.
    len_to_list = len(to_list)  # 미응답자 계산을 위함.
    special_comment_list = []  # 특별 설문으로 몇 번이나 선정되었는지.
    for respondent in submit_user_list:  # 유저리스트 돌면서 순회.
        if respondent == None:
            continue
        # 본인이 답한 것에 대한 통계.
        answers = models.HomeworkAnswer.objects.filter(question=question,
                                                       respondent=respondent)
        mean = 0
        count = 0
        var = 0
        for answer in answers:
            count += 1
            mean += float(answer.contents)
            var += float(answer.memo)
        try:  # count=0 이면 나누기 에러.
            mean = mean/count
            var = var/count
        except:
            pass
        mean_list.append(mean)
        var_list.append(var)
        not_res_list.append(len_to_list - count)
        # 받은 평균 담기. +특별설문 선정 횟수 계산.
        given_mean = 0
        count = 0
        try:  # 선생님은 학생객체가 없어 애러 뜸.
            to_student = models.Student.objects.get(admin=respondent, school=school)
            answers = models.HomeworkAnswer.objects.filter(question=question, to_student=to_student)
            for answer in answers:
                count += 1
                given_mean += float(answer.contents)
            try:
                given_mean = given_mean / count
            except:
                pass
            special_content = str(to_student.student_code) + to_student.name
            special_count = models.HomeworkSubmit.objects.filter(base_homework=homework, content=special_content).count
        except:
            given_mean = None
            special_count = None
        special_comment_list.append(special_count)
        given_mean_list.append(given_mean)
        # given_var 구하기.
        given_var = 0
        answers = models.HomeworkAnswer.objects.filter(question=question, respondent=respondent)
        for answer in answers:
            given_var += (mean - float(answer.contents)) **2  # 분산.
        try:
            given_var = given_var / count
        except:
            pass
        given_var_list.append(given_var)
    # 초기 df 만들기.
    df = pd.DataFrame({'계정': submit_user_list, '제출자': user_name_list, '받은 평균':given_mean_list,
                       '부여점수 평균':mean_list, '부여분산(무지성 방지)':given_var_list, '평가점수 분산(벗어남정도)':var_list,'미응답 수':not_res_list,
                       '특수댓글 수':special_comment_list})
    df = df.set_index('계정')  # 인덱스로 만든다.
    df = df[~df.index.duplicated(keep='first')]  # 제출자가 여럿 나와서, 중복자를 제거한다.
    context['data_list'] = df.to_dict(orient='records')
    return render(request, 'school_report/classroom/homework/survey/statistics_spreadsheet.html', context)

def peerreview_select_comment(request, submit_id):
    submit = get_object_or_404(models.HomeworkSubmit, pk=submit_id)  # 제출 찾아오기.
    posting = submit.base_homework
    if posting.classroom:  # 지금은 어쩔 수 없이 학교..로 해뒀는데, 나중엔 교실에 속한 경우에도 할 수 있도록... 구성하자.
        school = posting.classroom.school
    if posting.subject_object:
        school = posting.subject_object.school
    to_student = check.Check_student(request, school).in_school_and_none()  # 학생계정 배정.

    if submit.to_user == request.user:#to_student
        pass
    else:
        messages.error(request, '설문의 주인만 선택할 수 있습니다.')
        return redirect(request.META.get('HTTP_REFERER', None))  # 이전 화면으로 되돌아가기.


    answer_key = request.GET.get('content')
    answer = models.HomeworkAnswer.objects.get(to_student=to_student, contents=answer_key)  # 고른 선택지 객체 가져오기.
    respondent_student = models.Student.objects.get(admin=answer.respondent, school=school)
    submit.content = str(respondent_student.student_code) + respondent_student.name  # 선택된 학생계정을 담는다.
    submit.save()
    messages.success(request, '반영하였습니다.')
    return redirect(request.META.get('HTTP_REFERER', None))  # 이전 화면으로 되돌아가기.

def peerreview_who_is_special(request, posting_id):
    '''여기 말고 스프레드시트에 합쳐서 나타내면 계수에 더 좋지 않나?'''
    homework = get_object_or_404(models.Homework, pk=posting_id)
    context = {}
    if homework.classroom:  # 지금은 어쩔 수 없이 학교..로 해뒀는데, 나중엔 교실에 속한 경우에도 할 수 있도록... 구성하자.
        school = homework.classroom.school
    if homework.subject_object:
        school = homework.subject_object.school
    teacher = check.Check_teacher(request, school).in_school_and_none()
    if teacher == None:
        messages.error(request, "학교에 등록된 교사가 아닙니다.")
        return render(request, 'school_report/classroom/create.html', context)

    submits = models.HomeworkSubmit.objects.filter(base_homework=homework)
    df = pd.DataFrame(submits.values('content'))
    value_counts = df['content'].value_counts()
    # Series를 DataFrame으로 변환
    result_df = pd.DataFrame({'학생': value_counts.index, '횟수': value_counts.values})
    # 내림차순으로 정렬
    df = result_df.sort_values(by='횟수', ascending=False)

    df = df.to_dict(orient='records')
    return render(request, 'school_report/classroom/homework/survey/statistics_spreadsheet.html', {'data_list': df})

