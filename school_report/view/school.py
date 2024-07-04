from django.shortcuts import render, get_object_or_404, redirect, resolve_url, HttpResponse
from .. import models  # 모델 호출.
from ..forms import HomeroomForm, SchoolForm, SubjectForm
from django.contrib import messages
from custom_account.decorator import custom_login_required as login_required
import openpyxl
from . import check
from django.http import HttpResponse
import random
from boards.models import Board, Board_category, Board_name
from .for_api import SchoolMealsApi
from django.utils.encoding import escape_uri_path
def main(request, school_id):
    context = {}
    school = get_object_or_404(models.School, pk=school_id)
    context['school'] = school
    context['announcement_list'] = school.announcebox.announcement_set.order_by('-create_date')
    context['homework_list'] = school.homeworkbox.homework_set.order_by('-create_date')
    # 교사여부.
    teacher = check.Teacher(user=request.user, school=school, request=request).in_school_and_none()
    context['teacher'] = teacher
    # 학생여부.
    student = check.Student(user=request.user, school=school, request=request).in_school_and_none()
    context['student'] = student
    # 소속교실, 소속교과만 가져온다.
    if teacher:  # 교사인 경우엔 다.
        context['homeroom_list'] = school.homeroom_set.all().order_by('name')
        context['subject_list'] = school.subject_set.all().order_by('subject_name')
        context['classroom_list'] = school.classroom_set.all().order_by('homeroom__name', 'name')
    if student:
        homeroom_list = student.homeroom.all().order_by('name')
        context['homeroom_list'] = homeroom_list
        classroom_list = school.classroom_set.filter(homeroom__in=homeroom_list).order_by('base_subject').select_related(
            'homeroom')
        # subject_list = []
        # for homeroom in homeroom_list:
        #     subjects = school.subject_set.filter(homeroom=homeroom).order_by('subject_name')
        #     subject_list.append(subjects)
        context['classroom_list'] = classroom_list
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

def name_trimming(name):
    instr = name
    outstr = ''
    for i in range(0, len(instr)):  # 문자열 내 공백 없애기.
        if instr[i] != ' ':
            outstr += instr[i]
    return outstr

@login_required()
def school_create(request):
    context = {}
    if request.method == 'POST':  # 포스트로 요청이 들어온다면... 글을 올리는 기능.
        form = SchoolForm(request.POST)  # 폼을 불러와 내용입력을 받는다.
        if form.is_valid():  # 문제가 없으면 다음으로 진행.
            school = form.save(commit=False)  # commit=False는 저장을 잠시 미루기 위함.(입력받는 값이 아닌, view에서 다른 값을 지정하기 위해)
            school.master = request.user  # 추가한 속성 author 적용
            name = name_trimming(school.name)  # 이름에서 공백 제거해 적용.
            school.name = name
            # 게시판 생성 및 연동.
            board_name = str(school.name) + " 교직원 게시판"
            board_name, _ = Board_name.objects.get_or_create(name=board_name)  # 이름객체를 생성한다.(이거 은근 불편하네;; 역대 게시판을 모을 수 있다는 점에선 좋지만... 검색해도 될듯?)
            category = Board_category.objects.get(pk=7)  # 교직원게시판의 카테고리.
            school.save()  # 객체 생성을 해야 게시판을 만들 수 있다.
            board, _ = Board.objects.get_or_create(board_name=board_name, category=category, enter_year=school.year, author=request.user, school=school)
            school.teacher_board_id = board.id  # 게시판 지정.
            school.save()
            # 과제박스 생성.
            homework_box, created = models.HomeworkBox.objects.get_or_create(school=school)
            announce_box, created = models.AnnounceBox.objects.get_or_create(school=school)
            return redirect('school_report:school_main', school_id=school.id)
    else:  # 포스트 요청이 아니라면.. form으로 넘겨 내용을 작성하게 한다.
        form = SchoolForm()
    context['form'] = form  # 폼에서 오류가 있으면 오류의 내용을 담아 create.html로 넘긴다.
    return render(request, 'school_report/school/school_create.html', context)
@login_required()
def school_modify(request, school_id):
    school = get_object_or_404(models.School, pk=school_id)
    if request.user != school.master:
        messages.error(request, '수정권한이 없습니다')
        return redirect('school_report:school_main', school_id=school.id)
    if request.method == "POST":
        form = SchoolForm(request.POST, instance=school)  # 받은 내용을 객체에 담는다. instance에 제대로 된 걸 넣지 않으면 새로운 인스턴스를 만든다.
        if form.is_valid():
            school = form.save(commit=False)
            name = name_trimming(school.name)  # 이름에서 공백 제거해 적용.
            school.name = name
            school.save()
            return redirect('school_report:school_main', school_id=school.id)
    else:  # GET으로 요청된 경우.
        form = SchoolForm(instance=school)  # 해당 모델의 내용을 가져온다!
        # 태그를 문자열화 하여 form과 함께 담는다.
    context = {'form': form}
    return render(request, 'school_report/school/school_modify.html', context)

