from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal

class ConsultationPrice(models.Model):
    """قیمت‌گذاری خدمات مشاوره و پرونده"""
    
    SERVICE_TYPE_CHOICES = (
        ('free_consultation', 'مشاوره رایگان (15 دقیقه)'),
        ('hourly_rate', 'نرخ ساعتی مشاوره'),
        ('case_study', 'مطالعه و تجزیه‌تحلیل پرونده'),
        ('other', 'سایر خدمات'),
    )
    
    service_type = models.CharField(
        max_length=30, 
        choices=SERVICE_TYPE_CHOICES, 
        unique=True,
        verbose_name='نوع خدمت'
    )
    
    description = models.TextField(
        verbose_name='توضیحات خدمت',
        blank=True
    )
    
    price = models.DecimalField(
        max_digits=12, 
        decimal_places=0,
        validators=[MinValueValidator(Decimal('0'))],
        default=0,
        verbose_name='قیمت (تومان)',
        help_text='برای مشاوره رایگان، مقدار 0 وارد کنید'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='فعال'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    
    class Meta:
        verbose_name = "قیمت خدمت"
        verbose_name_plural = "قیمت‌های خدمات"
        ordering = ['service_type']
    
    def __str__(self):
        return f"{self.get_service_type_display()} - {self.price:,.0f} تومان"
    
    def get_formatted_price(self):
        """نمایش قیمت با جداکنندگی هزارگان"""
        return f"{self.price:,.0f}"


class Consultation(models.Model):
    """ثبت مشاوره و اطلاعات مراجعین"""
    
    STATUS_CHOICES = (
        ('pending', 'در انتظار مشاوره'),
        ('completed', 'مشاوره انجام‌شده'),
        ('converted_to_case', 'تبدیل‌شده به پرونده'),
        ('cancelled', 'لغو‌شده'),
    )
    
    PAYMENT_STATUS_CHOICES = (
        ('free', 'رایگان'),
        ('unpaid', 'پرداخت‌نشده'),
        ('paid', 'پرداخت‌شده'),
        ('partial', 'جزئی‌ پرداخت‌شده'),
    )
    
    # اطلاعات مراجع
    client_name = models.CharField(max_length=200, verbose_name='نام مراجع')
    client_phone = models.CharField(max_length=20, verbose_name='شماره تماس')
    client_national_id = models.CharField(
        max_length=10, 
        verbose_name='کد ملی',
        blank=True,
        null=True
    )
    client_address = models.TextField(
        verbose_name='آدرس',
        blank=True
    )
    client_email = models.EmailField(
        verbose_name='ایمیل',
        blank=True,
        null=True
    )
    
    # مشخصات مشاوره
    consultation_subject = models.CharField(
        max_length=300,
        verbose_name='موضوع مشاوره'
    )
    consultation_details = models.TextField(
        verbose_name='جزئیات مشاوره',
        blank=True
    )
    
    consultation_date = models.DateTimeField(
        verbose_name='تاریخ و ساعت مشاوره'
    )
    
    assigned_lawyer = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='consultations',
        limit_choices_to={'profile__role': 'lawyer'},
        verbose_name='وکیل مسئول'
    )
    
    # وضعیت و هزینه
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending',
        verbose_name='وضعیت'
    )
    
    consultation_fee = models.DecimalField(
        max_digits=12, 
        decimal_places=0,
        default=0,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name='هزینه مشاوره (تومان)',
        help_text='اگر مشاوره رایگان است، 0 وارد کنید'
    )
    
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='free',
        verbose_name='وضعیت پرداخت'
    )
    
    amount_paid = models.DecimalField(
        max_digits=12, 
        decimal_places=0,
        default=0,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name='مبلغ پرداخت‌شده (تومان)'
    )
    
    # تبدیل به پرونده
    converted_to_case = models.OneToOneField(
        'CaseFile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='consultation_source',
        verbose_name='تبدیل‌شده به پرونده'
    )
    
    conversion_date = models.DateTimeField(
        verbose_name='تاریخ تبدیل به پرونده',
        null=True,
        blank=True
    )
    
    final_contract_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=0,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name='مبلغ نهایی قرارداد (تومان)'
    )
    
    conversion_notes = models.TextField(
        verbose_name='توضیحات تبدیل',
        blank=True
    )
    
    # یادداشت‌های کلی
    notes = models.TextField(
        verbose_name='یادداشت‌های کلی',
        blank=True
    )
    
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='created_consultations',
        verbose_name='ثبت‌کننده'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    
    class Meta:
        verbose_name = "مشاوره"
        verbose_name_plural = "مشاورات"
        ordering = ['-consultation_date']
    
    def __str__(self):
        return f"{self.client_name} - {self.consultation_subject}"
    
    def get_formatted_fee(self):
        """نمایش هزینه با جداکنندگی هزارگان"""
        return f"{self.consultation_fee:,.0f}"
    
    def get_formatted_paid(self):
        """نمایش مبلغ پرداخت‌شده"""
        return f"{self.amount_paid:,.0f}"
    
    def get_formatted_contract_amount(self):
        """نمایش مبلغ قرارداد"""
        if self.final_contract_amount:
            return f"{self.final_contract_amount:,.0f}"
        return '-'
    
    def get_fee_difference(self):
        """محاسبه اختلاف بین هزینه مشاوره رایگان و نهایی قرارداد"""
        if self.final_contract_amount:
            # اگر مشاوره رایگان بود (0) و حالا قرارداد شد
            return self.final_contract_amount - self.consultation_fee
        return 0


