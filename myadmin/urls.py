
from django.contrib import admin
from django.urls import path,re_path,include
from myadmin import views


urlpatterns = [
    
    path('',views.app_index),
    path('login/', views.acc_login),
    path('logout/', views.acc_logout,name="logout"),
    re_path('(\w+)/(\w+)/(\d+)/change/$',views.table_obj_change,name="table_obj_change"),
    re_path('(\w+)/(\w+)/(\d+)/delete/$',views.table_obj_delete,name="obj_delete"),
    re_path('(\w+)/(\w+)/add/$',views.table_obj_add,name="table_obj_add"),
    re_path('(\w+)/(\w+)/$',views.table_obj_list,name="table_obj_list"),
    
    
]
