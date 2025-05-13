from django.http import HttpRequest
from django.shortcuts import render, get_object_or_404, redirect, resolve_url
from .forms import *
from django.contrib import messages  # 메시지 모듈을 불러오고,
from school_report import models


def main(request):
    return render(request, 'utility/main.html', {})

def compound_interest(request):
    #  폼을 통해 들어온 데이터를 받는다.
    principal = request.GET.get('principal')
    interest_rate = request.GET.get('interest_rate')
    how_many = request.GET.get('how_many')
    additional = request.GET.get('additional')
    result = 0  # 아무 것도 넣지 않았을 때 반환.
    form = Compound_interest_form(request.GET)  # 데이터를 폼에 대응.
    if form.is_valid():  # 폼이 정상적일 때에만 진행.
        # 연산을 하자.
        if interest_rate and principal and how_many:  # 원금과 이자율만 기입한 경우. 필요한 요소가 있을 때에만 ㄱㄱ
            principal = float(principal)
            interest_rate = float(interest_rate) /100
            how_many = int(how_many)
            result = principal * (1+interest_rate)**how_many
            if additional:  # 추가로 넣는 금액까지 기입할 때 ㄱ
                additional = float(additional)
                result = result + additional*(1-interest_rate**how_many)/(1-interest_rate)

    context = {'result':result,
               'form':form,
               }
    return render(request, 'utility/compound_interest.html', context)

from django.http import HttpResponse
def test_secure(request):
    '''csrf 토큰이 잘 되는지 확인.'''
    return HttpResponse(f"request.is_secure(): {request.is_secure()}")

def do_DB(request):

    return render(request, 'utility/main.html', {})

def do_DB2(request):



    return render(request, 'utility/main.html', {})


def do_DB3(request):


    return render(request, 'utility/main.html', {})

# 끝난 것들.

