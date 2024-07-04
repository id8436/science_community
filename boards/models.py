from django.conf import settings
from django.db import models
from school_report.models import Profile, School

class Board(models.Model):
    board_name = models.ForeignKey('Board_name', on_delete=models.PROTECT, null=True, blank=True)  # board_name.
    name = models.CharField(max_length=50)
    category = models.ForeignKey('Board_category', on_delete=models.PROTECT, null=False, blank=True)
    enter_year = models.IntegerField(null=False, blank=True)  # 입학년도 혹은 개최년도를 기입하자.
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                               related_name='board_author')
    text_1 = models.ManyToManyField('Comment', blank=True, related_name='+')  # 한 줄 코멘트 다는 용도. 혹은 컨텐츠.
    text_2 = models.ManyToManyField('Comment', blank=True, related_name='+')

    interest_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='board_interest_users')
    interest_count = models.IntegerField(default=0)

    # 점수공유에 대한 기능. + 학교게시판.
    school = models.ForeignKey(School, on_delete=models.SET_NULL, null=True, blank=True)  # 주관단체
    # official_check = models.BooleanField(default=False)  # 공식 체크가 되어있는지 여부
    # official_teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
    #                            related_name='official_teacher')  # 시험점수를 입력한 사람을 기록하기 위해.
    test_code_min = models.IntegerField(null=True, blank=True)  # 수험번호의 최소
    test_code_max = models.IntegerField(null=True, blank=True)  # 수험번호의 최대. 생태교란자를 파악하기 위함.
    association = models.ForeignKey('Board', on_delete=models.SET_NULL, null=True, blank=True, related_name='associated_exam')  # 연관실험.(시간연속성)
    def __str__(self):
        return str(self.board_name) + str(self.enter_year)
    class Meta:
        unique_together = (
            ('board_name', 'enter_year', 'category')
            )

class Board_name(models.Model):
    '''게시판 접속을 위한 코드로...'''
    name = models.CharField(max_length=32)
    def __str__(self):
        return self.name

class Board_category(models.Model):
    name = models.CharField(max_length=32)
    def __str__(self):
        return self.name
class Subject(models.Model):
    '''시험 하위 과목'''  # form에서 컴마로 구분되게 하면 어떨까? 태그 기입하듯.
    base_exam = models.ForeignKey('Board', null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=20)  # 과목명.
    sj_code = models.TextField(null=True, blank=True)  # 과목코드.

    official_check = models.BooleanField(default=False)  # 공식 체크가 되어있는지 여부
    official_teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                                         related_name='official_teacher')  # 시험점수를 입력한 사람을 기록하기 위해.
    right_answer = models.TextField(null=True, blank=True)  # 정답은 Json으로 받아 저장한다.
    distribution = models.TextField(null=True, blank=True)  # 위와 동일하게 저장.
    descriptive_distribution = models.TextField(null=True, blank=True)  # 서술형 배점정보.
    def __str__(self):
        return self.name
    class Meta:
        unique_together = (
            ('name', 'base_exam')
        )
        ordering = ['sj_code']  # 기본 정렬.
class Score(models.Model):
    user = models.ForeignKey('Exam_profile', on_delete=models.CASCADE, null=False)  # 프로파일을 생성해 담자.
    base_subject = models.ForeignKey('Subject', on_delete=models.CASCADE, null=False)
    score = models.FloatField(null=True, blank=True)  # 한 번 기입하면 변경이 불가능. 아니, 이력이 남게 하면 어때?
    real_score = models.FloatField(default=None, null=True, blank=True)  # 생성 후 입력해서 null이 필요하다. 객관식 점수.
    answer = models.TextField(null=True, blank=True)  # 시험에서의 응답을 담기 위한 것. Json으로 받는다.
    descriptive_score = models.FloatField(default=None, null=True, blank=True)  # 서술형점수.
    descriptive = models.TextField(null=True, blank=True)  # 서술형 배점정보(응시자가 받은 점수).
    real_total_score = models.FloatField(default=None, null=True, blank=True)
    def __str__(self):
        return str(self.user)
    # class Meta:  # 학생 인증할 때 옮기는 데... 유니크 제한이 방해가 된다.
    #     unique_together = (
    #         ('user', 'base_subject')
    #     )
