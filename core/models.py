from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django_jalali.db import models as jmodels
import random
import string
import threading
from contextlib import contextmanager
from datetime import datetime, timedelta
from django.utils import timezone

def generate_personnel_id():
    """تولید شماره پرسنلی 4 رقمی رندوم"""
    return str(random.randint(1000, 9999))

def get_unique_personnel_id():
    """تولید شماره پرسنلی یونیک"""
    from django.db.models import Model
    while True:
        personnel_id = generate_personnel_id()
        # بررسی یونیک بودن
        if not UserProfile.objects.filter(personnel_id=personnel_id).exists():
            return personnel_id

class UserProfile(models.Model):
    """پروفایل بسط‌یافته کاربر - شامل اطلاعات کارمند"""
    # انتخاب‌ها
    ROLE_CHOICES = (
        ('admin', 'ادمین'),
        ('lawyer', 'وکیل'),
        ('employee', 'کارمند'),
    )
    
    GENDER_CHOICES = (
        ('M', 'مرد'),
        ('F', 'زن'),
    )
    
    # فهرست سمت‌های پیشفرض برای راهنمایی
    JOB_TITLE_SUGGESTIONS = [
        'مدیر',
        'افسر',
        'دستیار',
        'کارآموز',
        'وکیل',
        'حسابدار',
        'منابع انسانی',
        'فناوری اطلاعات',
    ]
    
    CONTRACT_TYPE_CHOICES = (
        ('full_time', 'تمام وقت'),
        ('part_time', 'پاره وقت'),
        ('project_based', 'پروژه‌ای'),
        ('temporary', 'موقت'),
        ('intern', 'کارآموزی'),
    )
    
    EMPLOYMENT_STATUS_CHOICES = (
        ('active', 'فعال'),
        ('leave', 'مرخصی'),
        ('inactive', 'غیرفعال'),
        ('terminated', 'اخراج'),
    )
    
    PAYMENT_METHOD_CHOICES = (
        ('bank', 'بانکی'),
        ('cash', 'نقدی'),
        ('both', 'هردو'),
    )
    
    # ارتباط با کاربر
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name='کاربر')
    
    # نقش و دپارتمان
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee', verbose_name='نقش')
    department = models.CharField(max_length=100, blank=True, null=True, verbose_name='دپارتمان')
    
    # اطلاعات شناسایی و احراز هویت
    national_id = models.CharField(max_length=10, unique=True, verbose_name="کد ملی",
                                  blank=False, null=False)
    personnel_id = models.CharField(max_length=4, unique=True, verbose_name="شماره پرسنلی",
                                   default=get_unique_personnel_id, editable=False)
    
    # نام نمایشی (نام و نام خانوادگی برای سیستم)
    display_name = models.CharField(max_length=200, verbose_name="نام و نام خانوادگی", default='کاربر جدید')
    
    # مشخصات شخصی
    phone = models.CharField(max_length=11, blank=True, null=True, verbose_name='شماره تماس')
    birth_date = jmodels.jDateField(blank=True, null=True, verbose_name="تاریخ تولد")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True,
                             verbose_name="جنسیت")
    address = models.TextField(blank=True, null=True, verbose_name="آدرس محل سکونت")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='تصویر پروفایل')
    bio = models.TextField(blank=True, null=True, verbose_name='درباره')
    profile_picture = models.ImageField(upload_to='employee_pictures/', blank=True, null=True,
                                       verbose_name="عکس پرسنلی")
    
    # اطلاعات کاری
    branch = models.ForeignKey('Branch', on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='profile_employees', verbose_name="دپارتمان/شعبه")
    job_title = models.CharField(max_length=100, verbose_name="سمت/شغل")
    contract_type = models.CharField(max_length=50, choices=CONTRACT_TYPE_CHOICES,
                                    default='full_time', verbose_name="نوع قرارداد")
    employment_status = models.CharField(max_length=20, choices=EMPLOYMENT_STATUS_CHOICES,
                                        default='active', verbose_name="وضعیت فعلی")
    hire_date = jmodels.jDateField(verbose_name="تاریخ استخدام", blank=True, null=True)
    contract_end_date = jmodels.jDateField(blank=True, null=True,
                                          verbose_name="تاریخ پایان قرارداد")
    
    # اطلاعات مالی و حقوق
    base_salary = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True,
                                     verbose_name="حقوق پایه")
    benefits = models.TextField(blank=True, null=True, verbose_name="مزایا و اضافه کاری")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES,
                                     default='bank', verbose_name="روش پرداخت")
    bank_account_number = models.CharField(max_length=24, blank=True, null=True,
                                          verbose_name="شماره حساب بانکی")
    insurance_info = models.TextField(blank=True, null=True, 
                                     verbose_name="بیمه و مزایای رفاهی")
    
    # سابقه و مهارت‌ها
    education = models.TextField(blank=True, null=True, verbose_name="تحصیلات")
    internal_notes = models.TextField(blank=True, null=True, 
                                     verbose_name="یادداشت‌های داخلی")
    
    # تاریخ‌ها
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    
    class Meta:
        verbose_name = "پروفایل کاربر"
        verbose_name_plural = "پروفایل‌های کاربر"
    
    def __str__(self):
        return f"{self.display_name} ({self.national_id}) - {self.get_role_display()}"
    
    def save(self, *args, **kwargs):
        # اگر personnel_id داده نشده‌ی، خودکار تولید کن
        if not self.personnel_id:
            self.personnel_id = get_unique_personnel_id()
        super().save(*args, **kwargs)



# ============================================
# مدیریت انسانی (HR Management Models)
# ============================================

