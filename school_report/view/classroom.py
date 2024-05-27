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
from school_report.view import homework
import random
@login_required()
def create(request, school_id):
    '''교과와 학급이 만들어진 상태에서 교과를 학급에 배정.'''
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
        # teacher = check.Check_teacher(request, school).in_school_and_none()  # 옛날에. 선생모델.
        check_teacher = check.Teacher(user=request.user, school=school, request=request)
        profile = check_teacher.in_school()
        if profile == None:
            return check_teacher.redirect_to_school()
        #form = ClassroomForm(request.POST)  # 폼을 불러와 내용입력을 받는다.
        #if form.is_valid():  # 문제가 없으면 다음으로 진행.
        homeroom_list = request.POST.getlist('homeroom_list')
        for homeroom_id in homeroom_list:  # 받은 데이터에 해당하는 걸 넣는다.
            homeroom = get_object_or_404(models.Homeroom, pk=homeroom_id)
            classroom, _ = models.Classroom.objects.get_or_create(base_subject=subject, school=school, homeroom=homeroom)
            homework_box, created = models.HomeworkBox.objects.get_or_create(classroom=classroom)
            announce_box, created = models.AnnounceBox.objects.get_or_create(classroom=classroom)
        return redirect('school_report:subject_main', subject_id=subject.id)  # 작성이 끝나면 작성한 글로 보낸다.
    else:  # 포스트 요청이 아니라면.. form으로 넘겨 내용을 작성하게 한다.
        #form = ClassroomForm()
        pass
    #context['form'] = form  # 폼에서 오류가 있으면 오류의 내용을 담아 create.html로 넘긴다.
    return render(request, 'school_report/classroom/create.html', context)
def main(request, classroom_id):
    classroom = get_object_or_404(models.Classroom, pk=classroom_id)
    context ={'classroom': classroom}
    # 선생님, 혹은 학생객체 가져오기.
    context['student'] = check.Student(request=request, user=request.user,
                                                classroom=classroom).in_homeroom_and_none()
    context['teacher'] = check.Teacher(request=request, user=request.user,
                                                school=classroom.school).in_school_and_none()  # 선생님객체.
    # 교과과제목록.
    homework_box = classroom.base_subject.homeworkbox
    subject_homework_list = homework_box.homework_set.order_by('-create_date')
    #subject_homework_list = classroom.base_subject.homework_set.order_by('-create_date')
    context['subject_homework_list'] = subject_homework_list
    # 교실과제목록.
    homework_box = classroom.homeworkbox
    homework_list = homework_box.homework_set.order_by('-create_date')
    context['homework_list'] = homework_list
    return render(request, 'school_report/classroom/main.html', context)

# @login_required()
# def homework_create(request, classroom_id):# homework에 box_id 보내면서 없애도 될듯.
#     classroom = get_object_or_404(models.Classroom, pk=classroom_id)
#     homework_box = models.HomeworkBox.objects.get(classroom=classroom)
#     return homework.create(request, homework_box_id=homework_box.id)
# def homework_modify(request, posting_id):
#     # 별 기능이 없다면... 고쳐보자 언젠가. 근데 혹시나 쓸 일이 있을지도 모르니. # 지금은 안씀. url 우회해두었으니. 안쓰면 과감하게 지워버리자.
#     return homework.modify(request, posting_id)
# @login_required()
# def homework_detail(request, posting_id):
#     return homework.detail(request, posting_id)

########### 이것도 안쓰는 기능 아닌감?
def homework_resubmit(request, submit_id):
    submit = get_object_or_404(models.HomeworkSubmit, pk=submit_id)
    submit.check = False
    submit.save()
    return redirect('school_report:homework_detail', posting_id=submit.base_homework.id)
