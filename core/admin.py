from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.core.exceptions import PermissionDenied
from django.forms.formsets import DELETION_FIELD_NAME
from django.forms.models import BaseInlineFormSet
from django_jalali.admin.filters import JDateFieldListFilter
from django_jalali.db import models as jmodels
from admincharts.admin import AdminChartMixin
from .models import (
    UserProfile,
    Branch, Employee, ActivityReport,
    Income, Expense,
    Loan, LoanBuyer, LoanBuyerStatusHistory, LoanCreditor, LoanCreditorInstallment,
    ActivityLog
)

# ثبتی خدمات
from registry.models import (
    IdentityDocuments, ContactInfo, License, 
    TradeAcquisition, TradePartnership, Company
)

# Unregister the default User Admin
admin.site.unregister(User)


# ============================================
# توابع کمکی برای کنترل دسترسی (Permission Helpers)
# ============================================

def is_admin(user):
    """بررسی کاربر ادمین است - تنها superuser یا کاربران با role='admin'"""
    if user.is_superuser:
        return True
    # بررسی اینکه کاربر role='admin' داشته باشد (نه تنها is_staff)
    if hasattr(user, 'profile') and user.profile.role == 'admin':
        return True
    return False

def is_employee(user):
    """بررسی کاربر کارمند است"""
    if hasattr(user, 'profile'):
        return user.profile.role == 'employee'
    return False

def is_lawyer(user):
    """بررسی کاربر وکیل است"""
    if hasattr(user, 'profile'):
        return user.profile.role == 'lawyer'
    return False

def is_non_admin(user):
    """بررسی کاربر کارمند یا وکیل است (غیر ادمین)"""
    return is_employee(user) or is_lawyer(user)

def is_pure_admin(user):
    """بررسی کاربر admin واقعی است (superuser یا role='admin')"""
    if user.is_superuser:
        return True
    if hasattr(user, 'profile') and user.profile.role == 'admin':
        return True
    return False


# ============================================
# فرم‌های سفارشی برای LoanAdmin
# ============================================

class LoanForm(forms.ModelForm):
    """فرم سفارشی برای وام - نوع وام دستی"""
    
    class Meta:
        model = Loan
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # loan_type به صورت TextField (input type text)
        self.fields['loan_type'].widget = forms.TextInput(attrs={
            'placeholder': 'مثال: مسکن، شخصی، خودرو، کسب‌وکار، ...',
            'size': 50
        })
        
        # نمایش مبالغ با جداکنندگی هزارگان به صورت read-only
        if self.instance.pk:
            self.fields['amount'].help_text = f"مبلغ فعلی: {self.instance.get_formatted_amount()}"
            if self.instance.purchase_rate:
                self.fields['purchase_rate'].help_text = f"قیمت فعلی: {self.instance.get_formatted_purchase_rate()}"

# ============================================
# Inline Admin برای UserProfile
# ============================================

class UserProfileInlineFormSet(BaseInlineFormSet):
    def save(self, commit=True):
        if not commit:
            return super().save(commit)
        self.new_objects = []
        self.changed_objects = []
        self.deleted_objects = []
        instances = []
        existing_profile = UserProfile.objects.filter(user=self.instance).first()
        for form in self.forms:
            if not hasattr(form, 'cleaned_data'):
                continue
            if form.cleaned_data.get(DELETION_FIELD_NAME):
                continue
            if not form.has_changed() and existing_profile:
                continue
            data = {}
            for field_name, value in form.cleaned_data.items():
                if field_name in ('id', 'user', DELETION_FIELD_NAME):
                    continue
                data[field_name] = value
            profile, created = UserProfile.objects.update_or_create(
                user=self.instance,
                defaults=data
            )
            form.instance = profile
            if created:
                self.new_objects.append(profile)
            elif form.has_changed():
                self.changed_objects.append((profile, form.changed_data))
            if hasattr(form, 'save_m2m'):
                form.save_m2m()
            instances.append(profile)
            existing_profile = profile
        return instances


