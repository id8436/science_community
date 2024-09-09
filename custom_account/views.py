from django.shortcuts import render, redirect, get_object_or_404

import config.secret
from .forms import User_create_form, User_update_form
from django.contrib import messages
from config.secret import SERVICE_DOMAIN

def login_test(request):
    return render(request, 'custom_account/login_social.html', {})

def login_main(request):
    try:  # 로그인을 안한 경우엔 is_social 속성이 없기 때문에 에러를 반환한다.
        is_social = request.user.is_social
        if is_social == False:
            raise ValueError  # 소셜계정이어야 해.
    except:
        messages.error(request, '잘못된 접근입니다.')
        return redirect('main:show')
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

def user_info_change(request):
    '''이메일에서 버튼을 눌러 수정되게끔.'''
    if request.method == "POST":
        if email_verify(request):
            pass
        else:
            messages.error(request, '부정한 접근인 듯한데요;;;')
            return redirect('custom_account:password_find')  # 비밀번호 찾기 페이지로 보내기.
        user_id = request.COOKIES.get('user_id')  # 이메일을 보낼 때 쿠키에 넣었던 아이디의 수정만 가능하도록.
        target_user = get_user_model().objects.get(id=user_id)
        # 과거의 정보는 폼처리가 되기 전에 저장되어야 한다. 이메일이 달라지는 경우 이메일 인증 풀기.
        old_email = target_user.email
        form = User_update_form(request.POST, instance=target_user)
        ## 비밀번호 인증은 없앴으니까.
        # from django.contrib.auth import authenticate
        # password = request.POST.get('password_confirm', None)
        # authentication = authenticate(username=target_user.username, password=password)
        if form.is_valid():
            user = form.save(commit=False)
            if old_email != user.email:  # 이메일정보가 달라지면 인증 취소.
                user.email_check = False
            if request.POST.get('password1') != None:  # 비밀번호 체크.
                if request.POST.get('password1') == request.POST.get('password2'):
                    user.set_password(request.POST.get('password1'))
                else:
                    messages.error(request, '두 비밀번호가 일치하지 않습니다.')
                    return render(request, 'custom_account/user_info_change.html', {'form': form})
            user.save()
            from django.contrib.auth import logout  # 프로필로 돌아가는데, 소셜계정으로 들어가진다. 때문에 일단 로그아웃.
            logout(request)
            messages.success(request, '다시 로그인해주세요~')
            return redirect('custom_account:profile')
    else:
        if email_verify(request):
            pass
        else:
            messages.info(request, '본인의 이메일로 회원정보 변경코드를 보냅니다.')
            return redirect('custom_account:password_find')  # 비밀번호 찾기 페이지로 보내기.
        user_id = request.COOKIES.get('user_id')  # 이메일을 보낼 때 쿠키에 넣었던 아이디의 수정만 가능하도록.
        user = get_user_model().objects.get(id=user_id)
        form = User_update_form(instance=user)
        email_verification_code = request.COOKIES.get('email_verification_code')
    return render(request, 'custom_account/user_info_change.html', {'form': form, 'email_verification_code': email_verification_code})

from django.contrib.auth import get_user_model
def find_id_and_password_reset_code(request):
    '''회원정보 변경을 위한 이메일 보내기.'''
    context = {}
    if request.method == "POST":
        try:
            email = request.POST.get('email')
            user = get_user_model().objects.get(email=email)  # 계정 찾기.
        except:
            messages.error(request, '해당 이메일을 가진 계정이 없습니다.')
            return redirect('custom_account:password_find')
        context['user_info'] = user  # 아이디정보 담기.

        from django.shortcuts import reverse
        context['to_url'] = SERVICE_DOMAIN + reverse('custom_account:user_info_change')
        response = send_email_cookie_content(request, user.id, "아이디 확인 및 비밀번호 초기화", [email],
                                             'custom_account/email_verification_for_password.html', context)
        return response
    else:
        try:  # 로그인 안된 상태에서 접근하면 에러가 난다.
            if request.user.email:
                context['email'] = request.user.email
        except:
            messages.error(request, '로그인 후 진행하세요~(같은 브라우저에서 로그인 된 상태여야 합니다.)')
            return render(request, 'custom_account/find_id_and_password_reset_code.html', context)
    return render(request, 'custom_account/find_id_and_password_reset_code.html', context)
from django.contrib.auth import get_user_model
def email_verification_for_password(request):
    '''이 함수 버리고... 회원정보 변경 페이지로 보낸다.'''
    '''이메일 인증기능.'''
    if email_verify(request):
        user_id = request.POST.getlist('user_id')
        user_list = []
        for id in user_id:
            user = get_user_model().objects.get(id=id)
            user_list.append(user)
        # 비밀번호 랜덤 지정.
        import random
        password = random.randint(100000, 999999)
        for user in user_list:
            user.set_password(password)  # 비밀번호 설정.
            user.save()
        messages.error(request, "비밀번호는 잠깐 동안만 알려드립니다. 바로 기억해두세요!")
        text = '비밀번호는 ' + str(password) + ' 입니다.'
        messages.success(request, text)

        response = redirect('custom_account:login')  # 다음으로 갈 페이지 지정.
        response.delete_cookie('email_verification_code')  # 확인했으니, 저장했던 쿠키를 지워준다.

        return redirect('custom_account:login')

