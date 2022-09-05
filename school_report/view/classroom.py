from django.shortcuts import render, get_object_or_404, redirect, resolve_url, HttpResponse
from .. import models  # 모델 호출.
from ..forms import ClassroomForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
@login_required()
def create(request, school_id):
    school = get_object_or_404(models.School, pk=school_id)
    context = {'school': school}
    homeroom_list = school.homeroom_set.all()  # 학교 하위의 학급들.
    context['homeroom_list'] = homeroom_list
    if request.method == 'POST':  # 포스트로 요청이 들어온다면... 글을 올리는 기능.
        if school.code != request.POST.get('code'):  # 코드가 같아야 진행.
            messages.error(request, "학교 코드가 맞지 않습니다.")
            context['form'] = ClassroomForm(request.POST)
            return render(request, 'school_report/classroom/create.html', context)
        form = ClassroomForm(request.POST)  # 폼을 불러와 내용입력을 받는다.
        if form.is_valid():  # 문제가 없으면 다음으로 진행.
            subject = request.POST.get('subject')
            homeroom_list = request.POST.getlist('homeroom_list')
            for homeroom_id in homeroom_list:  # 받은 데이터에 해당하는 걸 넣는다.
                homeroom = get_object_or_404(models.Homeroom, pk=homeroom_id)
                classroom = models.Classroom.objects.create(subject=subject, master=request.user, school=school, homeroom=homeroom)
            return render(request, 'school_report/classroom/main.html', context)  # 작성이 끝나면 작성한 글로 보낸다.
    else:  # 포스트 요청이 아니라면.. form으로 넘겨 내용을 작성하게 한다.
        form = ClassroomForm()
    context['form'] = form  # 폼에서 오류가 있으면 오류의 내용을 담아 create.html로 넘긴다.
    return render(request, 'school_report/classroom/create.html', context)

def main(request, homeroom_id):
    homeroom = get_object_or_404(models.Homeroom, pk=homeroom_id)
    context ={'homeroom': homeroom}
    return render(request, 'school_report/homeroom/main.html', context)