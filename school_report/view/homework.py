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

## 편의, 공통 기능들.
# def get_assigned_profile(homework_id):
#     '''해당 과제가 이미 배정된 프로파일 얻기.'''
#     homework = get_object_or_404(models.Homework, pk=homework_id)
#     profile_ids = models.HomeworkSubmit.objects.filter(base_homework=homework).values_list('target_profile', flat=True).distinct()
#     profiles = models.Profile.objects.filter(id__in=profile_ids)
#     return profiles


@login_required()
def create(request, homework_box_id):
    '''room 모델 하위에 과제 배치.'''
    context = {}
    if request.method == 'POST':  # 포스트로 요청이 들어온다면... 글을 올리는 기능.
        homework_box = get_object_or_404(models.HomeworkBox, pk=homework_box_id)
        create_base(request, homework_box)
        return homework_box.redirect_to_upper()
    else:  # 포스트 요청이 아니라면.. form으로 넘겨 내용을 작성하게 한다.
        form = HomeworkForm()
    context['form'] = form  # 폼에서 오류가 있으면 오류의 내용을 담아 create.html로 넘긴다.
    return render(request, 'school_report/classroom/homework/create.html', context)
def create_base(request, homework_box):
    '''교과교실에서 작성. .'''  # 과제 제작에 대한 것만 두자.
    # 프로필 모델을 가져오게끔 구성하자. models.Profile.object.filter(admin=request.user, ) # 학교정보와 같이 있으면 괜찮을 듯한데. box에 학교정보가 같이 있게...?
    school = homework_box.get_school_model()
    profile = models.Profile.objects.filter(admin=request.user, school=school).first()  # 나중에 get으로 바꾸자. 프로필은 인당 1개만 만들게 하고.
    form = HomeworkForm(request.POST)  # 폼을 불러와 내용입력을 받는다.
    if form.is_valid():  # 문제가 없으면 다음으로 진행.
        homework = form.save(commit=False)  # commit=False는 저장을 잠시 미루기 위함.(입력받는 값이 아닌, view에서 다른 값을 지정하기 위해)
        homework.author_profile = profile  # 작성자 프로파일 지정.
        homework.homework_box = homework_box  # 게시판 지정.
        homework.save()
        ### 자동 과제 분배.
        profiles = homework_box.get_profiles()
        for to_profile in profiles:
            individual, created = models.HomeworkSubmit.objects.get_or_create(to_profile=to_profile,
                                                                          base_homework=homework)
@login_required()
def modify(request, posting_id):
    homework = get_object_or_404(models.Homework, pk=posting_id)
    author = homework.author_profile.admin  # 유저모델로 비교.
    if request.user != author:
        messages.error(request, '수정권한이 없습니다')
        return redirect('school_report:homework_detail', posting_id=homework.id)
    if request.method == "POST":
        is_secret = homework.is_secret  # 비밀설문을 다시 공개로 바꿀 수 없게.
        form = HomeworkForm(request.POST, instance=homework)  # 받은 내용을 객체에 담는다. instance에 제대로 된 걸 넣지 않으면 새로운 인스턴스를 만든다.
        if form.is_valid():
            homework = form.save(commit=False)  # commit=False는 저장을 잠시 미루기 위함.(입력받는 값이 아닌, view에서 다른 값을 지정하기 위해)
            if is_secret:
                homework.is_secret = is_secret
            homework.save()
            # 개별 확인을 위한 개별과제 체크 해제.(제출상태 취소)
            submit_list = models.HomeworkSubmit.objects.filter(base_homework=homework)
            for submit in submit_list:
                submit.check = False
                submit.save()
            return redirect('school_report:homework_detail', posting_id=homework.id)
    else:  # GET으로 요청된 경우.
        form = HomeworkForm(instance=homework)  # 해당 모델의 내용을 가져온다!
        # 태그를 문자열화 하여 form과 함께 담는다.
    context = {'form': form}
    messages.error(request, '수정하면 기존 확인한 학생들의 체크는 "읽지않음"으로 갱신됩니다.')
    return render(request, 'school_report/classroom/homework/create.html', context)