class Branch(models.Model):
    """شعبه سازمان"""
    STATUS_CHOICES = (
        ('active', 'فعال'),
        ('inactive', 'غیرفعال'),
        ('temporary_close', 'تعطیل موقت'),
    )
    
    BRANCH_TYPE_CHOICES = (
        ('headquarters', 'مرکزی'),
        ('agency', 'نمایندگی'),
        ('store', 'فروشگاه'),
        ('office', 'دفتر'),
        ('other', 'دیگر'),
    )
    
    # اطلاعات شناسایی
    name = models.CharField(max_length=150, verbose_name="نام شعبه")
    code = models.CharField(max_length=50, unique=True, verbose_name="کد شعبه",
                           blank=True, null=True)
    branch_type = models.CharField(max_length=50, choices=BRANCH_TYPE_CHOICES, 
                                   default='office', verbose_name="نوع شعبه")
    
    # اطلاعات مکانی
    address = models.TextField(verbose_name="آدرس کامل")
    city = models.CharField(max_length=100, verbose_name="شهر", blank=True, null=True)
    province = models.CharField(max_length=100, verbose_name="استان", blank=True, null=True)
    postal_code = models.CharField(max_length=10, verbose_name="کد پستی", blank=True, null=True)
    
    # اطلاعات تماس
    phone = models.CharField(max_length=11, verbose_name="شماره تلفن")
    
    # مدیریت داخلی
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='managed_branches', verbose_name="مدیر شعبه")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active',
                             verbose_name="وضعیت فعالیت")
    
    # سایر اطلاعات
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات داخلی")
    working_start_time = models.TimeField(blank=True, null=True, verbose_name="ساعت شروع کاری")
    working_end_time = models.TimeField(blank=True, null=True, verbose_name="ساعت پایان کاری")
    founding_date = jmodels.jDateField(blank=True, null=True, verbose_name="تاریخ تأسیس")
    monthly_budget = models.DecimalField(max_digits=15, decimal_places=2, 
                                        blank=True, null=True, verbose_name="بودجه ماهانه")
    
    # recorded_by field was removed in migration 0005 but remained in model definition
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "شعبه"
        verbose_name_plural = "شعبه‌ها"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_branch_type_display()})"


class Employee(models.Model):
    """کارمند سازمان"""
    GENDER_CHOICES = (
        ('M', 'مرد'),
        ('F', 'زن'),
    )
    
    JOB_TITLE_CHOICES = (
        ('manager', 'مدیر'),
        ('officer', 'افسر'),
        ('assistant', 'دستیار'),
        ('intern', 'کارآموز'),
        ('lawyer', 'وکیل'),
        ('accountant', 'حسابدار'),
        ('hr', 'منابع انسانی'),
        ('it', 'فناوری اطلاعات'),
        ('other', 'دیگر'),
    )
    
    CONTRACT_TYPE_CHOICES = (
        ('full_time', 'تمام وقت'),
        ('part_time', 'پاره وقت'),
        ('project_based', 'پروژه‌ای'),
        ('temporary', 'موقت'),
        ('intern', 'کارآموزی'),
    )
    
    EMPLOYMENT_STATUS_CHOICES = (
        ('active', 'فعال'),
        ('leave', 'مرخصی'),
        ('inactive', 'غیرفعال'),
        ('terminated', 'اخراج'),
    )
    
    PAYMENT_METHOD_CHOICES = (
        ('bank', 'بانکی'),
        ('cash', 'نقدی'),
        ('both', 'هردو'),
    )
    
    # مشخصات شخصی
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    national_id = models.CharField(max_length=10, unique=True, verbose_name="کد ملی",
                                  blank=True, null=True)
    phone = models.CharField(max_length=11, verbose_name="شماره تماس", blank=True, null=True)
    birth_date = jmodels.jDateField(blank=True, null=True, verbose_name="تاریخ تولد")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True,
                             verbose_name="جنسیت")
    address = models.TextField(blank=True, null=True, verbose_name="آدرس محل سکونت")
    
    # اطلاعات کاری
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='employees', verbose_name="دپارتمان/شعبه")
    personnel_id = models.CharField(max_length=50, unique=True, verbose_name="شماره پرسنلی",
                                   blank=True, null=True)
    job_title = models.CharField(max_length=50, choices=JOB_TITLE_CHOICES, 
                                verbose_name="سمت/شغل")
    contract_type = models.CharField(max_length=50, choices=CONTRACT_TYPE_CHOICES,
                                    default='full_time', verbose_name="نوع قرارداد")
    employment_status = models.CharField(max_length=20, choices=EMPLOYMENT_STATUS_CHOICES,
                                        default='active', verbose_name="وضعیت فعلی")
    hire_date = jmodels.jDateField(verbose_name="تاریخ استخدام", blank=True, null=True)
    
    # اطلاعات مالی و حقوق
    base_salary = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True,
                                     verbose_name="حقوق پایه")
    benefits = models.TextField(blank=True, null=True, verbose_name="مزایا و اضافه کاری")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES,
                                     default='bank', verbose_name="روش پرداخت")
    bank_account_number = models.CharField(max_length=24, blank=True, null=True,
                                          verbose_name="شماره حساب بانکی")
    insurance_info = models.TextField(blank=True, null=True, 
                                     verbose_name="بیمه و مزایای رفاهی")
    
    # سابقه و مهارت‌ها
    education = models.TextField(blank=True, null=True, verbose_name="تحصیلات")
    
    # اطلاعات اضافی
    profile_picture = models.ImageField(upload_to='employee_pictures/', blank=True, null=True,
                                       verbose_name="عکس پرسنلی")
    internal_notes = models.TextField(blank=True, null=True, 
                                     verbose_name="یادداشت‌های داخلی")
    contract_end_date = jmodels.jDateField(blank=True, null=True,
                                          verbose_name="تاریخ پایان قرارداد")
    
    # recorded_by field was removed in migration 0005 but remained in model definition
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "کارمند"
        verbose_name_plural = "کارمندان"
        ordering = ['user__first_name', 'user__last_name']
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.get_job_title_display()}"