# def homework_copy(request, homework_id):
#     homework = models.Homework.objects.get(id=homework_id)
#     context = {}
#     admin = homework.author
#     if request.method == 'POST':
#         print('포스트 들어옴.')
#         classroom_list = request.POST.getlist('classroom_list')
#         subject_list = request.POST.getlist('subject_list')
#         print(classroom_list)
#         print(subject_list)
#         # 여기부터 복사과정
#         copied = homework.copy_create(classroom_list=classroom_list, subject_list=subject_list)
#         return redirect('school_report:homework_detail', copied.id)
#     # 사용자가 관리하는 객체를 보이기 위한 사전작업.
#     if homework.school:
#         school = homework.school
#     elif homework.subject_object:
#         school = homework.subject_object.school
#     elif homework.classroom:
#         school = homework.classroom.school
#     # 사용자가 관리하는 객체들을 보여준다.
#     admin_teacher = models.Teacher.objects.get(admin=admin, school=school)
#     classroom_list = models.Classroom.objects.filter(master=admin_teacher, school=school)
#     subject_list = models.Subject.objects.filter(master=admin_teacher, school=school)
#     context['classroom_list'] = classroom_list
#     context['subject_list'] = subject_list
#
#     return render(request, 'school_report/classroom/homework/copy.html', context)
# #    return redirect('school_report:homework_detail', posting_id=submit.base_homework.id)




def homework_survey_list(request, posting_id):
    '''특수설문 지정.'''
    posting = get_object_or_404(models.Homework, pk=posting_id)  # 과제 찾아오기.
    context = {'posting': posting}  # 어떤 과제의 하위로 만들지 전달하기 위해.
    if request.method == 'POST':  # 포스트로 요청이 들어온다면... 글을 올리는 기능.
        surveyType = request.POST.get('surveyType')
        posting.is_special = surveyType
        if surveyType == "None":  # 일반설문은 None.
            posting.is_special = None
            return posting.to_homework()
        posting.save()  # 특수설문 타입 저장.
        context['surveyType'] = surveyType  # 폼의 hidden에 담기 위해 전달.
        address = 'school_report/classroom/homework/survey/special/' + str(surveyType) + '.html'
        return render(request, address, context)
    return render(request, 'school_report/classroom/homework/survey/special/list.html', context)





def make_spreadsheet_df(request, posting_id):
    '''응답에 대한 df를 제작.'''
    homework = get_object_or_404(models.Homework, id=posting_id)
    question_list = homework.homeworkquestion_set.order_by('ordering')
    box = homework.homework_box
    school = box.get_school_model()
    # 1if homework.classroom:  # 지금은 어쩔 수 없이 학교..로 해뒀는데, 나중엔 교실에 속한 경우에도 할 수 있도록... 구성하자.
    #     school = homework.classroom.school
    # elif homework.subject_object:
    #     school = homework.subject_object.school

    # 제출자 명단.
    submit_list = homework.homeworksubmit_set.all()
    submit_profile_list = []
    user_name_list = []
    code_list = []
    user_pk_list = []  # ai에 보낼 학생을 선택하기 위해.
    for submit in submit_list:
        # try:  # 교사계정도 제출자에 포함하기 위해.
        profile = submit.to_profile
        # res_user = models.Profile.objects.get(admin=submit.to_user, school=school)
        student_code = profile.code
        # user_pk = res_user.admin.id
        # except:
        #     try:
        #         res_user = models.Teacher.objects.get(admin=submit.to_user, school=school)
        #         student_code = None
        #         user_pk = res_user.admin.id
        #     except:
        #         student_code = None  # res_user 없을 때에도 담게끔.
        # 각 열 제작.
        # try:  # 등록을 안한 학생계정 등이 있을 때 res_user가 None이다.
        #     if res_user.name and user_pk and submit.to_user:
        #         user_name_list.append(res_user.name)  # 학생계정 및 선생계정 이름.
        #         user_pk_list.append(user_pk)  # ai 세특 저장용.
        #         submit_profile_list.append(submit.to_user)  # 인덱스가 될 유저.
        # except:
        #     user_name_list.append(None)
        #     user_pk_list.append(None)
        #     submit_profile_list.append(None)
        # student_code_list.append(student_code)
        submit_profile_list.append(profile)
        user_name_list.append(profile.name)
        code_list.append(profile.code)
    # 초기 df 만들기.
    df = pd.DataFrame({'프로필': submit_profile_list, '제출자': user_name_list, '학번': code_list})
    df = df.set_index('프로필')  # 인덱스로 만든다.
    df = df[~df.index.duplicated(keep='first')]  # 제출자가 여럿 나와서, 중복자를 제거한다.

    # 질문에 대한 응답 담기.
    for question in question_list:
        answer_list = []
        user_list = []
        answers = models.HomeworkAnswer.objects.filter(question=question,
                                                       target_profile=submit.target_profile)  # 해당 질문에 대한 답변들 모음.
        for answer in answers:
            answer_list.append(answer.contents)
            user_list.append(answer.to_profile)
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
    student = check.Student(request, school).in_school_and_none()
    teacher = check.Teacher(request, school).in_school_and_none()
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
    df, user_pk_list = make_spreadsheet_df(request, posting_id)
    from main.view import df_funcs
    response = df_funcs.df_to_excel_download(df, '설문결과')
    return response