def create_performance_score(request, subject_id):
    subject = get_object_or_404(models.Subject, pk=subject_id)
    category = get_object_or_404(Board_category, pk=6)  # 점수게시판 생성을 위해.
    context = {}
    school = subject.school
    board_name_str = str(school.name) +'/'+ str(subject.subject_name) +'/'+ '수행평가'
    board_name, _ = Board_name.objects.get_or_create(name=board_name_str)
    board, _ = Board.objects.get_or_create(category=category, author=subject.master.admin, board_name=board_name, enter_year=school.year,
                                           school=school)
    return redirect('boards:board_detail', board.id)
@login_required()
def download_excel_form(request, school_id):
    '''교사 명단 폼.'''
    school = get_object_or_404(models.School, pk=school_id)
    wb = openpyxl.Workbook()
    ws = wb.create_sheet('명단 form', 0)
    ws['A1'] = '(선택)교사코드'
    ws['B1'] = '이름'
    ws['C1'] = '가입인증코드(없으면 랜덤 6개)'
    ws['D1'] = '학년'
    ws['E1'] = '반'
    ws['F1'] = '(선택)교실이름'
    teachers = school.teacher_set.all()
    code_line = 'A'
    name_line = 'B'  # 이름 담을 라인.
    confirm_code_line = 'C'
    grade_line = 'D'
    cl_num_line = 'E'
    homeroom_name_line = 'F'
    for i, teacher in enumerate(teachers):
        num = str(i + 2)
        ws[code_line + num] = teacher.code
        ws[name_line + num] = teacher.name
        ws[confirm_code_line + num] = teacher.confirm_code
        ws[grade_line + num] = teacher.homeroom.last().grade
        ws[cl_num_line + num] = teacher.homeroom.last().cl_num
        ws[homeroom_name_line + num] = teacher.homeroom.last().name
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{escape_uri_path("교사명단.xlsx")}"'
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
        work_sheet = wb.worksheets[0]  # 첫번째 워크시트를 사용한다.

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
                profile_code = data[0]
                name = data[1]
                confirm_code = data[2]
                grade = data[3]
                cl_num = data[4]
                homeroom_name = data[5]
                profile, created = models.Profile.objects.get_or_create(name=name, code=profile_code, school=school, position='teacher')
                if not confirm_code:  # 이런 방식으로 받으면 문자열로 들어온다;
                    # 2개 데이터만 들어온 경우로, 코드정보가 없으면 랜덤으로 배정.
                    profile.confirm_code = random.randint(100000, 999999)  # 코드 지정.
                else:
                    profile.confirm_code = confirm_code
                profile.save()
                # 담임교실 배정 및 생성.
                if grade and cl_num:  # 학년, 반이 다 들어온 경우.
                    homeroom, cteated = models.Homeroom.objects.get_or_create(grade=grade, cl_num=cl_num, school=school)
                    homeroom_name_ = f'{grade}학년 {cl_num}반'
                    homeroom.name = homeroom_name_  # 학년,반으로 홈룸이름 지정.
                    homeroom.master_profile = profile
                    if homeroom_name:  # 홈룸네임이 있는 경우 덮어쓰기.
                        homeroom.name = homeroom_name
                elif homeroom_name:  # 홈룸네임만 있는 경우.
                    homeroom, cteated = models.Homeroom.objects.get_or_create(name=homeroom_name, school=school)
                    homeroom.master_profile = profile
                else:
                    continue  # 저장과정으로 넘어가지 않고 다음으로.
                homeroom.save()


    return redirect('school_report:teacher_assignment', school_id=school_id)  # 필요에 따라 렌더링.




@login_required()
def teacher_code_input(request, school_id):
    school = get_object_or_404(models.School, pk=school_id)
    context = {'school': school}
    if request.method == 'POST':  # 포스트로 요청이 들어온다면...
        confirm_code = request.POST.get('code')
        try:
            teacher = models.Profile.objects.filter(school=school, confirm_code=confirm_code)[0]  # 해당 계정 중 1번째.
            if teacher.obtained == True:
                messages.error(request, '이미 누군가 등록한 프로필입니다.')
                return render(request, 'school_report/school/teacher_code_input.html', context)
            # 이상 없으면 확인 페이지로 이동시킨다.
            return redirect('school_report:teacher_code_confirm', teacher_id=teacher.id)
        except:
            messages.error(request, '코드 해당계정이 없습니다.')
    return render(request, 'school_report/school/teacher_code_input.html', context)

