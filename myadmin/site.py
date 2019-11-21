
from myadmin.base_admin import BaseMyAdmin
class Adminsite(object):

	def __init__(self):
	
		self.enabled_admins={}


	def register(self,model_class,admin_class=None):
		app_name = model_class._meta.app_label
		model_name=model_class._meta.model_name
		#实例化admin_class，避免其他的model共用BaseGoldeightAdmin的内存冲突
		if admin_class:
			admin_class=admin_class()
		else:
			admin_class=BaseMyAdmin()
		admin_class.model=model_class
		if  app_name not in self.enabled_admins:
			self.enabled_admins[app_name]={}
		self.enabled_admins[app_name][model_name] = admin_class
site=Adminsite()