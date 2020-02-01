from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from myadmin.base_admin import BaseMyAdmin
from django.db.models import Q
from django import conf
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from myadmin import app_setup
from myadmin.site import site
from myadmin import form_handle
from CRM import models
import datetime,json

app_setup.myadmin_auto_discover()


@login_required
def app_index(request):

	return render(request,"myadmin/app_index.html",{"site":site})

# 字段过滤函数
def get_filter_result(request,querrysets):
	filter_condtions={}
	for key,val in request.GET.items():
		if key in ("_page","_o","_q"):continue
		if val:
			filter_condtions[key]=val
	return querrysets.filter(**filter_condtions),filter_condtions

# 按字段排序函数
def sort_reasult(request,querrysets,admin_class):
	current_order_column={}
	orderby_index=request.GET.get("_o")
	if orderby_index:
		orderby_key = admin_class.list_display[abs(int(orderby_index))]
		current_order_column[orderby_key] = orderby_index
		if orderby_index.startswith("-"):
			orderby_key = "-" + orderby_key
		return querrysets.order_by(orderby_key),current_order_column
	else:
		return querrysets,current_order_column

# 搜索框过滤函数
def search_filter(request,querrysets,admin_class):
		search_key = request.GET.get("_q")
		if search_key:
			q=Q()
			q.connector="OR"
			
			for search_field in admin_class.search_fields:
				q.children.append(("%s__contains"%search_field,search_key))
			return querrysets.filter(q)
		return querrysets


@login_required
def table_obj_list(request, app_name, model_name):
	"""myadmin 数据展示页 取model数据过滤后传给前端 """
	admin_class=site.enabled_admins[app_name][model_name]
	
	if request.method == "POST":
		
		selected_action =request.POST.get("action")
		selected_ids = json.loads(request.POST.get("selected_ids"))
		
		if not selected_action:
			if selected_ids:
				admin_class.model.objects.filter(id__in=selected_ids).delete()
		else:
			selected_objs = admin_class.model.objects.filter(id__in=selected_ids)
			admin_func_action=getattr(admin_class,selected_action)
			response=admin_func_action(request,selected_objs)
			if response:
				return response
	
	
	querrysets=admin_class.model.objects.all().order_by("-id")
	# 字段过滤
	querrysets,filter_condtions=get_filter_result(request,querrysets)
	admin_class.filter_condtions=filter_condtions
	
	# 搜索框过滤
	querrysets = search_filter(request, querrysets, admin_class)
	admin_class.search_key=request.GET.get("_q","")
	
	# 按字段排序
	querrysets,current_order_column=sort_reasult(request,querrysets,admin_class)
	
	# 分页过滤
	paginator = Paginator(querrysets,admin_class.list_per_page)
	page = request.GET.get("_page")
	try:
		querrysets = paginator.page(page)
	except PageNotAnInteger:
		querrysets = paginator.page(1)
	except EmptyPage:
		querrysets =paginator.page(paginator.num_pages)
	
	return render(request,"myadmin/table_obj_list.html",{
		"querrysets":querrysets,"site":site,"admin_class":admin_class,"current_order_column":current_order_column
	})

@login_required
def table_obj_change(request,app_name, model_name,tag_id):
	'''myadmin 数据修改页'''
	admin_class = site.enabled_admins[app_name][model_name]
	model_form=form_handle.create_dynamic_model_form(admin_class)
	obj=admin_class.model.objects.get(id=tag_id)
	if request.method == "GET":
		form_obj =model_form(instance=obj)
	elif request.method == "POST":
		form_obj = model_form(instance=obj,data=request.POST)
		if form_obj.is_valid():
			form_obj.save()
			if request.session['user_login_role']=='老师':
				return redirect('class_manage')
			return redirect("/myadmin/%s/%s"%(app_name,model_name))
	return render(request,"myadmin/table_obj_change.html",locals())

@login_required
def table_obj_delete(request,app_name, model_name,obj_id):
	admin_class = site.enabled_admins[app_name][model_name]
	obj = admin_class.model.objects.get(id=obj_id)
	
	if request.method == "POST":
		obj.delete()
		return redirect("/myadmin/{app_name}/{model_name}/".format(app_name=app_name,model_name=model_name))
	return render(request,"myadmin/table_obj_delete.html",locals())

@login_required
def table_obj_add(request,app_name, model_name):
	admin_class = site.enabled_admins[app_name][model_name]
	model_form = form_handle.create_dynamic_model_form(admin_class,form_add=True)
	if request.method == "GET":
		form_obj =model_form()
	elif request.method == "POST":
		form_obj = model_form(data=request.POST)
		if form_obj.is_valid():
			form_obj.save()
			if request.session['user_login_role']=='老师':
				return redirect('class_manage')
			return redirect("myadmin/%s/%s"%(app_name,model_name))
	return render(request,"myadmin/table_obj_add.html",locals())

def acc_login(request):
	error_msg = ""
	if request.method == "POST":
		username = request.POST.get("username")
		password = request.POST.get("password")
		
		user = authenticate(username=username, password=password)
		if user:
			login(request,user)
			return redirect(request.GET.get("next", "/myadmin/"))
		else:
			error_msg = "用户名或密码错误"
	
	return render(request, "myadmin/login.html", {"error_msg": error_msg})

def acc_logout(request):
	logout(request)
	
	return redirect("myadmin/login/")