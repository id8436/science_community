from django.shortcuts import redirect
from functools import wraps

def custom_login_required():
    '''로그인 데코레이터의 기능에 현재 페이지를 저장하기 위해.'''
    def _decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # 로그인 하지 않았을 때에만.
            if not request.user.is_authenticated:
                request.session['before_login'] = request.path
                return redirect('custom_account:login_social')  # 로그인 페이지로 이동.
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return _decorator