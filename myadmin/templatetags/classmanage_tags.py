from django.template import Library
register = Library()


@register.simple_tag
def get_status_sign(status):
    status_list = {0:'glyphicon glyphicon-remove', 1: 'glyphicon glyphicon-ok', 2: 'glyphicon glyphicon-log-in',
                   3: 'glyphicon glyphicon-log-out'}
    return  status_list[int(status)]
