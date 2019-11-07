
from django import conf


def Goldeight_auto_discover():
	
	for app_name in conf.settings.INSTALLED_APPS:
		try:
			mod=__import__("%s.GoldeightAdmin"%app_name)
		except ImportError as e:
			pass