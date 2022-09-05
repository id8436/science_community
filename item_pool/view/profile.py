from django.contrib.auth.decorators import login_required #로그인이 있어야 가능함
from django.shortcuts import render, redirect
from django.utils import timezone  # 시간입력을 위해.

from item_pool.forms import SchoolProfileForm

@login_required(login_url='membership:login')
def create(request):
    if request.method == "POST":
        form =  SchoolProfileForm(request.POST)
        if form.is_valid():
            SchoolProfile = form.save(commit=False)
            SchoolProfile.year = 2020  # 나중에 현재 연도 불러오는 걸로 구현하자.
            SchoolProfile.profiles_owner = request.user  # 유저와 연결.
            SchoolProfile.save()
            request.user.schoolprofile = SchoolProfile
            request.user.save()
            return redirect('membership:profile')
    else:
        form = SchoolProfileForm()
    context = {'form': form}
    return render(request, 'profile_create.html', context)