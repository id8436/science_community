from django.shortcuts import render, get_object_or_404, redirect, resolve_url, HttpResponse
from .. import models  # 모델 호출.
from ..forms import ClassroomForm, HomeworkForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required

@login_required()
def create(request, school_id):
    school = get_object_or_404(models.School, pk=school_id)
    context = {'school': school}
    homeroom_list = school.homeroom_set.all()  # 학교 하위의 학급들.
    context['homeroom_list'] = homeroom_list
    if request.method == 'POST':  # 포스트로 요청이 들어온다면... 글을 올리는 기능.
        if school != request.user.teacher.school:  # 같아야 진행.
            messages.error(request, "학교에 등록된 교사가 아닙니다.")
            context['form'] = ClassroomForm(request.POST)
            return render(request, 'school_report/classroom/create.html', context)
        form = ClassroomForm(request.POST)  # 폼을 불러와 내용입력을 받는다.
        if form.is_valid():  # 문제가 없으면 다음으로 진행.
            subject = request.POST.get('subject')
            homeroom_list = request.POST.getlist('homeroom_list')
            for homeroom_id in homeroom_list:  # 받은 데이터에 해당하는 걸 넣는다.
                homeroom = get_object_or_404(models.Homeroom, pk=homeroom_id)
                classroom = models.Classroom.objects.get_or_create(subject=subject, master=request.user.teacher, school=school, homeroom=homeroom)
            return redirect('school_report:school_main', school_id=school.id)  # 작성이 끝나면 작성한 글로 보낸다.
    else:  # 포스트 요청이 아니라면.. form으로 넘겨 내용을 작성하게 한다.
        form = ClassroomForm()
    context['form'] = form  # 폼에서 오류가 있으면 오류의 내용을 담아 create.html로 넘긴다.
    return render(request, 'school_report/classroom/create.html', context)

def main(request, classroom_id):
    classroom = get_object_or_404(models.Classroom, pk=classroom_id)
    context ={'classroom': classroom}

    homework_list = classroom.homework_set.all()
    context['homework_list'] = homework_list
    return render(request, 'school_report/classroom/main.html', context)

@login_required()
def homework_create(request, classroom_id):
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
            student_list = models.Student.objects.filter(homeroom=classroom.homeroom)
            for student in student_list:
                individual, created = models.HomeworkSubmit.objects.get_or_create(to_student=student,
                          base_homework=homework)

            return redirect('school_report:classroom_main', classroom.id)  # 작성이 끝나면 작성한 글로 보낸다.
    else:  # 포스트 요청이 아니라면.. form으로 넘겨 내용을 작성하게 한다.
        form = HomeworkForm()
    context['form'] = form  # 폼에서 오류가 있으면 오류의 내용을 담아 create.html로 넘긴다.
    return render(request, 'school_report/classroom/homework/create.html', context)

def homework_modify(request, posting_id):
    posting = get_object_or_404(models.Homework, pk=posting_id)
    if request.user != posting.author:
        messages.error(request, '수정권한이 없습니다')
        return redirect('school_report:homework_detail', posting_id=posting.id)
    if request.method == "POST":
        form = HomeworkForm(request.POST, instance=posting)  # 받은 내용을 객체에 담는다. instance에 제대로 된 걸 넣지 않으면 새로운 인스턴스를 만든다.
        if form.is_valid():
            posting = form.save(commit=False)  # commit=False는 저장을 잠시 미루기 위함.(입력받는 값이 아닌, view에서 다른 값을 지정하기 위해)
            posting.save()
            # 개별 확인을 위한 개별과제 체크 해제.
            submit_list = models.HomeworkSubmit.objects.filter(base_homework=posting)
            for submit in submit_list:
                submit.check = False
                submit.save()
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
    classroom = posting.classroom
    posting.delete()
    return redirect('school_report:classroom_main', classroom_id=classroom.id)
def homework_detail(request, posting_id):
    '''과제 상세페이지와 과제제출 기능.'''
    context = {}
    posting = get_object_or_404(models.Homework, pk=posting_id)
    context['posting'] = posting
    classroom = posting.classroom
    if request.method == 'POST':  # 과제를 제출한 경우.
        homework_submit = get_object_or_404(models.HomeworkSubmit, base_homework=posting, to_student=request.user.student)
        content = request.POST.get('content')
        homework_submit.content = content
        homework_submit.check = True  # 제출표시
        homework_submit.save()
        return redirect('school_report:homework_detail', posting.id)  # 작성이 끝나면 작성한 글로 보낸다.
    else:
        form = get_object_or_404(models.HomeworkSubmit, base_homework=posting, to_student=request.user.student)  # 해당 모델의 내용을 가져온다!
        # 태그를 문자열화 하여 form과 함께 담는다.
        context['form'] = form
    if request.user == posting.author:  # 작성자가 제출여부 볼 수 있다.
        context['classroom'] = classroom
        submit_list = models.HomeworkSubmit.objects.filter(base_homework=posting)
        context['submit_list'] = submit_list
    student = get_object_or_404(models.Student, admin=request.user, homeroom=classroom.homeroom)  # 학생객체 가져와서...
    individual_announcement = get_object_or_404(models.HomeworkSubmit, to_student=student,
                                                base_homework=posting)
    individual_announcement.read = True
    individual_announcement.save()
    context['individual_announcement'] = individual_announcement
    return render(request, 'school_report/classroom/homework/detail.html', context)

def homework_resubmit(request, submit_id):
    submit = get_object_or_404(models.HomeworkSubmit, pk=submit_id)
    submit.check = False
    submit.save()
    return redirect('school_report:homework_detail', posting_id=submit.base_homework.id)