@login_required()
def spreadsheet_upload_excel(request, posting_id):
    homework = get_object_or_404(models.Homework, id=posting_id)
    if request.user == homework.author_profile.admin:
        pass
    else:
        messages.error(request, '과제 작성자만 올릴 수 있습니다.')
        return redirect(request.META.get('HTTP_REFERER', None))

    from main.view import df_funcs
    df = df_funcs.upload_to_df(request.FILES["uploadedFile"])
    school = homework.get_school_model()

    # 1단계. 질문 목록 호출.
    question_list = []
    i = 0
    for question_title in df.columns[2:]:
        i += 1
        question, _ = models.HomeworkQuestion.objects.get_or_create(homework=homework, ordering=i)
        question.question_title = question_title
        question.question_type = 'long'
        question.save()
        question_list.append(question)

    # 2단계. df를 읽으며 학생 목록 호출. 및 넣기.
    for index in df.index:
        row = df.loc[index]
        try:
            student = models.Profile.objects.get(school=school, code=int(row['학번']))
        except:
            messages.error(request, '적절하지 않은 학번의 경우 건너뜁니다. ' + str(row[0]))
            continue
        for question_title, question in zip(df.columns[2:], question_list):
            answer, _ = models.HomeworkAnswer.objects.get_or_create(question=question, to_profile=student)
            answer.contents = row[question_title]  # 질문의 열에 있는 정보를 담는다.
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
    homework = get_object_or_404(models.Homework, pk=posting_id)  # 과제 찾아오기.
    context = {'posting': homework}  # 어떤 과제의 하위로 만들지 전달하기 위해.

    # 과제에 속한 학생 목록 얻기.(동료평가 지정 대상자를 설정함, POST에서 단체에 해당하는 학생에게 과제를 부여하기 위해.)
    box = homework.homework_box
    type, id = box.type()
    student_list = box.get_profiles()

    # 제출한다면.
    if request.method == 'POST':
        target_list = request.POST.getlist('user_list')
        all_random = request.POST.getlist('all_random')
        ## 이 설문을 포함해서 계산이 되기도 하니까, 연습은 그때그때 지우는 게 좋다.
        try:  # 기존의 설문은 제거한다.
            origins = models.HomeworkSubmit.objects.filter(base_homework=homework, target_profile=None)
            for origin in origins:
                origin.delete()
        except:  # 없으면 패스.
            pass
        if all_random:  # 랜덤으로 들어온 경우.
            target_list = list(box.get_profiles_id())
        # 위에서부터 리스트를 받아 생성 및 배정.
        random.shuffle(target_list)  # 리스트 자체, 내부에서 섞음.
        teacher_profile = models.Profile.objects.get(school=box.get_school_model(), admin=request.user)  # 교사 대응용.
        for target in target_list:
            target_profile = models.Profile.objects.get(pk=target)
            # 학급의 학생들에게 배정.
            for to_profile in student_list:
                submit, _ = models.HomeworkSubmit.objects.get_or_create(base_homework=homework,
                target_profile=target_profile, to_profile=to_profile, title=target_profile)
            # 작성자도 대응시킨다.(확인용, 교사 채점용.)
            submit, _ = models.HomeworkSubmit.objects.get_or_create(base_homework=homework,
            target_profile=target_profile, to_profile=teacher_profile, title=target_profile)
        return redirect('school_report:homework_detail', posting_id=homework.id)


    for to_student in student_list:  # 동료평가를 만들 수 있는 학생 목록.
        submit = models.HomeworkSubmit.objects.filter(base_homework=homework ,target_profile=to_student).exists()  # 있나 여부만 파악.
        to_student.submit = submit  # 있으면 True
    context['student_list'] = student_list
    return render(request, 'school_report/classroom/homework/survey/special/peerReview_create.html', context)


