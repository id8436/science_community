from django.shortcuts import render, redirect
import allauth

def main_show(request):
    user = request.user
    context = {}
    try:  # 로그인을 안한 경우엔 is_social 속성이 없기 때문에 에러를 반환한다.
        is_social = user.is_social
        connected_user = request.user.connected_user
        test = '로그인함'
    except Exception as e:
        is_social = None
        test = '로그인안함.'

    if is_social == True:
        if connected_user:  # 소셜계정과 유저가 연결되어 있을 때.
            from django.contrib.auth import logout, login
            logout(request)
            login(request, connected_user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('/')
        else:
            # social_accounts = []
            # for accounts in request.user.user_set.all():
            #     social_accounts.append(accounts.socialaccount_set.all().first())
            # context['social_accounts'] = social_accounts
            return render(request, 'custom_account/login_main.html')
    else:
        return render(request, 'main/main.html', context)


def main_about(request):
    return render(request, 'main/about.html',)
