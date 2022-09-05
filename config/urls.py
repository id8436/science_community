"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls'), name=""),
    path('accounts/', include('allauth.urls')), # allauth의 기능을 accounts라는 주소 아래 담는다.
    path('custom_account/', include('custom_account.urls')),
    path('boards/', include('boards.urls')),
    path('item_pool/', include('item_pool.urls')),
    path('school_report/', include('school_report.urls')),
]

# 미디어 파일을 위한 url
from django.conf.urls.static import static
from django.conf import settings
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# static을 연결하는데, 경로는 settings에서 설정한 MEDIA_URL로,
# 실제경로는 settings에서 설정한 MEDIA_ROOT로  지정한다.