@login_required()
def detail(request, posting_id):
    '''과제 상세페이지와 과제제출 기능.'''
    context = {}
    homework = get_object_or_404(models.Homework, pk=posting_id)
    context['posting'] = homework

    # 주어진 과제 보여지기. 아마 과거의 흔적인듯.
    # individual_announcement = []  # 주어진 과제를 담을 공간.
    # sumbits = models.HomeworkSubmit.objects.filter(to_user=request.user, base_homework=homework)
    # for submit in sumbits:
    #     submit.read = True
    #     submit.save()
    #     individual_announcement.append(submit)
    # context['individual_announcement'] = individual_announcement

    # 학생과 교사 가르기.
    school = homework.homework_box.get_school_model()
    profile = models.Profile.objects.filter(admin=request.user, school=school).first()  # 나중에 정돈이 되면 filter가 아니라 get으로 바꾸자. 25년엔 괜찮을듯.
    #student = check.Check_student(request, school).in_school_and_none()
    #teacher = check.Check_teacher(request, school).in_school_and_none()
    # 교사라면 모든 설문관련 정보를 볼 수 있다.
    if homework.author_profile.admin == request.user:
        submit_list = models.HomeworkSubmit.objects.filter(base_homework=homework)
        context['submit_list'] = submit_list

    context['survey'] = homework.homeworkquestion_set.exists()  # 설문객체 여부.

    # 개인 과제에 대해
    private_submits = models.HomeworkSubmit.objects.filter(base_homework=homework, to_profile=profile)
    for private_submit in private_submits:  # 동료평가 등 여러 과제일 수 있음.
        private_submit.read = True
        private_submit.save()
    context['private_submits'] = private_submits  # 열람자의 정보 담기.

    # 동료평가에서의 기능.
    if homework.is_special == 'peerReview':  # 동료평가의 경우, 지금 부여한 평균 보여주기.
        # 평가 관련 데이터.
        try:  # 평가한 게 없으면 df가 None이 됨.
            question = models.HomeworkQuestion.objects.get(homework=homework, ordering=1)  # 동료평가의 첫번째 질문.
            answers = models.HomeworkAnswer.objects.filter(respondent=request.user, question=question)  # 내가 부여한 것.
            df = pd.DataFrame.from_records(answers.values('contents'))
            df['contents'] = pd.to_numeric(df['contents'], errors='coerce')
            score_mean = df['contents'].mean()
            variance = df['contents'].organization()
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
@login_required()
def delete(request, posting_id):
    homework = get_object_or_404(models.Homework, pk=posting_id)
    if request.user != homework.author_profile.admin:
        messages.error(request, '삭제권한이 없습니다. 꼼수쓰지 마라;')
        return redirect(request.META.get('HTTP_REFERER', None))  # 이전 화면으로 되돌아가기.
    homework.delete()
    messages.success(request, '삭제 성공~!')
    homework_box = homework.homework_box
    return homework_box.redirect_to_upper()  # box를 소유한 상위객체로 리다이렉트.
def survey_create(request, posting_id):
    '''설문의 수정도 이곳에서 처리.'''
    homework = get_object_or_404(models.Homework, pk=posting_id)  # 과제 찾아오기.
    context = {'posting': homework}

    if request.method == 'POST':  # 포스트로 요청이 들어온다면... 글을 올리는 기능.
        if homework.author_profile.admin == request.user:  # 과제의 주인인 경우에만 가능.
            previous_question = list(homework.homeworkquestion_set.all())  # 기존에 등록되어 있던 질문들. list로 불러야 현재 상황 반영.
            question_type = request.POST.getlist('question_type')
            is_essential = request.POST.getlist('is_essential')
            is_special = request.POST.getlist('is_special')
            question_title = request.POST.getlist('question_title')
            question_id = request.POST.getlist('question_id')
            for i in range(len(question_type)):  # 질문 갯수만큼 순회.
                j = i+1
                try:  # 만들어진 것 같다면 불러와본다.
                    question = models.HomeworkQuestion.objects.get(pk=question_id[i])
                    if question.homework != homework:  # 기존 질문이 상위과제와 일치하지 않는다면 부정접근.
                        messages.error(request,'부정접근')
                        return redirect('school_report:homework_detail', posting_id=homework.id)
                    if question in previous_question:  # 기존 질문에 있던 거라면
                        previous_question.remove(question)  # 리스트에서 제거.
                    question.question_title = question_title[i]
                except:  # 없다면 새로 만들기.
                    question = models.HomeworkQuestion.objects.create(homework=homework, question_title=question_title[i])
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
        return redirect('school_report:homework_detail', posting_id=homework.id)
    question_list = homework.homeworkquestion_set.all()
    question_list = question_list.order_by('ordering')  # 주어진 순서대로 정렬.
    context['question_list'] = question_list
    for question in question_list:  # option값을 탬플릿에 전달하기 위함.
        if question.options:
            question.options = json.loads(question.options)  # 리스트화+저장하지 않고 옵션에 리스트 부여.(이게 되네?!)
    return render(request, 'school_report/classroom/homework/survey/create.html', context)
