
from django.forms import ModelForm


def create_dynamic_model_form(admin_class,form_add=False):
	class Meta:
		model = admin_class.model
		fields="__all__"
		if form_add:
			admin_class.form_add = True
		else:
			exclude = admin_class.readonly_fields
			admin_class.form_add =False
			
	def __new__(cls,*args,**kwargs):
		for field_name in cls.base_fields:
			field_obj = cls.base_fields[field_name]
			field_obj.widget.attrs.update({"class":"form-control"})
		return ModelForm.__new__(cls)
	
	dynamic_form = type("DanamicModelForm",(ModelForm,),{"__new__":__new__,"Meta":Meta})
	
	return dynamic_form