from .models import Notification
def notification_show(request):
    notifications = Notification.objects.filter(to_user=request.user)
    notifications = notifications.order_by('-created_date')
    context = {'notifications': notifications}
    return render(request, 'custom_account/notification_show.html', context)

def notification_add(request, classification, type, to_users, message, url):
    # type에 대한 규율은 모델을 보자.
    # 어디에 달리는 알람이냐에 따라 다르게 짜줘야 할 필요가 있을지도.... 아니면 포스팅이나 이런저런거에 기본적인 게 달리게 하자.
    for to_user in to_users:
        Notification.objects.create(classification=classification, type=type, to_user=to_user, from_user=request.user,
                                               url=url,
                                               message=message)
def notification_add_for_one(official, classification, type, from_user, to_user, message, url):
    if to_user:  # 전달할 유저가 있을 때에만 진행.
        Notification.objects.create(official=official, classification=classification, type=type, to_user=to_user, from_user=from_user,
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
    social_provider = []
    social_accounts = []
    for social_account in request.user.socialaccount_set.all():
        try:
            social_provider.append(social_account.get_provider_display())  # 공급자 없는 장고계정에선 get에러.
            try:
                social_accounts.append(social_account.get_provider_account().to_str())  # to_str로 계정정보를 받아오는데, 없으면 get 에러.
            except:
                social_accounts.append('정보없음.')
        except:
            pass
    # 아래는 위 코드의 과거형. 혹시 몰라 남겨둔다.
    #for accounts in request.user.user_set.all():
    #    account = accounts.socialaccount_set.all().first()
    #    try:
    #        social_provider.append(account.get_provider_display())  # 공급자 없는 장고계정에선 get에러.
    #        try:
    #            social_accounts.append(account.get_provider_account().to_str())  # to_str로 계정정보를 받아오는데, 없으면 get 에러.
    #        except:
    #            social_accounts.append('정보없음.')
    #    except:
    #        pass
    social_account_info = list(zip(social_provider, social_accounts))
    context = {'social_account_info': social_account_info}

    return render(request, 'custom_account/profile.html', context)

def send_email_cookie_content(request, user_id, subject, to, html, content):
    '''이메일을 통해 쿠키 인증 링크를 보낸다.'''
    '''to는 리스트 형태로 받는다. content는 사전.'''
    # 쿠키 설정.
    import random
    email_verification_code = random.random()
    print(email_verification_code)
    response = redirect(request.META.get('HTTP_REFERER', '/'))  # 다음에 보낼 페이지를 지정해 응답을 받아야 한다.(그래야 저장됨)
    response.set_cookie('email_verification_code', email_verification_code, max_age=300)  # 사용자의 쿠키에 검증코드 저장
    response.set_cookie('user_id', user_id, max_age=300)  # 회원정보 변경 등 user id가 일치해야 할 경우.
    messages.info(request, '이메일을 확인해보세요~ 5분동안 유효합니다~')  # 테스트용
    print(request.COOKIES.get('email_verification_code'))
    content['email_verification_code'] = email_verification_code  # 되돌려받을 쿠키 담기.
    # 이메일 보내기.
    from django.core.mail import EmailMessage  # 이메일을 보내는 모듈. 파이썬에선 smtplib를 사용하지만, 장고 자체의 기능이 더 편리하다.
    from django.template.loader import render_to_string  # 템플릿을 렌더링하기 위한 기능.
    msg = EmailMessage(subject=subject,  # 이메일 제목
                       body=render_to_string(html, content),
                       to=to,
                       )  # 보내는 사람 메일은 settings.py에 따른다.
    msg.content_subtype = 'html'  # html 코드로 나타내기 위함.
    msg.send()
    messages.success(request, '이메일 발송 성공~')
    return response


def send_email_verify_code(request): #  쿠키를 이용해 검증해보자.
    from django.shortcuts import reverse

    # from config import secret
    user = request.user
    content = {'user': user,
               # http를 안넣어주면... 이메일 도메인을 호스트로 삼아 움직인다;
               'to_url': SERVICE_DOMAIN + reverse('custom_account:email_verification'),
               }  # 이메일에 코드를 담아보낸다.
    user_id = request.user.id  # 보안을 위해 유저 id와 쿠키를 함께 보내자.
    response = send_email_cookie_content(request, user_id, "이메일 인증", [request.user.email],
                                         'custom_account/email_verification.html', content)
    return response

def email_verify(request):
    user = request.user
    cookie = request.COOKIES.get('email_verification_code')
    try:
        code = request.POST['email_verification_code']
        print('포스트로.')
        print(code)
    except:
        print('포스트 실패')
        code = request.GET.get('email_verification_code')  # 둘 다 없으면 에러가 생기니 한쪽은 get으로 받는다.
    if cookie == None:  # 쿠키와 폼에서 온 값 모두 없을 때 pass가 되어버리니, None일 때 처리가 따로 필요하다.
        messages.error(request, '코드가 만료되었습니다. 이메일 발송 후 5분 이내에 처리하세요~')
        return False
    if code == cookie:  # 쿠키에 있는 걸 쓰면 될듯.
        user.email_check = True
        user.save()
        messages.info(request, '이메일 인증이 완료되었습니다.')
    else:
        messages.error(request, '뭔가 문제 생김.(아래는 코드)')
        messages.error(request, code)
        messages.error(request, '뭔가 ?? 생김.(아래는 쿠키)')
        messages.error(request, cookie)
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