'''
24.4.2 과제 제출 내역 없는 거 다 지웠다가 교사프로필도 지워짐;
    school = models.School.objects.get(name='강원과학고등학교', year='2024')
    profile = models.Profile.objects.get(school=school, admin=request.user)
    homeworks = models.Homework.objects.filter(author_profile=None)
    for homework in homeworks:
        homework.author_profile = profile
        homework.save()
        submits = models.HomeworkSubmit.objects.all()
    for submit in submits:
        user = submit.to_user
        base_homework = submit.base_homework

        profile = models.Profile.objects.filter(admin=user).first()
        # try:  # 프로필이 없기도..
        #     box = base_homework.homework_box
        #     school = box.get_school_model()
        #     profile = models.Profile.objects.filter(admin=user, school=school)
        #     submit.to_profile = profile
        #     submit.save()
        # except:
        #     pass
        submit.to_profile = profile
        submit.save()
24.4.1 프로필이 너무 많이 생성되어 반영함.
## 과제 제출 내역이 없는 프로필들은 다 지워버려.
    profiles = models.Profile.objects.all()
    for profile in profiles:
        submits = models.HomeworkSubmit.objects.filter(to_profile=profile, check=True).exists()
        if submits:
            pass
        else:
            profiles.delete()

    # 다시 학생을 프로필로 옮겨.
    student = models.Student.objects.all()
    for i in student:
        try:  # 유니크 에러가 나기도 함. 이땐 그냥 패스하자.
            profile, created = models.Profile.objects.get_or_create(school=i.school, obtained = i.obtained,
                                                                    name=i.name)
            profile.code = i.student_code
            profile.admin=i.admin
            profile.position='student'
            for homeroom in i.homeroom.all():
                profile.homeroom.add(homeroom)
            profile.save()
        except:
            pass
    target_model = models.HomeworkSubmit.objects.all()
    for i in target_model:
        old_user = i.to_user
        base_homework = i.base_homework
        if base_homework.subject_object:
            school = base_homework.subject_object.school
        elif base_homework.classroom:
            classroom = base_homework.classroom
            school = classroom.school
        elif base_homework.homeroom:
            school = base_homework.homeroom.school
        elif base_homework.homework_box:  # base_homework.homework_box
            box = base_homework.homework_box
            school = box.get_school_model()
        else:
            pass
        i.to_profile = models.Profile.objects.filter(admin=old_user, school=school).first()
        try:  # None인 경우는 에러처리되니 넘기자.
            target_user = i.to_student.admin
            i.target_profile = models.Profile.objects.filter(admin=target_user, school=school).first()
        except:
            pass
        i.save()


24.3.28 반영.
    student = models.Profile.objects.all()
    for profile in student:
        if profile.position == "student":
            if profile.homeroom.exists():
                pass
            else:
                profile.delete()
        else:  # 교사라면..
            if profile.homeroom_master.exists():
                pass
            else:
                profile.delete()



24.03.12 반영. homework box 만들기.(학교, 학급, 교실, 교과)
    # 각 객체별 homeworkbox 생성.
    target_model = models.School.objects.all()
    for i in target_model:
        box, created = models.HomeworkBox.objects.get_or_create(school=i)
    target_model = models.Homeroom.objects.all()
    for i in target_model:
        box, created = models.HomeworkBox.objects.get_or_create(homeroom=i)
    target_model = models.Classroom.objects.all()
    for i in target_model:
        box, created = models.HomeworkBox.objects.get_or_create(classroom=i)
        homework_list = i.homework_set.all()
        for homework in homework_list:
            homework.homework_box = box
            homework.save()
    target_model = models.Subject.objects.all()
    for i in target_model:
        box, created = models.HomeworkBox.objects.get_or_create(subject=i)
        homework_list = i.homework_set.all()
        for homework in homework_list:
            homework.homework_box = box
            homework.save()
    # 각 객체별 announcebox 생성.
    target_model = models.School.objects.all()
    for i in target_model:
        box, created = models.AnnounceBox.objects.get_or_create(school=i)
    target_model = models.Homeroom.objects.all()
    for i in target_model:
        box, created = models.AnnounceBox.objects.get_or_create(homeroom=i)
    target_model = models.Classroom.objects.all()
    for i in target_model:
        box, created = models.AnnounceBox.objects.get_or_create(classroom=i)
    target_model = models.Subject.objects.all()
    for i in target_model:
        box, created = models.HomeworkBox.objects.get_or_create(subject=i)
    ############################## code가 아니라 student code로 했어야 했는데;;;
    # 교사, 학생 프로필 전환.
    teacher = models.Teacher.objects.all()
    for i in teacher:
        profile, created = models.Profile.objects.get_or_create(admin=i.admin, obtained=i.obtained,
                                                                created=i.created,
                                                                activated=i.activated, school=i.school,
                                                                position='teacher', name=i.name)
    student = models.Student.objects.all()
    for i in student:
        try:  # 유니크 에러가 나기도 함. 이땐 그냥 패스하자.
            profile, created = models.Profile.objects.get_or_create(admin=i.admin, obtained=i.obtained,
                                                                    created=i.activated, activated=i.activated,
                                                                    school=i.school, position='student',
                                                                    name=i.name,
                                                                    code=i.code)
            for homeroom in i.homeroom.all():
                profile.homeroom.add(homeroom)
            profile.save()
        except:
            pass
    # 기존 제출 교사, 학생 프로필 새 프로필로 전환.
    target_model = models.HomeworkSubmit.objects.all()
    for i in target_model:
        old_user = i.to_user
        base_homework = i.base_homework
        if base_homework.subject_object:
            school = base_homework.subject_object.school
        elif base_homework.classroom:
            classroom = base_homework.classroom
            school = classroom.school
        elif base_homework.homeroom:
            school = base_homework.homeroom.school
        elif base_homework.homework_box:  # base_homework.homework_box
            box = base_homework.homework_box
            school = box.get_school_model()
        else:
            pass
        i.to_profile = models.Profile.objects.filter(admin=old_user, school=school).first()
        try:  # None인 경우는 에러처리되니 넘기자.
            target_user = i.to_student.admin
            i.target_profile = models.Profile.objects.filter(admin=target_user, school=school).first()
        except:
            pass
        i.save()
# 과제 수정. author모델 새 프로필로 전환.
    target_model = models.Homework.objects.all()
    for i in target_model:
        if i.author_profile:
            continue  # 지정되어 있으면 굳이 찾지 말고.
        if i.school:
            school = i.school
        elif i.subject_object:
            school = i.subject_object.school
        elif i.classroom:
            classroom = i.classroom
            school = classroom.school
        elif i.homeroom:
            school = i.homeroom.school
        elif i.homework_box:
            school = box.get_school_model()
        else:
            continue  # 여기에서 에러 나는 건 진~짜 오래된 객체이기 때문에.
        i.author_profile = models.Profile.objects.filter(admin=i.author, school=school).first()
        i.save()
    # 공지 저자를 전환.
    target_model = models.Announcement.objects.all()
    for i in target_model:
        if i.author_profile:
            continue  # 지정되어 있으면 굳이 찾지 말고.
        if i.classroom:
            classroom = i.classroom
            school = classroom.school
        elif i.homeroom:
            school = i.homeroom.school
        elif i.homework_box:
            school = box.get_school_model()
        elif i.school:
            school = i.school
        else:
            pass # 진짜 오래된 모델은 연결점이 없음.
        i.author_profile = models.Profile.objects.filter(admin=i.author, school=school).first()
        i.save()
    # classroom. teacher에서 전환.
    target_model = models.Classroom.objects.all()
    for i in target_model:
        teacher = i.master
        if teacher == None:  # 새로 만들어진 객체에선 교사모델 없음.
            continue
        profile = models.Profile.objects.filter(admin=teacher.admin, school=teacher.school).first()
        i.master_profile = profile
        i.save()
    # homeroom.
    target_model = models.Homeroom.objects.all()
    for i in target_model:
        teacher = i.master
        if teacher == None:
            continue
        profile = models.Profile.objects.filter(admin=teacher.admin, school=teacher.school).first()
        i.master_profile = profile
        i.save()
    # subject.
    target_model = models.Subject.objects.all()
    for i in target_model:
        teacher = i.master
        if teacher == None:
            continue
        profile = models.Profile.objects.filter(admin=teacher.admin, school=teacher.school).first()
        i.master_profile = profile
        i.save()


'''
'''23.10.12기준 반영. 동료평가 응답에서 submit이 아니라 학생계정 연동시키는 것.
answers = models.HomeworkAnswer.objects.all()
print(answers)
for answer in answers:
    try:
        print(answer.submit)
        answer.to_student = answer.submit.to_student
    except:
        pass'''