class Attendance(models.Model):
    """حضور و غیاب - سیستم جامع ورود و خروج"""
    STATUS_CHOICES = (
        ('present', 'حاضر'),
        ('absent', 'غایب'),
        ('leave', 'مرخصی'),
        ('late', 'تاخیر'),
        ('incomplete', 'ناقص'),  # ورود بدون خروج
        ('early_leave', 'خروج زودهنگام'),
    )
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendances', verbose_name='کارمند')
    date = models.DateField(verbose_name='تاریخ')
    
    # زمان ورود و خروج
    check_in = models.TimeField(blank=True, null=True, verbose_name='ساعت ورود')
    check_out = models.TimeField(blank=True, null=True, verbose_name='ساعت خروج')
    
    # مدت زمان (بر حسب دقیقه)
    work_duration = models.IntegerField(blank=True, null=True, verbose_name='مدت زمان کار (دقیقه)')
    overtime_duration = models.IntegerField(blank=True, null=True, default=0, verbose_name='مدت اضافه‌کاری (دقیقه)')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='absent', verbose_name='وضعیت')
    notes = models.TextField(blank=True, null=True, verbose_name='یادداشت‌ها')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='آخرین به‌روزرسانی')
    
    class Meta:
        verbose_name = "حضور و غیاب"
        verbose_name_plural = "حضور و غیاب‌ها"
        unique_together = ('employee', 'date')
        ordering = ['-date', '-check_in']
    
    def __str__(self):
        return f"{self.employee} - {self.date} ({self.get_status_display()})"
    
    def get_work_duration_display(self):
        """نمایش مدت زمان کار به صورت ساعت:دقیقه"""
        if self.work_duration is None:
            return "نامشخص"
        hours = self.work_duration // 60
        minutes = self.work_duration % 60
        return f"{hours}:{minutes:02d}"
    
    def get_overtime_display(self):
        """نمایش اضافه‌کاری به صورت ساعت:دقیقه"""
        if self.overtime_duration is None or self.overtime_duration == 0:
            return "ندارد"
        hours = self.overtime_duration // 60
        minutes = self.overtime_duration % 60
        return f"{hours}:{minutes:02d}"
    
    def update_status_from_login(self):
        """به‌روزرسانی وضعیت بر اساس آخرین ورود کاربر امروز"""
        from django.utils import timezone
        from django.db.models import Q
        
        # اگر وضعیت مرخصی باشد، تغییر ندهید
        if self.status == 'leave':
            return
        
        # بررسی آخرین ورود کاربر در این روز
        last_login = self.employee.user.last_login
        
        if last_login:
            login_date = last_login.date() if hasattr(last_login, 'date') else last_login
            
            if login_date == self.date:
                login_time = last_login.time() if hasattr(last_login, 'time') else timezone.now().time()
                self.check_in = login_time
                self.status = 'present'
            else:
                self.status = 'absent'
        else:
            self.status = 'absent'
    
    def calculate_work_duration(self):
        """محاسبه مدت زمان کار و اضافه‌کاری"""
        if not self.check_in or not self.check_out:
            return False
        
        try:
            # تبدیل TimeField به datetime برای محاسبه
            check_in_dt = datetime.combine(self.date, self.check_in)
            check_out_dt = datetime.combine(self.date, self.check_out)
            
            # اگر خروج قبل از ورود باشد (خروج شب)
            if check_out_dt < check_in_dt:
                check_out_dt += timedelta(days=1)
            
            # محاسبه مدت زمان کار (دقیقه)
            work_seconds = (check_out_dt - check_in_dt).total_seconds()
            self.work_duration = int(work_seconds / 60)
            
            # استاندارد 8 ساعت کاری در روز
            standard_hours = 480  # 8 * 60 minutes
            
            # محاسبه اضافه‌کاری
            if self.work_duration > standard_hours:
                overtime = self.work_duration - standard_hours
                self.overtime_duration = min(overtime, 120)  # max 2 hours per day
            else:
                self.overtime_duration = 0
            
            # تعیین وضعیت بر اساس زمان ورود و خروج
            self.status = 'present'
            
            return True
        except Exception as e:
            print(f"خطا در محاسبه مدت زمان: {e}")
            return False





class ActivityLog(models.Model):
    """لاگ فعالیت‌های سیستم و کاربران"""
    ACTION_CHOICES = (
        ('create', 'ایجاد'),
        ('update', 'ویرایش'),
        ('delete', 'حذف'),
        ('login', 'ورود به سیستم'),
        ('logout', 'خروج از سیستم'),
        ('download', 'دانلود'),
        ('export', 'صادرات'),
        ('import', 'واردات'),
        ('other', 'سایر'),
    )
    
    # معلومات کاربر
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                            related_name='activity_logs', verbose_name="کاربر")
    action = models.CharField(max_length=50, choices=ACTION_CHOICES, verbose_name="عملیات")
    
    # معلومات رکورد متاثر
    content_type = models.CharField(max_length=100, verbose_name="نوع مدل", blank=True, null=True)
    object_id = models.CharField(max_length=100, verbose_name="شناسه رکورد", blank=True, null=True)
    object_description = models.CharField(max_length=500, verbose_name="توضیح رکورد", blank=True, null=True)
    
    # جزئیات تغییرات (JSON)
    details = models.TextField(verbose_name="جزئیات تغییرات", blank=True, null=True,
                              help_text="تغییرات انجام‌شده به فرمت JSON")
    
    # معلومات فنی
    ip_address = models.GenericIPAddressField(verbose_name="آدرس IP", blank=True, null=True)
    
    # تاریخ و زمان (شمسی)
    timestamp = jmodels.jDateTimeField(auto_now_add=True, verbose_name="تاریخ و زمان ایجاد")
    
    class Meta:
        verbose_name = "لاگ فعالیت"
        verbose_name_plural = "لاگ‌های فعالیت"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user} - {self.get_action_display()} - {self.timestamp}"


