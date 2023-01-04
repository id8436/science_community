from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from school_report.models import Teacher, Student

class UserManager(BaseUserManager):
    def create_user(self, username, password=None):
        user = self.model(              # 이 안에 유저 정보에 필요한 필드를 넣으면 된다.
            username = username     # 왼쪽이 필드, 오른쪽이 넣을 값.
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password):
        user = self.create_user(
            username,
            password=password,
        )
        user.is_admin = True
        user.is_staff = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    username = models.CharField(max_length=15, unique=True, null=False)  # identifier. 다른서비스와 연동될 때 username을 식별자로 많이 사용하기에.. 이는 선택지가 없다.
    # 기본 기능들
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    objects = UserManager()  # 회원가입을 다룰 클래스를 지정한다.
    USERNAME_FIELD = 'username'  # 식별자로 사용할 필드.
    REQUIRED_FIELDS = []         # 회원가입 때 필수 입력필드.

    #----- 추가 기능들
    is_social = models.BooleanField(default=True)  # 소셜계정인가 여부. 기본적으로 True로 두어 추가계정 연결을 꾀한다.
    connected_user = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField(max_length=128, null=True, blank=False)  # 이메일은 반드시 입력하게끔.(소셜계정은 메일이 없는 경우가 있어서;;)
    # 누군가 악의적으로 남의 이메일을 등록할 수 있으니 유니크는 걸지 않는다.
    email_check = models.BooleanField(default=False)
    nickname = models.CharField(max_length=15, unique=True, null=True, blank=False)
    created_date = models.DateTimeField(auto_now_add='True')
    is_notification = models.BooleanField(default=False)

    # 학교기능 관련.
    #teacher = models.OneToOneField(Teacher, default=None, blank=True, null=True, on_delete=models.SET_NULL)  # 연결된 교사프로필
    #student = models.OneToOneField(Student, default=None, blank=True, null=True, on_delete=models.SET_NULL, related_name='connected_student')  # 연결된 학생프로필
    def __str__(self):
        if self.nickname:
            return self.nickname
        return self.username

    def has_module_perms(self, app_label):
        '''앱 라벨을 받아, 해당 앱에 접근 가능한지 파악'''
        return True
    def has_perm(self, perm, obj=None):
        '''권한 소지여부를 판단하기 위한 메서드'''
        return True

class Notification(models.Model):
    to_user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='to_user')
    # 1:게시판, 2:포스팅, 3:답글, 4:코멘트
    # 11:관심게시, 12:게시글추가, 21:포스팅좋아요, 22:답글추가, 31:답글좋아요, 32:대댓글추가, 41:코멘트좋아요
    type = models.IntegerField()
    from_user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='from_user')
    message = models.TextField()
    user_has_seen = models.BooleanField(default=False)
    url = models.URLField()  # 이동할 url이 담기는 곳.
    created_date = models.DateTimeField(auto_now_add='True')
    def __str__(self):
        return self.message