from django.shortcuts import render,HttpResponse,redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from CRM.models import *
import chunk,os
# Create your views here.

def index(request):

    return render(request,'index.html')

@login_required
def homework(request):
    if request.method=='POST':
        try:
            upload_files=request.FILES.dict()
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'upload_files')
            if not os.path.exists('%s/%s'%(path,request.user)):
                os.mkdir('%s/%s'%(path,request.user))
            for name,file in upload_files.items():
                f = open('%s/%s/%s-%s'%(path,request.user,name,file.name),'wb')
                for i in file.chunks():
                    f.write(i)
        except Exception as e:
            print(e)
        return redirect('student_index')
    homework_dict = {}
    try:
        stu_obj = Student.objects.get(user=request.user)
        stu_class_list = stu_obj.class_grades.all()
        for stu_class in stu_class_list:
            stu_homeworks= CourseRecord.objects.filter(class_grade=stu_class,has_homework=1).all()
            for homework in stu_homeworks:
                key = str(homework.date.strftime('%Y%m%d'))+homework.title
                homework_dict[key] = homework.content
    except Exception as e:
        print(e)
    return render(request,'student/homework.html',{'homework_dict':homework_dict})

@login_required
def score(request):
    score_list = []
    try:
        stu_obj = Student.objects.get(user=request.user)
        stu_score_list = StudyRecord.objects.filter(student=stu_obj).all().order_by('date')
        for record in stu_score_list:
            score_list.append({record.course_record:record.score})
    except Exception as e:
        print(e)
    return render(request,'student/score.html',{'score_list':score_list})

def contact_template(request):
    res={'contact_template':None,'contact':None}
    cls_id = request.GET.get('cls_id',None)
    cls_obj = ClassList.objects.get(id =cls_id)
    try:
        res['contact_template'] =str(cls_obj.contact_template)
        res['contact'] = str(cls_obj.contact_template.contact)
    except Exception as e:
        print(e)
    return JsonResponse(res)