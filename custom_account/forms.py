from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm  # 제공하는 폼이 있다.
from django.contrib.auth import get_user_model  # 장고에 커스텀으로 등록한 모델을 불러온다.

class User_create_form(UserCreationForm):
    class Meta:
        model = get_user_model()  #  설정된 커스텀모델
        fields = ["username", "nickname", "email"]  # password1,2 필드는 자동추가된다.

class User_update_form(UserChangeForm):
    class Meta:
        model = get_user_model()  #  설정된 커스텀모델
        fields = ["nickname", "email"]  # password1,2 필드는 자동추가된다. 근데..아마 패스워드 폼은 따로 두어야 할 것 같은데;