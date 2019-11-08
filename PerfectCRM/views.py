from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth import login,logout
from django.db.models import Q
from CRM.models import UserProfile



# 个性化验证，返回一个user对象,检测密码要用对象的check_password方法。
def authenticate(request=None,**conditions):
    try:
        user = UserProfile.objects.get(Q(name=conditions['username'])|Q(email=conditions['username']))
        if user.check_password(conditions['password']):
            role_list = []
            for role in user.role.values('name'):
                role_list.append(role['name'])
            user = user if conditions['role'] in role_list else None
    except Exception as e:
        print(e)
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