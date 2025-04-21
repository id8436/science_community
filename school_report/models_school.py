from django.db import models
import os  # 파일 수정시간 파악을 위해..
from .models_base import School, Profile  # 같은 프로젝트 안의 model 내부 클래스들 사용 가능.
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile

def compress_image(image_field):
    '''다 jpeg 파일로 바꾸어 용량 낮추어 저장함.'''
    try:
        if image_field:
            img = Image.open(image_field)
            if img.mode != 'RGB':
                img = img.convert('RGB')

            output_io = BytesIO()
            quality = 85
            img.save(output_io, format='JPEG', quality=quality)

            while output_io.tell() > 1024 * 1024 and quality > 10:  # 1024*1024가 1mb
                quality -= 5
                output_io.seek(0)
                output_io.truncate()
                img.save(output_io, format='JPEG', quality=quality)

            output_io.seek(0)
            filename = os.path.splitext(image_field.name)[0] + '.jpeg'

            return InMemoryUploadedFile(
                output_io,
                'ImageField',
                filename,
                'image/jpeg',
                output_io.tell(),
                None
            )
    except Exception as e:
        # 로깅 등을 추가할 수 있음
        print(f"이미지 압축 중 오류 발생: {e}")

    return None


class LostItemBoard(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='lost_board')
    # 교사가 남기는 공지성 메시지
    teacher_message = models.TextField(blank=True)
    teacher = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True)  # 메시지 작성자.
    message_updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.school}"

class LostItem(models.Model):
    STATUS_CHOICES = [
        ('lost', '분실'),
        ('found', '찾음'),
    ]

    board = models.ForeignKey(LostItemBoard, on_delete=models.CASCADE, related_name='lost_items')
    author = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True)
    is_teacher = models.BooleanField(default=False)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='lost')
    modified_at = models.DateTimeField(auto_now=True)
    where = models.CharField(max_length=255)  # 관련 장소.
    when = models.CharField(max_length=255)  # 관련 시간.
    description = models.TextField()  # 물건 서술.

    photo_item = models.ImageField(upload_to='school/lost_items/lost/', blank=True, null=True)
    photo_claimed = models.ImageField(upload_to='school/lost_items/claimed/', blank=True, null=True)

    def __str__(self):
        return f"{self.description[:20]} - {self.get_status_display()}"

    def save(self, *args, **kwargs):
        # 두 이미지 필드에 대해 압축 처리
        if self.photo_item:
            self.photo_item = compress_image(self.photo_item)
        if self.photo_claimed:
            self.photo_claimed = compress_image(self.photo_claimed)

        super().save(*args, **kwargs)

class FeedbackBoard(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='feedback_board')
    # 교사가 남기는 공지성 메시지
    teacher_message = models.TextField(blank=True)
    teacher = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True)  # 메시지 작성자.
    message_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.school}"


class Feedback(models.Model):
    STATUS_CHOICES = [
        ('pending', '대기'),
        ('in_progress', '진행'),
        ('resolved', '해결'),
        ('rejected', '반려'),
    ]

    board = models.ForeignKey('FeedbackBoard', on_delete=models.CASCADE, related_name='feedbacks', verbose_name='게시판')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='처리 상태')
    requester = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name='feedbacks_requester')
    content = models.TextField(verbose_name='내용')
    created_at = models.DateTimeField(verbose_name='작성일시')
    related_image = models.ImageField(upload_to='school/FeedbackBoard/want/', blank=True, null=True)

    updated_at = models.DateTimeField(verbose_name='수정일시')
    answerer = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name='feedbacks_answerer')
    answered_at = models.DateTimeField(null=True, blank=True, verbose_name='답변 일시')
    answer_content = models.TextField(null=True, blank=True, verbose_name='답변 내용')
    answer_image = models.ImageField(upload_to='school/FeedbackBoard/answer_image/', null=True, blank=True, verbose_name='답변 관련 이미지')

    def __str__(self):
        return f'{self.title} - {self.get_status_display()}'

    def save(self, *args, **kwargs):
        # 두 이미지 필드에 대해 압축 처리
        if self.related_image:
            self.related_image = compress_image(self.related_image)
        if self.answer_image:
            self.answer_image = compress_image(self.answer_image)

        super().save(*args, **kwargs)