def peerreview_end(request, posting_id):
    homework = get_object_or_404(models.Homework, pk=posting_id)  # 과제 찾아오기.
    context = {}
    # 과제 제출자인 경우에만 진행한다.
    if request.user == homework.author_profile.admin:
        homework.deadline = datetime.now()  # 현재 시간으로 마감.
        homework.is_end = True
        homework.save()
        question = models.HomeworkQuestion.objects.get(homework=homework, ordering=1)  # 동료평가의 첫번째 질문.

        # 연습용 submit, answer 지우기.
        delete_list = models.HomeworkSubmit.objects.filter(base_homework=homework, target_profile=None)  # 연습용이라 만들어졌던 설문.
        delete_list.delete()
        # 어째서인지... DB 관련해 뭔가 문제가 있는 듯한데, 연동된 answer가 안지워져.
        # 아.. submit과 answer의 연동을 끊고 answer에서 바로 대상자를 지정해서 그래.
        delete_list = models.HomeworkAnswer.objects.filter(question=question, target_profile=None)
        delete_list.delete()

        homework_submits = models.HomeworkSubmit.objects.filter(base_homework=homework)
        target_list = []  # 동료평가 대상자의 목록.
        for submit in homework_submits:
            target_list.append(submit.target_profile)
        target_list = set(target_list)  # 중복값 제거.
        user_list = []  # 설문 참여자의 목록.
        for submit in homework_submits:
            user_list.append(submit.to_profile)
        user_list = set(user_list)  # 중복값 제거.

        # 필요없을지도. student_mean = {}  # 학생명에 평균을 담을 사전.
        for target_profile in target_list:
            # 이건 왜...? question_list = homework.homeworkquestion_set.filter('ordering')
            answers = models.HomeworkAnswer.objects.filter(target_profile=target_profile, question=question)
            df = pd.DataFrame.from_records(answers.values('contents'))
            if df.empty:
                continue  # df가 비었다면 패스.
            df = df.rename(columns={'contents': 'score'})  # 행이름 바꿔주기.(아래에서 그대로 써먹기 위해)
            df = df.astype({'score': float})
            mean = df.mean(axis=0)[0]  # 타겟의 평균 구하기.
            for respondent in user_list:  # 평가자 돌며 평균에서 차 담기.
                try:  # 응답 안한 사람이 있으면 answer객체가 없기도 하다.
                    answer = models.HomeworkAnswer.objects.get(to_profile=respondent, target_profile=target_profile, question=question)
                    answer.memo = (float(answer.contents) - mean)**2  # 평균에서의 차, 제곱 담기.
                    answer.save()
                except Exception as e:
                    print(e)
        messages.success(request, "계산 완료.")
    return redirect(request.META.get('HTTP_REFERER', None))  # 이전 화면으로 되돌아가기.
        # to_student에 따라 평균 구하고... 사전으로 정리??
