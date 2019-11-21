
from django.urls import path,re_path,include
from CRM import views


urlpatterns = [
    path('',views.dashboard,name="sales_dashbord"),
    path('customers/',views.dashboard,name="sales_dashbord"),
    re_path('stu_enrollment/(\d+)/contact_audit/$',views.contact_audit,name="contact_audit"),
	path('stu_enrollment/', views.stu_enrollment, name="stu_enrollment"),
    re_path('enrollment/(\d+)/$',views.enrollment,name="enrollment"),
    re_path('enrollment/(\d+)/file-upload/$',views.enrollment_fileUpload,name="enrollment_fileUpload"),
    
]
