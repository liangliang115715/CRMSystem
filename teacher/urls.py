"""student URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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

from django.urls import path,re_path,include
from teacher import views

urlpatterns = [
    re_path('class_manage/courserecord/(?P<cls_id>\d+)/$', views.class_manage_courserecord, name='class_manage_courserecord'),
    re_path('class_manage/classmember/(?P<cls_id>\d+)/$', views.class_manage_classmember, name='class_manage_classmember'),
    re_path('class_manage/class_score/(?P<record_id>\d+)/$', views.class_manage_classscore, name='class_manage_classscore'),
    re_path('class_manage/class_score/(?P<record_id>\d+)/add_studyrecord/$', views.class_manage_add_studyrecord, name='class_manage_add_studyrecord'),
    re_path('class_manage/classmember_score/(?P<stu_id>\d+)/$', views.class_manage_classmember_score, name='class_manage_classmember_score'),

    path('',views.index,name='teacher_index'),
    path('class_manage/',views.class_manage,name='class_manage'),
]
