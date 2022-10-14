from django.contrib.auth.decorators import login_required #로그인이 있어야 가능함
from django.shortcuts import render, get_object_or_404, redirect, resolve_url, HttpResponse
import json
from django.utils import timezone  # 시간입력을 위해.
from _datetime import datetime,timedelta  # 시간데이터 활용을 위해
from django.contrib import messages  # 넌필드 오류를 반환하기 위한 것

from ..models import * #모델을 불러온다.
from django.db.models import Q, Count  # 검색을 위함. filter에서 OR조건으로 조회하기 위한 함수.(장고제공)
import openpyxl
from openpyxl.styles import PatternFill
from openpyxl.styles import Color
from school_report.view import check
from custom_account.models import Notification
from custom_account.views import notification_add
import numpy

def calculate_score(score_list):
    average = numpy.mean(score_list).round(2)
    variation = numpy.var(score_list).round(2)
    std = numpy.std(score_list).round(2)
    return [average, variation, std]
def result_main(request, board_id):
    board = get_object_or_404(Board, pk=board_id)
    context = {'board':board}
    subject_list = board.subject_set.filter(base_exam=board)  # 교과들을 불러와서...
    subject_data = {}
    for subject in subject_list:
        score_list = []
        scores = subject.score_set.all()  # 과목 내의 점수들을 가져오고,
        try:  # 점수가 등록되지 않는 과목들이 있는 경우.
            if scores.last().real_score:  # 공식으로 등록된 점수가 있다면 공식 점수를...
                for score in scores:
                    score_list.append(score.real_score)
            else:
                for score in scores:
                    score_list.append(score.score)
            # 점수 리스트를 구했으니, 이를 조작해 다양한 걸 얻을 수 있다.
            info = calculate_score(score_list)  # 해당 과목의 평균, 분산, 표준편차를 얻는다.
            info.append(max(score_list))  # 최고점
            info.append(min(score_list))
            subject_data[subject] = info  # 교과와 교과정보를 한데 담아 보낸다.
        except:
            messages.error(request, str(subject)+'에 대해 등록된 점수가 없습니다.')
    context['subject_data'] = subject_data

    # 프로필 가져오기.
    exam_profile = Exam_profile.objects.get(master=request.user, base_exam=board)
    context['exam_profile'] = exam_profile
    self_data = {}
    for subject in subject_list:
        subject_score_data = []
        scores = subject.score_set.filter(user=exam_profile, base_subject=subject)
        for score in scores:
            if score.real_score:
                score_num = score.real_score

            else:
                score_num = score.score
            subject_score_data.append(score_num)  # 자신의 점수를 담는다.
            mean = subject_data[subject][0]
            std = subject_data[subject][2]
            std_score = (score_num - mean) / std
            subject_score_data.append(std_score)
        self_data[subject] = subject_score_data
    context['self_data'] = self_data

    return render(request, 'boards/score/result/main.html', context)

def subject_answer_info_form_download(request, subject_id):
    subject = get_object_or_404(Subject, pk=subject_id)
    wb = openpyxl.Workbook()
    ws = wb.create_sheet('명단 form', 0)
    ws['A1'] = subject.name
    ws['A3'] = '학번↓'
    ws['B1'] = '문항번호->'
    ws['B2'] = '배점->'
    ws['B3'] = '문항정답->'
    ws['B4'] = '이 열은 비우기'
    ws.column_dimensions['B'].width = 10
    # 색 채우기
    black_fill = PatternFill(fill_type='solid', fgColor=Color('000000'))
    yellow_fill = PatternFill(fill_type='solid', fgColor=Color('ffff99'))
    red_fill = PatternFill(fill_type='solid', fgColor=Color('ff9999'))
    for cell in ws["B"]:
        cell.fill = black_fill
    for cell in ws["1"]:
        cell.fill = yellow_fill
    for cell in ws["2:2"]:
        cell.fill = red_fill
    for cell in ws["3"]:
        cell.fill = yellow_fill
    for cell in ws["A:A"]:
        cell.fill = yellow_fill
    for i in range(10):  # 과목명을 가장 첫행에 기입해넣는다.
        ws.cell(row=1, column=i + 3).value = i+1  # 문항번호.
        ws.cell(row=2, column=i + 3).value = 0  # 문항배점칸.
        ws.cell(row=3, column=i + 3).value = 0   # 정답칸.

    response = HttpResponse(content_type="application/vnd.ms-excel")
    response["Content-Disposition"] = 'attachment; filename=' + '명단양식' + '.xls'
    wb.save(response)

    return response


