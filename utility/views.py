from django.http import HttpRequest
from django.shortcuts import render, get_object_or_404, redirect, resolve_url
from .forms import *

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

from boards.models import Score
def do_DB(request):
    scores = Score.objects.all()
    for i in scores:
        if i.real_score == None:
            i.real_score = 0
        if i.descriptive_score == None:
            i.descriptive_score = 0
        i.real_total_score = i.real_score + i.descriptive_score
        i.save()
    return render(request, 'utility/main.html', {})