class Leave(models.Model):
    """مدل مرخصی - درخواست مرخصی کارمندان و وکیلا"""
    LEAVE_TYPE_CHOICES = (
        ('annual', 'مرخصی سالانه'),
        ('sick', 'مرخصی بیماری'),
        ('personal', 'مرخصی شخصی'),
        ('maternity', 'مرخصی زایمان'),
        ('paternity', 'مرخصی پدری'),
        ('unpaid', 'مرخصی بدون‌حقوق'),
        ('half_day', 'نیم‌روز'),
    )
    
    DURATION_TYPE_CHOICES = (
        ('hourly', 'ساعتی'),
        ('daily', 'روزانه'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'در انتظار تایید'),
        ('approved', 'تایید شده'),
        ('rejected', 'رد شده'),
        ('cancelled', 'لغو شده'),
    )
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leaves', verbose_name='کارمند')
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPE_CHOICES, verbose_name='نوع مرخصی')
    
    # نوع مدت (ساعتی یا روزانه)
    duration_type = models.CharField(max_length=10, choices=DURATION_TYPE_CHOICES, default='daily', verbose_name='نوع مدت')
    
    # برای مرخصی روزانه
    start_date = jmodels.jDateField(verbose_name='تاریخ شروع', blank=True, null=True)
    end_date = jmodels.jDateField(verbose_name='تاریخ پایان', blank=True, null=True)
    duration_days = models.IntegerField(verbose_name='مدت (روز)', blank=True, null=True)
    
    # برای مرخصی ساعتی
    date = jmodels.jDateField(verbose_name='تاریخ مرخصی', blank=True, null=True)
    start_time = models.TimeField(verbose_name='ساعت شروع', blank=True, null=True)
    end_time = models.TimeField(verbose_name='ساعت پایان', blank=True, null=True)
    duration_hours = models.FloatField(verbose_name='مدت (ساعت)', blank=True, null=True)
    
    # علت و توضیحات
    reason = models.TextField(verbose_name='دلیل/توضیحات', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='وضعیت')
    
    # تایید‌کننده
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='approved_leaves', verbose_name='تایید‌شده توسط')
    approval_date = models.DateTimeField(blank=True, null=True, verbose_name='تاریخ تایید')
    approval_notes = models.TextField(blank=True, null=True, verbose_name='یادداشت‌های تایید')
    
    # تاریخ‌ها
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ درخواست')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='آخرین به‌روزرسانی')
    
    class Meta:
        verbose_name = "مرخصی"
        verbose_name_plural = "مرخصی‌ها"
        ordering = ['-created_at']
    
    def __str__(self):
        if self.duration_type == 'hourly':
            return f"{self.employee} - {self.get_leave_type_display()} ({self.date} ساعتی)"
        else:
            return f"{self.employee} - {self.get_leave_type_display()} ({self.start_date} تا {self.end_date})"
    
    def get_duration_display(self):
        """محاسبه مدت مرخصی"""
        if self.duration_type == 'daily' and self.start_date and self.end_date:
            from datetime import date
            delta = self.end_date - self.start_date
            return delta.days + 1  # شامل هر دو روز شروع و پایان
        elif self.duration_type == 'hourly' and self.start_time and self.end_time:
            from datetime import datetime, time
            start_dt = datetime.combine(datetime.today(), self.start_time)
            end_dt = datetime.combine(datetime.today(), self.end_time)
            if end_dt < start_dt:  # اگر تا فردا ادامه دارد
                end_dt = end_dt.replace(day=end_dt.day + 1)
            delta = end_dt - start_dt
            return delta.total_seconds() / 3600  # تبدیل به ساعت
        return 0
    
    def save(self, *args, **kwargs):
        """محاسبه خودکار مدت مرخصی"""
        if self.duration_type == 'daily' and self.start_date and self.end_date:
            self.duration_days = self.get_duration_display()
        elif self.duration_type == 'hourly' and self.start_time and self.end_time:
            self.duration_hours = self.get_duration_display()
        super().save(*args, **kwargs)


