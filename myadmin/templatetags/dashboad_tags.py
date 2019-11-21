
from django.template import Library
from django.utils.safestring import mark_safe
from django.urls import reverse
register = Library()

@register.simple_tag
def get_menu_list(user):
    menu_list= []
    s = '' #返回的结果
    role_list = user.role.all()
    for role in role_list:
        for menu in role.menus.select_related():
            if menu not in menu_list:
                menu_list.append(menu)

    for menu in menu_list:
        if menu.url_type == 0:
            s += '<li><a href="%s">%s</a></li>'%(menu.url_name,menu.name)
        else:
            str = reverse(menu.url_name)
            s +='<li><a href="%s">%s</a></li>'%(str,menu.name)

    return mark_safe(s)