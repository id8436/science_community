from __future__ import absolute_import, unicode_literals

import os

from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')  # 설정파일 위치.

app = Celery('config')  # 보통 settings.py 파일이 있는 디렉토리 이름을 넣는다.

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')  # 장고의 설정을 읽고, 네임스페이스를 설정한다.

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()  # 선택사항. 자동으로 하위 앱의 tasks.py를 탐색한다.