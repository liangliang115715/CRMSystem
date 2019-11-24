from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth import login,logout
from django.db.models import Q
from CRM.models import UserProfile
import json


# 个性化验证，返回一个user对象,检测密码要用对象的check_password方法。
def authenticate(request=None,**conditions):
    try:
        user = UserProfile.objects.get(Q(name=conditions['username'])|Q(email=conditions['username']))
        if user.check_password(conditions['password']):
            role_list = []
            for role in user.role.values('name'):
                role_list.append(role['name'])
            user = user if conditions['role'] in role_list else None
        else:
            user=None
    except Exception:
        user = None
    return user

def acc_login(request):
    error_msg=""
    if request.method=="POST":
        username=request.POST.get("username",None)
        password=request.POST.get("password",None)
        role = request.POST.get("role",None)
        user=authenticate(username=username,password=password,role=role)
        if user:
            login(request,user)
            return redirect(request.GET.get("next","/CRM/"))
        else:
            error_msg="用户名或密码错误"
    
    return render(request,"login.html",{"error_msg":error_msg})

def acc_logout(request):
    
    logout(request)
    
    return redirect("/login/")

def changepwd(request):
    error=None
    user = request.user
    if request.method == "POST":
        raw_password = request.POST.get('raw_password',None)
        new_password = request.POST.get('new_password',None)
        print('new_password:',new_password,'user:',user)
        print(new_password,user.check_password(789))
        if new_password and user.check_password(raw_password):
            user.set_password(new_password)
            user.save()
            return redirect('/login/')
        else:error='身份信息验证失败'

    return render(request,'changepwd.html',{'error':error})