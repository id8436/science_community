from django.shortcuts import render, redirect, get_object_or_404
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

def notification_add(request, type, to_users, message, url):
    # type에 대한 규율은 notification.html을 보자.
    # 어디에 달리는 알람이냐에 따라 다르게 짜줘야 할 필요가 있을지도.... 아니면 포스팅이나 이런저런거에 기본적인 게 달리게 하자.
    for to_user in to_users:
        Notification.objects.create(type=type, to_user=to_user, from_user=request.user,
                                               url=url,
                                               message=message)
def notification_click(request, notification_id):
    notification = get_object_or_404(Notification, pk=notification_id)
    notification.user_has_seen = True
    notification.save()
    return redirect(notification.url)


from django.contrib.auth.decorators import login_required #로그인이 있어야 가능함

@login_required()
def profile(request):
    # 연결된 소셜계정 정보.
    #print(dir(request.user.user_set.all()[1].socialaccount_set.all().first()))
    #print(request.user.user_set.all()[1].socialaccount_set.all())
    social_accounts = []
    for accounts in request.user.user_set.all():
        social_accounts.append(accounts.socialaccount_set.all().first())
    context = {'social_accounts': social_accounts}

    return render(request, 'custom_account/profile.html', context)


def send_email_verify_code(request): #  쿠키를 이용해 검증해보자.
    from django.core.mail import EmailMessage  # 이메일을 보내는 모듈. 파이썬에선 smtplib를 사용하지만, 장고 자체의 기능이 더 편리하다.
    from django.template.loader import render_to_string  # 템플릿을 렌더링하기 위한 기능.
    import random
    from django.shortcuts import reverse
    from config import secret
    user = request.user
    email_verification_code = random.random()
    print(email_verification_code)
    response = redirect(request.META.get('HTTP_REFERER', '/'))  # 다음에 보낼 페이지를 지정해 응답을 받아야 한다.(그래야 저장됨)
    response.set_cookie('email_verification_code', email_verification_code, max_age=300)  # 사용자의 쿠키에 검증코드 저장
    content = {'user': user,
               'email_verification_code': email_verification_code,
               # http를 안넣어주면... 네이버를 호스트로 삼아 움직인다;
               'to_url': 'http://' + request.get_host() + reverse('custom_account:email_verification'),
               }  # 이메일에 코드를 담아보낸다.
    msg = EmailMessage(subject="이메일 인증",  # 이메일 제목
                       body=render_to_string('custom_account/email_verification.html', content),
                       to=[request.user.email],
                       )  # 보내는 사람 메일은 settings.py에 따른다.
    msg.content_subtype = 'html'  # html 코드로 나타내기 위함.
    msg.send()
    messages.info(request, '이메일을 확인해보세요~ 5분동안 유효합니다~')  # 테스트용
    print(request.COOKIES.get('email_verification_code'))
    return response

def email_verify(request):
    user = request.user
    cookie = request.COOKIES.get('email_verification_code')
    code = request.GET.get('email_verification_code')
    if  code == cookie:  # 쿠키에 있는 걸 쓰면 될듯.
        user.email_check = True
        user.save()
        messages.info(request, '이메일 인증이 완료되었습니다.')
    else:
        messages.error(request, '뭔가 문제 생김.')
        messages.error(request, request.GET['email_verification_code'])
        messages.error(request, '뭔가 ?? 생김.')
        messages.error(request, request.COOKIES.get('email_verification_code'))
    if cookie == None:
        messages.error(request, '쿠키가 삭제되었습니다. 이메일 요청을 다시 하세요~')
    return True
def email_verification(request):
    '''이메일 인증기능.'''
    if email_verify(request):
        response = redirect('custom_account:profile')  # 다음으로 갈 페이지 지정.
        response.delete_cookie('email_verification_code')  # 확인했으니, 저장했던 쿠키를 지워준다.
        return response
# 네이버 로그인데서 추가로 비밀번호 입력이 안되게 해둬서... 고민해봤는데.. 비밀번호가 없으면 운영이 안될텐데;;
# def signup_by_email(request):
#     user_id = request.GET.get('user_id')
#     if email_verify(request):