class Exam_profile(models.Model):
    '''테스트에서 비공개로 댓글 등을 사용하기 위함. + 점수 보게끔.'''
    # 생성될 때 임의의 이름을 부여하는 함수도 같이 짜주어야 한다.
    master = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, related_name='exam_user')
    student = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True)
    base_exam = models.ForeignKey(Board, null=True, blank=True, on_delete=models.CASCADE)
    test_code = models.TextField(blank=False)  # 수험번호, 학번
    modify_num = models.IntegerField(default=-1, null=True, blank=True)  # 시험점수 수정횟수 지정.
    name = models.CharField(max_length=10)  # 랜덤한 숫자와 글자 조합으로 구성하게 할까.
    official = models.BooleanField(default=False)  # 공식 프로필과 연결되었는지.
    # 하위모델로 score가 있어 함께 조작해주어야 한다.
    def __str__(self):
        try:
            return self.student.name
        except:
            try:
                return self.master.nickname
            except:
                return "학생계정도, 마스터계정도 없습니다."
    # class Meta:
    #     unique_together = (
    #         ('test_code', 'base_exam')  # 근데, 이건 학생 인증할 때 옮겨야 해서...참 어렵다;
    #     )

class Posting(models.Model):
    #- 게시판으로서의 기능.
    board = models.ForeignKey('Board', on_delete=models.PROTECT, null=True, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                               related_name="posting_author")
    subject = models.CharField(max_length=100)  # 제목
    content = models.TextField()  # 내용, 문제내기.

    create_date = models.DateTimeField(auto_now_add=True)
    modify_date = models.DateTimeField(auto_now=True, null=True, blank=True)

    tag = models.ManyToManyField('Tag', blank=True)  # 태그 모델과 연결.
    like_users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='posting_like_users')
    like_count = models.IntegerField(default=0)  # 불필요한 연산 없이 진행하기 위해.
    dislike_users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='posting_dislike_users')
    dislike_count = models.IntegerField(default=0)  # 불필요한 연산 없이 진행하기 위해.
    interest_users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='posting_interest_users')
    interest_count = models.IntegerField(default=0)

    #- 건의, 문제제출용의 기능.
    source = models.TextField(null=True, blank=True)  # 출처 표기. + 정답 저장용으로 사용. +
    boolean_1 = models.BooleanField(default=True, null=True, blank=True)  # 저자 공개여부로 사용.(비공개가 False)
    boolean_2 = models.BooleanField(default=True, null=True, blank=True)  # 내용 공개여부로 사용.(비공개가 False)
    boolean_3 = models.BooleanField(default=False, null=True, blank=True)  # 건의사항 해결 여부로 사용(처리하면 True)
    report_user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, related_name='report_user', on_delete=models.SET_NULL)  # 유저 신고용.
    def __str__(self):
            return str(self.subject)
    ## 추가정보 관련 idea.
    # 추후 학교정보나 대회정보 등에서 내용을 추가하게 할 때... user_text 따위로 추가해서.. 다대다로 추가하게 하면 좋을듯.
    # 수정이력은 위 모델의 작성내역으로 대신하면 깔끔하게 될듯. 새 정보 등록버튼, 수정이력을 보면 대댓글처럼 나오게.(내용, 작성자, 등록일자.)
    # '등록만 가능하고, 수정, 삭제는 불가하니 신중하게 등록.
    # class user_text: text=, created=auto_add_now
    ## 신고 관련 아이디어.
    # 모달로 새 창 띄워서 별명으로 신고대상자 넣어서... 게시글, 답변 등에서 변수를 넣는 방식으로 신고방식을 통일할 수 있을듯.

class Answer(models.Model):  # 세부내용은 필요에 따라..
    posting = models.ForeignKey(Posting, on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                               related_name="answer_author")
    content = models.CharField(max_length=300)
    create_date = models.DateTimeField(auto_now_add='True')
    modify_date = models.DateTimeField(null=True, blank=True)
    voter = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="answer_voter")


class Comment(models.Model):
    answer = models.ForeignKey(Answer, null=True, blank=True, on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    content = models.CharField(max_length=150)
    create_date = models.DateTimeField(auto_now_add='True')
    modify_date = models.DateTimeField(null=True, blank=True)
    voter = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="comment_voter")

class Tag(models.Model):
    name = models.CharField(max_length=32)
    def __str__(self):
        return self.name
'''

'''