class ActivityReport(models.Model):
    """گزارش فعالیت (کار انجام شده توسط کارمند)"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='activity_reports', verbose_name='کارمند')
    title = models.CharField(max_length=200, verbose_name="عنوان")
    description = models.TextField(verbose_name="توضیحات")
    date = jmodels.jDateField(verbose_name="تاریخ")
    time = models.TimeField(blank=True, null=True, verbose_name="ساعت و دقیقه")
    # recorded_by field was removed in migration 0005 but remained in model definition
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    
    class Meta:
        verbose_name = "گزارش فعالیت"
        verbose_name_plural = "گزارش‌های فعالیت"
    
    def __str__(self):
        return f"{self.employee} - {self.title} ({self.date})"


# ============================================
# مدیریت مالی (Finance Management Models)
# ============================================

class Income(models.Model):
    """درآمدها - مدل بهتری‌شده"""
    PAYMENT_METHOD_CHOICES = (
        ('cash', 'نقدی'),
        ('card', 'کارت'),
        ('transfer', 'انتقال بانکی'),
        ('check', 'چک'),
        ('other', 'دیگر'),
    )
    
    PAYMENT_STATUS_CHOICES = (
        ('received', 'دریافت شده'),
        ('pending', 'در انتظار'),
        ('returned', 'برگشت خورده'),
    )
    
    INCOME_CATEGORY_CHOICES = (
        ('sales', 'فروش'),
        ('services', 'خدمات'),
        ('rent', 'اجاره'),
        ('interest', 'سود'),
        ('other', 'دیگر'),
    )
    
    # اطلاعات پایه
    title = models.CharField(max_length=200, verbose_name="عنوان/توضیح درآمد")
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات داخلی")
    
    # مالی
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="مبلغ درآمد")
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES,
                                     default='cash', verbose_name="روش دریافت")
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES,
                                     default='pending', verbose_name="وضعیت پرداخت")
    
    # طبقه‌بندی
    category = models.CharField(max_length=50, choices=INCOME_CATEGORY_CHOICES,
                               default='other', verbose_name="دسته‌بندی درآمد")
    
    # تاریخ‌ها
    registration_date = jmodels.jDateField(blank=True, null=True, verbose_name="تاریخ ثبت")
    received_date = jmodels.jDateField(blank=True, null=True, verbose_name="تاریخ واقعی دریافت")
    
    # مرتبط با منابع
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='incomes', verbose_name="شعبه")
    
    # اطلاعات اضافی
    is_verified = models.BooleanField(default=False, verbose_name="بررسی شده")
    attachment = models.FileField(upload_to='income_documents/', blank=True, null=True,
                                 verbose_name="سند مالی/فاکتور")
    
    # recorded_by removed in migration 0005 - field kept for compatibility but not in database
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    
    class Meta:
        verbose_name = "درآمد"
        verbose_name_plural = "درآمدها"
        ordering = ['-registration_date']
    
    def __str__(self):
        return f"{self.title} - {self.get_formatted_amount()}"
    
    def get_formatted_amount(self):
        """بازگرداندن مبلغ درآمد با جداکننده هزارگان"""
        from core.formatters import format_number_with_thousand_sep
        return format_number_with_thousand_sep(self.amount)



class Expense(models.Model):
    """هزینه‌ها - مدل بهتری‌شده"""
    PAYMENT_METHOD_CHOICES = (
        ('cash', 'نقدی'),
        ('card', 'کارت'),
        ('transfer', 'انتقال بانکی'),
        ('check', 'چک'),
        ('other', 'دیگر'),
    )
    
    PAYMENT_STATUS_CHOICES = (
        ('paid', 'پرداخت شده'),
        ('pending', 'در انتظار'),
        ('returned', 'برگشت خورده'),
    )
    
    EXPENSE_CATEGORY_CHOICES = (
        ('salary', 'حقوق و دستمزد'),
        ('rent', 'اجاره'),
        ('utilities', 'خدمات و قبوض'),
        ('equipment', 'خرید مواد و تجهیزات'),
        ('services', 'خدمات'),
        ('tax', 'مالیات'),
        ('travel', 'سفر'),
        ('other', 'دیگر'),
    )
    
    # اطلاعات پایه
    title = models.CharField(max_length=200, verbose_name="عنوان/توضیح هزینه")
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات داخلی")
    
    # مالی
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="مبلغ هزینه")
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES,
                                     default='cash', verbose_name="روش پرداخت")
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES,
                                     default='pending', verbose_name="وضعیت پرداخت")
    
    # طبقه‌بندی
    category = models.CharField(max_length=50, choices=EXPENSE_CATEGORY_CHOICES,
                               default='other', verbose_name="دسته‌بندی هزینه")
    
    # تاریخ‌ها
    registration_date = jmodels.jDateField(blank=True, null=True, verbose_name="تاریخ ثبت")
    payment_date = jmodels.jDateField(blank=True, null=True, verbose_name="تاریخ واقعی پرداخت")
    
    # مرتبط با منابع
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='expenses', verbose_name="شعبه")
    
    # اطلاعات اضافی
    is_verified = models.BooleanField(default=False, verbose_name="بررسی شده")
    attachment = models.FileField(upload_to='expense_documents/', blank=True, null=True,
                                 verbose_name="سند مالی/فاکتور/رسید")
    
    # recorded_by removed in migration 0005 - field kept for compatibility but not in database
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    
    class Meta:
        verbose_name = "هزینه"
        verbose_name_plural = "هزینه‌ها"
        ordering = ['-registration_date']
    
    def __str__(self):
        return f"{self.title} - {self.get_formatted_amount()}"
    
    def get_formatted_amount(self):
        """بازگرداندن مبلغ هزینه با جداکننده هزارگان"""
        from core.formatters import format_number_with_thousand_sep
        return format_number_with_thousand_sep(self.amount)


# ============================================
# مدیریت وام‌ها (Loan Management Models)
# ============================================

class Loan(models.Model):
    """وام - مدل بهتری‌شده"""
    STATUS_CHOICES = (
        ('available', 'موجود'),
        ('unsuccessful', 'ناموفق'),
        ('purchased', 'خریدشده'),
    )
    
    # اطلاعات پایه
    bank_name = models.CharField(max_length=150, default='', verbose_name="نام بانک")
    loan_type = models.CharField(max_length=100, default='',
                                verbose_name="نوع وام",
                                help_text="نوع وام را به صورت دستی وارد کنید (مثال: مسکن، شخصی، خودرو، کسب‌وکار، ...)")
    
    # مالی
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="مبلغ وام")
    duration_months = models.IntegerField(default=0, verbose_name="مدت وام (به ماه)")
    purchase_rate = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True,
                                       verbose_name="قیمت خرید وام")
    payment_type = models.CharField(max_length=50, choices=[('cash', 'نقدی'), ('installment', 'اقساطی')],
                                   default='installment', verbose_name="نوع پرداخت")
    
    # وضعیت
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available',
                            verbose_name="وضعیت وام")
    
    # تاریخ‌ها
    registration_date = jmodels.jDateField(blank=True, null=True, verbose_name="تاریخ مراجعه/ثبت وام")
    
    # مرتبط با منابع
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='loans', verbose_name="شعبه مربوطه")
    
    # مسئول و معرفی‌کننده
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='loans_recorded', verbose_name="کارمند ثبت‌کننده",
                                   limit_choices_to={'profile__role': 'employee'})
    referrer = models.CharField(max_length=200, blank=True, null=True, verbose_name="معرفی‌کننده (نام فرد/شرکت)")
    
    # اطلاعات صاحب وام
    applicant_first_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="نام صاحب وام")
    applicant_last_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="نام خانوادگی صاحب وام")
    applicant_national_id = models.CharField(max_length=10, blank=True, null=True, verbose_name="کد ملی صاحب وام")
    applicant_phone = models.CharField(max_length=11, blank=True, null=True, verbose_name="شماره تماس صاحب وام")
    
    # اطلاعات اضافی
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات داخلی")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    
    class Meta:
        verbose_name = "وام"
        verbose_name_plural = "وام‌ها"
        ordering = ['-registration_date']
    
    def __str__(self):
        return f"{self.bank_name} - {self.get_formatted_amount()} ({self.loan_type})"
    
    def get_formatted_amount(self):
        """بازگرداندن مبلغ وام با جداکننده هزارگان"""
        from core.formatters import format_number_with_thousand_sep
        return format_number_with_thousand_sep(self.amount)
    
    def get_formatted_purchase_rate(self):
        """بازگرداندن قیمت خرید با جداکننده هزارگان"""
        from core.formatters import format_number_with_thousand_sep
        if self.purchase_rate:
            return format_number_with_thousand_sep(self.purchase_rate)
        return '-'
    
    def save(self, *args, **kwargs):
        """اتومات پر کردن recorded_by"""
        # این متد توی Admin صدا زده می‌شود که request داریم
        # اما اینجا فقط یک placeholder است
        super().save(*args, **kwargs)


class LoanBuyer(models.Model):
    """خریدار وام - مدل بهتری‌شده"""
    STATUS_CHOICES = (
        ('registered', 'ثبت درخواست'),
        ('under_review', 'در حال بررسی'),
        ('qualification_transfer', 'انتقال امتیاز'),
        ('bank_validation', 'اعتبار سنجی بانک'),
        ('loan_paid', 'پرداخت وام'),
        ('guarantor_defective', 'نقص ضامن'),
        ('borrower_defective', 'نقص وام گیرنده'),
        ('completed', 'انجام شده'),
    )
    
    SALE_TYPE_CHOICES = (
        ('cash', 'نقدی'),
        ('conditional', 'شرایطی'),
    )
    
    # اطلاعات شخصی
    first_name = models.CharField(max_length=100, default='', verbose_name="نام")
    last_name = models.CharField(max_length=100, default='', verbose_name="نام خانوادگی")
    national_id = models.CharField(max_length=10, unique=True, default='', verbose_name="کد ملی")
    phone = models.CharField(max_length=11, default='', verbose_name="شماره تماس")
    
    # اطلاعات وام و مالی
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='buyers',
                            verbose_name="وام هدف", blank=True, null=True)
    requested_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                          verbose_name="مبلغ درخواستی")
    bank = models.CharField(max_length=150, default='', verbose_name="بانک عامل", blank=True)
    sale_price = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                    verbose_name="قیمت فروش", blank=True, null=True)
    sale_type = models.CharField(max_length=20, choices=SALE_TYPE_CHOICES, default='cash',
                                verbose_name="نوع فروش")
    
    # تاریخ‌ها و وضعیت‌ها
    application_date = jmodels.jDateField(blank=True, null=True,
                                         verbose_name="تاریخ مراجعه/ثبت درخواست")
    current_status = models.CharField(max_length=50, choices=STATUS_CHOICES,
                                     default='registered', verbose_name="وضعیت فعلی")
    
    # مسئولیت کارگذار (خودکار)
    broker = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='loan_buyers_as_broker',
                              limit_choices_to={'profile__role': 'employee'},
                              verbose_name="کارگذار ثبت‌کننده", editable=False)
    
    # ایجادکننده (برای کنترل دسترسی سطح ردیف)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='loan_buyers_created',
                                   limit_choices_to={'profile__role': 'employee'},
                                   verbose_name="ایجادکننده", editable=False)
    
    # اطلاعات اضافی
    internal_notes = models.TextField(blank=True, null=True, verbose_name="یادداشت‌های داخلی")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    
    class Meta:
        verbose_name = "خریدار وام"
        verbose_name_plural = "خریداران وام"
        ordering = ['-application_date']
    
    def __str__(self):
        loan_name = self.loan.bank_name if self.loan else 'بدون وام'
        return f"{self.first_name} {self.last_name} - {loan_name}"
    
    def get_full_name(self):
        """بازگرداندن نام کامل خریدار"""
        return f"{self.first_name} {self.last_name}".strip()
    
    def clean(self):
        """بررسی اعتبار شرطی فیلد‌ها"""
        from django.core.exceptions import ValidationError
        if self.current_status == 'completed':
            errors = {}
            if not self.loan:
                errors['loan'] = 'وام الزامی است زمانی‌که وضعیت "انجام شده" است'
            if not self.sale_price:
                errors['sale_price'] = 'قیمت فروش الزامی است زمانی‌که وضعیت "انجام شده" است'
            if not self.bank:
                errors['bank'] = 'بانک عامل الزامی است زمانی‌که وضعیت "انجام شده" است'
            if errors:
                raise ValidationError(errors)
    
    def save(self, *args, **kwargs):
        """ایجاد یا به‌روزرسانی تاریخچه وضعیت + خودکار ایجاد وام خریدار"""
        is_new = self.pk is None
        old_status = None
        
        # اگر رکورد قدیمی است، وضعیت قدیم رو بگیر
        if not is_new:
            try:
                old_obj = LoanBuyer.objects.get(pk=self.pk)
                old_status = old_obj.current_status
            except LoanBuyer.DoesNotExist:
                old_status = None
        
        # ذخیره رکورد
        super().save(*args, **kwargs)
        
        # اگر رکورد جدید است یا وضعیت تغییر کرده است
        if is_new or old_status != self.current_status:
            # ایجاد تاریخچه وضعیت جدید
            LoanBuyerStatusHistory.objects.create(
                loan_buyer=self,
                status=self.current_status
            )
        
        # اگر وضعیت به "completed" تبدیل شد
        if old_status != 'completed' and self.current_status == 'completed':
            self._handle_completed_status()
    
    def _handle_completed_status(self):
        """
        وقتی خریدار وام وضعیتش "انجام شده" می‌شود:
        1. وضعیت وام به "purchased" تغییر می‌کند
        2. خودکار یک LoanCreditor جدید ساخته می‌شود (بستانکار = صاحب وام)
        """
        if not self.loan:
            return
        
        # ۱. تغییر وضعیت وام
        self.loan.status = 'purchased'
        self.loan.save(update_fields=['status', 'updated_at'])
        
        # ۲. ایجاد LoanCreditor جدید براساس اطلاعات صاحب وام (applicant)
        # بستانکار همان صاحب وام اصلی است که قرار است پول دریافت کند
        LoanCreditor.objects.get_or_create(
            loan=self.loan,
            national_id=self.loan.applicant_national_id or '',
            defaults={
                'first_name': self.loan.applicant_first_name or '',
                'last_name': self.loan.applicant_last_name or '',
                'phone': self.loan.applicant_phone or '',
                'total_amount': self.sale_price or self.loan.amount,
                'payment_type': self.loan.payment_type,  # نوع پرداخت از وام
                'settlement_status': 'unsettled',
                'category': 'individual',
                'recorded_by': self.loan.recorded_by,  # فرد ثبت‌کننده وام
                'broker': self.loan.recorded_by,
                'branch': self.loan.branch,
                'description': f"صاحب وام: {self.loan.applicant_first_name} {self.loan.applicant_last_name} (ID: {self.loan.applicant_national_id})",
            }
        )


class LoanBuyerStatusHistory(models.Model):
    """تاریخچه وضعیت خریدار وام"""
    STATUS_CHOICES = (
        ('registered', 'ثبت درخواست'),
        ('under_review', 'در حال بررسی'),
        ('qualification_transfer', 'انتقال امتیاز'),
        ('bank_validation', 'اعتبار سنجی بانک'),
        ('loan_paid', 'پرداخت وام'),
        ('guarantor_defective', 'نقص ضامن'),
        ('borrower_defective', 'نقص وام گیرنده'),
        ('completed', 'انجام شده'),
    )
    
    # ارتباط
    loan_buyer = models.ForeignKey(LoanBuyer, on_delete=models.CASCADE,
                                  related_name='status_history',
                                  verbose_name="خریدار وام")
    
    # وضعیت و تاریخ
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='registered',
                            verbose_name="وضعیت")
    status_date = jmodels.jDateField(blank=True, null=True, verbose_name="تاریخ ثبت وضعیت",
                                    help_text="تاریخ وضعیت (اتومات به تاریخ امروز تنظیم می‌شود)")
    description = models.TextField(blank=True, null=True,
                                  verbose_name="توضیحات اختیاری")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    
    class Meta:
        verbose_name = "تاریخچه وضعیت خریدار وام"
        verbose_name_plural = "تاریخچه‌های وضعیت خریدار وام"
        ordering = ['loan_buyer', '-status_date']
    
    def save(self, *args, **kwargs):
        """اتومات تاریخ را به تاریخ امروز تنظیم کن اگر تنظیم نشده باشد"""
        import jdatetime
        if not self.status_date:
            self.status_date = jdatetime.date.today()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.loan_buyer} - {self.get_status_display()} ({self.status_date})"


class LoanCreditor(models.Model):
    """بستانکار وام - مدل بهتری‌شده"""
    SETTLEMENT_STATUS_CHOICES = (
        ('unsettled', 'انجام نشده'),
        ('settled', 'انجام شده'),
        ('partial', 'جزئی'),
    )
    
    PAYMENT_TYPE_CHOICES = (
        ('cash', 'نقدی'),
        ('installment', 'قسطی'),
    )
    
    CREDITOR_CATEGORY_CHOICES = (
        ('individual', 'شخصی'),
        ('company', 'شرکت'),
        ('organization', 'سازمان'),
    )
    
    # اطلاعات شخصی بستانکار (خوانده شده از وام)
    first_name = models.CharField(max_length=100, default='', verbose_name="نام")
    last_name = models.CharField(max_length=100, default='', verbose_name="نام خانوادگی")
    national_id = models.CharField(max_length=10, default='', verbose_name="کد ملی")
    phone = models.CharField(max_length=11, default='', verbose_name="شماره تماس")
    
    # وضعیت تسویه و پرداخت
    settlement_status = models.CharField(max_length=20, choices=SETTLEMENT_STATUS_CHOICES,
                                        default='unsettled', verbose_name="وضعیت تسویه")
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES,
                                   default='installment', verbose_name="نوع پرداخت")
    installment_count = models.PositiveIntegerField(blank=True, null=True, 
                                                    verbose_name="تعداد قسط‌های برنامه‌ریزی‌شده",
                                                    help_text="تنها برای پرداخت قسطی - قسط‌ها خودکار ایجاد می‌شوند")
    
    # مبالغ
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="مبلغ کل (نرخ خرید از وام)")
    paid_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0, 
                                     verbose_name="جمع مبلغ پرداخت‌شده")
    
    # تاریخ‌ها
    creation_date = jmodels.jDateField(auto_now_add=True, blank=True, null=True, verbose_name="تاریخ ایجاد رکورد")
    settlement_date = jmodels.jDateField(blank=True, null=True, verbose_name="تاریخ تسویه کامل")
    
    # ارتباط با وام
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='creditors',
                            verbose_name="وام مرتبط")
    
    # ارتباط با شعبه و کارگذار
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='loan_creditors', verbose_name="شعبه مرتبط")
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='loan_creditors_recorded',
                                   limit_choices_to={'profile__role': 'employee'},
                                   verbose_name="کارمند ثبت‌کننده (اتومات)", editable=False)
    broker = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='loan_creditors_as_broker',
                              limit_choices_to={'profile__role': 'employee'},
                              verbose_name="کارگذار ثبت‌کننده")
    
    # دسته‌بندی
    category = models.CharField(max_length=20, choices=CREDITOR_CATEGORY_CHOICES,
                               default='individual', verbose_name="دسته‌بندی بستانکار")
    
    # شرح خودکار
    description = models.CharField(max_length=255, blank=True, default='', 
                                   verbose_name="شرح (ایدی وام - نوع وام - نام بانک)",
                                   help_text="پر می‌شود به صورت خودکار هنگام ایجاد")
    
    # یادداشت‌ها
    internal_notes = models.TextField(blank=True, null=True, verbose_name="یادداشت‌های داخلی")
    final_notes = models.TextField(blank=True, null=True, verbose_name="یادداشت نهایی (هنگام تسویه)")
    next_followup_date = jmodels.jDateField(blank=True, null=True, verbose_name="تاریخ پیگیری بعدی")
    
    # شماره سند داخلی
    internal_document_number = models.CharField(max_length=100, blank=True, null=True,
                                               verbose_name="شماره سند داخلی")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    
    class Meta:
        verbose_name = "بستانکار وام"
        verbose_name_plural = "بستانکاران وام"
        ordering = ['-creation_date']
        unique_together = ('national_id', 'loan')
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.loan.bank_name} ({self.total_amount})"
    
    @property
    def paid_percentage(self):
        """درصد پرداخت شده"""
        if self.total_amount > 0:
            return (self.paid_amount / self.total_amount) * 100
        return 0
    
    @property
    def remaining_installments(self):
        """تعداد قسط‌های باقی‌مانده"""
        if self.payment_type == 'installment':
            total_installments = self.installments.count()
            paid_installments = self.installments.filter(status='paid').count()
            return total_installments - paid_installments
        return 0
    
    def save(self, *args, **kwargs):
        """محاسبه و بروزرسانی خودکار"""
        import jdatetime
        # منطق تسویه برای پرداخت نقدی
        if self.payment_type == 'cash':
            # اگر تسویه کامل شد، مبلغ پرداخت‌شده برابر با مبلغ کل میشود
            if self.settlement_status == 'settled' or self.paid_amount >= self.total_amount:
                self.paid_amount = self.total_amount
                self.settlement_status = 'settled'
                if not self.settlement_date:
                    self.settlement_date = jdatetime.date.today()
            elif self.paid_amount > 0 and self.paid_amount < self.total_amount:
                self.settlement_status = 'partial'
            else:
                self.settlement_status = 'unsettled'
        # منطق تسویه برای پرداخت قسطی (فقط اگر pk داشته باشد)
        elif self.payment_type == 'installment' and self.pk:
            # جمع مبالغ قسط‌های پرداخت‌شده
            paid_installments_sum = self.installments.filter(status='paid').aggregate(models.Sum('paid_amount'))['paid_amount__sum'] or 0
            
            # مبلغ پرداخت‌شده برابر با جمع قسط‌های پرداخت‌شده
            self.paid_amount = paid_installments_sum
            
            if paid_installments_sum >= self.total_amount:
                self.settlement_status = 'settled'
                if not self.settlement_date:
                    self.settlement_date = jdatetime.date.today()
            elif paid_installments_sum > 0 and paid_installments_sum < self.total_amount:
                self.settlement_status = 'partial'
            else:
                self.settlement_status = 'unsettled'
        
        super().save(*args, **kwargs)


class LoanCreditorInstallment(models.Model):
    """قسط‌های بستانکار وام - مدل ساده‌شده (دستی)"""
    STATUS_CHOICES = (
        ('paid', 'پرداخت شده'),
        ('unpaid', 'پرداخت نشده'),
    )
    
    # ارتباط
    creditor = models.ForeignKey(LoanCreditor, on_delete=models.CASCADE,
                                related_name='installments', verbose_name="بستانکار")
    
    # اطلاعات قسط
    installment_number = models.PositiveIntegerField(verbose_name="شماره قسط", editable=False)
    paid_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                     verbose_name="مبلغ قسط (پرداخت‌شده)")
    due_date = jmodels.jDateField(blank=True, null=True, verbose_name="تاریخ سررسید قسط")
    payment_date = jmodels.jDateField(blank=True, null=True, verbose_name="تاریخ پرداخت قسط")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unpaid',
                             verbose_name="وضعیت قسط")
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات قسط")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    
    class Meta:
        verbose_name = "قسط بستانکار وام"
        verbose_name_plural = "قسط‌های بستانکار وام"
        ordering = ['creditor', 'installment_number']
        unique_together = ('creditor', 'installment_number')
    
    def __str__(self):
        return f"قسط {self.installment_number} - {self.creditor.first_name} {self.creditor.last_name} ({self.paid_amount} ریال)"
    
    @property
    def remaining_amount(self):
        """باقی‌مانده قسط (همیشه 0 چون paid_amount همان مبلغ قسط است)"""
        return 0
    
    def save(self, *args, **kwargs):
        """اتومات شماره قسط و به‌روزرسانی paid_amount بستانکار"""
        if not self.installment_number:
            # پیدا کردن آخرین شماره قسط برای این بستانکار
            last_installment = LoanCreditorInstallment.objects.filter(
                creditor=self.creditor
            ).order_by('-installment_number').first()
            
            if last_installment:
                self.installment_number = last_installment.installment_number + 1
            else:
                self.installment_number = 1
        
        super().save(*args, **kwargs)
        
        # به‌روزرسانی paid_amount در LoanCreditor
        # جمع مبالغ تمام قسط‌های پرداخت‌شده
        if self.creditor.payment_type == 'installment':
            total_paid = self.creditor.installments.aggregate(models.Sum('paid_amount'))['paid_amount__sum'] or 0
            self.creditor.paid_amount = total_paid
            self.creditor.save(update_fields=['paid_amount'])


# ============================================
# Signal Handlers
# ============================================


@receiver(pre_save, sender=Attendance)
def calculate_attendance_duration(sender, instance, **kwargs):
    """محاسبه خودکار مدت زمان کار و اضافه‌کاری هنگام ذخیره"""
    # اگر هر دو check_in و check_out وجود داشت، مدت را محاسبه کن
    if instance.check_in and instance.check_out:
        instance.calculate_work_duration()


# ⚠️ Signal زیر غیرفعال شده است زیرا ایجاد LoanCreditor اکنون توسط
# LoanBuyer._handle_completed_status() انجام می‌شود (بر اساس صاحب وام نه خریدار)
# این سیگنال national_id های AUTO-XXXX ایجاد می‌کرد که غلط بود
# @receiver(post_save, sender=Loan)
# def auto_create_loan_creditor(sender, instance, created, **kwargs):
#     """ایجاد خودکار بستانکار وام هنگام تغییر وضعیت وام به 'purchased' (DISABLED)"""
#     pass


@receiver(post_save, sender=LoanCreditor)
def auto_update_loan_creditor_paid_amount(sender, instance, **kwargs):
    """
    خودکار به‌روزرسانی paid_amount برای نقدی
    وقتی settlement_status نقدی به 'settled' تغییر کند، paid_amount = total_amount
    """
    if instance.payment_type == 'cash' and instance.settlement_status == 'settled':
        if instance.paid_amount != instance.total_amount:
            # استفاده از update برای جلوگیری از حلقه نامتناهی
            LoanCreditor.objects.filter(pk=instance.pk).update(
                paid_amount=instance.total_amount
            )


@receiver(post_save, sender=LoanBuyer)
def auto_populate_loan_buyer_broker(sender, instance, created, **kwargs):
    """خودکار به‌روزرسانی کارگذار خریدار وام"""
    from django.http import request as http_request
    # این سیگنال در admin.py به‌روز می‌شود
    pass