def teacher_code_confirm(request, teacher_id):
    teacher = get_object_or_404(models.Profile, pk=teacher_id)
    context={'teacher':teacher}
    if request.method == 'POST':  # 포스트로 요청이 들어온다면...
        confirm_code = request.POST.get('code')
        if confirm_code == teacher.confirm_code:
            teacher.admin = request.user
            teacher.obtained = True
            teacher.confirm_code = None
            teacher.save()
            # request.user.teacher = teacher  # 계정에 등록.
            # request.user.save()  # 이것도 저장 해주어야 해.
            messages.info(request, '인증에 성공하였습니다.')
            return redirect('school_report:main')
        else:
            messages.error(request, '코드가 안맞는데요;')
            return render(request, 'school_report/school/teacher_code_confirm.html', context)

    return render(request, 'school_report/school/teacher_code_confirm.html', context)
def teacher_delete(request, teacher_id):
    teacher = get_object_or_404(models.Profile, pk=teacher_id)
    school = teacher.school
    if school.master == request.user:
        messages.error(request, "삭제하였습니다.")
        teacher.delete()
        return redirect(request.META.get('HTTP_REFERER', None))  # 이전 화면으로 되돌아가기.
    else:
        messages.error(request, '관리자만이 가능합니다.')
        return redirect(request.META.get('HTTP_REFERER', None))  # 이전 화면으로 되돌아가기.

@login_required()
def teacher_assignment(request, school_id):
    '''관리자가 보는 교사 명단'''
    school = get_object_or_404(models.School, pk=school_id)
    context = {'school': school}
    if school.master == request.user:
        teacher_list_resistered = models.Profile.objects.filter(school=school, obtained=True, position='teacher')  # 학교 내에 등록된 프로필만 가져온다.
        context['teacher_list_resistered'] = teacher_list_resistered

        teacher_list_unresistered = models.Profile.objects.filter(school=school, obtained=False, position='teacher')  # 등록 안한 사람만 반환.
        context['teacher_list_unresistered'] = teacher_list_unresistered
        return render(request, 'school_report/school/assignment.html', context)

def school_profile_delete(request, profile_id):
    profile = get_object_or_404(models.Profile, pk=profile_id)
    school = profile.school
    if school.master == request.user:
        messages.error(request, "삭제하였습니다.")
        profile.delete()
        return redirect(request.META.get('HTTP_REFERER', None))  # 이전 화면으로 되돌아가기.
    else:
        messages.error(request, '관리자만이 가능합니다.')
        return redirect(request.META.get('HTTP_REFERER', None))  # 이전 화면으로 되돌아가기.

############################## 학생 관련.
def student_assignment(request, school_id):
    school = get_object_or_404(models.School, pk=school_id)
    context = {'school': school}
    if school.master == request.user:
        student_list_resistered = models.Profile.objects.filter(school=school, obtained=True, position='student')  # 학교 내에 등록된 프로필만 가져온다.
        context['student_list_resistered'] = student_list_resistered

        student_list_unresistered = models.Profile.objects.filter(school=school, obtained=False, position='student')  # 등록 안한 사람만 반환.
        context['student_list_unresistered'] = student_list_unresistered
        return render(request, 'school_report/school/student_assignment.html', context)

