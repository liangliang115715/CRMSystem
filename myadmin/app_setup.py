
from django import conf


def myadmin_auto_discover():
	
	for app_name in conf.settings.INSTALLED_APPS:
		try:
			mod=__import__("%s.myadmin"%app_name)
		except ImportError as e:
			pass