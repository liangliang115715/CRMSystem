from django.db import models
from django.contrib.auth.models import User
# Create your models here.

from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser,PermissionsMixin
)


class UserProfileManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            name=name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
            name=name,
        )
        user.is_superuser = True
        user.save(using=self._db)
        return user


class UserProfile(AbstractBaseUser,PermissionsMixin):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    name = models.CharField(max_length=32, verbose_name="用户名",unique=True)
    role = models.ManyToManyField("Role", blank=True, verbose_name="用户角色")

    is_active = models.BooleanField(default=True)
    # is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=True)
    objects = UserProfileManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    class Meta:
        verbose_name_plural="用户信息表"
    def __str__(self):
        return self.name

    # def has_perm(self, perm, obj=None):
    #     "Does the user have a specific permission?"
    #     # Simplest possible answer: Yes, always
    #     return True
    #
    # def has_module_perms(self, app_label):
    #     "Does the user have permissions to view the app `app_label`?"
    #     # Simplest possible answer: Yes, always
    #     return True

    # @property
    # def is_staff(self):
    #     "Is the user a member of staff?"
    #     # Simplest possible answer: All admins are staff
    #     return self.is_admin

# class UserProfile(models.Model):
#     """用户信息表"""
#     user=models.OneToOneField(User,on_delete=models.CASCADE,verbose_name="用户")
#     name=models.CharField(max_length=32,verbose_name="用户名")
#     role=models.ManyToManyField("Role",blank=True,verbose_name="用户角色")
#
#     def __str__(self):
#         return self.name
#     class Meta:
#         verbose_name_plural="用户信息表"


class Role(models.Model):
    """角色表"""
    name=models.CharField(max_length=32,verbose_name="角色名称")
    menus=models.ManyToManyField("Menus",verbose_name="分配权限",blank=True)

    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = "角色表"

class CustomerInfo(models.Model):
    """客户信息表"""
    name=models.CharField(max_length=32,default=None,verbose_name="客户姓名")
    contact_type_choice=((0,"qq"),(1,"微信"),(2,"手机号"))
    contact_type=models.SmallIntegerField(choices=contact_type_choice,default=0,verbose_name="联系方式")
    contact = models.CharField(max_length=64,unique=True,verbose_name="联系方式号码")
    source_choices=((0,"QQ群"),
                    (1,"51CTO"),
                    (2,"百度推广"),
                    (3,"知乎"),
                    (4,"转介绍"),
                    (5,"其他"),
                    )
    source=models.SmallIntegerField(choices=source_choices,verbose_name="用户来源")
    referral_from=models.ForeignKey("self",verbose_name="转介绍人",on_delete=models.CASCADE,blank=True,null=True)
    consult_courses = models.ManyToManyField('Course', verbose_name="咨询课程")
    consult_content=models.TextField(verbose_name="咨询内容",blank=True)
    status_choices=((0,"未报名"),(1,"已报名"),(2,"已退学"))
    status= models.SmallIntegerField(choices=status_choices,verbose_name="客户跟踪状态")
    consultant=models.ForeignKey("UserProfile",verbose_name="课程顾问",on_delete=models.CASCADE)
    date=models.DateField(auto_now_add=True,verbose_name="创建日期")
    id_card = models.CharField(max_length=128,blank=True,null=True,verbose_name="身份证号")
    emergency_contact = models.CharField(max_length=128,blank=True,null=True,verbose_name="紧急联系方式")
    sex_choices = ((0,"男"),(1,"女"))
    sex = models.PositiveSmallIntegerField(choices=sex_choices,blank=True,null=True,verbose_name="性别")

    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = "客户信息表"
class CustomerFollowUp(models.Model):
    """客户跟踪记录表"""
    customer=models.ForeignKey("CustomerInfo",on_delete=models.CASCADE,verbose_name="跟进客户")
    content=models.TextField(verbose_name="跟踪内容")
    user=models.ForeignKey("UserProfile",verbose_name="跟进人",on_delete=models.CASCADE)
    status_choices=((0,"近期无报名计划"),
                    (1,"一个月内报名"),
                    (2,"2周内报名"),
                    (3,"已报名"),
                    )
    status=models.SmallIntegerField(choices=status_choices,verbose_name="跟进客户状态")
    date=models.DateField(auto_now_add=True,verbose_name="创建日期")

    def __str__(self):
        return "%s"%self.content
    class Meta:
        verbose_name_plural = "客户跟踪记录表"
class Course(models.Model):
    """课程表"""
    name=models.CharField(max_length=64,verbose_name="课程名",unique=True)
    price=models.PositiveIntegerField(verbose_name="课程价格(千元)")
    period=models.PositiveIntegerField(verbose_name="课程周期(月)",default=5)
    outline=models.TextField(verbose_name="大纲")

    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = "课程表"

class ClassList(models.Model):
    """班级列表"""
    branch=models.ForeignKey("Branch",on_delete=models.CASCADE,verbose_name="所属校区")
    course=models.ForeignKey("Course",on_delete=models.CASCADE,verbose_name="班级课程")
    class_type_choices=((0,"脱产"),(1,"周末"),(2,"网络班"))
    class_type=models.SmallIntegerField(verbose_name="班级类型",choices=class_type_choices)
    semester=models.SmallIntegerField(verbose_name="学期")
    teachers=models.ManyToManyField("UserProfile",verbose_name="讲师")
    contact_template = models.ForeignKey("ContractTemplate",verbose_name="班级合同",on_delete=models.CASCADE,blank=True,null=True)
    start_date=models.DateField("开班日期")
    graduate_date=models.DateField("毕业日期",blank=True,null=True)

    def __str__(self):
        return "%s(%s)期"%(self.course,self.semester)
    class Meta:
        unique_together=("branch","course","semester","class_type")
        verbose_name_plural = "班级列表"

