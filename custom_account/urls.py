from django.urls import path
from . import views  # 해당 앱의 뷰를 불러온다.
from django.contrib.auth import views as auth_views  #장고에서 제공하는 기능 활용!

app_name = 'custom_account'  # 이름공간을 위한, 인덱싱을 위한 변수이다. 이걸 작성하면 인덱스는 '앱이름:인덱스'로 바뀐다.

urlpatterns = [
    path('social_login/', auth_views.LoginView.as_view(template_name='custom_account/login_social.html'), name='login_social'),
    path('login/', views.login_main, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.signup, name='signup'),

    path('notification/show/', views.notification_show, name='notification_show'),
    path('profile/', views.profile, name='profile'),

]