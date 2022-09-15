from .settings import *

DEBUG = False  # DEBUG=True이면 개발모드, False면 운영모드로 인식한다.

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'mysite',
        'USER': 'user',
        'PASSWORD': '1234',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}