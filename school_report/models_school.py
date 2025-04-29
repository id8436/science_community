from django.db import models
import os  # 파일 수정시간 파악을 위해..
from .models_base import School, Profile  # 같은 프로젝트 안의 model 내부 클래스들 사용 가능.
from PIL import Image, ExifTags
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from datetime import datetime

def compress_image(image_field, megabytes=0.5):
    '''다 jpeg 파일로 바꾸어 용량 낮추어 저장함.'''
    try:
        if image_field:
            img = Image.open(image_field)

            # EXIF 데이터를 통해 이미지 회전 처리
            try:
                # EXIF 데이터에서 회전 정보를 읽음
                for orientation in ExifTags.TAGS.keys():
                    if ExifTags.TAGS[orientation] == 'Orientation':
                        break
                exif = img._getexif()
                if exif is not None:
                    orientation_value = exif.get(orientation, None)
                    if orientation_value == 3:
                        img = img.rotate(180, expand=True)
                    elif orientation_value == 6:
                        img = img.rotate(270, expand=True)
                    elif orientation_value == 8:
                        img = img.rotate(90, expand=True)
            except (AttributeError, KeyError, IndexError):
                # EXIF 데이터가 없으면 예외가 발생할 수 있으므로 무시
                pass

            if img.mode != 'RGB':
                img = img.convert('RGB')

            output_io = BytesIO()
            quality = 85
            img.save(output_io, format='JPEG', quality=quality)

            while output_io.tell() > 1024 * 1024 * megabytes and quality > 10:  # 1024*1024가 1mb
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
def lost_item_upload_path(instance, filename):
    '''파일 저장 경로 지정.'''
    today = datetime.today()
    return f"school/lost_items/lost/{today.year}/{today.month:02d}/{today.day:02d}/{filename}"
def claimed_item_upload_path(instance, filename):
    today = datetime.today()
    return f"school/lost_items/claimed/{today.year}/{today.month:02d}/{today.day:02d}/{filename}"
class LostItem(models.Model):
    STATUS_CHOICES = [
        ('lost', '분실'),
        ('found', '찾음'),
    ]

    board = models.ForeignKey(LostItemBoard, on_delete=models.CASCADE, related_name='lost_items')
    author = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True)
    is_report = models.BooleanField(default=False)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='lost')
    modified_at = models.DateTimeField(auto_now=True)
    where = models.CharField(max_length=255)  # 관련 장소.
    when = models.DateTimeField(null=True, blank=True)  # 관련 시간.
    description = models.TextField()  # 물건 서술.

    photo_item = models.ImageField(upload_to=lost_item_upload_path, blank=True, null=True)
    photo_claimed = models.ImageField(upload_to=claimed_item_upload_path, blank=True, null=True)

    def __str__(self):
        return f"{self.description[:20]} - {self.get_status_display()}"

    def save(self, *args, **kwargs):
        # 두 이미지 필드에 대해 압축 처리
        if self.photo_item:
            self.photo_item = compress_image(self.photo_item)
        if self.photo_claimed:
            self.photo_claimed = compress_image(self.photo_claimed)

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # 파일을 삭제하는 로직
        if self.photo_item:
            if os.path.isfile(self.photo_item.path):
                os.remove(self.photo_item.path)
        if self.photo_claimed:
            if os.path.isfile(self.photo_claimed.path):
                os.remove(self.photo_claimed.path)
        super().delete(*args, **kwargs)
class SuggestionBoard(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='suggestion_board')
    # 교사가 남기는 공지성 메시지
    teacher_message = models.TextField(blank=True)
    teacher = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True)  # 메시지 작성자.
    message_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.school}"


class Suggestion(models.Model):
    STATUS_CHOICES = [
        ('pending', '대기'),
        ('in_progress', '진행'),
        ('resolved', '해결'),
        ('rejected', '반려'),
    ]

    board = models.ForeignKey('SuggestionBoard', on_delete=models.CASCADE, related_name='suggestion', verbose_name='게시판')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='처리 상태')
    requester = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name='suggestion_requester')
    content = models.TextField(verbose_name='내용')
    created_at = models.DateTimeField(verbose_name='작성일시')
    related_image = models.ImageField(upload_to='school/SuggestionBoard/want/', blank=True, null=True)

    updated_at = models.DateTimeField(verbose_name='수정일시')
    answerer = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name='suggestion_answerer')
    answered_at = models.DateTimeField(null=True, blank=True, verbose_name='답변 일시')
    answer_content = models.TextField(null=True, blank=True, verbose_name='답변 내용')
    answer_image = models.ImageField(upload_to='school/SuggestionBoard/answer_image/', null=True, blank=True, verbose_name='답변 관련 이미지')

    def __str__(self):
        return f'{self.title} - {self.get_status_display()}'

    def save(self, *args, **kwargs):
        # 두 이미지 필드에 대해 압축 처리
        if self.related_image:
            self.related_image = compress_image(self.related_image)
        if self.answer_image:
            self.answer_image = compress_image(self.answer_image)

        super().save(*args, **kwargs)