from django.shortcuts import render, get_object_or_404, redirect, resolve_url, HttpResponse
from .. import models  # 모델 호출.
from ..forms import HomeroomForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import openpyxl
from . import check
from django.http import HttpResponse
import random
from boards.models import Board, Board_category

def main(request, school_id):
    context = {}
    school = get_object_or_404(models.School, pk=school_id)
    context['school'] = school
    homeroom_list = school.homeroom_set.all()
    context['homeroom_list'] = homeroom_list
    classroom_list = school.classroom_set.all()
    context['classroom_list'] = classroom_list
    # 교사여부.
    teacher = check.Check_teacher(request, school).in_school_and_none()
    context['teacher'] = teacher
    # 학생여부.
    student = check.Check_student(request, school).in_school_and_none()
    context['student'] = student
    # 시험문제목록.
    category = Board_category.objects.get(id=6)
    context['category'] = category  # 게시판 생성 때 카테고리 아이디도 필요해서.
    exam_list = Board.objects.filter(school=school, category=category)
    context['exam_list'] = exam_list
    return render(request, 'school_report/school/main.html', context)
def list(request):
    context = {}
    school_list = models.School.objects.order_by('-id')  # 생성순서의 반대.
    #-----검색기능
    keyword = request.GET.get('keyword', '')  # 검색어를 받는다.
    if keyword != '':  # 검색어가 있다면
        result = []  # 검색결과를 담기 위한 리스트를 만든다.
        keywords = keyword.split(' ')  # 공백이 있는 경우 나눈다.
        for kw in keywords:  # 띄어쓰기로 검색을 하는 경우가 많으니까, 다 찾아줘야지.
            result += school_list.filter(name__icontains=kw) # 제목검색
    school_list = result
    context['board_list'] = school_list
    return render(request, 'school_report/school/list.html', context)

@login_required()
def download_excel_form(request, school_id):
    school = get_object_or_404(models.School, pk=school_id)
    wb = openpyxl.Workbook()
    ws = wb.create_sheet('명단 form', 0)
    ws['A1'] = '이름'
    ws['B1'] = '추가할 담임학급'
    students = school.teacher_set.all()
    a = 'A'  # 이름 담을 라인.
    for i, teacher in enumerate(students):
        num = str(i + 2)
        ws[a + num] = teacher.name
    response = HttpResponse(content_type="application/vnd.ms-excel")
    response["Content-Disposition"] = 'attachment; filename=' + '명단양식' + '.xls'
    wb.save(response)

    return response


@login_required()
def upload_excel_form(request, school_id):
    context = {}
    if request.method == "POST":
        school = get_object_or_404(models.School, pk=school_id)
        context['school'] = school
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
        work_sheet_data = work_sheet_data[1:]  # 첫번째 행은 버린다.

        if request.user == school.master:
            for data in work_sheet_data:  # 행별로 데이터를 가져온다.
                name = data[0]
                homeroom_name = data[1]
                teacher, created = models.Teacher.objects.get_or_create(name=name, school=school)
                teacher.code = random.randint(100000, 999999)  # 코드 지정.

                # 학급정보가 있다면 그냥 만들어버리기.
                if homeroom_name != None:  # 학급, 학년정보가 있다면.
                    # 가능하면 교사 1인이 홈룸 1개 갖게끔...
                    homeroom, created = models.Homeroom.objects.get_or_create(school=school, name=homeroom_name)
                    homeroom.master = teacher
                    homeroom.save()
                teacher.save()

    return redirect('school_report:teacher_assignment', school_id=school_id)  # 필요에 따라 렌더링.

