from django.urls import path
from . import views  # 해당 앱의 뷰를 불러온다.
from django.contrib.auth import views as auth_views  #장고에서 제공하는 기능 활용!

app_name = 'custom_account'  # 이름공간을 위한, 인덱싱을 위한 변수이다. 이걸 작성하면 인덱스는 '앱이름:인덱스'로 바뀐다.

urlpatterns = [
    # 유저 계정.
    path('social_login/', auth_views.LoginView.as_view(template_name='custom_account/login_social.html'), name='login_social'),
    path('login/', views.login_main, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.signup, name='signup'),
    path('password_find/', views.find_id_and_password_reset_code, name='password_find'),
    path('email_verification_for_password/', views.email_verification_for_password, name='email_verification_for_password'),

    path('user_info_change/', views.user_info_change, name='user_info_change'),

    path('notification/show/', views.notification_show, name='notification_show'),
    path('notification/click/<int:notification_id>', views.notification_click, name='notification_click'),

    # 프로필 관련.
    path('profile/', views.profile, name='profile'),
    path('send_email_verify_code/', views.send_email_verify_code, name='send_email_verify_code'),
    path('email_verification/', views.email_verification, name='email_verification'),

    # OAuth2.0 관련.
    path('OAuth2.0/client_list', views.OAuth_client_list, name='OAuth_client_list'),
    path('OAuth2.0/detail/<int:pk>', views.OAuth_client_edit, name='OAuth_client_edit'),
    path('OAuth2.0/register', views.OAuth_register_client, name='OAuth_register_client'),
    path('OAuth2.0/delete/<int:pk>', views.OAuth_delete_client, name='OAuth_delete_client'),
]