class CaseFile(models.Model):
    """پرونده حقوقی یا قضایی"""
    
    STATUS_CHOICES = (
        ('pending', 'در انتظار'),
        ('in_progress', 'در حال بررسی'),
        ('completed', 'تکمیل‌شده'),
        ('closed', 'بسته‌شده'),
    )
    
    CASE_TYPE_CHOICES = (
        ('legal', 'حقوقی'),
        ('judicial', 'قضایی'),
        ('other', 'سایر'),
    )
    
    PRIORITY_CHOICES = (
        ('low', 'کم'),
        ('medium', 'متوسط'),
        ('high', 'بالا'),
        ('urgent', 'فوری'),
    )
    
    # اطلاعات شناسایی
    case_number = models.CharField(
        max_length=100, 
        unique=True, 
        verbose_name='شماره پرونده'
    )
    title = models.CharField(
        max_length=200, 
        verbose_name='عنوان پرونده'
    )
    case_type = models.CharField(
        max_length=20,
        choices=CASE_TYPE_CHOICES,
        default='legal',
        verbose_name='نوع پرونده'
    )
    
    # اطلاعات طرف مقابل و مراجع
    client_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='نام مراجع/موکل'
    )
    client_national_id = models.CharField(
        max_length=10,
        blank=True,
        verbose_name='کد ملی مراجع'
    )
    client_phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='تلفن مراجع'
    )
    client_address = models.TextField(
        blank=True,
        verbose_name='آدرس مراجع'
    )
    
    # جزئیات پرونده
    description = models.TextField(
        blank=True,
        verbose_name='توضیحات و خلاصه پرونده'
    )
    case_details = models.TextField(
        blank=True,
        verbose_name='جزئیات تفصیلی'
    )
    
    # مشخصات قانونی
    legal_basis = models.TextField(
        blank=True,
        verbose_name='مبنای قانونی/ماده‌های مربوط'
    )
    court_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='نام دادگاه'
    )
    court_case_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='شماره پرونده دادگاه'
    )
    judge_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='نام قاضی'
    )
    
    # زمان‌بندی
    case_start_date = models.DateField(
        verbose_name='تاریخ شروع پرونده',
        null=True,
        blank=True
    )
    case_end_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='تاریخ پایان پرونده'
    )
    next_hearing_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='تاریخ جلسه بعدی'
    )
    
    # اطلاعات مالی
    contract_amount = models.DecimalField(
        max_digits=15,
        decimal_places=0,
        default=0,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name='مبلغ قرارداد (تومان)'
    )
    paid_amount = models.DecimalField(
        max_digits=15,
        decimal_places=0,
        default=0,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name='مبلغ پرداخت‌شده (تومان)'
    )
    
    # وضعیت
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium',
        verbose_name='اولویت'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='وضعیت'
    )
    
    # اختصاصات و مسئولیت
    assigned_lawyer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='assigned_cases',
        limit_choices_to={'profile__role': 'lawyer'},
        verbose_name='وکیل مسئول'
    )
    co_lawyers = models.ManyToManyField(
        User,
        related_name='co_assigned_cases',
        blank=True,
        limit_choices_to={'profile__role': 'lawyer'},
        verbose_name='وکلای همکار'
    )
    
    # یادداشت‌ها
    notes = models.TextField(
        blank=True,
        verbose_name='یادداشت‌های کلی'
    )
    
    # اطلاعات سیستمی
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_cases',
        verbose_name='ایجاد‌کننده'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ایجاد'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='تاریخ بروزرسانی'
    )
    
    class Meta:
        verbose_name = "پرونده"
        verbose_name_plural = "پرونده‌ها"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.case_number} - {self.title}"
    
    def get_formatted_contract_amount(self):
        """نمایش مبلغ قرارداد با جداکنندگی"""
        return f"{self.contract_amount:,.0f}"
    
    def get_formatted_paid_amount(self):
        """نمایش مبلغ پرداخت‌شده با جداکنندگی"""
        return f"{self.paid_amount:,.0f}"
    
    def get_remaining_amount(self):
        """محاسبه مبلغ باقی‌مانده"""
        return self.contract_amount - self.paid_amount


