
from django.template import Library
from django.utils.safestring import mark_safe
import time,datetime


register = Library()


@register.simple_tag
def build_table_row(tag,admin_class):
	ele=""
	if admin_class.list_display:
		for index,column_name in enumerate(admin_class.list_display):
			
			column_obj = admin_class.model._meta.get_field(column_name)#获取自定义admin list_display中的对应字段对象
			
			if column_obj.choices:
				column_data = getattr(tag,"get_%s_display"%column_name)() # 获取带XX_type_choices中数字的对应值
			else:
				column_data = getattr(tag,column_name) # 一般字段提取字段值
			td_ele = "<td>%s</td>"%column_data
			
			if index == 0:
				td_ele="<td><a href='%s/change'>%s</a></td>"%(tag.id,column_data)
			
			ele+=td_ele
	else:
		td_ele = "<td><a href='%s/change'>%s</a></td>" %(tag.id,tag)
		ele += td_ele
	return mark_safe(ele)
@register.simple_tag
def build_filter_ele(filter_column,admin_class):
	column_obj=admin_class.model._meta.get_field(filter_column)
	try:
		filter_ele = "<select name='%s'>" % filter_column
		for choice in column_obj.get_choices():
			selected = ""
			# if filter_column in admin_class.filter_condtions:
			if str(choice[0]) == admin_class.filter_condtions.get(filter_column):
				selected="selected"
			option="<option value='%s' %s>%s</option>"%(choice[0],selected,choice[1])
			filter_ele += option
	except AttributeError:
		filter_ele = "<select name='%s__gte'>" % filter_column
		if column_obj.get_internal_type() in ('DateTimeField','DateField'):
			time_obj=datetime.datetime.now()
			time_list=[
				["","----------"],
				[time_obj.replace(day=1),"本月内"],
				[time_obj.replace(month=1,day=1),"一年内"],
				[time_obj, "Today"],
				[time_obj - datetime.timedelta(3), "三天内"],
				[time_obj - datetime.timedelta(90), "三个月内"],
				["","ALL"],
			]
			option=""
			for i in time_list:
				select=""
				i[0] = "" if not i[0] else "%s-%s-%s"%(i[0].year,i[0].month,i[0].day)
				if i[0] == admin_class.filter_condtions.get("%s__gte"%filter_column):
					select="selected"
				# 每年的一号和每月的一号 显示会出bug，应该要用正则解决
				# if i[0] == "%s-1-1"%(i[0].year) and i[1] == "一年内":
				# 	select=""
				# if i[0] == "%s-%s-1"%(i[0].year,i[0].month) and i[1] == "本月内":
				# 	select=""
				option += "<option value=%s %s>%s</option>"%(i[0],select,i[1])
			filter_ele += option
			
	filter_ele += "</select>"
	return mark_safe(filter_ele)
@register.simple_tag
def get_column_model_name(admin_class):
	"""返回当前表单名（大写）"""
	return admin_class.model._meta.model_name.upper()

@register.simple_tag
def get_readonly_field_obj(form_obj,field):
	"""获取只读字段对象"""
	return getattr(form_obj.instance,field)

@register.simple_tag
def rander_paginator(querrysets,current_order_column):
	"""创建底部分页"""
	ele='''<ul class="pagination">'''
	sorted_ele = ""
	if current_order_column:
		sorted_ele = "&_o=%s" % list(current_order_column.values())[0]
	if querrysets.number-1 > 0:
		ele += '''<li><a href="?_page=%s%s" aria-label="Previous"><span aria-hidden="true">
					&laquo;</span></a></li>'''%(querrysets.number-1,sorted_ele)
	
	for i in querrysets.paginator.page_range:
		if abs(querrysets.number - i) < 2:
			active=""
			if querrysets.number == i:
				active = "active"
			p_ele='''<li class=%s><a  href="?_page=%s%s">%s</a></li>'''%(active,i,sorted_ele,i)
			ele += p_ele
	if querrysets.number+1 in querrysets.paginator.page_range:
		ele += ''' <li><a href="?_page=%s%s" aria-label="Next">
					<span aria-hidden="true">&raquo;</span></a>'''%(querrysets.number+1,sorted_ele)
	ele += "</ul>"
	return mark_safe(ele)

@register.simple_tag
def render_filters(admin_class):
	ele = ""
	if admin_class.filter_condtions:
		for k,v in admin_class.filter_condtions.items():
			ele += "&%s=%s"%(k,v)
	return ele


@register.simple_tag
def get_order_result(current_order_column,column,forloop):
	"""生成升降序的url后缀"""
	if column in current_order_column:
		if int(current_order_column[column]) == forloop:
			forloop = str(-1*forloop)
			if current_order_column[column]=="0":
				forloop = "-"+str(forloop)
	return forloop
@register.simple_tag
def generater_arrow (column,current_order_column):
	"""生成升序或降序的箭头样式"""
	ele = ""
	if column in current_order_column:
		if current_order_column[column]== "-0" or int(current_order_column[column]) < 0 :
			ele += '''<span class="glyphicon glyphicon-menu-down" aria-hidden="true"></span>'''
		else:
			ele += '''<span class="glyphicon glyphicon-menu-up" aria-hidden="true"></span>'''
	return mark_safe(ele)

@register.simple_tag
def get_current_sorted_conditions(current_order_column):
	"""生成排序字段的url后缀"""
	value=""
	if current_order_column:
		value=list(current_order_column.values())[0]
	return value

@register.simple_tag
def get_available_m2m_data(field_name,form_obj,admin_class):
	"""返回m2m字段关联表的所有数据"""
	field_obj = admin_class.model._meta.get_field(field_name)
	obj_list = set(field_obj.related_model.objects.all())
	if form_obj.instance.id:
		selected_data = set(getattr(form_obj.instance,field_name).all())
	
		return obj_list - selected_data
	else:
		return obj_list
@register.simple_tag
def get_selected_m2m_data(field_name,form_obj,admin_class):
	"""返回已选择的m2m关联字段"""
	if form_obj.instance.id:
		selected_data = getattr(form_obj.instance,field_name).all()
		
		return selected_data
	else:
		return None

@register.simple_tag
def display_all_related_objs(obj):
	
	"""显示要删除的对象的所有关联数据"""
	ele = "<ul>"
	for reverse_fk_obj in obj._meta.related_objects:
		related_table_name = reverse_fk_obj.name # 取得多对一的表名
		related_lookup_key = "%s_set"%related_table_name # 准备反向查询关联数据
		related_objs = getattr(obj,related_lookup_key).all() # 通过反射查询的到关联对象
		
		ele += "<li>%s<ul>"%related_table_name
		#打印关联对象名称
		if reverse_fk_obj.get_internal_type() == "ManyToManyField":
			for i in related_objs:
				ele += "<li><a href='/myadmin/%s/%s/%s/change/'>%s</a> 与%s相关数据将被删除</li>"\
				       %(i._meta.app_label,i._meta.model_name,i.id,i,obj)
			ele += "</ul></li>"
		else:
			for i in related_objs:
				ele += "<li><a href='/myadmin/%s/%s/%s/change/'>%s</a></li>" % (i._meta.app_label, i._meta.model_name, i.id,i)
				ele += display_all_related_objs(i)
			ele += "</ul></li>"
	ele +="</ul>"
	
	return ele

@register.simple_tag
def delete_cancle_href(obj):
	app_name = obj._meta.app_label
	model_name = obj._meta.model_name
	href = "/myadmin/%s/%s/%s/change"%(app_name,model_name,obj.id)
	return href
	
	
	
	