def subject_answer_info_form_upload(request, subject_id):
    subject = get_object_or_404(Subject, pk=subject_id)
    board = subject.base_exam
    school = subject.base_exam.school
    if check.Check_teacher(request, school).in_school_and_none() and request.method == "POST":
        pass
    else:
        return check.Check_teacher(request, school).redirect_to_school()
    uploadedFile = request.FILES["uploadedFile"]  # post요청 안의 name속성으로 찾는다.
    wb = openpyxl.load_workbook(uploadedFile, data_only=True)  # 파일을 핸들러로 읽는다.
    work_sheet = wb["명단 form"]  # 첫번째 워크시트를 사용한다.

    # 엑셀 데이터를 리스트 처리한다.
    work_sheet_data = []  # 전체 데이터를 담기 위한 리스트.
    for row in work_sheet.rows:  # 열을 순회한다.
        row_data = []  # 열 데이터를 담기 위한 리스트
        for cell in row:
            row_data.append(cell.value)  # 셀 값을 하나씩 리스트에 담는다.
        work_sheet_data.append(row_data)  # 워크시트 리스트 안에 열 리스트를 담아...
        # work_sheet_data[열번호][행번호] 형태로 엑셀의 데이터에 접근할 수 있게 된다.

    # 과목객체에 정답정보 담기.
    answer_info = work_sheet_data[2]  # 3행은 정답정보.
    right_answer_list = []
    for i in range(len(answer_info)-2):
        answer = answer_info[i+2]
        right_answer_list.append(answer)  # 정답 순서대로 담는다.
    subject.right_answer = json.dumps(right_answer_list)
    # 배점정보 담기.
    distribution_info = work_sheet_data[1]  # 2행은 배점정보.
    distribution_list = []
    for i in range(len(distribution_info)-2):
        distribution = distribution_info[i+2]
        distribution_list.append(distribution)  # 정답 순서대로 담는다.
    subject.distribution = json.dumps(distribution_list)
    subject.save()  # 정보를 담고 저장.

    # 학생 정보 저장.
    work_sheet_data = work_sheet_data[3:]  # 1~3번째 행은 버린다.(메타데이터)
    for data in work_sheet_data:  # 행별로 데이터를 가져온다.
        if data[0] == None:  # 위의 행을 비우고 올린 경우가 있다. 이런 경우엔 지나가주자.
            continue
        student_code = str(data[0])
        try:
            student = Student.objects.get(school=school, student_code=student_code)
        except Exception as e:
            messages.error(request, str(student_code) +'수험자 정보에 이상이 있습니다. 수험자를 기관에 먼저 등록하세요.')
            return redirect('boards:board_detail', board_id=board.id)

        if student.admin != None:  # 이 서비스를 이용하지 않는사람에겐 학생계정이 없어 문제가 생긴다.
            user = student.admin  # 계정 소유자.
            exam_profile, created = Exam_profile.objects.get_or_create(master=user, base_exam=board)  # 시험용 프로필.
        else:
            exam_profile, created = Exam_profile.objects.get_or_create(student=student, base_exam=board)
        if created:
            from boards.templatetags.board_filter import create_random_name
            exam_profile.name = create_random_name(10)  # 새로 생성되었다면 이름 배정조치.
        exam_profile.student = student  # 프로필에 관련 정보를 담아줘야지~!
        exam_profile.test_code = student_code
        exam_profile.save()

        score, created = Score.objects.get_or_create(user=exam_profile, base_subject=subject)  # 점수 생성.
        user_answer = []  # 사용자의 답을 담기 위한 리스트.
        for i in range(len(data)-2):
            answer = data[i+2]
            user_answer.append(answer)
        score.answer = json.dumps(user_answer)
        # 점수 계산.
        try:  # 배점정보가 있을 때.
            test = distribution_list[0]
            result_score = 0
            for right, answer, distribution in zip(right_answer_list, user_answer, distribution_list):
                if right == answer:
                     result_score += float(distribution)
            score.real_score = result_score
        except:
            pass
        score.save()  # 해당 학생의 답변을 저장하고 닫는다.
    messages.info(request, '등록 성공')
    board.official_check = True

    return redirect('boards:board_detail', board_id=board.id)

def show_answer(request, score_id):
    # 나중에 과목별로 답변을 보게 하면 좋겠네. 한번에 볼 수 있게.
    score = Score.objects.get(id=score_id)
    if request.user == score.user.master:  # 당사자일 때에만 읽게 한다.
        context = {}
        decoder = json.decoder.JSONDecoder()  # 디코더객체 설정.
        subject = score.base_subject
        right_answer = decoder.decode(subject.right_answer)
        user_anser = decoder.decode(score.answer)
        context['right_answer'] = zip(right_answer, user_anser)  # 이중for문을 위하여~
        #context['user_answer'] = decoder.decode(score.answer)
        context['subject'] = score.base_subject
        return render(request, 'boards/score/result/show_answer.html', context)
    else:
        messages.error(request, '자신의 정답만 확인할 수 있습니다.')
    return redirect('boards:board_detail', board_id=score.base_subject.base_exam.id)

def show_answer_for_teacher(request, subject_id):
    subject = Subject.objects.get(id=subject_id)
    context = {}
    if check.Check_teacher(request, subject.base_exam.school).in_school_and_none():
        pass
    else:
        messages.error(request, '꼼수 쓰지 마라.')
        return redirect('boards:board_detail', board_id=subject.base_exam.id)
    scores = subject.score_set.all()
    decoder = json.decoder.JSONDecoder()  # 디코더객체 설정.
    # 정답 담기.
    if subject.right_answer:
        right_answer = decoder.decode(subject.right_answer)
        context['right_answer'] = right_answer
    # 배점 담기.
    if subject.distribution:
        distributions = decoder.decode(subject.distribution)
        context['distributions'] = distributions
    # 학생정보 담기.
    student_answer_info = {}
    for score in scores:
        try:  # 외부인이 계정 없이 임의로 등록한 거라면... 학생계정에 매칭이 되지 않는다. 그냥 무시.
            student = score.user.student.student_code
            answer = decoder.decode(score.answer)  # 답을 리스트로.
            info = [score.real_score, answer]  # 개별 점수와 정답정보를 담는다.
            student_answer_info[student] = info  # 사전 안에 리스트로 담는다.
        except:
            pass
    context['student_answer_info'] = student_answer_info
    return render(request, 'boards/score/result/show_answer_for_teacher.html', context)