@login_required()
def survey_submit(request, submit_id):
    '''submit_id는 개별 아이디니... 설문 자체에 접근하게끔 하는 방략을 생각해야 할듯. 설문 ID를 주고..?
    설문 자체에 대한 링크는 주지 않는 게 좋을듯.'''
    '''사용자의 설문 제출.'''
    submit = get_object_or_404(models.HomeworkSubmit, pk=submit_id)  # 과제 찾아오기.
    homework = submit.base_homework
    # 제출기한이 지났다면 제출되지 않도록.
    if homework.deadline:
        import pytz  # 타임존이 안맞아 if에서 대소비교가 안되어 처리.
        deadline = homework.deadline.astimezone(pytz.UTC)
        if deadline < datetime.now(pytz.UTC) or homework.is_end:  # 데드라인이 지났다면... 안되지.
            messages.error(request, "이미 제출기한이 지난 과제입니다.")
            return redirect(request.META.get('HTTP_REFERER', None))  # 이전 화면으로 되돌아가기.

    context = {'posting': homework, 'submit':submit}
    # 설문 정보 불러오기.
    question_list = homework.homeworkquestion_set.all().order_by('ordering')
    for question in question_list:  # option값을 탬플릿에 전달하기 위함.
        if question.options:
            question.options = json.loads(question.options)  # 리스트화+저장하지 않고 옵션에 리스트 부여.(이게 되네?!)

    # 본인의 설문인지 검사.
    if submit.to_profile.admin == request.user:
        pass
    else:
        messages.error(request, '다른 사람의 응답을 할 수는 없어요~')
        return redirect('school_report:homework_detail', posting_id=homework.id)

    if request.method == 'POST':  # 포스트로 요청이 들어온다면... 글을 올리는 기능.
        for question_id in request.POST.getlist('question'):
            question = models.HomeworkQuestion.objects.get(pk=question_id)
            if question.homework != homework:  # 부정접근 방지.
                return redirect('school_report:homework_detail', posting_id=homework.id)
            answer,_ = models.HomeworkAnswer.objects.get_or_create(question=question, to_profile=submit.to_profile)
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
        return redirect('school_report:homework_detail', posting_id=homework.id)

    for question in question_list:
        try:  # 연동된 제출의 응답 가져오기.
            answer = models.HomeworkAnswer.objects.get(question=question, to_profile=submit.to_profile)
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
def survey_statistics(request, submit_id):
    '''과제 통계 제시.'''
    submit = models.HomeworkSubmit.objects.get(id=submit_id)
    homework = submit.base_homework
    question_list = homework.homeworkquestion_set.order_by('ordering')
    context = {}
    school = homework.homework_box.get_school_model()
    teacher = check.Teacher(user=request.user, school=school).in_school_and_none()  # 교사라면 교사객체가 반환됨. 교과 뿐 아니라 학교, 학급 등에서도 일관적으로 작동할 수 있게 해야 할텐데...

    if submit.to_profile.admin == request.user or teacher:  # 설문대상학생이거나 교사. 자기만 볼 수 있게.
        if not teacher and homework.is_secret_student:
            messages.error(request, '학생들에겐 비공개 되어 있습니다.')
            return redirect(request.META.get('HTTP_REFERER', None))
        question_list = question_list_statistics(question_list, submit)  # question_list 의 info에 정보를 담아 반환한다.
        context['question_list'] = question_list
        context['submit'] = submit  # 동료평가에서 특별한 댓글 선택하기에서.
        return render(request, 'school_report/classroom/homework/survey/statistics.html', context)
    else:
        messages.error(request, "설문대상자 혹은 교사만 열람이 가능합니다.")
        return redirect(request.META.get('HTTP_REFERER', None))
