from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from CRM.models import *
from django.db.models import F,Q
from . import forms



def index(request):
    return render(request, 'index.html')


@login_required
def class_manage(request):
    user = request.user
    cls_list = ClassList.objects.filter(teachers=user).all()

    return render(request, 'teacher/class_manage.html', {'cls_list': cls_list})


@login_required
def class_manage_courserecord(request, **kwargs):
    if request.method == 'GET':
        response_content = ''
        cls_id = kwargs['cls_id']
        cls_obj = ClassList.objects.get(id=cls_id)
        # 目前思路  把想要的后端样式写成字符串返回给ajax，利用jq添加元素
        # 具体的功能可以请求myadmin下的具体链接，伪装成本页面搞定
        querrysets = CourseRecord.objects.filter(class_grade=cls_obj).all().order_by('-date')[:5]
        # 返回内容拼接
        thead = '''<div class="other_order"><a href='/myadmin/CRM/courserecord/'>查看更多</a>  <a href='/myadmin/CRM/courserecord/add/'>添加记录</a></div>
        
            <table class="table table-striped"><thead><tr>
                    <th>id</th>
                    <th>title</th>
                    <th>teacher</th>
                    <th>date</th>
                    <th>option</th></thead>'''
        tbody = '<tbody>'
        for index, record in enumerate(querrysets, 1):
            tbody += '''<tr>
                        <td><a href='/myadmin/CRM/courserecord/%s/change/'>%s</a></td>
                        <td>%s</td>
                        <td>%s</td>                   
                        <td>%s</td>
                        <td><a href='/teacher/class_manage/class_score/%s/'>班级成绩</a></td>                   
                    </tr>''' % (record.id, index, record.title, record.teacher, record.date, record.id)

        tbody += '</tbody>'
        tend = '</table>'

        response_content = thead + tbody + tend

        return JsonResponse(response_content, safe=False)


@login_required
def class_manage_classmember(request, **kwargs):
    if request.method == 'GET':
        cls_id = kwargs['cls_id']
        cls_obj = ClassList.objects.get(id=cls_id)
        cls_member_list = Student.objects.filter(class_grades__id=cls_obj.id).all()
        response_content = '<div>'
        for index, member in enumerate(cls_member_list, 1):
            if index % 6 == 0:
                response_content += '</div><div>'
            response_content += '<a href="/teacher/class_manage/classmember_score/%s/" class="btn btn-info">%s</a>   ' % (
            member.id, member.user.name)
        response_content += '</div>'

        return JsonResponse(response_content, safe=False)


def class_manage_classscore(request, **kwargs):
    if request.method == 'GET':
        record_id = kwargs['record_id']
        record_obj = CourseRecord.objects.get(id=record_id)
        cls_id = record_obj.class_grade.id
        cls_score_list = StudyRecord.objects.filter(course_record=record_obj).all().order_by('-score')

        has_score_stu_list = []
        for score_obj in cls_score_list:
            has_score_stu_list.append(str(score_obj.student.id))
        other_stu_list = Student.objects.filter(class_grades__id=cls_id).all().exclude(id__in=has_score_stu_list)

        return render(request, 'teacher/class_score_list.html',
                      {"cls_score_list": cls_score_list, "record_obj": record_obj, 'other_stu_list': other_stu_list})
    if request.method == 'POST':
        pass

        return redirect('class_manage_classscore')


def class_manage_classmember_score(request, **kwargs):
    if request.method == 'GET':
        stu_id = kwargs['stu_id']
        stu_obj = Student.objects.get(id=stu_id)
        stu_score_list = StudyRecord.objects.filter(student=stu_obj).order_by('-date')

        return render(request, 'teacher/classmember_score_list.html',
                      {"stu_obj": stu_obj, "stu_score_list": stu_score_list})


def class_manage_add_studyrecord(request, **kwargs):
    if request.method == 'GET':
        record_id = kwargs['record_id']
        student_id = request.GET.get('student_id')
        record_obj = CourseRecord.objects.get(id=record_id)
        student_obj = Student.objects.get(id=student_id)
        studyrecordForm = forms.StudyRecordForm(initial={"course_record": record_obj, "student": student_obj})
        response = ''
        for field in studyrecordForm:
            response += '<lable class="label label-primary" for="id_%s">%s</lable>' % (field.name, field.label)
            response += '%s' % field
            response += '<br>'
        return JsonResponse(response, safe=False)
    if request.method == 'POST':
        # __init__() got an unexpected keyword argument 'student'
        # student_obj = Student.objects.get(id=request.POST['student'])
        # record_obj = CourseRecord.objects.get(id=request.POST['course_record'])
        # submit_dict = request.POST.copy()
        # submit_dict['student'] = student_obj
        # submit_dict['course_record'] = record_obj
        # studyrecordForm = forms.StudyRecordForm(**submit_dict)
        # if studyrecordForm.is_valid():
        #     studyrecordForm.save()
        #     return redirect('/teacher/class_manage/class_score/%s/'%request.POST['course_record'])
        # else:
        #     return HttpResponse(studyrecordForm.errors)
        student_obj = Student.objects.get(id=request.POST['student'])
        record_obj = CourseRecord.objects.get(id=request.POST['course_record'])

        StudyRecord.objects.get_or_create(student=student_obj,course_record=record_obj,
                                          score=request.POST['score'],show_status=request.POST['show_status'],
                                          note=request.POST['note']
                                          )
        return redirect('/teacher/class_manage/class_score/%s/' % record_obj.id)
