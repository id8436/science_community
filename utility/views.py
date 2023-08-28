from django.http import HttpRequest
from django.shortcuts import render, get_object_or_404, redirect, resolve_url
from .forms import *
from school_report import models
from django.contrib import messages  # 메시지 모듈을 불러오고,


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



from school_report.models import HomeworkSubmit
def do_DB(request):
    homeworks = models.Homework.objects.all()
    for homework in homeworks:
        submits = homework.homeworksubmit_set.all()
        for submit in submits:
            if submit.content:  # 제출한 내용이 있다면..
                user = submit.to_user
                try:  # 질문이 하나인 경우만 뽑아내기 위해.
                    question = models.HomeworkQuestion.objects.get(homework=homework)
                    messages.info(request, submit)
                    answer = models.HomeworkAnswer.objects.get(respondent=user, question=question)
                    answer.contents = submit.content
                    answer.save()
                except Exception as e:
                    messages.error(request, e)
    return render(request, 'utility/main.html', {})

'''지난 것들
    # 반영함. 별 문제 없으면 지우자. 과제에 학생 배치시키는 게 아니라, 유저모델 대응시키기.
    # object = HomeworkSubmit.objects.all()
    # for i in object:
    #     user = i.to_student.admin
    #     i.to_user = user
    #     i.save()
    
'''