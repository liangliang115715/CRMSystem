from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth.decorators import login_required
from CRM import models,forms
from django.views.decorators.csrf import csrf_exempt
from django import conf
import os,json
from django.utils.timezone import datetime
from django.db.utils import IntegrityError
# Create your views here.

@login_required
def dashboard(request):
	
	return render(request,"crm/dashboard.html")

@login_required
def stu_enrollment(request):
	'''开始学生注册'''
	customers = models.CustomerInfo.objects.all()
	class_list = models.ClassList.objects.all()
	if request.method == "POST":
		customer_id = request.POST.get("customer_id")
		class_grade_id = request.POST.get("class_grade_id")
		try:
			enrollment_obj = models.StudentEnrollment.objects.create(
				customer_id = customer_id,
				class_grade_id = class_grade_id,
				consultant_id = request.user.id,
			)
		except Exception as e:
			enrollment_obj = models.StudentEnrollment.objects.get(customer_id = customer_id,class_grade_id = class_grade_id)
			if enrollment_obj.contract_agreed:
				return redirect("crm/stu_enrollment/%s/contact_audit/"%enrollment_obj.id)
		
		enrollment_link = "http://localhost:8000/CRM/enrollment/%s"%enrollment_obj.id
		
	return render(request,"crm/stu_enrollment.html",locals())

@login_required
def contact_audit(request,enrollment_id):
	'''报名审核'''
	enrollment_obj = models.StudentEnrollment.objects.get(id=enrollment_id)
	if request.method == "POST":
		enrollment_form = forms.EnrollmentForm(instance=enrollment_obj,data=request.POST)
		if enrollment_form.is_valid():
			if enrollment_form.cleaned_data['contract_agreed']:
				enrollment_obj.contract_aproved = True
			enrollment_form.save()
			# save之前帮客户注册一个userprofile，分配一个统一的初始密码
			new_user_role = models.Role.objects.get(name='学生')
			new_user_obj = models.UserProfile.objects.get_or_create(
				**{'email':enrollment_form.instance.customer.email,'name':enrollment_form.instance.customer.name,'password':'999999'}
			)[0]
			new_user_obj.role.add(new_user_role)
			stu_obj = models.Student.objects.get_or_create(customer=enrollment_obj.customer,user=new_user_obj)[0]
			stu_obj.class_grades.add(enrollment_obj.class_grade_id)
			stu_obj.save()
			enrollment_obj.customer.status = 1
			enrollment_obj.customer.save()
			
			return redirect("/myadmin/CRM/customerinfo/%s/change"%enrollment_obj.customer.id)
		
	else:
		customer_form = forms.CustomerForm(instance=enrollment_obj.customer)
		enrollment_form = forms.EnrollmentForm(instance=enrollment_obj)
	return render(request,"crm/contact_audit.html",locals())


def enrollment(request,enrollment_id):
	'''学生注册具体信息'''
	enrollment_obj = models.StudentEnrollment.objects.get(id = enrollment_id)
	if enrollment_obj.contract_agreed:
		if enrollment_obj.contract_aproved and enrollment_obj.customer.email:
			return redirect('/login/')
		return HttpResponse("合同正在审核中，请耐心等待！")

	if request.method == "POST":
		contact_agreed = request.POST.get("contact_agreed")
		customer_form = forms.CustomerForm(instance=enrollment_obj.customer,data=request.POST)
		if customer_form.is_valid() and contact_agreed:
			customer_form.save()
			enrollment_obj.contract_agreed = True
			enrollment_obj.contract_signed_date = datetime.now()
			enrollment_obj.save()
			return HttpResponse("报名信息已提交，请您耐心等待审批结果！！！")
	elif request.method=='GET':
		customer_form = forms.CustomerForm(instance=enrollment_obj.customer)
	# """列出已上传文件"""
	uploaded_files = []
	enrollment_upload_dir = os.path.join(conf.settings.CRM_FILE_UPLOAD_DIR, enrollment_id)
	if  os.path.isdir(enrollment_upload_dir):
		
		uploaded_files = os.listdir(enrollment_upload_dir)
	
	return render(request,"crm/enrollment.html",locals())

@csrf_exempt
def enrollment_fileUpload(request,enrollment_id):
	response = {"status": True, "error_msg": ""}
	enrollment_upload_dir = os.path.join(conf.settings.CRM_FILE_UPLOAD_DIR,enrollment_id)
	if not os.path.isdir(enrollment_upload_dir):
		os.mkdir(enrollment_upload_dir)
	file_obj = request.FILES.get("file")
	if len(os.listdir(enrollment_upload_dir)) <= 3:
		
		with open(os.path.join(enrollment_upload_dir,file_obj.name),"wb") as f:
			for chunks in file_obj.chunks():
				f.write(chunks)
	else:
		response["status"] = False
		response["error_msg"] = "最大传输文件个数为3"
	return HttpResponse(json.dumps(response))
	