class CourseRecord(models.Model):
    """上课记录"""
    class_grade=models.ForeignKey("ClassList",on_delete=models.CASCADE,verbose_name="上课班级")
    day_num=models.PositiveSmallIntegerField(verbose_name="课程节次")
    teacher=models.ForeignKey("UserProfile",verbose_name="课程讲师",on_delete=models.CASCADE)
    title = models.CharField(verbose_name="本节主题",max_length=64)
    content=models.TextField(verbose_name="课程内容")
    has_homework=models.BooleanField(verbose_name="是否留有作业",default=1)
    homework=models.TextField(verbose_name="作业需求",blank=True)
    date= models.DateTimeField(auto_now_add=True,verbose_name="上课时间")
    def __str__(self):
        return  "%s第(%s)节"%(self.class_grade,self.day_num)
    class Meta:
        unique_together=("class_grade","day_num")
        verbose_name_plural = "上课记录"

class StudyRecord(models.Model):
    """学习记录表"""
    course_record=models.ForeignKey("CourseRecord",on_delete=models.CASCADE,verbose_name="所属课程记录")
    student=models.ForeignKey("Student",on_delete=models.CASCADE,verbose_name="学员")

    score_choices=((100,"A+"),
                   (90,"A"),
                   (85,"B+"),
                   (80,"B"),
                   (75,"B-"),
                   (70,"C+"),
                   (60,"C"),
                   (40,"C-"),
                   (-50,"D"),
                   (0,"N/A"),
                   (-100,"COPY"),
                   )
    score=models.SmallIntegerField(choices=score_choices,default=0,verbose_name="学员成绩")
    show_choices=((0,"缺勤"),
                  (1,"已签到"),
                  (2,"迟到"),
                  (3,"早退"),
                  )
    show_status=models.SmallIntegerField(choices=show_choices,default=1,verbose_name="考勤情况")
    note=models.TextField("成绩备注",blank=True,null=True)
    
    date=models.DateTimeField(auto_now_add=True,verbose_name="创建日期")
    
    def __str__(self):
        
        return "%s %s %s"%(self.course_record,self.student,self.score)
    
    class Meta:
        verbose_name_plural = "学习记录表"
    
class Student(models.Model):
    """学员表"""
    customer=models.OneToOneField("CustomerInfo",on_delete=models.CASCADE,verbose_name="用户")
    class_grades=models.ManyToManyField("ClassList",verbose_name="所属班级")
    
    def __str__(self):
        return "%s"%self.customer.name
    class Meta:
        verbose_name_plural = "学员表"
    
class Branch(models.Model):
    """校区"""
    name=models.CharField(max_length=64,unique=True,verbose_name="学校")
    addr=models.CharField(max_length=64,unique=True,null=True,verbose_name="学校地址")
    
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = "校区"

class Menus(models.Model):
    """权限表"""
    name=models.CharField(max_length=64,verbose_name="权限")
    url_type_choices=((0,"绝对地址"),(1,"正则地址"))
    url_type=models.SmallIntegerField(choices=url_type_choices,verbose_name="地址书写形式",default=0)
    url_name=models.CharField(max_length=128,verbose_name="地址",default="/CRM/")
    
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural="权限表"
        unique_together=("name","url_name")

class ContractTemplate(models.Model):
    """合同表"""
    name = models.CharField(max_length=32,verbose_name="合同名称")
    contact = models.TextField(verbose_name="合同内容")
    
    date = models.DateField(auto_now_add=True,verbose_name="合同日期")
    
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = "合同表"

class StudentEnrollment(models.Model):
    """报名表"""
    customer = models.ForeignKey("CustomerInfo",on_delete=models.CASCADE,verbose_name="签订人")
    class_grade = models.ForeignKey("ClassList",on_delete=models.CASCADE,verbose_name="班级")
    consultant = models.ForeignKey("UserProfile",on_delete=models.CASCADE,verbose_name="顾问")
    contract_agreed = models.BooleanField(default=False,verbose_name="合同确定状态")
    contract_signed_date = models.DateTimeField(blank=True,null=True,verbose_name="合同签订日期")
    contract_aproved = models.BooleanField(default=False,verbose_name="审核状态")
    contract_aproved_date = models.DateTimeField(blank=True,null=True,verbose_name="审核确定日期")
    def __str__(self):
        return "%s"%self.customer
    class Meta:
        unique_together = ("customer","class_grade")
        verbose_name_plural = "报名表"

class PaymentRecord(models.Model):
    """缴费表"""
    enrollment = models.ForeignKey("StudentEnrollment",on_delete=models.CASCADE,verbose_name="签订合同")
    payment_type_choice = ((0,"报名费"),(1,"学费"),(2,"退款"))
    payment_choice = models.SmallIntegerField(choices=payment_type_choice,verbose_name="缴费类型")
    amount = models.IntegerField(default=500,verbose_name="缴费金额")
    consultant = models.ForeignKey("UserProfile",on_delete=models.CASCADE,verbose_name="收费顾问")
    date = models.DateTimeField(auto_now_add=True,verbose_name="缴费日期")
    
    def __str__(self):
        return "%s"%self.enrollment
    class Meta:
        verbose_name_plural = "缴费记录表"