def homework_end(request, homework_id):
    homework = get_object_or_404(models.Homework, pk=homework_id)  # 과제 찾아오기.
    # 과제 제출자인 경우에만 진행한다.
    if request.user == homework.author:
        homework.deadline = datetime.now()
        homework.is_end = True
        homework.save()
        messages.success(request, "과제를 현 시간으로 마감하였습니다.")
    return redirect(request.META.get('HTTP_REFERER', None))  # 이전 화면으로 되돌아가기.
def homework_end_cancel(request, homework_id):
    homework = get_object_or_404(models.Homework, pk=homework_id)  # 과제 찾아오기.
    context = {}
    # 과제 제출자인 경우에만 진행한다.
    if request.user == homework.author_profile.admin:
        homework.deadline = None
        homework.is_end = False
        homework.save()
        messages.success(request, "과제 마감을 취소하였습니다.")
    return redirect(request.META.get('HTTP_REFERER', None))  # 이전 화면으로 되돌아가기.
def peerreview_statistics(request, posting_id):
    '''표 형식으로 제시. 최종 통계.'''
    homework = get_object_or_404(models.Homework, pk=posting_id)  # 과제 찾아오기.
    context = {}
    question = models.HomeworkQuestion.objects.get(homework=homework, ordering=1)  # 동료평가용. 첫번째 질문.
    box = homework.homework_box
    school = box.get_school_model()
    teacher = check.Teacher(user=request.user, school=school).in_school_and_none()
    # 제출자 명단.
    submit_list = homework.homeworksubmit_set.all()
    submit_profile_list = []  # 설문 참여자.
    user_name_list = []  # 계정이 아니라 학생명, 교사명을 담을 리스트.
    to_list = []  # 동료평가 대상자.

    if teacher:
        for submit in submit_list:
            profile = submit.to_profile
            submit_profile_list.append(profile)  # 프로파일 순환하여 연산.
            user_name_list.append(str(profile.code)+profile.name)  # 학생계정 및 선생계정 이름. 평가자 목록.
            to_list.append(submit.target_profile)  # 동료평가 대상자에 추가.
    else:  # 학생이라면 자기의 결과만 볼 수 있게.
        profile = models.Profile.objects.get(admin=request.user, school=school)
        submit_profile_list.append(profile)  # 인덱스가 될 유저.
        user_name_list.append(str(profile.code)+profile.name)
        for submit in submit_list:
            to_list.append(submit.target_profile)  # 평가대상리스트 만들기.

    given_mean_list = []  # 평가 대상자가 받은 평균값을 담을 리스트.
    give_mean_list = []  # 부여한 평균값을 담을 리스트.
    give_var_list = []  # 평가자가 얼마나 점수를 많이 분포시켰느냐.(무지성으로 한 점수만 찍는 아이들 대비)
    verification_var_list = []  # 각 응답자가 부여한 평균 오차(분산)를 담을 리스트.
    not_res_list = []  # 응답자들이 평가하지 않은 횟수를 담을 리스트.
    to_list = set(to_list)  # 중복값 제거. 평가대상 리스트.
    len_to_list = len(to_list)  # 미응답자 계산을 위함.
    special_comment_list = []  # 특별 설문으로 몇 번이나 선정되었는지.
    for respondent in submit_profile_list:  # 유저리스트 돌면서 순회.
        if respondent == None:
            continue
        # 본인이 답한 것에 대한 통계.
        try:  # answer이 빈 경우엔 에러가 난다.
            answers = models.HomeworkAnswer.objects.filter(to_profile=respondent, question=question)  # 내가 부여한 것.
            df = pd.DataFrame.from_records(answers.values('contents'))
            df['contents'] = pd.to_numeric(df['contents'], errors='coerce')
            give_mean = df['contents'].mean()
            give_var = df['contents'].var()
            # 위 코드로 대체함.
            # answers = models.HomeworkAnswer.objects.filter(question=question,
            #                                                to_profile=respondent)
            # 점수를 얼마나 잘 부여했는가에 대한 지표 구하기.
            squere_sum = 0
            count = 0
            for answer in answers:
                count += 1
                squere_sum += float(answer.memo)
            try:  # count=0 이면 나누기 에러.
                verification_var = squere_sum/count  # 친구에게 부여한 점수가 얼마나 잘못되었는지에 대한 지표.
            except:
                pass
        except:  # 응답이 없는 경우.
            give_mean, give_var, verification_var = None, None, None
            count = 0
        give_mean_list.append(give_mean)
        give_var_list.append(give_var)
        not_res_list.append(len_to_list - count)
        verification_var_list.append(verification_var)
        # 위 주석 위 코드로 대체됨.
        # 부여한 것에 대한 var 구하기. 위의 평균을 구하고 진행되어야 해서 다시 sql 호출.
        # give_var = 0
        # answers = models.HomeworkAnswer.objects.filter(question=question, to_profile=respondent)
        # for answer in answers:
        #     give_var += (give_mean - float(answer.contents)) ** 2  # 분산.
        # try:
        #     give_var = give_var / count
        # except:
        #     pass
        # give_var_list.append(give_var)


        # 받은 평균 담기.
        # given_mean = 0
        # count = 0
        try:  # answer이 빈 경우엔 에러가 난다.
            answers = models.HomeworkAnswer.objects.filter(question=question, target_profile=respondent)
            df = pd.DataFrame.from_records(answers.values('contents'))
            df['contents'] = pd.to_numeric(df['contents'], errors='coerce')
            given_mean = df['contents'].mean()
            # # 위 코드로 대체됨.
            # for answer in answers:
            #     count += 1
            #     given_mean += float(answer.contents)
            # try:  # count =0 인 경우가 있음.
            #     given_mean = given_mean / count
            # except:
            #     given_mean = None
        except:
            given_mean = None
        given_mean_list.append(given_mean)

        # 특수댓글 카운트.
        special_content = str(respondent.code) + respondent.name
        special_count = models.HomeworkSubmit.objects.filter(base_homework=homework, content=special_content).count
        #special_count = None
        special_comment_list.append(special_count)
    # 초기 df 만들기.
    df = pd.DataFrame({'프로필': submit_profile_list, '제출자': user_name_list, '받은 평균':given_mean_list,
                       '부여점수 평균':give_mean_list, '부여한 점수의 분산(무지성 방지)':give_var_list, '평가한 점수가 받은 분산(평가의 벗어남정도)':verification_var_list,'미응답 수':not_res_list,
                       '특수댓글 수':special_comment_list})
    df = df.sort_values(by='제출자', ascending=True)
    df = df.set_index('프로필')  # 인덱스로 만든다.
    df = df[~df.index.duplicated(keep='first')]  # 제출자가 여럿 나와서, 중복자를 제거한다.
    context['data_list'] = df.to_dict(orient='records')
    return render(request, 'school_report/classroom/homework/survey/statistics_spreadsheet.html', context)

def peerreview_select_comment(request, submit_id):
    submit = get_object_or_404(models.HomeworkSubmit, pk=submit_id)  # 제출 찾아오기.
    posting = submit.base_homework
    homework_box = posting.homework_box
    school = homework_box.get_school_model()
    student = check.Student(user=request.user, school=school).in_school_and_none()  # 학생계정 배정.

    if submit.to_profile.admin == request.user:  #to_student
        pass
    else:
        messages.error(request, '설문의 주인만 선택할 수 있습니다.')
        return redirect(request.META.get('HTTP_REFERER', None))  # 이전 화면으로 되돌아가기.


    answer_key = request.GET.get('content')
    answer = models.HomeworkAnswer.objects.get(target_profile=student, contents=answer_key)  # 고른 선택지 객체 가져오기.
    respondent_student = answer.to_profile
    #respondent_student = models.Student.objects.get(admin=answer.to_profile, school=school)
    submit.content = str(respondent_student.code) + respondent_student.name  # 선택된 학생계정을 담는다.
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
    teacher = check.Teacher(request, school).in_school_and_none()
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