@login_required()
def school_student_download_excel_form(request, school_id):
    school = get_object_or_404(models.School, pk=school_id)
    wb = openpyxl.Workbook()
    ws = wb.create_sheet('명단 form', 0)
    ws['A1'] = '학번'
    ws['B1'] = '이름'
    ws['C1'] = '가입인증코드(없으면 랜덤 6개)'
    ws['D1'] = '학년(선택사항)'
    ws['E1'] = '반(선택사항)'
    students = models.Profile.objects.filter(school=school, position='student')  # 학교에 속한 학생.
    a = 'A'  # 학번쓰는 라인.
    b = 'B'  # 이름쓰는 라인.
    c = 'C'  # 코드 쓰는 라인.
    d = 'D'  # 학년
    e = 'E'  # 반
    for i, student in enumerate(students):
        num = str(i + 2)
        ws[a + num] = student.code
        ws[b + num] = student.name
        if student.obtained:
            ws[c + num] = '등록함'
        else:
            ws[c + num] = student.confirm_code  # 가입인증코드.
        if student.homeroom:
            homeroom = student.homeroom.all().first()  # 여러 학급에 등록되어 있을 수 있으니.
            ws[d + num] = homeroom.grade
            ws[e + num] = homeroom.cl_num
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{escape_uri_path("학생명단.xlsx")}"'
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
            return check.Teacher(school=school).redirect_to_school()
        uploadedFile = request.FILES["uploadedFile"]  # post요청 안의 name속성으로 찾는다.
        wb = openpyxl.load_workbook(uploadedFile, data_only=True)  # 파일을 핸들러로 읽는다.
        work_sheet = wb.worksheets[0]  # 첫번째 워크시트를 사용한다.

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
            student_code = data[0]
            name = data[1]
            confirm_code = data[2]
            grade = data[3]
            cl_num = data[4]

            profile, created = models.Profile.objects.get_or_create(school=school, name=name, code=student_code, position='student')
            # if created:
            #     exam_profiles = student.exam_profile_set.all()
            #     for profile in exam_profiles:
            #         profile.master = student.admin
            #         profile.save()  # 시험등록 때 계정이 없던 사람은 시험프로필을 학생에 연결해두었으므로 이를 계정에 직접 연결해준다.

            # 학급정보가 있다면 만들어버리기.
            if not confirm_code:  # 이런 방식으로 받으면 문자열로 들어온다;
                # 2개 데이터만 들어온 경우로, 코드정보가 없으면 랜덤으로 배정.
                profile.confirm_code = random.randint(100000, 999999)  # 코드 지정.
            else:
                profile.confirm_code = confirm_code
            if grade and cl_num:  # 학년, 반이 다 들어온 경우.
                homeroom, cteated = models.Homeroom.objects.get_or_create(grade=grade, cl_num=cl_num, school=school)
                profile.homeroom.add(homeroom)
            profile.save()
        messages.info(request, '반영 완료.')

    return redirect('school_report:student_assignment', school_id=school_id)  # 필요에 따라 렌더링.

@login_required()
def student_code_input(request, school_id):
    '''학생 인증하기.'''
    school = get_object_or_404(models.School, pk=school_id)
    context = {'school': school}
    student = check.Student(user=request.user, school=school).in_school_and_none()
    if student == None:
        pass
    else:
        messages.error(request, '이미 이 기관에 인증되었습니다.' + str(student.student_code))
        return redirect('school_report:school_main', school_id=school_id)
    if request.method == 'POST':  # 포스트로 요청이 들어온다면...
        confirm_code = request.POST.get('code')
        try:
            student = models.Profile.objects.filter(school=school, confirm_code=confirm_code)[0]
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
    student = get_object_or_404(models.Profile, pk=student_id)
    context={'student':student}
    if request.method == 'POST':  # 포스트로 요청이 들어온다면...
        confirm_code = request.POST.get('code')
        if confirm_code == student.confirm_code:
            student.admin = request.user
            student.obtained = True
            student.confirm_code = None
            student.save()
            #request.user.student = student  # 계정에 등록. 이거 없어도 될듯. 필요없어진 기능.
            #request.user.save()
            messages.info(request, '인증에 성공하였습니다.')
            return redirect('school_report:school_main', school_id=student.school.id)
        else:
            messages.error(request, '코드가 안맞는데요;')
            return render(request, 'school_report/school/student_code_confirm.html', context)
    return render(request, 'school_report/school/student_code_confirm.html', context)

def meal_info(request, school_id):
    school = get_object_or_404(models.School, pk=school_id)
    context = {}
    # 급식정보
    if school.school_code:  # 학교코드가 있어야 진행.
        school_meal = SchoolMealsApi(ATPT_OFCDC_SC_CODE=school.education_office, SD_SCHUL_CODE=school.school_code)
        # 표에 넣기 위해 항목별로 차례대로 넣는다.
        meal_data = {'일자': [], '식사': [], '메뉴': [], '칼로리': [], '영양정보': [], '재료정보': []}
        try:  # 개학 전엔 식사정보가 없어 None을 반환한다. 그럼 에러뜸.
            for i in school_meal.get_data():
                date = i['MLSV_YMD']
                date = date[4:6] + '월' + date[6:] + '일'
                meal_data['일자'].append(date)  # 급식일자.
                meal_data['식사'].append(i['MMEAL_SC_NM'])  # 조,중,석식 분류.
                meal_data['메뉴'].append(i['DDISH_NM'])  # 메뉴
                meal_data['칼로리'].append(i['CAL_INFO'])  # 칼로리.
                meal_data['영양정보'].append(i['NTR_INFO'])  # 영양정보
                meal_data['재료정보'].append(i['ORPLC_INFO'])  # 재료정보
            context['meal_data'] = meal_data
        except:
            pass
    return render(request, 'school_report/school/meal_info.html', context)

def profile_reset(request, profile_id):
    profile = models.Profile.objects.get(pk=profile_id)
    profile.obtained = False
    profile.confirm_code = random.randint(100000, 999999)
    profile.save()
    return redirect('school_report:student_assignment', school_id=profile.school.id)