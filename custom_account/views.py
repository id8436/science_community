from django.shortcuts import render, redirect
from .forms import User_create_form
from django.contrib import messages

def login_test(request):
    return render(request, 'custom_account/login_social.html', {})

def login_main(request):
    if request.method == 'GET':
        return render(request, 'custom_account/login_main.html')

    elif request.method == 'POST':
        context = {}
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)

        if not (username and password):
            context['error'] = "모든 값을 입력하세요"
        else:
            from django.contrib.auth import authenticate, login
            to_user = authenticate(username=username, password=password)
            if to_user:
                request.user.connected_user = to_user  # 유저를 연결한다.
                request.user.save()  # 저장
                login(request, user=to_user)
                ##
                return redirect('/')
            else:
                context['error'] = "계정 인증에 실패하였습니다.(아이디, 비밀번호 오류)"
        return render(request, 'custom_account/login_main.html', context)

def signup(request):
    if request.method == "POST":
        from django.contrib.auth import authenticate, login
        form = User_create_form(request.POST)
        if form.is_valid():
            form.save()  # 폼값을 불러와 저장.
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            request.user.connected_user = user  # 현재 로그인된 소셜계정에 가입한 계정 연결하기.
            user.is_social = False  # 소셜계정이 아님을 설정.
            user.save()  # 모델의 변형값 저장.
            login(request, user)
            return redirect('/')  # 회원 가입 후 어디로 돌릴지.
    else:
        form = User_create_form()
        messages.info(request, "비밀번호는 단방향 암호화 되어 보관됩니다.(관리자도 해독을 못한다는 사실!)")
    return render(request, 'custom_account/signup.html', {'form': form})

from .models import Notification
def notification_show(request):
    notifications = Notification.objects.filter(to_user=request.user)
    notifications = notifications.order_by('-created_date')
    context = {'notifications': notifications}
    return render(request, 'custom_account/notification_show.html', context)
#def add_notification(category, to_user, from_user, message, url):

def notification_add(request, type, to_user, message):
    # type에 대한 규율은 notification.html을 보자.
    # 어디에 달리는 알람이냐에 따라 다르게 짜줘야 할 필요가 있을지도.... 아니면 포스팅이나 이런저런거에 기본적인 게 달리게 하자.
    notification = Notification.objects.create(type=type, to_user=to_user, from_user=request.user,
                                               url=request.META.get('HTTP_REFERER', '/'),
                                               message=message)



from django.contrib.auth.decorators import login_required #로그인이 있어야 가능함

@login_required()
def profile(request):


    # 연결된 소셜계정 정보.
    #print(dir(request.user.user_set.all()[1].socialaccount_set.all().first()))
    #print(request.user.user_set.all()[1].socialaccount_set.all())
    social_accounts = []
    for accounts in request.user.user_set.all():
        social_accounts.append(accounts.socialaccount_set.all().first())
    print(social_accounts)
    context = {'social_accounts': social_accounts}

    return render(request, 'custom_account/profile.html', context)