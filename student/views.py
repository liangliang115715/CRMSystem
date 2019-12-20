from django.shortcuts import render,HttpResponse,redirect
from CRM.models import *
import chunk,os
# Create your views here.


def index(request):

    return render(request,'index.html')

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
        stu_class = stu_obj.class_grades.get()
        stu_homeworks= CourseRecord.objects.filter(class_grade=stu_class,has_homework=1).all()
        for homework in stu_homeworks:
            key = str(homework.date.strftime('%Y%m%d'))+homework.title
            homework_dict[key] = homework.content
    except Exception as e:
        print(e)
    return render(request,'student/homework.html',{'homework_dict':homework_dict})

