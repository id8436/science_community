from django.db import models
from django.conf import settings

class Task(models.Model):
    '''언젠가 셀러리에 넣을 자료를 지정한다.'''
    created = models.DateTimeField(auto_now_add=True)
    modify_date = models.DateTimeField(auto_now=True, null=True, blank=True)  # 수정되면 자동으로...
    content = models.TextField(default=None)  # 처리할 데이터. 혹은 메모.
    completion_status = models.BooleanField(default=False)
    error_message = models.TextField(null=True, blank=True)


class UploadedImage(models.Model):
    image = models.ImageField(upload_to='uploaded_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image {self.id} - {self.image.name}"