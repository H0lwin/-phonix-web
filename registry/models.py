"""
مدل‌های سیستم ثبتی خدمات
Registry Services Models System
"""
from django.db import models
from django.contrib.auth.models import User
from django_jalali.db import models as jmodels
from django.core.validators import FileExtensionValidator, MinValueValidator
import os


class IdentityDocuments(models.Model):
    """مدارک و اسناد هویتی - قابل استفاده مجدد"""
    DOCUMENT_TYPE_CHOICES = (
        ('national_id', 'کارت ملی'),
        ('birth_cert', 'شناسنامه'),
        ('passport', 'گذرنامه'),
        ('other', 'سایر'),
    )
    
    # معلومات هویتی
    first_name = models.CharField(max_length=100, verbose_name="نام")
    last_name = models.CharField(max_length=100, verbose_name="نام خانوادگی")
    national_id = models.CharField(max_length=10, unique=True, verbose_name="کد ملی")
    certificate_number = models.CharField(max_length=20, verbose_name="شماره شناسنامه")
    birth_date = jmodels.jDateField(verbose_name="تاریخ تولد")
    birth_place = models.CharField(max_length=100, verbose_name="محل صدور شناسنامه")
    
    # تصویر اسناد
    national_id_image = models.ImageField(
        upload_to='documents/national_id/%Y/%m/%d/',
        verbose_name="عکس کارت ملی",
        help_text="فرمت‌های مجاز: JPG, PNG (حداکثر 10 مگابایت)"
    )
    
    # سایر مدارک (اختیاری)
    additional_documents = models.FileField(
        upload_to='documents/additional/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name="سایر مدارک",
        help_text="PDF, ZIP یا سایر فرمت‌ها (حداکثر 10 مگابایت)"
    )
    
    # متاداده
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_identity_documents',
        verbose_name="ثبت‌کننده"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")
    
    class Meta:
        verbose_name = "مدارک هویتی"
        verbose_name_plural = "مدارک هویتی"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.national_id})"


class ContactInfo(models.Model):
    """اطلاعات تماس - قابل استفاده مجدد"""
    # اطلاعات شناخت‌شخص
    first_name = models.CharField(
        max_length=100,
        verbose_name="نام"
    )
    last_name = models.CharField(
        max_length=100,
        verbose_name="نام خانوادگی"
    )
    national_id = models.CharField(
        max_length=10,
        unique=True,
        verbose_name="کد ملی"
    )
    
    # اطلاعات تماس
    phone_number = models.CharField(
        max_length=11,
        blank=True,
        null=True,
        verbose_name="شماره تلفن ثابت"
    )
    mobile_number = models.CharField(
        max_length=11,
        blank=True,
        null=True,
        verbose_name="شماره تلفن موبایل"
    )
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name="آدرس ایمیل"
    )
    address = models.TextField(
        blank=True,
        null=True,
        verbose_name="آدرس کامل"
    )
    postal_code = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name="کد پستی"
    )
    
    # متاداده
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_contact_infos',
        verbose_name="ثبت‌کننده"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")
    
    class Meta:
        verbose_name = "اطلاعات تماس"
        verbose_name_plural = "اطلاعات تماس"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.national_id})"


class RegistryServiceCategory(models.Model):
    """دسته‌کلان خدمات ثبتی"""
    CATEGORY_CHOICES = (
        ('licenses', 'مجوزها'),
        ('trade', 'بازرگانی'),
        ('companies', 'شرکت‌ها'),
    )
    
    name = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        unique=True,
        verbose_name="نام دسته"
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="توضیحات کلی"
    )
    
    # متاداده
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "دسته خدمات ثبتی"
        verbose_name_plural = "دسته‌های خدمات ثبتی"
    
    def __str__(self):
        return self.get_name_display()


# ============================================
# 1. مجوزها (Licenses)
# ============================================

class License(models.Model):
    """خدمات ثبتی - مجوزها"""
    SUBCATEGORY_CHOICES = (
        ('household', 'خانگی'),
        ('professional', 'صنفی'),
        ('other', 'سایر'),
    )
    
    # دسته‌بندی
    subcategory = models.CharField(
        max_length=50,
        choices=SUBCATEGORY_CHOICES,
        verbose_name="دسته‌بندی جزئی"
    )
    
    # اطلاعات خدمت
    service_title = models.CharField(
        max_length=200,
        verbose_name="عنوان خدمت"
    )
    
    # مدارک و اطلاعات
    identity_documents = models.ForeignKey(
        IdentityDocuments,
        on_delete=models.PROTECT,
        related_name='licenses',
        verbose_name="مدارک هویتی"
    )
    contact_info = models.ForeignKey(
        ContactInfo,
        on_delete=models.PROTECT,
        related_name='licenses',
        verbose_name="اطلاعات تماس"
    )
    
    # مالی
    amount_received = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="مبلغ دریافتی",
        validators=[MinValueValidator(0)]
    )
    
    # توضیحات
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="توضیحات"
    )
    
    # متاداده
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_licenses'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "مجوز"
        verbose_name_plural = "مجوزها"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.service_title} - {self.get_subcategory_display()}"


# ============================================
# 2. بازرگانی (Trade)
# ============================================

