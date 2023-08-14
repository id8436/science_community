from django.shortcuts import render, redirect, HttpResponse
import allauth

def main_show(request):
    user = request.user
    context = {}
    # # 소셜계정 연결 확인.
    # try:  # 로그인을 안한 경우엔 is_social 속성이 없기 때문에 에러를 반환한다.
    #     is_social = user.is_social
    #     connected_user = request.user.connected_user
    #     test = '로그인함'
    # except Exception as e:
    #     is_social = None
    #     test = '로그인안함.'
    if request.user.is_authenticated:  # 로그인 한 경우에만.
        is_social = user.is_social
        connected_user = request.user.connected_user
        if is_social == True:  # 소셜계정으로 로그인한 경우, 장고 계정으로 연결하고 지운다.
            if connected_user:
                social_user = request.user.socialaccount_set.all().first()  # 소셜계정을 가져온다.
                social_user.user = connected_user  # 소셜유저의 포린키 유저를 연결된 유저로 재지정.
                social_user.save()
                from django.contrib.auth import logout, login
                origin_user = request.user  # 삭제를 위해 기존 유저를 저장해둔다.
                logout(request)
                login(request, connected_user, backend='django.contrib.auth.backends.ModelBackend')
                origin_user.delete()  # 로그인에 성공했다면 기존 유저를 지운다.
                return redirect('/')
            else:
                # social_accounts = []
                # for accounts in request.user.user_set.all():
                #     social_accounts.append(accounts.socialaccount_set.all().first())
                # context['social_accounts'] = social_accounts
                return render(request, 'custom_account/login_main.html')
        # 로그인 전 접속했던 주소로 리다이렉트 하자.
        url = request.session.get('before_login')  # 기존 주소 획득.
        if url != None:
            del request.session['before_login']
            return redirect(url)
        return render(request, 'main/main.html', context)
    else:
        return render(request, 'main/main.html', context)


def main_about(request):
    return render(request, 'main/about.html',)
