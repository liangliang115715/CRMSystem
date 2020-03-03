from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import HttpResponse
from django.middleware import csrf
from importlib import import_module
from CRM.models import *
import re

role_to_urlprefix_dict = {
    '老师': {'prefix': 'teacher', 'extra_url': [
                                                    r'/myadmin/CRM/courserecord/$',
                                                    r'/myadmin/CRM/studyrecord/$',
                                                    r'/myadmin/CRM/courserecord/(?P<action_teacher_2>add)/$',
                                                    r'/myadmin/CRM/studyrecord/(?P<action_teacher_2>add)/$',
                                                    r'/myadmin/CRM/courserecord/(?P<id>\d+)/(?P<action_teacher_3>\w+)/$',
                                                    r'/myadmin/CRM/studyrecord/(?P<id>\d+)/(?P<action_teacher_3>\w+)/$',

                                              ]},
    '学生': {'prefix': 'student', 'extra_url': []},
    '销售': {'prefix': 'CRM', 'extra_url': [
                                                    r'/myadmin/CRM/customerinfo/$',
                                                    r'/myadmin/CRM/customerinfo/(?P<action_crm_2>add)/$',
                                                    r'/myadmin/CRM/customerinfo/(?P<id>\d+)/(?P<action_crm_3>\w+)/$'
                                                ]},
}
class ValidationPass(Exception):
    def __init__(self):
        pass
class PermissionViewMiddleware(MiddlewareMixin):

    def process_request(self, request):
        try:
            #学生注册的特例  包含一个表单页面和文件传输两个路由
            if re.match(re.compile('/CRM/enrollment/'),request.path):raise ValidationPass
            # 判断通行的url请求：
            pass_url_prefix = ['admin', 'login', 'logout', 'changepwd', 'favicon.ico','static','']
            request_prefix = request.path.split("/")
            if request_prefix[1] == 'CRM' and not request_prefix[2]: raise ValidationPass
            if request_prefix[1] in pass_url_prefix: raise ValidationPass
            login_role = request.session['user_login_role']
            login_user = request.user
            # 判断登录角色的合法性，防止篡改session中的user_login_role
            if login_role == '管理员':
                if login_user.is_superuser():
                    raise ValidationPass
                else:
                    raise Exception
            login_role = Role.objects.get(name=login_role)
            if str(login_role) not in [str(role_obj) for role_obj in login_user.role.all()] : raise Exception
            # 判断权限匹配结果
            resulte = self.judge_request(request,login_role)
            if not resulte: raise Exception
        except ValidationPass:
            pass
        except Exception as e:
            return HttpResponse("you doesn't have this permission!!!\n",e)

    def judge_request(self,request,login_role):
        role_prefix = role_to_urlprefix_dict[str(login_role)]['prefix']
        role_extra_allowed_urls = role_to_urlprefix_dict[str(login_role)]['extra_url']
        try:
            # 导入相应模块下的url路由
            urlconf_module = import_module(role_prefix)
            # 匹配对应模块下的路由
            urlpatterns = getattr(urlconf_module.urls, 'urlpatterns')
            for url_obj in urlpatterns:
                matching_url_list = request.path.split(role_prefix + '/')
                match_url = url_obj.resolve(matching_url_list[1]) if len(matching_url_list) > 1 else None
                if match_url: return True
            # 判断特殊路由,匹配成功返回True，失败False；
            for url in role_extra_allowed_urls:
                match_url = re.match(re.compile(url), request.path)
                if match_url:
                    match_group = [ arg for arg in match_url.groups()]
                    judge_resulte = self.judge_action_object(request, login_role,match_group)
                    return judge_resulte
            return False
        except Exception as e:
            print('judge_error',e)
            return False

    def judge_action_object(self,request,login_role,match_group):
        '''判断操作的对象是否在权限中,返回（True/False）
            对于老师 add，change，delete只能操作自己班级成员。
            对于销售 add，change，delete只能添加自己的客户

            match_group最多有3个参数：
              0个：展示列表
              1个：add请求（add，）
              2个：change/delete请求（xx，change/delete）
        '''
        if request.method == 'GET':
            if len(match_group) < 2:
                return True
            action_id = int(match_group[0])
            allwed_action_id_list = []

            if str(login_role) == '老师':
                action_table = request.path.split('/')[3]
                tea_couserrecord_list = CourseRecord.objects.filter(teacher=request.user).all()
                tea_couserrecord_id_list = [course.id for course in tea_couserrecord_list]
                if action_table == 'courserecord':
                    allwed_action_id_list=tea_couserrecord_id_list
                elif action_table=='studyrecord':
                    allwed_action_id_list = [record.id for record in StudyRecord.objects.filter().all()]
            elif str(login_role) == '销售':
                allwed_action_id_list = [customer.id for customer in CustomerInfo.objects.filter(consultant__id = request.user.id).all()]
            if action_id not in allwed_action_id_list: return False
            return True
        elif request.method == 'POST':
            if len(match_group):
                action = match_group[1]
                action_id = None
                allwed_action_id_list = []
                if str(login_role) == '老师':
                    action_table = request.path.split('/')[3]
                    tea_cls_list = ClassList.objects.filter(teachers__id=request.user.id).all()
                    tea_cls_id_list = [cls.id for cls in tea_cls_list]
                    tea_couserrecord_list = [courserecord.id for courserecord in
                                             CourseRecord.objects.filter(teacher=request.user).all()]
                    tea_student_id_list = [stu.id for stu in
                                        Student.objects.filter(class_grades__in=tea_cls_id_list).all()]
                    if action_table == 'courserecord':
                        if action == 'delete':
                            action_id =int(match_group[0])
                            allwed_action_id_list = tea_couserrecord_list
                        else:
                            action_id =(int(request.POST['teacher'][0]),int(request.POST['class_grade'][0]))
                            allwed_action_id_list=[(request.user.id,id)for id in tea_cls_id_list]
                    elif action_table == 'studyrecord':
                        if action == 'delete':
                            action_id = int(match_group[0])
                            allwed_action_id_list = [record.id for record in StudyRecord.objects.filter(course_record__id__in=tea_couserrecord_list).all()]
                        else:
                            course_record_id = int(request.POST['course_record'][0])
                            if course_record_id not in tea_couserrecord_list:return False
                            action_id=(course_record_id,int(request.POST['student'][0]))
                            allwed_action_id_list=[(course_record_id,id)for id in tea_student_id_list]
                elif str(login_role) == '销售':
                    action_id = int(match_group[0])
                    allwed_action_id_list = [customer.id for customer in CustomerInfo.objects.filter(consultant__id = request.user.id).all()]
                if action_id not in allwed_action_id_list: return False
                return True
        return True





