from django.forms import ModelForm,ValidationError
from CRM import models
# from django.db import models as dbmodels

class CustomerForm(ModelForm):

	def __new__(cls, *args, **kwargs):
		for field_name in cls.base_fields:

			field_obj = cls.base_fields[field_name]
			field_obj.widget.attrs.update({"class": "form-control"})
			
			if field_name in cls.Meta.readonly_fields:
				field_obj.widget.attrs.update({"disabled": "true"})
	
		return ModelForm.__new__(cls)
	
	def clean(self):
		if self.errors:
			raise ValidationError(("Please fix errors befo re-submit"))
		if self.instance.id is not None:
			for field in self.Meta.readonly_fields:
				old_field_val = getattr(self.instance,field)
				form_val = self.cleaned_data.get(field)
				
				if old_field_val != form_val:
					self.add_error(field,"Readonly Field: field must be {value} not {new_value}".format
					(**{"value":old_field_val,"new_value":form_val}))
		if not self.cleaned_data['email']:
			raise ValidationError(('email is required'))
	class Meta:
		model = models.CustomerInfo
		fields = "__all__"
		exclude = ["consult_content","status","consult_courses",]
		readonly_fields = ["contact_type","contact","consultant","referral_from","source",]
			
class EnrollmentForm(ModelForm):
	def __new__(cls, *args, **kwargs):
		for field_name in cls.base_fields:
			field_obj = cls.base_fields[field_name]
			field_obj.widget.attrs.update({"class": "form-control"})
			
			if field_name in cls.Meta.readonly_fields:
				field_obj.widget.attrs.update({"disabled": "true"})
		
		return ModelForm.__new__(cls)
	
	def clean(self):
		if self.errors:
			raise ValidationError(("Please fix errors befo re-submit"))
		if self.instance.id is not None:
			for field in self.Meta.readonly_fields:
				old_field_val = getattr(self.instance, field)
				form_val = self.cleaned_data.get(field)
				
				if old_field_val != form_val:
					self.add_error(field, "Readonly Field: field must be {value} not {new_value}".format
					(**{"value": old_field_val, "new_value": form_val}))
	
	class Meta:
		model = models.StudentEnrollment
		fields = "__all__"
		exclude = ["contract_aproved_date",]
		readonly_fields = ["contract_agreed",]
	
	