def question_list_statistics(question_list, submit):
    '''question_list를 받아 실질적인 통계를 내고 다시 반환.'''
    for question in question_list:
        answers = models.HomeworkAnswer.objects.filter(question=question, to_profile=submit.to_profile)
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
def below_standard_set(request, submit_id):
    '''수준미달 과제 지정.'''
    submit = models.HomeworkSubmit.objects.get(id=submit_id)
    submit.state = '수준미달'
    submit.save()
    messages.success(request, '지정하였습니다.')
    return redirect(request.META.get('HTTP_REFERER', None))  # 이전 화면으로 되돌아가기.
def below_standard_unset(request, submit_id):
    submit = models.HomeworkSubmit.objects.get(id=submit_id)
    submit.state = None
    submit.save()
    messages.success(request, '해제하였습니다.')
    return redirect(request.META.get('HTTP_REFERER', None))  # 이전 화면으로 되돌아가기.

## 동료평가.


def copy(request, homework_id):
    homework = models.Homework.objects.get(id=homework_id)
    context = {}
    admin = homework.author_profile.admin
    if request.method == 'POST':
        classroom_list = request.POST.getlist('classroom_list')
        subject_list = request.POST.getlist('subject_list')
        # 여기부터 복사과정
        copied = homework.copy_create(classroom_list=classroom_list, subject_list=subject_list)
        ### 자동 과제 분배.
        type, id = copied.homework_box.type()
        if type != 'school':  # 학교객체가 아니라면 자동으로 하위에 과제 부여.
            profiles = copied.homework_box.get_profiles()
            for to_profile in profiles:
                individual, created = models.HomeworkSubmit.objects.get_or_create(to_profile=to_profile,
                                                                              base_homework=copied)
        return redirect('school_report:homework_detail', copied.id)
    # 사용자가 관리하는 객체를 보이기 위한 사전작업.
    homework_box = homework.homework_box
    school = homework_box.get_school_model()
    # 사용자가 관리하는 객체들을 보여준다.
    admin_profile = models.Profile.objects.get(admin=admin, school=school)
    subject_list = models.Subject.objects.filter(master_profile=admin_profile, school=school)
    subject_ids = [subject.id for subject in subject_list]
    classroom_list = models.Classroom.objects.filter(base_subject__id__in=subject_ids)
    context['classroom_list'] = classroom_list
    context['subject_list'] = subject_list

    return render(request, 'school_report/classroom/homework/copy.html', context)
#    return redirect('school_report:homework_detail', posting_id=submit.base_homework.id)

def distribution(request, homework_id):  # [profile로 바꾸자.]
    # 개별 확인을 위한 개별과제 생성.
    # 개별 부여할 사람을 탬플릿에서 받는 것도 괜찮을듯...? 흠... []
    homework = get_object_or_404(models.Homework, pk=homework_id)
    homework_box = homework.homework_box
    context = {}
    # post로 들어오면 배정.
    if request.method == 'POST':
        profile_ids = request.POST.getlist('profile_ids')
        for profile_id in profile_ids:
            to_profile = models.Profile.objects.get(id=profile_id)
            individual, created = models.HomeworkSubmit.objects.get_or_create(to_profile=to_profile, base_homework=homework)
        return redirect('school_report:homework_detail', posting_id=homework.id)

    # 추가 부여 가능 대상자 찾기.
    submits = models.HomeworkSubmit.objects.filter(base_homework=homework)
    submit_profile_ids = [submit.to_profile.id for submit in submits]
    available_profile_ids = homework_box.get_profiles_id()
    teacher_id = homework.author_profile.values_list('id', flat=True)
    available_profile_ids.union(teacher_id)  # 교사 프로필의 id도 추가.
    filtered_available_profile_ids = [profile_id for profile_id in available_profile_ids if profile_id not in submit_profile_ids]
    filtered_profiles = models.Profile.objects.filter(id__in=filtered_available_profile_ids)
    context['filtered_profiles'] = filtered_profiles

    return render(request, 'school_report/classroom/homework/homework_distribution.html', context)