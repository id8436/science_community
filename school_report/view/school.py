from django.shortcuts import render, get_object_or_404, redirect, resolve_url, HttpResponse
from .. import models  # 모델 호출.
from ..forms import HomeroomForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import openpyxl
from openpyxl.writer.excel import save_virtual_workbook

from django.http import HttpResponse
import random

def main(request, school_id):
    context = {}
    school = get_object_or_404(models.School, pk=school_id)
    context['school'] = school
    homeroom_list = school.homeroom_set.all()
    context['homeroom_list'] = homeroom_list
    classroom_list = school.classroom_set.all()
    context['classroom_list'] = classroom_list

    teacher_list = models.Teacher.objects.filter(school=school, obtained=True)  # 학교 내에 등록된 프로필만 가져온다.
    for teacher in teacher_list:
        if teacher.admin == request.user:  # 프로필 등록자 중에 해당한다면..
            context['teacher_list'] = teacher_list
    return render(request, 'school_report/school/main.html', context)

@login_required()
def download_excel_form(request):
    wb = openpyxl.Workbook()
    ws = wb.create_sheet('명단 form', 0)
    ws['A1'] = '이름'
    ws['B1'] = '담임학년'
    ws['C1'] = '담임반'

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
                teacher, created = models.Teacher.objects.get_or_create(name=data[0], school=school)
                if created:
                   teacher.code = random.randint(100000, 999999)  # 코드 지정.

                # 학급이 있다면 그냥 만들어버리기.
                if (data[1] != None) and (data[2] != None):  # 학급, 학년정보가 있다면.
                    homeroom, created = models.Homeroom.objects.get_or_create(master=teacher, grade=data[1], cl_num=data[2], school=school)
                    homeroom.code = random.randint(100000, 999999)
                    homeroom.save()
                    teacher.grade = data[1]
                    teacher.cl_num = data[2]
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
        teacher_list = models.Teacher.objects.filter(school=school, obtained=False)  # 등록 안한 사람만 반환.
        context['teacher_list'] = teacher_list
        return render(request, 'school_report/school/assignment.html', context)
