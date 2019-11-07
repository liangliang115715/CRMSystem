from CRM import models
from myadmin.site import site
from myadmin.base_admin import BaseMyAdmin

class CustomerAdmin(BaseMyAdmin):
	list_display = ["id","name","source","contact_type","contact","consultant","consult_content","status","date"]
	list_filter = ["source","contact_type","consultant","status","date"]
	search_fields = ["contact","consultant__name"]
	readonly_fields=["status","date"]
	filter_horizontal= ["consult_courses",]
	list_per_page = 4
	actions = ["change_status",]
	
	def change_status(self,request,querrysets):
		print(querrysets)
		
class StudenAdmin(BaseMyAdmin):
	# list_display = ["customer","class_grades"]
	filter_horizontal = ["class_grades"]
	
site.register(models.CustomerInfo,CustomerAdmin)
site.register(models.Role)
site.register(models.Branch)
site.register(models.ClassList)
site.register(models.Course)
site.register(models.CourseRecord)
site.register(models.StudyRecord)
site.register(models.Student,StudenAdmin)