@login_required()
def teacher_code_input(request, school_id):
    school = get_object_or_404(models.School, pk=school_id)
    context = {'school': school}
    if request.method == 'POST':  # 포스트로 요청이 들어온다면...
        code = request.POST.get('code')
        try:
            teacher = models.Teacher.objects.filter(school=school, code=code)[0]  # 해당 계정 중 1번째.
            if teacher.obtained == True:
                messages.error(request, '이미 누군가 등록한 프로필입니다.')
                return render(request, 'school_report/school/teacher_code_input.html', context)
            # 이상 없으면 확인 페이지로 이동시킨다.
            return redirect('school_report:teacher_code_confirm', teacher_id=teacher.id)
        except:
            messages.error(request, '코드 해당계정이 없습니다.')
    return render(request, 'school_report/school/teacher_code_input.html', context)

def teacher_code_confirm(request, teacher_id):
    teacher = get_object_or_404(models.Teacher, pk=teacher_id)
    context={'teacher':teacher}
    if request.method == 'POST':  # 포스트로 요청이 들어온다면...
        code = request.POST.get('code')
        if code == teacher.code:
            teacher.admin = request.user
            teacher.obtained = True
            teacher.code = None
            teacher.save()
            request.user.teacher = teacher  # 계정에 등록.
            request.user.save()  # 이것도 저장 해주어야 해.
            messages.info(request, '인증에 성공하였습니다.')
            return redirect('school_report:main')
        else:
            messages.error(request, '코드가 안맞는데요;')
            return render(request, 'school_report/school/teacher_code_confirm.html', context)

    return render(request, 'school_report/school/teacher_code_confirm.html', context)


@login_required()
def assignment(request, school_id):
    school = get_object_or_404(models.School, pk=school_id)
    context = {'school': school}
    if school.master == request.user:
        teacher_list_resistered = models.Teacher.objects.filter(school=school, obtained=True)  # 학교 내에 등록된 프로필만 가져온다.
        context['teacher_list_resistered'] = teacher_list_resistered

        teacher_list_unresistered = models.Teacher.objects.filter(school=school, obtained=False)  # 등록 안한 사람만 반환.
        context['teacher_list_unresistered'] = teacher_list_unresistered
        return render(request, 'school_report/school/assignment.html', context)


############################## 학생 관련.
def student_assignment(request, school_id):
    school = get_object_or_404(models.School, pk=school_id)
    context = {'school': school}
    if school.master == request.user:
        student_list_resistered = models.Student.objects.filter(school=school, obtained=True)  # 학교 내에 등록된 프로필만 가져온다.
        context['student_list_resistered'] = student_list_resistered

        student_list_unresistered = models.Student.objects.filter(school=school, obtained=False)  # 등록 안한 사람만 반환.
        context['student_list_unresistered'] = student_list_unresistered
        return render(request, 'school_report/school/student_assignment.html', context)

@login_required()
def school_student_download_excel_form(request, school_id):
    school = get_object_or_404(models.School, pk=school_id)
    wb = openpyxl.Workbook()
    ws = wb.create_sheet('명단 form', 0)
    ws['A1'] = '학번'
    ws['B1'] = '이름'
    ws['C1'] = '넣을 학급(띄어쓰기 없음)'
    ws['D1'] = '가입인증코드(없으면 랜덤 6개)'
    students = school.student_set.all()  # 학교에 속한 학생.
    a = 'A'  # 학번쓰는 라인.
    b = 'B'  # 이름쓰는 라인.
    c = 'C'  # 학번쓰는 라인.(안씀)
    d = 'D'  # 코드 쓰는 라인.
    for i, student in enumerate(students):
        num = str(i + 2)
        ws[a + num] = student.student_code
        ws[b + num] = student.name
        if student.obtained:
            ws[d + num] = '등록함'
        else:
            ws[d + num] = student.code  # 가입인증코드.
    response = HttpResponse(content_type="application/vnd.ms-excel")
    response["Content-Disposition"] = 'attachment; filename=' + '명단양식' + '.xls'
    wb.save(response)

    return response