class UserProfileInline(admin.StackedInline):
    """Inline مدیریت پروفایل کاربر در User Admin"""
    model = UserProfile
    formset = UserProfileInlineFormSet
    extra = 1
    max_num = 1
    fk_name = 'user'
    can_delete = False
    verbose_name_plural = "اطلاعات کارمندی و احراز هویت"
    
    fieldsets = (
        ('هویت کاربر (الزامی)', {
            'fields': ('national_id', 'display_name', 'personnel_id'),
            'description': 'کد ملی اجباری است و نام نمایشی باید برای سیستم وارد شود'
        }),
        ('نقش و دپارتمان', {
            'fields': ('role', 'department')
        }),
        ('مشخصات شخصی', {
            'fields': ('birth_date', 'gender', 'phone', 'address')
        }),
        ('تصاویر', {
            'fields': ('avatar', 'profile_picture')
        }),
        ('اطلاعات کاری (الزامی)', {
            'fields': ('job_title', 'hire_date', 'branch', 'contract_type', 
                      'employment_status', 'contract_end_date'),
            'description': 'تاریخ استخدام الزامی است؛ تاریخ پایان قرارداد تنها در صورت اتمام قرارداد پر شود'
        }),
        ('اطلاعات مالی', {
            'fields': ('base_salary', 'benefits', 'payment_method', 
                      'bank_account_number', 'insurance_info')
        }),
        ('تحصیلات و یادداشت‌ها', {
            'fields': ('education', 'bio', 'internal_notes'),
            'classes': ('collapse',)
        }),
        ('تاریخ‌های ثبت', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'personnel_id')
    
    def get_formset(self, request, obj=None, **kwargs):
        """تنظیم فیلدهای formset برای نمایش نام‌های پیشنهادی سمت"""
        formset = super().get_formset(request, obj, **kwargs)
        # نمایش راهنمایی برای سمت
        form = formset.form
        if hasattr(form.base_fields.get('job_title'), 'help_text'):
            form.base_fields['job_title'].help_text = f"مثال‌ها: {', '.join(UserProfile.JOB_TITLE_SUGGESTIONS[:4])}"
        return formset


# ============================================
# مدیریت کاربران (User Management)
# ============================================

@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    """مدیریت کاربران سیستم - تمام کاربران کارمند هستند"""
    inlines = [UserProfileInline]
    
    list_display = ('get_display_name', 'get_national_id', 'get_personnel_id', 
                    'email', 'get_role', 'get_job_title', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'profile__role', 'profile__employment_status', 
                   'profile__branch', 'profile__hire_date')
    search_fields = ('profile__national_id', 'profile__display_name', 'email', 
                    'profile__personnel_id', 'profile__job_title')
    
    add_fieldsets = (
        ('حساب کاربری', {
            'fields': ('username', 'email', 'password1', 'password2'),
            'description': 'نام کاربری و رمز عبور برای ورود به سیستم (یا استفاده از کد ملی)'
        }),
        ('اجازه‌ها', {
            'fields': ('is_active', 'is_staff', 'is_superuser'),
            'classes': ('collapse',)
        }),
    )
    
    fieldsets = (
        ('حساب کاربری', {
            'fields': ('username', 'email', 'password'),
            'description': 'اطلاعات ورود به سیستم'
        }),
        ('اجازه‌ها و دسترسی', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('تاریخ‌ها', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )
    
    def get_display_name(self, obj):
        """نمایش نام و نام خانوادگی از پروفایل"""
        if hasattr(obj, 'profile') and obj.profile.display_name:
            return obj.profile.display_name
        return obj.username
    get_display_name.short_description = "نام و نام خانوادگی"
    
    def get_national_id(self, obj):
        """نمایش کد ملی کاربر"""
        if hasattr(obj, 'profile') and obj.profile.national_id:
            return obj.profile.national_id
        return '-'
    get_national_id.short_description = "کد ملی"
    
    def get_personnel_id(self, obj):
        """نمایش شماره پرسنلی"""
        if hasattr(obj, 'profile') and obj.profile.personnel_id:
            return obj.profile.personnel_id
        return '-'
    get_personnel_id.short_description = "شماره پرسنلی"
    
    def get_role(self, obj):
        """نمایش نقش کاربر"""
        if hasattr(obj, 'profile'):
            return obj.profile.get_role_display()
        return '-'
    get_role.short_description = "نقش"
    
    def get_job_title(self, obj):
        """نمایش سمت کاربر"""
        if hasattr(obj, 'profile') and obj.profile.job_title:
            return obj.profile.job_title
        return '-'
    get_job_title.short_description = "سمت/شغل"
    
    def has_module_permission(self, request):
        """فقط ادمین می‌تواند این مدل را ببیند - کارمندان دسترسی ندارند"""
        return is_admin(request.user)
    
    def has_view_permission(self, request, obj=None):
        """فقط ادمین"""
        return is_admin(request.user)
    
    def has_add_permission(self, request):
        """فقط ادمین"""
        return is_admin(request.user)
    
    def has_change_permission(self, request, obj=None):
        """فقط ادمین"""
        return is_admin(request.user)
    
    def has_delete_permission(self, request, obj=None):
        """فقط ادمین"""
        return is_admin(request.user)




# ============================================
# مدیریت انسانی (HR Management Admin)
# ============================================

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    """مدیریت شعبه‌ها - فقط ادمین"""
    list_display = ('name', 'code', 'branch_type', 'city', 'status', 'manager', 'phone', 'get_working_hours')
    list_filter = ('status', 'branch_type', ('founding_date', JDateFieldListFilter), 'manager')
    search_fields = ('name', 'code', 'phone', 'address', 'city', 'province')
    readonly_fields = ('created_at', 'updated_at')
    
    def has_module_permission(self, request):
        """فقط ادمین می‌تواند این مدل را ببیند"""
        return is_admin(request.user)
    
    def has_view_permission(self, request, obj=None):
        """فقط ادمین می‌تواند شعبه‌ها را ببیند"""
        return is_admin(request.user)
    
    def has_add_permission(self, request):
        """فقط ادمین می‌تواند شعبه اضافه کند"""
        return is_admin(request.user)
    
    def has_change_permission(self, request, obj=None):
        """فقط ادمین می‌تواند شعبه تغییر بدهد"""
        return is_admin(request.user)
    
    def has_delete_permission(self, request, obj=None):
        """فقط ادمین می‌تواند شعبه حذف کند"""
        return is_admin(request.user)
    
    fieldsets = (
        ('اطلاعات شناسایی', {
            'fields': ('name', 'code', 'branch_type')
        }),
        ('اطلاعات مکانی', {
            'fields': ('address', 'city', 'province', 'postal_code')
        }),
        ('اطلاعات تماس', {
            'fields': ('phone',)
        }),
        ('مدیریت داخلی', {
            'fields': ('manager', 'status')
        }),
        ('سایر اطلاعات', {
            'fields': ('description', 'working_start_time', 'working_end_time', 'founding_date', 'monthly_budget')
        }),
        ('تاریخ‌ها', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_working_hours(self, obj):
        if obj.working_start_time and obj.working_end_time:
            return f"{obj.working_start_time.strftime('%H:%M')} - {obj.working_end_time.strftime('%H:%M')}"
        return '-'
    get_working_hours.short_description = "ساعات کاری"



@admin.register(ActivityReport)
class ActivityReportAdmin(admin.ModelAdmin):
    """مدیریت گزارش فعالیت - فقط ادمین"""
    list_display = ('employee', 'title', 'date', 'time', 'created_at')
    list_filter = ('date', 'employee__branch', 'created_at')
    search_fields = ('title', 'description', 'employee__user__first_name')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'date'
    
    fieldsets = (
        ('کارمند', {
            'fields': ('employee', 'date', 'time')
        }),
        ('گزارش', {
            'fields': ('title', 'description')
        }),
        ('تاریخ‌ها', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_module_permission(self, request):
        """فقط ادمین می‌تواند این مدل را ببیند - کارمندان دسترسی ندارند"""
        return is_admin(request.user)
    
    def has_view_permission(self, request, obj=None):
        """فقط ادمین می‌تواند ببیند"""
        return is_admin(request.user)
    
    def has_add_permission(self, request):
        """فقط ادمین می‌تواند اضافه کند"""
        return is_admin(request.user)
    
    def has_change_permission(self, request, obj=None):
        """فقط ادمین می‌تواند تغییر دهد"""
        return is_admin(request.user)
    
    def has_delete_permission(self, request, obj=None):
        """فقط ادمین می‌تواند حذف کند"""
        return is_admin(request.user)
    
    def get_queryset(self, request):
        """تصفیه گزارش‌های فعالیت بر اساس نقش کاربر"""
        qs = super().get_queryset(request)
        if is_admin(request.user):
            return qs
        # کارمندان نمی‌توانند گزارش‌ها ببینند
        if is_employee(request.user):
            try:
                employee = Employee.objects.get(user=request.user)
                return qs.filter(employee=employee)
            except Employee.DoesNotExist:
                return qs.none()
        return qs
    
    def save_model(self, request, obj, form, change):
        """تنظیم کارمند برای رکورد جدید"""
        if not change and is_employee(request.user):  # رکورد جدید
            try:
                employee = Employee.objects.get(user=request.user)
                obj.employee = employee
            except Employee.DoesNotExist:
                pass
        super().save_model(request, obj, form, change)


# ============================================
# مدیریت مالی (Finance Management Admin)
# ============================================


@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    """مدیریت درآمدها - فقط ادمین"""
    list_display = ('title', 'get_formatted_amount', 'category', 'payment_status', 'branch', 'registration_date')
    list_filter = ('category', 'payment_status', 'payment_method', ('registration_date', JDateFieldListFilter),
                   'branch', 'is_verified')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at', 'registration_date')
    date_hierarchy = 'registration_date'
    
    def has_module_permission(self, request):
        """فقط ادمین می‌تواند این مدل را ببیند"""
        return is_admin(request.user)
    
    def has_view_permission(self, request, obj=None):
        """فقط ادمین می‌تواند درآمدها را ببیند"""
        return is_admin(request.user)
    
    def has_add_permission(self, request):
        """فقط ادمین می‌تواند درآمد اضافه کند"""
        return is_admin(request.user)
    
    def has_change_permission(self, request, obj=None):
        """فقط ادمین می‌تواند درآمد تغییر بدهد"""
        return is_admin(request.user)
    
    def has_delete_permission(self, request, obj=None):
        """فقط ادمین می‌تواند درآمد حذف کند"""
        return is_admin(request.user)
    
    def get_formatted_amount(self, obj):
        return obj.get_formatted_amount()
    get_formatted_amount.short_description = "مبلغ درآمد"
    
    fieldsets = (
        ('اطلاعات پایه', {
            'fields': ('title', 'description')
        }),
        ('جزئیات مالی', {
            'fields': ('amount', 'payment_method', 'payment_status')
        }),
        ('طبقه‌بندی', {
            'fields': ('category',)
        }),
        ('تاریخ‌ها', {
            'fields': ('registration_date', 'received_date')
        }),
        ('منابع', {
            'fields': ('branch',)
        }),
        ('حسابرسی و پیوست‌ها', {
            'fields': ('is_verified', 'attachment')
        }),
        ('تاریخ‌های سیستم', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    """مدیریت هزینه‌ها - فقط ادمین"""
    list_display = ('title', 'get_formatted_amount', 'category', 'payment_status', 'branch', 'registration_date')
    list_filter = ('category', 'payment_status', 'payment_method', ('registration_date', JDateFieldListFilter),
                   'branch', 'is_verified')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at', 'registration_date')
    date_hierarchy = 'registration_date'
    
    def has_module_permission(self, request):
        """فقط ادمین می‌تواند این مدل را ببیند"""
        return is_admin(request.user)
    
    def has_view_permission(self, request, obj=None):
        """فقط ادمین می‌تواند هزینه‌ها را ببیند"""
        return is_admin(request.user)
    
    def has_add_permission(self, request):
        """فقط ادمین می‌تواند هزینه اضافه کند"""
        return is_admin(request.user)
    
    def has_change_permission(self, request, obj=None):
        """فقط ادمین می‌تواند هزینه تغییر بدهد"""
        return is_admin(request.user)
    
    def has_delete_permission(self, request, obj=None):
        """فقط ادمین می‌تواند هزینه حذف کند"""
        return is_admin(request.user)
    
    def get_formatted_amount(self, obj):
        return obj.get_formatted_amount()
    get_formatted_amount.short_description = "مبلغ هزینه"
    
    fieldsets = (
        ('اطلاعات پایه', {
            'fields': ('title', 'description')
        }),
        ('جزئیات مالی', {
            'fields': ('amount', 'payment_method', 'payment_status')
        }),
        ('طبقه‌بندی', {
            'fields': ('category',)
        }),
        ('تاریخ‌ها', {
            'fields': ('registration_date', 'payment_date')
        }),
        ('منابع', {
            'fields': ('branch',)
        }),
        ('حسابرسی و پیوست‌ها', {
            'fields': ('is_verified', 'attachment')
        }),
        ('تاریخ‌های سیستم', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# ============================================
# مدیریت وام‌ها (Loan Management Admin)
# ============================================

class LoanBuyerStatusHistoryInline(admin.TabularInline):
    """نمایش تاریخچه وضعیت خریدار وام"""
    model = LoanBuyerStatusHistory
    extra = 1
    fields = ('status', 'status_date', 'description')
    ordering = ['-status_date']


class LoanBuyerInline(admin.TabularInline):
    """نمایش خریداران وام در Loan"""
    model = LoanBuyer
    extra = 0
    fields = ('first_name', 'last_name', 'national_id', 'current_status')


class LoanCreditorInline(admin.TabularInline):
    """نمایش بستانکاران وام در Loan - فقط خواندنی"""
    model = LoanCreditor
    extra = 0
    fields = ('first_name', 'last_name', 'national_id', 'description', 'total_amount', 'settlement_status')
    readonly_fields = ('first_name', 'last_name', 'national_id', 'description', 'total_amount', 'settlement_status')
    can_delete = False


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    """مدیریت وام‌ها - فقط ادمین"""
    form = LoanForm
    list_display = ('bank_name', 'loan_type', 'get_formatted_amount', 'get_formatted_purchase_rate', 'duration_months', 'status', 'registration_date')
    list_filter = ('loan_type', 'status', 'payment_type', ('registration_date', JDateFieldListFilter), 'branch')
    search_fields = ('bank_name', 'description', 'applicant_first_name', 'applicant_last_name', 'applicant_phone', 'applicant_national_id', 'referrer')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'registration_date'
    inlines = [LoanBuyerInline, LoanCreditorInline]
    
    def has_module_permission(self, request):
        """فقط ادمین می‌تواند این مدل را ببیند"""
        return is_pure_admin(request.user)
    
    def has_view_permission(self, request, obj=None):
        """فقط ادمین می‌تواند وام‌ها را ببیند"""
        return is_pure_admin(request.user)
    
    def has_add_permission(self, request):
        """فقط ادمین می‌تواند وام اضافه کند"""
        return is_pure_admin(request.user)
    
    def has_change_permission(self, request, obj=None):
        """فقط ادمین می‌تواند وام تغییر بدهد"""
        return is_pure_admin(request.user)
    
    def has_delete_permission(self, request, obj=None):
        """فقط ادمین می‌تواند وام حذف کند"""
        return is_pure_admin(request.user)
    
    def get_formatted_amount(self, obj):
        """برای نمایش در list_display"""
        return obj.get_formatted_amount()
    get_formatted_amount.short_description = "مبلغ وام"
    
    def get_formatted_purchase_rate(self, obj):
        """برای نمایش در list_display"""
        return obj.get_formatted_purchase_rate()
    get_formatted_purchase_rate.short_description = "قیمت خرید"
    
    def get_fieldsets(self, request, obj=None):
        """تغییر fieldsets برای ایجاد و تغییر"""
        if obj is None:  # ایجاد جدید
            return self.add_fieldsets
        return self.change_fieldsets
    
    add_fieldsets = (
        ('اطلاعات بانک و وام', {
            'fields': ('bank_name', 'loan_type', 'payment_type')
        }),
        ('جزئیات مالی', {
            'fields': ('amount', 'duration_months', 'purchase_rate')
        }),
        ('اطلاعات صاحب وام', {
            'fields': ('applicant_first_name', 'applicant_last_name', 'applicant_national_id', 'applicant_phone'),
            'description': 'کد ملی صاحب وام برای ایجاد بستانکار استفاده می‌شود'
        }),
        ('وضعیت', {
            'fields': ('status',)
        }),
        ('معرفی‌کننده', {
            'fields': ('referrer',)
        }),
        ('منابع', {
            'fields': ('branch',)
        }),
        ('توضیحات', {
            'fields': ('description',)
        }),
        ('تاریخ‌ها', {
            'fields': ('registration_date',)
        }),
    )
    
    change_fieldsets = (
        ('اطلاعات بانک و وام', {
            'fields': ('bank_name', 'loan_type', 'payment_type')
        }),
        ('جزئیات مالی', {
            'fields': ('amount', 'duration_months', 'purchase_rate'),
            'description': f'💡 نکته: مبالغ با جداکنندگی هزارگان در لیست نمایش داده می‌شوند'
        }),
        ('اطلاعات صاحب وام', {
            'fields': ('applicant_first_name', 'applicant_last_name', 'applicant_national_id', 'applicant_phone'),
            'description': 'کد ملی صاحب وام برای ایجاد بستانکار استفاده می‌شود'
        }),
        ('وضعیت', {
            'fields': ('status',)
        }),
        ('کارمند ثبت‌کننده', {
            'fields': ('recorded_by',),
            'description': 'کارمندی که وام را ثبت کرده است (اتومات پر می‌شود)'
        }),
        ('معرفی‌کننده', {
            'fields': ('referrer',)
        }),
        ('منابع', {
            'fields': ('branch',)
        }),
        ('توضیحات', {
            'fields': ('description',)
        }),
        ('تاریخ‌ها', {
            'fields': ('registration_date', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """اتومات پر کردن کارمند ثبت‌کننده"""
        if not change:  # رکورد جدید
            obj.recorded_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(LoanBuyer)
class LoanBuyerAdmin(admin.ModelAdmin):
    """مدیریت خریداران وام - فقط ادمین"""
    list_display = ('get_full_name', 'national_id', 'loan', 'requested_amount', 'current_status', 'broker')
    list_filter = ('loan__loan_type', 'current_status', ('application_date', JDateFieldListFilter), 
                   'sale_type', 'broker')
    search_fields = ('first_name', 'last_name', 'national_id', 'phone')
    readonly_fields = ('created_at', 'updated_at', 'broker')
    date_hierarchy = 'application_date'
    inlines = [LoanBuyerStatusHistoryInline]
    
    fieldsets = (
        ('اطلاعات شخصی', {
            'fields': ('first_name', 'last_name', 'national_id', 'phone')
        }),
        ('اطلاعات وام و مالی', {
            'fields': ('loan', 'bank', 'requested_amount', 'sale_price', 'sale_type')
        }),
        ('وضعیت و پیگیری', {
            'fields': ('current_status', 'application_date')
        }),
        ('مسئولیت کارگذار', {
            'fields': ('broker',),
            'description': 'کارگذار خودکار از کاربر فعلی تعیین می‌شود'
        }),
        ('اطلاعات اضافی', {
            'fields': ('internal_notes',)
        }),
        ('تاریخ‌ها', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_module_permission(self, request):
        """فقط ادمین می‌تواند این مدل را ببیند"""
        return is_pure_admin(request.user)
    
    def has_view_permission(self, request, obj=None):
        """فقط ادمین می‌تواند ببیند"""
        return is_pure_admin(request.user)
    
    def has_add_permission(self, request):
        """فقط ادمین می‌تواند اضافه کند"""
        return is_pure_admin(request.user)
    
    def has_change_permission(self, request, obj=None):
        """فقط ادمین می‌تواند تغییر بدهد"""
        return is_pure_admin(request.user)
    
    def has_delete_permission(self, request, obj=None):
        """فقط ادمین می‌تواند حذف کند"""
        return is_pure_admin(request.user)
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    get_full_name.short_description = "نام و نام خانوادگی"
    
    def get_queryset(self, request):
        """تصفیه بر اساس نقش کاربر"""
        qs = super().get_queryset(request)
        if is_pure_admin(request.user):
            return qs
        return qs.none()
    
    def save_model(self, request, obj, form, change):
        """تنظیم کارگذار برای رکورد جدید"""
        if not change:  # رکورد جدید
            obj.broker = request.user
        super().save_model(request, obj, form, change)


@admin.register(LoanBuyerStatusHistory)
class LoanBuyerStatusHistoryAdmin(admin.ModelAdmin):
    """مدیریت تاریخچه وضعیت خریدار وام - فقط ادمین"""
    list_display = ('loan_buyer', 'status', 'status_date', 'description_short')
    list_filter = ('status', ('status_date', JDateFieldListFilter), 'loan_buyer__loan__bank_name')
    search_fields = ('loan_buyer__first_name', 'loan_buyer__last_name', 'description')
    readonly_fields = ('created_at', 'status_date')
    date_hierarchy = 'status_date'
    
    def has_module_permission(self, request):
        """فقط ادمین می‌تواند این مدل را ببیند"""
        return is_pure_admin(request.user)
    
    def has_view_permission(self, request, obj=None):
        """فقط ادمین می‌تواند تاریخچه وضعیت را ببیند"""
        return is_pure_admin(request.user)
    
    def has_add_permission(self, request):
        """فقط ادمین می‌تواند اضافه کند"""
        return is_pure_admin(request.user)
    
    def has_change_permission(self, request, obj=None):
        """فقط ادمین می‌تواند تغییر بدهد"""
        return is_pure_admin(request.user)
    
    def has_delete_permission(self, request, obj=None):
        """فقط ادمین می‌تواند حذف کند"""
        return is_pure_admin(request.user)
    
    fieldsets = (
        ('خریدار وام', {
            'fields': ('loan_buyer',)
        }),
        ('وضعیت و توضیح', {
            'fields': ('status', 'description')
        }),
        ('تاریخ‌ها', {
            'fields': ('status_date', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def description_short(self, obj):
        if obj.description:
            return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
        return '-'
    description_short.short_description = "توضیحات"


class LoanCreditorInstallmentInline(admin.TabularInline):
    """نمایش و مدیریت قسط‌های بستانکار - دستی و ساده‌شده (مثل ExpenseInline)"""
    model = LoanCreditorInstallment
    extra = 1  # یک فرم خالی برای اضافه کردن قسط جدید
    fields = ('installment_number', 'paid_amount', 'due_date', 'payment_date', 'status', 'description')
    readonly_fields = ('installment_number', 'paid_amount')  # شماره قسط و مبلغ پرداخت‌شده اتومات پر می‌شوند
    ordering = ['installment_number']


@admin.register(LoanCreditor)
class LoanCreditorAdmin(admin.ModelAdmin):
    """مدیریت بستانکاران وام - فقط ادمین"""
    list_display = ('get_full_name', 'national_id', 'loan', 'total_amount', 'get_paid_percentage', 'settlement_status', 'category')
    list_filter = ('settlement_status', 'payment_type', 'category', ('creation_date', JDateFieldListFilter), 'loan__bank_name', 'broker')
    search_fields = ('first_name', 'last_name', 'national_id', 'phone', 'internal_document_number')
    readonly_fields = ('created_at', 'updated_at', 'paid_percentage', 'remaining_installments', 'creation_date', 'description', 'recorded_by', 'paid_amount')
    date_hierarchy = 'creation_date'
    inlines = [LoanCreditorInstallmentInline]
    
    def get_inlines(self, request, obj):
        """اگر نوع پرداخت نقدی است، inline قسط‌ها را پنهان کنید"""
        if obj and obj.payment_type == 'cash':
            return []
        return self.inlines
    
    fieldsets = (
        ('اطلاعات شخصی', {
            'fields': ('first_name', 'last_name', 'national_id', 'phone')
        }),
        ('اطلاعات وام', {
            'fields': ('loan', 'description', 'branch', 'recorded_by')
        }),
        ('مبالغ و وضعیت تسویه', {
            'fields': ('total_amount', 'paid_amount', 'paid_percentage', 'settlement_status', 'settlement_date')
        }),
        ('نوع پرداخت', {
            'fields': ('payment_type', 'remaining_installments')
        }),
        ('مسئولیت کارگذار', {
            'fields': ('broker',)
        }),
        ('دسته‌بندی و سند', {
            'fields': ('category', 'internal_document_number')
        }),
        ('یادداشت‌ها و پیگیری', {
            'fields': ('internal_notes', 'final_notes', 'next_followup_date')
        }),
        ('تاریخ‌ها', {
            'fields': ('creation_date', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_module_permission(self, request):
        """فقط ادمین می‌تواند این مدل را ببیند"""
        return is_pure_admin(request.user)
    
    def has_view_permission(self, request, obj=None):
        """فقط ادمین می‌تواند ببیند"""
        return is_pure_admin(request.user)
    
    def has_add_permission(self, request):
        """فقط ادمین می‌تواند اضافه کند"""
        return is_pure_admin(request.user)
    
    def has_change_permission(self, request, obj=None):
        """فقط ادمین می‌تواند تغییر بدهد"""
        return is_pure_admin(request.user)
    
    def has_delete_permission(self, request, obj=None):
        """فقط ادمین می‌تواند حذف کند"""
        return is_pure_admin(request.user)
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    get_full_name.short_description = "نام و نام خانوادگی"
    
    def get_paid_percentage(self, obj):
        return f"{obj.paid_percentage:.1f}%"
    get_paid_percentage.short_description = "درصد پرداخت شده"
    
    def get_queryset(self, request):
        """تصفیه بر اساس نقش کاربر"""
        qs = super().get_queryset(request)
        if is_pure_admin(request.user):
            return qs
        return qs.none()
    
    def save_model(self, request, obj, form, change):
        """تنظیم کارگذار برای رکورد جدید"""
        if not change:  # رکورد جدید
            obj.broker = request.user
        super().save_model(request, obj, form, change)


@admin.register(LoanCreditorInstallment)
class LoanCreditorInstallmentAdmin(admin.ModelAdmin):
    """مدیریت قسط‌های بستانکار وام - فقط ادمین"""
    list_display = ('get_creditor_name', 'installment_number', 'paid_amount', 'status', 'payment_date')
    list_filter = ('status', ('payment_date', JDateFieldListFilter), 'creditor__category')
    search_fields = ('creditor__first_name', 'creditor__last_name', 'creditor__national_id', 'description')
    readonly_fields = ('created_at', 'updated_at', 'installment_number')
    date_hierarchy = 'payment_date'
    
    fieldsets = (
        ('بستانکار', {
            'fields': ('creditor',)
        }),
        ('اطلاعات قسط', {
            'fields': ('installment_number', 'paid_amount', 'status')
        }),
        ('تاریخ‌های سررسید و پرداخت', {
            'fields': ('due_date', 'payment_date')
        }),
        ('توضیحات', {
            'fields': ('description',)
        }),
        ('تاریخ‌های سیستمی', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_module_permission(self, request):
        """فقط ادمین می‌تواند این مدل را ببیند"""
        return is_pure_admin(request.user)
    
    def has_view_permission(self, request, obj=None):
        """فقط ادمین می‌تواند قسط‌ها را ببیند"""
        return is_pure_admin(request.user)
    
    def has_add_permission(self, request):
        """فقط ادمین می‌تواند قسط اضافه کند"""
        return is_pure_admin(request.user)
    
    def has_change_permission(self, request, obj=None):
        """فقط ادمین می‌تواند قسط تغییر بدهد"""
        return is_pure_admin(request.user)
    
    def has_delete_permission(self, request, obj=None):
        """فقط ادمین می‌تواند قسط حذف کند"""
        return is_pure_admin(request.user)
    
    def get_creditor_name(self, obj):
        return f"{obj.creditor.first_name} {obj.creditor.last_name}"
    get_creditor_name.short_description = "نام بستانکار"
    
    def get_remaining_amount(self, obj):
        """نمایش باقی‌مانده قسط"""
        return f"{obj.remaining_amount:,.0f} ریال"
    get_remaining_amount.short_description = "باقی‌مانده"


# User Admin customization
class UserProfileInline(admin.StackedInline):
    """نمایش پروفایل در User Admin"""
    model = UserProfile
    can_delete = False

class CustomUserAdmin(BaseUserAdmin):
    """مدیریت کاربران - فقط ادمین"""
    inlines = [UserProfileInline]
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_role')
    
    def has_module_permission(self, request):
        """فقط ادمین می‌تواند این مدل را ببیند"""
        return is_admin(request.user)
    
    def has_view_permission(self, request, obj=None):
        """فقط ادمین می‌تواند ببیند"""
        return is_admin(request.user)
    
    def has_add_permission(self, request):
        """فقط ادمین می‌تواند اضافه کند"""
        return is_admin(request.user)
    
    def has_change_permission(self, request, obj=None):
        """فقط ادمین می‌تواند تغییر بدهد"""
        return is_admin(request.user)
    
    def has_delete_permission(self, request, obj=None):
        """فقط ادمین می‌تواند حذف کند"""
        return is_admin(request.user)
    
    def get_role(self, obj):
        try:
            return obj.profile.get_role_display()
        except:
            return 'نامشخص'
    get_role.short_description = 'نقش'

# اگر User قبلاً ثبت شده باشد، ابتدا unregister کنید
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# ============================================
# لاگ فعالیت (Activity Log) - نمایش و گزارش‌گیری
# ============================================

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    """مدیریت و مشاهده لاگ‌های فعالیت سیستم - فقط ادمین"""
    
    list_display = ('get_timestamp_display', 'get_action_display_colored', 'get_user_display', 'content_type', 'get_description_short', 'ip_address')
    list_filter = ('action', 'content_type')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'object_description', 'ip_address')
    readonly_fields = ('timestamp', 'user', 'action', 'content_type', 'object_id', 'object_description', 'details_formatted', 'ip_address')
    
    fieldsets = (
        ('اطلاعات کاربر', {
            'fields': ('user', 'ip_address')
        }),
        ('نوع عملیات', {
            'fields': ('action', 'content_type')
        }),
        ('اطلاعات رکورد', {
            'fields': ('object_id', 'object_description')
        }),
        ('جزئیات تغییرات', {
            'fields': ('details_formatted',),
            'classes': ('collapse',)
        }),
        ('زمان', {
            'fields': ('timestamp',),
            'classes': ('collapse',)
        }),
    )
    
    def has_module_permission(self, request):
        """فقط ادمین می‌تواند این مدل را ببیند"""
        return is_admin(request.user)
    
    def has_view_permission(self, request, obj=None):
        """فقط ادمین می‌تواند ببیند"""
        return is_admin(request.user)
    
    def has_add_permission(self, request):
        """جلوگیری از افزودن دستی"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """فقط ادمین می‌تواند تغییر بدهد"""
        return is_admin(request.user)
    
    def has_delete_permission(self, request, obj=None):
        """فقط ادمین می‌تواند حذف کند"""
        return is_admin(request.user)
    
    def get_timestamp_display(self, obj):
        """نمایش تاریخ و ساعت به صورت خواندنی"""
        if obj.timestamp:
            return f"{obj.timestamp.strftime('%Y/%m/%d %H:%M:%S')}"
        return "-"
    get_timestamp_display.short_description = "تاریخ و ساعت"
    
    def get_action_display_colored(self, obj):
        """نمایش رنگی نوع عملیات"""
        colors = {
            'create': '#27ae60',      # سبز
            'update': '#3498db',      # آبی
            'delete': '#e74c3c',      # قرمز
            'login': '#2ecc71',       # سبز روشن
            'logout': '#95a5a6',      # خاکستری
            'download': '#f39c12',    # نارنجی
            'export': '#9b59b6',      # بنفش
            'import': '#1abc9c',      # فیروزه‌ای
        }
        
        color = colors.get(obj.action, '#34495e')
        action_text = obj.get_action_display()
        
        return f'<span style="background-color: {color}; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold;">{action_text}</span>'
    get_action_display_colored.short_description = "نوع عملیات"
    get_action_display_colored.allow_tags = True
    
    def get_user_display(self, obj):
        """نمایش نام کاربر"""
        if obj.user:
            full_name = obj.user.get_full_name()
            username = obj.user.username
            if full_name:
                return f"{full_name} ({username})"
            return username
        return "سیستم خودکار"
    get_user_display.short_description = "کاربر"
    
    def get_description_short(self, obj):
        """نمایش خلاصه توضیح"""
        if obj.object_description:
            desc = obj.object_description
            if len(desc) > 60:
                return f"{desc[:57]}..."
            return desc
        return "-"
    get_description_short.short_description = "توضیح"
    
    def details_formatted(self, obj):
        """نمایش تنسیق‌شده جزئیات JSON"""
        if obj.details:
            import json
            try:
                data = json.loads(obj.details)
                html = '<pre style="direction: rtl; text-align: right; background-color: #f5f5f5; padding: 10px; border-radius: 5px;">'
                html += json.dumps(data, ensure_ascii=False, indent=2)
                html += '</pre>'
                return html
            except:
                return f'<pre>{obj.details}</pre>'
        return "بدون جزئیات"
    details_formatted.short_description = "جزئیات تغییرات"
    details_formatted.allow_tags = True
    
    def get_queryset(self, request):
        """تصفیه برای نمایش آخرین لاگ‌ها ابتدا"""
        qs = super().get_queryset(request)
        return qs.select_related('user').order_by('-timestamp')


# سفارشی‌سازی Admin Site
admin.site.site_header = "⚖️ مدیریت Phonix"
admin.site.site_title = "Phonix Admin"
admin.site.index_title = "خوش‌آمدید به پنل مدیریت Phonix"


# ============================================
# داشبورد اختصاصی کارمندان (Employee Admin)
# ============================================

class EmployeeAdminSite(admin.AdminSite):
    """داشبورد اختصاصی برای کارمندان - فقط مدل‌های مجاز"""
    site_header = "⚖️ پنل کارمندان - Phonix"
    site_title = "پنل کارمندان"
    index_title = "خوش‌آمدید به پنل کارمندی"
    
    def has_permission(self, request):
        """فقط کارمندان می‌توانند وارد شوند"""
        if not request.user.is_authenticated:
            return False
        return is_employee(request.user) or is_admin(request.user)
    
    def has_module_permission(self, request):
        """مدل‌ها برای کارمندان نمایش یابند"""
        if not request.user.is_authenticated:
            return False
        return is_employee(request.user) or is_admin(request.user)
    
    def index(self, request, extra_context=None):
        """داشبورد اصلی"""
        if not (is_employee(request.user) or is_admin(request.user)):
            raise PermissionDenied
        return super().index(request, extra_context)


# ایجاد instance از EmployeeAdminSite
employee_admin_site = EmployeeAdminSite(name='employee_admin')


# ============================================
# سیستم وکالت - داشبورد اختصاصی برای وکلا
# ============================================

class LawyerAdminSite(admin.AdminSite):
    """داشبورد اختصاصی برای وکلا - سیستم وکالت"""
    site_header = "👨‍⚖️ سیستم وکالت - Phonix"
    site_title = "سیستم وکالت"
    index_title = "خوش‌آمدید به سیستم وکالت"
    
    def has_permission(self, request):
        """فقط وکلا می‌توانند وارد شوند"""
        if not request.user.is_authenticated:
            return False
        return is_lawyer(request.user) or is_pure_admin(request.user)
    
    def has_module_permission(self, request):
        """مدل‌ها برای وکلا نمایش یابند"""
        if not request.user.is_authenticated:
            return False
        return is_lawyer(request.user) or is_pure_admin(request.user)
    
    def index(self, request, extra_context=None):
        """داشبورد اصلی"""
        if not (is_lawyer(request.user) or is_pure_admin(request.user)):
            raise PermissionDenied
        return super().index(request, extra_context)


# ایجاد instance از LawyerAdminSite
lawyer_admin_site = LawyerAdminSite(name='lawyer_admin')


# ============================================
# ثبت مدل‌های مجاز برای کارمندان
# ============================================

# اینلاین‌ها برای وام‌های کارمندان
class EmployeeLoanBuyerInline(admin.TabularInline):
    model = LoanBuyer
    extra = 0
    readonly_fields = ('created_at',)
    can_delete = False


class EmployeeLoanCreditorInline(admin.TabularInline):
    model = LoanCreditorInstallment
    extra = 0
    readonly_fields = ('created_at', 'paid_at')
    can_delete = False



# Loan برای کارمندان
class EmployeeLoanAdmin(admin.ModelAdmin):
    """مدیریت وام‌ها برای کارمندان - فقط وام‌های شخصی"""
    list_display = ('applicant_first_name', 'applicant_last_name', 'loan_type', 'amount', 'status', 'created_at')
    list_filter = ('loan_type', 'status', 'created_at')
    search_fields = ('applicant_first_name', 'applicant_last_name', 'applicant_national_id')
    readonly_fields = ('created_at', 'updated_at', 'recorded_by')
    
    fieldsets = (
        ('درخواست‌کننده', {
            'fields': ('applicant_first_name', 'applicant_last_name', 'applicant_national_id')
        }),
        ('جزئیات وام', {
            'fields': ('loan_type', 'description', 'amount', 'purchase_rate', 'status')
        }),
        ('تاریخ‌ها', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """فقط وام‌های ثبت‌شده توسط کاربر فعلی"""
        qs = super().get_queryset(request)
        if is_pure_admin(request.user):
            return qs
        # کارمندان فقط وام‌های خود را می‌توانند ببینند
        return qs.filter(recorded_by=request.user)
    
    def has_module_permission(self, request):
        """کارمندان می‌توانند این مدل را ببینند"""
        return is_employee(request.user) or is_pure_admin(request.user)
    
    def has_view_permission(self, request, obj=None):
        return is_employee(request.user) or is_pure_admin(request.user)
    
    def has_add_permission(self, request):
        return is_employee(request.user) or is_pure_admin(request.user)
    
    def has_change_permission(self, request, obj=None):
        """کارمند فقط وام‌های خود را می‌تواند تغییر دهد"""
        if is_pure_admin(request.user):
            return True
        if is_employee(request.user) and obj:
            return obj.recorded_by == request.user
        return False
    
    def has_delete_permission(self, request, obj=None):
        """عدم اجازه حذف"""
        return False
    
    def save_model(self, request, obj, form, change):
        """تنظیم ثبت‌کننده برای وام‌های جدید - فقط برای کارمندان"""
        if not change and is_employee(request.user):
            # اگر کارمند است، recorded_by = خودش
            obj.recorded_by = request.user
        # اگر ادمین است، recorded_by را هر چه که ادمین تنظیم کرد نگه دار
        super().save_model(request, obj, form, change)


# LoanBuyer برای کارمندان
class EmployeeLoanBuyerAdmin(admin.ModelAdmin):
    """مدیریت خریداران وام برای کارمندان - فقط خریداران وام‌های شخصی"""
    list_display = ('get_full_name', 'national_id', 'phone', 'current_status', 'loan', 'created_at')
    list_filter = ('current_status', 'application_date', 'created_at')
    search_fields = ('first_name', 'last_name', 'national_id', 'phone')
    readonly_fields = ('created_at', 'updated_at', 'created_by')
    
    fieldsets = (
        ('اطلاعات شخصی', {
            'fields': ('first_name', 'last_name', 'national_id', 'phone')
        }),
        ('وام و مالی', {
            'fields': ('loan', 'requested_amount', 'bank', 'sale_price', 'sale_type')
        }),
        ('وضعیت', {
            'fields': ('current_status', 'application_date')
        }),
        ('توضیحات', {
            'fields': ('internal_notes',)
        }),
        ('متاداده', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """فقط خریداران ثبت‌شده توسط کاربر فعلی"""
        qs = super().get_queryset(request)
        if is_pure_admin(request.user):
            return qs
        # کارمندان فقط خریداران خود را می‌توانند ببینند
        return qs.filter(created_by=request.user)
    
    def has_module_permission(self, request):
        """کارمندان می‌توانند این مدل را ببینند"""
        return is_employee(request.user) or is_pure_admin(request.user)
    
    def has_view_permission(self, request, obj=None):
        return is_employee(request.user) or is_pure_admin(request.user)
    
    def has_add_permission(self, request):
        """کارمندان می‌توانند خریدار اضافه کنند"""
        return is_employee(request.user) or is_pure_admin(request.user)
    
    def has_change_permission(self, request, obj=None):
        """کارمند فقط خریداران خود را می‌تواند تغییر دهد"""
        if is_pure_admin(request.user):
            return True
        if is_employee(request.user) and obj:
            return obj.created_by == request.user
        return False
    
    def has_delete_permission(self, request, obj=None):
        """کارمند فقط خریداران خود را می‌تواند حذف کند"""
        if is_pure_admin(request.user):
            return True
        if is_employee(request.user) and obj:
            return obj.created_by == request.user
        return False
    
    def save_model(self, request, obj, form, change):
        """تنظیم ایجادکننده برای خریداران جدید - فقط برای کارمندان"""
        if not change and is_employee(request.user):
            # اگر کارمند است، created_by = خودش
            obj.created_by = request.user
        # اگر ادمین است، created_by را هر چه که ادمین تنظیم کرد نگه دار
        super().save_model(request, obj, form, change)
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    get_full_name.short_description = "نام کامل"





# مدل‌های تکمیلی برای کارمندان
class EmployeeLoanBuyerStatusHistoryAdmin(admin.ModelAdmin):
    """تاریخچه وضعیت خریداران وام - فقط تاریخچه وام‌های شخصی"""
    list_display = ('loan_buyer', 'status', 'status_date', 'created_at')
    list_filter = ('status', 'status_date')
    search_fields = ('loan_buyer__first_name', 'loan_buyer__last_name')
    readonly_fields = ('created_at',)
    
    def get_queryset(self, request):
        """فقط تاریخچه وام‌های ثبت‌شده توسط کاربر فعلی"""
        qs = super().get_queryset(request)
        if is_pure_admin(request.user):
            return qs
        # کارمندان فقط تاریخچه وام‌های خود را می‌توانند ببینند
        return qs.filter(loan_buyer__loan__recorded_by=request.user)
    
    def has_module_permission(self, request):
        return is_employee(request.user) or is_pure_admin(request.user)
    
    def has_view_permission(self, request, obj=None):
        return is_employee(request.user) or is_pure_admin(request.user)
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


# ثبت مدل‌های وام برای کارمندان
employee_admin_site.register(Loan, EmployeeLoanAdmin)
employee_admin_site.register(LoanBuyer, EmployeeLoanBuyerAdmin)
employee_admin_site.register(LoanBuyerStatusHistory, EmployeeLoanBuyerStatusHistoryAdmin)


# ============================================
# ثبتی - خدمات (Registry Services)
# ============================================

# Import Registry Models
from registry.models import (
    License,
    TradeAcquisition,
    TradePartnership,
)

# مجوزها برای کارمندان
class EmployeeLicenseAdmin(admin.ModelAdmin):
    """مدیریت مجوزها برای کارمندان - فقط مجوزهای شخصی"""
    list_display = ('service_title', 'get_subcategory_colored', 'get_identity_info', 'get_amount_formatted', 'created_at')
    list_filter = ('subcategory', 'created_at')
    search_fields = ('service_title', 'description', 'identity_documents__first_name', 'identity_documents__last_name')
    readonly_fields = ('created_at', 'updated_at', 'created_by')
    
    fieldsets = (
        ('دسته‌بندی', {
            'fields': ('subcategory',)
        }),
        ('اطلاعات خدمت', {
            'fields': ('service_title',)
        }),
        ('مدارک و اطلاعات', {
            'fields': ('identity_documents', 'contact_info')
        }),
        ('مالی', {
            'fields': ('amount_received',)
        }),
        ('توضیحات', {
            'fields': ('description',)
        }),
        ('متاداده', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """فقط مجوزهای ثبت‌شده توسط کاربر فعلی"""
        qs = super().get_queryset(request)
        if is_admin(request.user):
            return qs
        # کارمندان فقط مجوزهای خود را می‌توانند ببینند
        return qs.filter(created_by=request.user)
    
    def has_module_permission(self, request):
        return is_employee(request.user) or is_admin(request.user)
    
    def has_view_permission(self, request, obj=None):
        return is_employee(request.user) or is_admin(request.user)
    
    def has_add_permission(self, request):
        return is_employee(request.user) or is_admin(request.user)
    
    def has_change_permission(self, request, obj=None):
        """کارمند فقط مجوزهای خود را می‌تواند تغییر دهد"""
        if is_admin(request.user):
            return True
        if is_employee(request.user) and obj:
            return obj.created_by == request.user
        return False
    
    def has_delete_permission(self, request, obj=None):
        """کارمند فقط مجوزهای خود را می‌تواند حذف کند"""
        if is_admin(request.user):
            return True
        if is_employee(request.user) and obj:
            return obj.created_by == request.user
        return False
    
    def save_model(self, request, obj, form, change):
        """تنظیم کاربر فعلی برای مجوزهای جدید - فقط برای کارمندان"""
        if not change and is_employee(request.user):
            # اگر کارمند است، created_by = خودش
            obj.created_by = request.user
        # اگر ادمین است یا در حال ویرایش است، created_by را نگه دار
        super().save_model(request, obj, form, change)
    
    def get_subcategory_colored(self, obj):
        """نمایش رنگی دسته‌بندی"""
        colors = {'household': '#3498db', 'professional': '#27ae60', 'other': '#95a5a6'}
        color = colors.get(obj.subcategory, '#34495e')
        text = obj.get_subcategory_display()
        return f'<span style="background-color: {color}; color: white; padding: 5px 10px; border-radius: 3px;">{text}</span>'
    get_subcategory_colored.short_description = "دسته‌بندی"
    get_subcategory_colored.allow_tags = True
    
    def get_identity_info(self, obj):
        """نمایش اطلاعات شخص"""
        doc = obj.identity_documents
        return f"{doc.first_name} {doc.last_name}"
    get_identity_info.short_description = "نام شخص"
    
    def get_amount_formatted(self, obj):
        """نمایش مبلغ با جدا‌کننده هزارگان"""
        return f"{obj.amount_received:,.2f} تومان"
    get_amount_formatted.short_description = "مبلغ دریافتی"


# دریافت بازرگانی برای کارمندان
class EmployeeTradeAcquisitionAdmin(admin.ModelAdmin):
    """مدیریت دریافت بازرگانی برای کارمندان - فقط دریافت‌های شخصی"""
    list_display = ('get_entity_type_colored', 'acquisition_type', 'check_category', 'get_amount_formatted', 'get_identity_info', 'created_at')
    list_filter = ('entity_type', 'check_category', 'created_at')
    search_fields = ('acquisition_type', 'description', 'identity_documents__national_id')
    readonly_fields = ('created_at', 'updated_at', 'created_by')
    
    fieldsets = (
        ('دسته‌بندی', {
            'fields': ('entity_type',)
        }),
        ('اطلاعات دریافت', {
            'fields': ('acquisition_type',)
        }),
        ('مدارک و اطلاعات', {
            'fields': ('identity_documents', 'contact_info')
        }),
        ('چک', {
            'fields': ('check_category',)
        }),
        ('مالی', {
            'fields': ('amount_received',)
        }),
        ('توضیحات', {
            'fields': ('description',)
        }),
        ('متاداده', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """فقط دریافت‌های ثبت‌شده توسط کاربر فعلی"""
        qs = super().get_queryset(request)
        if is_admin(request.user):
            return qs
        # کارمندان فقط دریافت‌های خود را می‌توانند ببینند
        return qs.filter(created_by=request.user)
    
    def has_module_permission(self, request):
        return is_employee(request.user) or is_admin(request.user)
    
    def has_view_permission(self, request, obj=None):
        return is_employee(request.user) or is_admin(request.user)
    
    def has_add_permission(self, request):
        return is_employee(request.user) or is_admin(request.user)
    
    def has_change_permission(self, request, obj=None):
        """کارمند فقط دریافت‌های خود را می‌تواند تغییر دهد"""
        if is_admin(request.user):
            return True
        if is_employee(request.user) and obj:
            return obj.created_by == request.user
        return False
    
    def has_delete_permission(self, request, obj=None):
        """کارمند فقط دریافت‌های خود را می‌تواند حذف کند"""
        if is_admin(request.user):
            return True
        if is_employee(request.user) and obj:
            return obj.created_by == request.user
        return False
    
    def save_model(self, request, obj, form, change):
        """تنظیم کاربر فعلی برای دریافت‌های جدید - فقط برای کارمندان"""
        if not change and is_employee(request.user):
            # اگر کارمند است، created_by = خودش
            obj.created_by = request.user
        # اگر ادمین است یا در حال ویرایش است، created_by را نگه دار
        super().save_model(request, obj, form, change)
    
    def get_entity_type_colored(self, obj):
        """نمایش رنگی نوع"""
        colors = {'legal': '#e74c3c', 'natural': '#3498db'}
        color = colors.get(obj.entity_type, '#95a5a6')
        text = obj.get_entity_type_display()
        return f'<span style="background-color: {color}; color: white; padding: 5px 10px; border-radius: 3px;">{text}</span>'
    get_entity_type_colored.short_description = "نوع"
    get_entity_type_colored.allow_tags = True
    
    def get_identity_info(self, obj):
        """نمایش اطلاعات شخص"""
        doc = obj.identity_documents
        return f"{doc.first_name} {doc.last_name}"
    get_identity_info.short_description = "نام شخص"
    
    def get_amount_formatted(self, obj):
        """نمایش مبلغ با جدا‌کننده هزارگان"""
        return f"{obj.amount_received:,.2f} تومان"
    get_amount_formatted.short_description = "مبلغ دریافتی"


# مشارکت بازرگانی برای کارمندان
class EmployeeTradePartnershipAdmin(admin.ModelAdmin):
    """مدیریت مشارکت بازرگانی برای کارمندان - فقط مشارکت‌های شخصی"""
    list_display = ('get_entity_type_colored', 'card_year', 'get_amount_formatted', 'get_identity_info', 'created_at')
    list_filter = ('entity_type', 'card_year', 'created_at')
    search_fields = ('description', 'identity_documents__national_id')
    readonly_fields = ('created_at', 'updated_at', 'created_by')
    
    fieldsets = (
        ('دسته‌بندی', {
            'fields': ('entity_type',)
        }),
        ('کارت بازرگانی', {
            'fields': ('card_year',)
        }),
        ('مدارک و اطلاعات', {
            'fields': ('identity_documents', 'contact_info')
        }),
        ('حدود و مبالغ', {
            'fields': ('import_ceiling', 'export_ceiling', 'import_amount', 'export_amount')
        }),
        ('مالی', {
            'fields': ('amount_received',)
        }),
        ('توضیحات', {
            'fields': ('description',)
        }),
        ('متاداده', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """فقط مشارکت‌های ثبت‌شده توسط کاربر فعلی"""
        qs = super().get_queryset(request)
        if is_admin(request.user):
            return qs
        # کارمندان فقط مشارکت‌های خود را می‌توانند ببینند
        return qs.filter(created_by=request.user)
    
    def has_module_permission(self, request):
        return is_employee(request.user) or is_admin(request.user)
    
    def has_view_permission(self, request, obj=None):
        return is_employee(request.user) or is_admin(request.user)
    
    def has_add_permission(self, request):
        return is_employee(request.user) or is_admin(request.user)
    
    def has_change_permission(self, request, obj=None):
        """کارمند فقط مشارکت‌های خود را می‌تواند تغییر دهد"""
        if is_admin(request.user):
            return True
        if is_employee(request.user) and obj:
            return obj.created_by == request.user
        return False
    
    def has_delete_permission(self, request, obj=None):
        """کارمند فقط مشارکت‌های خود را می‌تواند حذف کند"""
        if is_admin(request.user):
            return True
        if is_employee(request.user) and obj:
            return obj.created_by == request.user
        return False
    
    def save_model(self, request, obj, form, change):
        """تنظیم کاربر فعلی برای مشارکت‌های جدید - فقط برای کارمندان"""
        if not change and is_employee(request.user):
            # اگر کارمند است، created_by = خودش
            obj.created_by = request.user
        # اگر ادمین است یا در حال ویرایش است، created_by را نگه دار
        super().save_model(request, obj, form, change)
    
    def get_entity_type_colored(self, obj):
        """نمایش رنگی نوع"""
        colors = {'natural': '#3498db', 'legal': '#e74c3c', 'productive': '#27ae60'}
        color = colors.get(obj.entity_type, '#95a5a6')
        text = obj.get_entity_type_display()
        return f'<span style="background-color: {color}; color: white; padding: 5px 10px; border-radius: 3px;">{text}</span>'
    get_entity_type_colored.short_description = "نوع"
    get_entity_type_colored.allow_tags = True
    
    def get_identity_info(self, obj):
        """نمایش اطلاعات شخص"""
        doc = obj.identity_documents
        return f"{doc.first_name} {doc.last_name}"
    get_identity_info.short_description = "نام شخص"
    
    def get_amount_formatted(self, obj):
        """نمایش مبلغ با جدا‌کننده هزارگان"""
        return f"{obj.amount_received:,.2f} تومان"
    get_amount_formatted.short_description = "مبلغ دریافتی"


# ============================================
# کمپانی برای کارمندان
# ============================================

class EmployeeCompanyAdmin(admin.ModelAdmin):
    """مدیریت شرکت‌ها برای کارمندان - فقط شرکت‌های شخصی"""
    list_display = ('company_name', 'company_type', 'get_amount_formatted', 'get_identity_info', 'created_at')
    list_filter = ('company_type', 'created_at')
    search_fields = ('company_name', 'description', 'identity_documents__national_id')
    readonly_fields = ('created_at', 'updated_at', 'created_by')
    
    fieldsets = (
        ('اطلاعات شرکت', {
            'fields': ('company_name', 'company_type')
        }),
        ('مدارک و اطلاعات', {
            'fields': ('identity_documents', 'contact_info')
        }),
        ('مجوز', {
            'fields': ('has_license', 'license_file')
        }),
        ('مالی', {
            'fields': ('amount_received',)
        }),
        ('توضیحات', {
            'fields': ('description',)
        }),
        ('متاداده', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """فقط شرکت‌های ثبت‌شده توسط کاربر فعلی"""
        qs = super().get_queryset(request)
        if is_admin(request.user):
            return qs
        # کارمندان فقط شرکت‌های خود را می‌توانند ببینند
        return qs.filter(created_by=request.user)
    
    def has_module_permission(self, request):
        return is_employee(request.user) or is_admin(request.user)
    
    def has_view_permission(self, request, obj=None):
        return is_employee(request.user) or is_admin(request.user)
    
    def has_add_permission(self, request):
        return is_employee(request.user) or is_admin(request.user)
    
    def has_change_permission(self, request, obj=None):
        """کارمند فقط شرکت‌های خود را می‌تواند تغییر دهد"""
        if is_admin(request.user):
            return True
        if is_employee(request.user) and obj:
            return obj.created_by == request.user
        return False
    
    def has_delete_permission(self, request, obj=None):
        """کارمند فقط شرکت‌های خود را می‌تواند حذف کند"""
        if is_admin(request.user):
            return True
        if is_employee(request.user) and obj:
            return obj.created_by == request.user
        return False
    
    def save_model(self, request, obj, form, change):
        """تنظیم کاربر فعلی برای شرکت‌های جدید - فقط برای کارمندان"""
        if not change and is_employee(request.user):
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def get_identity_info(self, obj):
        """نمایش اطلاعات شخص"""
        doc = obj.identity_documents
        return f"{doc.first_name} {doc.last_name}"
    get_identity_info.short_description = "نام شخص"
    
    def get_amount_formatted(self, obj):
        """نمایش مبلغ با جدا‌کننده هزارگان"""
        return f"{obj.amount_received:,.2f} تومان"
    get_amount_formatted.short_description = "مبلغ دریافتی"


# ============================================
# مدارک هویتی و اطلاعات تماس برای کارمندان
# ============================================

class EmployeeIdentityDocumentsAdmin(admin.ModelAdmin):
    """مدیریت مدارک هویتی برای کارمندان - فقط مدارک شخصی"""
    list_display = (
        'get_full_name',
        'national_id',
        'birth_date',
        'created_at'
    )
    list_filter = (
        ('birth_date', JDateFieldListFilter),
        ('created_at', JDateFieldListFilter),
    )
    search_fields = (
        'first_name',
        'last_name',
        'national_id',
        'certificate_number'
    )
    readonly_fields = ('created_at', 'updated_at', 'created_by')
    
    fieldsets = (
        ('اطلاعات شخصی', {
            'fields': ('first_name', 'last_name')
        }),
        ('اطلاعات هویتی', {
            'fields': (
                'national_id',
                'certificate_number',
                'birth_date',
                'birth_place'
            )
        }),
        ('مدارک', {
            'fields': (
                'national_id_image',
                'additional_documents'
            )
        }),
        ('متاداده', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """فقط مدارک ثبت‌شده توسط کاربر فعلی"""
        qs = super().get_queryset(request)
        if is_admin(request.user):
            return qs
        # کارمندان فقط مدارک خود را می‌توانند ببینند
        return qs.filter(created_by=request.user)
    
    def has_module_permission(self, request):
        """کارمندان می‌توانند این مدل را ببینند"""
        return is_employee(request.user) or is_admin(request.user)
    
    def has_view_permission(self, request, obj=None):
        """کارمندان می‌توانند ببینند"""
        return is_employee(request.user) or is_admin(request.user)
    
    def has_add_permission(self, request):
        """کارمندان می‌توانند اضافه کنند"""
        return is_employee(request.user) or is_admin(request.user)
    
    def has_change_permission(self, request, obj=None):
        """کارمند فقط مدارک خود را می‌تواند تغییر دهد"""
        if is_admin(request.user):
            return True
        if is_employee(request.user) and obj:
            return obj.created_by == request.user
        return False
    
    def has_delete_permission(self, request, obj=None):
        """کارمند فقط مدارک خود را می‌تواند حذف کند"""
        if is_admin(request.user):
            return True
        if is_employee(request.user) and obj:
            return obj.created_by == request.user
        return False
    
    def save_model(self, request, obj, form, change):
        """تنظیم کاربر فعلی برای مدارک جدید - فقط برای کارمندان"""
        if not change and is_employee(request.user):
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def get_full_name(self, obj):
        """نمایش نام کامل"""
        return f"{obj.first_name} {obj.last_name}"
    get_full_name.short_description = "نام و نام خانوادگی"


class EmployeeContactInfoAdmin(admin.ModelAdmin):
    """مدیریت اطلاعات تماس برای کارمندان - فقط اطلاعات شخصی"""
    list_display = (
        'get_full_name',
        'national_id',
        'mobile_number',
        'phone_number'
    )
    list_filter = (
        ('created_at', JDateFieldListFilter),
    )
    search_fields = (
        'first_name',
        'last_name',
        'national_id',
        'mobile_number',
        'phone_number',
        'email'
    )
    readonly_fields = ('created_at', 'updated_at', 'created_by')
    
    fieldsets = (
        ('اطلاعات شناخت‌شخص', {
            'fields': (
                'first_name',
                'last_name',
                'national_id'
            )
        }),
        ('اطلاعات تماس', {
            'fields': (
                'phone_number',
                'mobile_number',
                'email'
            )
        }),
        ('آدرس', {
            'fields': (
                'address',
                'postal_code'
            )
        }),
        ('متاداده', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """فقط اطلاعات ثبت‌شده توسط کاربر فعلی"""
        qs = super().get_queryset(request)
        if is_admin(request.user):
            return qs
        # کارمندان فقط اطلاعات خود را می‌توانند ببینند
        return qs.filter(created_by=request.user)
    
    def has_module_permission(self, request):
        """کارمندان می‌توانند این مدل را ببینند"""
        return is_employee(request.user) or is_admin(request.user)
    
    def has_view_permission(self, request, obj=None):
        """کارمندان می‌توانند ببینند"""
        return is_employee(request.user) or is_admin(request.user)
    
    def has_add_permission(self, request):
        """کارمندان می‌توانند اضافه کنند"""
        return is_employee(request.user) or is_admin(request.user)
    
    def has_change_permission(self, request, obj=None):
        """کارمند فقط اطلاعات خود را می‌تواند تغییر دهد"""
        if is_admin(request.user):
            return True
        if is_employee(request.user) and obj:
            return obj.created_by == request.user
        return False
    
    def has_delete_permission(self, request, obj=None):
        """کارمند فقط اطلاعات خود را می‌تواند حذف کند"""
        if is_admin(request.user):
            return True
        if is_employee(request.user) and obj:
            return obj.created_by == request.user
        return False
    
    def save_model(self, request, obj, form, change):
        """تنظیم کاربر فعلی برای اطلاعات جدید - فقط برای کارمندان"""
        if not change and is_employee(request.user):
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def get_full_name(self, obj):
        """نمایش نام کامل"""
        return f"{obj.first_name} {obj.last_name}"
    get_full_name.short_description = "نام و نام خانوادگی"


# ============================================
# ثبت مدل‌های ثبتی برای کارمندان
# ============================================

employee_admin_site.register(License, EmployeeLicenseAdmin)
employee_admin_site.register(TradeAcquisition, EmployeeTradeAcquisitionAdmin)
employee_admin_site.register(TradePartnership, EmployeeTradePartnershipAdmin)
employee_admin_site.register(Company, EmployeeCompanyAdmin)
employee_admin_site.register(IdentityDocuments, EmployeeIdentityDocumentsAdmin)
employee_admin_site.register(ContactInfo, EmployeeContactInfoAdmin)