class TradeAcquisition(models.Model):
    """بازرگانی اخذ - دریافت"""
    ENTITY_TYPE_CHOICES = (
        ('legal', 'حقوقی'),
        ('natural', 'حقیقی'),
    )
    
    CHECK_CATEGORY_CHOICES = (
        ('has', 'دارد'),
        ('no', 'ندارد'),
    )
    
    # دسته‌بندی
    entity_type = models.CharField(
        max_length=50,
        choices=ENTITY_TYPE_CHOICES,
        verbose_name="نوع دریافت"
    )
    
    # اطلاعات خدمت
    acquisition_type = models.CharField(
        max_length=200,
        verbose_name="نوع دریافت تفصیلی"
    )
    
    # مدارک و اطلاعات
    identity_documents = models.ForeignKey(
        IdentityDocuments,
        on_delete=models.PROTECT,
        related_name='trade_acquisitions',
        verbose_name="مدارک هویتی"
    )
    contact_info = models.ForeignKey(
        ContactInfo,
        on_delete=models.PROTECT,
        related_name='trade_acquisitions',
        verbose_name="اطلاعات تماس"
    )
    
    # چک
    check_category = models.CharField(
        max_length=50,
        choices=CHECK_CATEGORY_CHOICES,
        verbose_name="دسته چک"
    )
    
    # مالی
    amount_received = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="مبلغ دریافتی",
        validators=[MinValueValidator(0)]
    )
    
    # توضیحات
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="توضیحات"
    )
    
    # متاداده
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_trade_acquisitions'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "بازرگانی اخذ"
        verbose_name_plural = "بازرگانی‌های اخذ"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"دریافت {self.get_entity_type_display()} - {self.acquisition_type}"


class TradePartnership(models.Model):
    """بازرگانی مشارکتی - کارت بازرگانی"""
    ENTITY_TYPE_CHOICES = (
        ('natural', 'حقیقی'),
        ('legal', 'حقوقی'),
        ('productive', 'تولیدی'),
    )
    
    # دسته‌بندی
    entity_type = models.CharField(
        max_length=50,
        choices=ENTITY_TYPE_CHOICES,
        verbose_name="نوع کارت بازرگانی"
    )
    
    # اطلاعات
    card_year = models.IntegerField(
        verbose_name="سال دریافت کارت"
    )
    import_ceiling = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="سقف واردات",
        validators=[MinValueValidator(0)]
    )
    export_ceiling = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="سقف صادرات",
        validators=[MinValueValidator(0)]
    )
    import_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="مبلغ واردات",
        validators=[MinValueValidator(0)]
    )
    export_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="مبلغ صادرات",
        validators=[MinValueValidator(0)]
    )
    
    # مدارک و اطلاعات
    identity_documents = models.ForeignKey(
        IdentityDocuments,
        on_delete=models.PROTECT,
        related_name='trade_partnerships',
        verbose_name="مدارک هویتی"
    )
    contact_info = models.ForeignKey(
        ContactInfo,
        on_delete=models.PROTECT,
        related_name='trade_partnerships',
        verbose_name="اطلاعات تماس"
    )
    
    # مالی
    amount_received = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="مبلغ دریافتی",
        validators=[MinValueValidator(0)]
    )
    
    # توضیحات
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="توضیحات"
    )
    
    # متاداده
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_trade_partnerships'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "بازرگانی مشارکتی"
        verbose_name_plural = "بازرگانی‌های مشارکتی"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"کارت بازرگانی {self.get_entity_type_display()} - سال {self.card_year}"


# ============================================
# 3. شرکت‌ها (Companies)
# ============================================

class Company(models.Model):
    """شرکت‌ها"""
    COMPANY_TYPE_CHOICES = (
        ('limited_liability', 'مسئولیت محدود'),
        ('joint_stock', 'سهامی عام'),
        ('cooperative', 'تعاونی'),
        ('transport', 'حمل و نقل'),
    )
    
    # دسته‌بندی
    company_type = models.CharField(
        max_length=50,
        choices=COMPANY_TYPE_CHOICES,
        verbose_name="نوع شرکت"
    )
    
    # اطلاعات
    company_name = models.CharField(
        max_length=200,
        verbose_name="نام شرکت"
    )
    
    # مدارک و اطلاعات
    identity_documents = models.ForeignKey(
        IdentityDocuments,
        on_delete=models.PROTECT,
        related_name='companies',
        verbose_name="مدارک هویتی"
    )
    contact_info = models.ForeignKey(
        ContactInfo,
        on_delete=models.PROTECT,
        related_name='companies',
        verbose_name="اطلاعات تماس"
    )
    
    # مجوز
    has_license = models.BooleanField(
        default=False,
        verbose_name="آیا مجوز موجود است؟"
    )
    license_file = models.FileField(
        upload_to='documents/licenses/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name="فایل مجوز",
        help_text="الزامی اگر مجوز موجود باشد (حداکثر 10 مگابایت)"
    )
    
    # مالی
    amount_received = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="مبلغ دریافتی",
        validators=[MinValueValidator(0)]
    )
    
    # توضیحات
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="توضیحات"
    )
    
    # متاداده
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_companies'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "شرکت"
        verbose_name_plural = "شرکت‌ها"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.company_name} ({self.get_company_type_display()})"
    
    def clean(self):
        """تایید دسترسی به فیلدها"""
        from django.core.exceptions import ValidationError
        
        # اگر مجوز موجود است، فایل الزامی است
        if self.has_license and not self.license_file:
            raise ValidationError({
                'license_file': 'فایل مجوز الزامی است اگر مجوز موجود باشد.'
            })