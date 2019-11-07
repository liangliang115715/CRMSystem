from django.shortcuts import render, HttpResponse, redirect
import json
class BaseMyAdmin(object):
	def __init__(self):
		self.actions.extend(self.defult_actions)
	
	list_display = []
	list_filter = []
	search_fields = []
	readonly_fields=[]
	filter_horizontal = []
	list_per_page = 5
	defult_actions=["delete_all_selected_objs"]
	actions=[]
	
	def delete_all_selected_objs(self,request,querrysets):
		
		querryset_ids=json.dumps([i.id for i in querrysets])
		return render(request,"goldeight/table_obj_delete.html",{"admin_class":self,
		                                                         "objs":querrysets,"querryset_ids":querryset_ids,
		                                                         })