class CaseFileAttachment(models.Model):
    """پیوست‌های فایل برای پرونده‌ها و مشاورات"""
    
    ATTACHMENT_TYPE_CHOICES = (
        ('document', 'سند'),
        ('contract', 'قرارداد'),
        ('evidence', 'مدرک/شاهد'),
        ('court_order', 'دستور دادگاه'),
        ('letter', 'نامه'),
        ('photo', 'عکس'),
        ('other', 'سایر'),
    )
    
    # پرونده یا مشاوره (حداقل یکی باید انتخاب شود)
    case = models.ForeignKey(
        CaseFile,
        on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name='پرونده',
        null=True,
        blank=True
    )
    
    consultation = models.ForeignKey(
        Consultation,
        on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name='مشاوره',
        null=True,
        blank=True
    )
    
    attachment_type = models.CharField(
        max_length=20,
        choices=ATTACHMENT_TYPE_CHOICES,
        default='document',
        verbose_name='نوع پیوست'
    )
    
    title = models.CharField(
        max_length=200,
        verbose_name='عنوان پیوست'
    )
    
    description = models.TextField(
        blank=True,
        verbose_name='توضیحات'
    )
    
    file = models.FileField(
        upload_to='case_attachments/%Y/%m/%d/',
        verbose_name='فایل'
    )
    
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='بارگذاری‌شده توسط'
    )
    
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ بارگذاری'
    )
    
    class Meta:
        verbose_name = "پیوست پرونده یا مشاوره"
        verbose_name_plural = "پیوست‌های پرونده و مشاورات"
        ordering = ['-uploaded_at']
    
    def __str__(self):
        """نمایش متن مدل"""
        if self.case:
            return f"{self.title} - پرونده {self.case.case_number}"
        elif self.consultation:
            return f"{self.title} - مشاوره {self.consultation.client_name}"
        return f"{self.title}"
    
    def clean(self):
        """اعتبارسنجی - حداقل یکی از case یا consultation باید انتخاب شود"""
        from django.core.exceptions import ValidationError
        if not self.case and not self.consultation:
            raise ValidationError('لطفاً حداقل یک پرونده یا مشاوره انتخاب کنید')
    
    def get_file_size_kb(self):
        """محاسبه اندازه فایل به کیلوبایت"""
        if self.file:
            return round(self.file.size / 1024, 2)
        return 0