@login_required()
def school_student_upload_excel_form(request, school_id):
    context = {}
    if request.method == "POST":
        school = get_object_or_404(models.School, pk=school_id)
        context['school'] = school
        if request.user == school.master:
            pass
        else:
            messages.error(request, '이 기능은 관리자만이 가능합니다.')
            return check.Check_teacher(request, school).redirect_to_school()  # 학교에 소속된 교사인지 검증.
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
        work_sheet_data = work_sheet_data[1:]  # 첫번째 행은 버린다.

        for data in work_sheet_data:  # 행별로 데이터를 가져온다.
            student_code = str(data[0])
            name = str(data[1])

            student, created = models.Student.objects.get_or_create(school=school, student_code=student_code)
            student.name = name
            if created:
                exam_profiles = student.exam_profile_set.all()
                for profile in exam_profiles:
                    profile.master = student.admin
                    profile.save()  # 시험등록 때 계정이 없던 사람은 시험프로필을 학생에 연결해두었으므로 이를 계정에 직접 연결해준다.

            # 학급정보가 있다면 만들어버리기.
            print(len(data))
            if len(data) < 3:
                # 2개 데이터만 들어온 경우로, 코드정보가 없으면 랜덤으로 배정.
                student.code = random.randint(100000, 999999)  # 코드 지정.
            else:
                to_homeroom = str(data[2])
                if to_homeroom != 'None':
                    try:
                        homeroom = models.Homeroom.objects.get(name=to_homeroom)  # 서버에러로 인식한다.
                        student.homeroom.add(homeroom)
                    except:
                        messages.error(request, "등록되지 않은 학급을 지정하였습니다. 학급 생성 먼저!\n" + student_code +'학생. 등록되지 않은 학급 ' + to_homeroom)
                # 코드정보가 있으면 대입한다.
                if (len(data) < 4) or (student.obtained):  # 코드 등록필요가 없다면...
                    pass
                else:
                    if data[3] == None:  # 내용이 없는 경우가 있음.
                        student.code = random.randint(100000, 999999)  # 코드 지정.
                    else:
                        student.code = data[3]
            student.save()
        messages.info(request, '반영 완료.')

    return redirect('school_report:student_assignment', school_id=school_id)  # 필요에 따라 렌더링.

@login_required()
def student_code_input(request, school_id):
    school = get_object_or_404(models.School, pk=school_id)
    context = {'school': school}
    if check.Check_student(request,school).in_school_and_none():
        pass
    else:
        messages.error(request, '이미 이 기관에 인증되었습니다.')
        return redirect('school_report:school_main', school_id=school_id)
    if request.method == 'POST':  # 포스트로 요청이 들어온다면...
        code = request.POST.get('code')
        try:
            student = models.Student.objects.get(school=school, code=code)
            if student.obtained == True:
                messages.error(request, '이미 누군가 등록한 프로필입니다.')
                return render(request, 'school_report/school/student_code_input.html', context)
            # 이상 없으면 확인 페이지로 이동시킨다.
            return redirect('school_report:student_code_confirm', student_id=student.id)
        except Exception as e:
            messages.error(request, e)
            messages.error(request, '코드 해당계정이 없습니다.')
    return render(request, 'school_report/school/student_code_input.html', context)

@login_required()
def student_code_confirm(request, student_id):
    student = get_object_or_404(models.Student, pk=student_id)
    context={'student':student}
    if request.method == 'POST':  # 포스트로 요청이 들어온다면...
        code = request.POST.get('code')
        if code == student.code:
            student.admin = request.user
            student.obtained = True
            student.code = None
            student.save()
            request.user.student = student  # 계정에 등록.
            request.user.save()
            messages.info(request, '인증에 성공하였습니다.')
            return redirect('school_report:school_main', school_id=student.school.id)
        else:
            messages.error(request, '코드가 안맞는데요;')
            return render(request, 'school_report/school/student_code_confirm.html', context)

    return render(request, 'school_report/school/student_code_confirm.html', context)