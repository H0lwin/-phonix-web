"""
Admin Interface برای سیستم ثبتی خدمات
"""
from django.contrib import admin
from django_jalali.admin.filters import JDateFieldListFilter
from django.utils.html import format_html
from .models import (
    IdentityDocuments,
    ContactInfo,
    RegistryServiceCategory,
    License,
    TradeAcquisition,
    TradePartnership,
    Company,
)


# ============================================
# توابع کمکی برای کنترل دسترسی (Permission Helpers)
# ============================================

def is_admin(user):
    """بررسی کاربر ادمین است"""
    return user.is_superuser or user.is_staff


def is_pure_admin(user):
    """بررسی کاربر admin واقعی است (superuser یا role='admin')"""
    if user.is_superuser:
        return True
    if hasattr(user, 'profile') and user.profile.role == 'admin':
        return True
    return False


def is_employee(user):
    """بررسی کاربر کارمند است"""
    if hasattr(user, 'profile'):
        return user.profile.role == 'employee'
    return False


# ============================================
# کمک‌کننده‌های قالب‌بندی
# ============================================

def format_currency(amount):
    """قالب‌بندی مبلغ با جدا‌کننده هزارگان"""
    if amount is None:
        return '-'
    return f"{amount:,.2f} تومان"


def format_amount_html(amount):
    """قالب‌بندی مبلغ با HTML رنگی"""
    if amount is None:
        return '-'
    formatted = f"{amount:,.2f}"
    return format_html(
        '<span style="color: #27ae60; font-weight: bold;">{}</span>',
        formatted
    )


# ============================================
# مدارک هویتی و اطلاعات تماس
# ============================================

@admin.register(IdentityDocuments)
class IdentityDocumentsAdmin(admin.ModelAdmin):
    """مدیریت مدارک هویتی - ادمین و کارمندان (خواندن)"""
    list_display = (
        'get_full_name',
        'national_id',
        'birth_date',
        'birth_place',
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
    readonly_fields = ('created_at', 'updated_at')
    
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
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_module_permission(self, request):
        """ادمین و کارمندان می‌توانند این مدل را ببینند"""
        return is_pure_admin(request.user) or is_employee(request.user)
    
    def has_view_permission(self, request, obj=None):
        """ادمین و کارمندان می‌توانند ببینند"""
        return is_pure_admin(request.user) or is_employee(request.user)
    
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
        """نمایش نام کامل"""
        return f"{obj.first_name} {obj.last_name}"
    get_full_name.short_description = "نام و نام خانوادگی"


@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    """مدیریت اطلاعات تماس - ادمین و کارمندان (خواندن)"""
    list_display = (
        'get_full_name',
        'national_id',
        'mobile_number',
        'phone_number',
        'get_address_short'
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
        'email',
        'address',
        'postal_code'
    )
    readonly_fields = ('created_at', 'updated_at')
    
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
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_module_permission(self, request):
        """ادمین و کارمندان می‌توانند این مدل را ببینند"""
        return is_pure_admin(request.user) or is_employee(request.user)
    
    def has_view_permission(self, request, obj=None):
        """ادمین و کارمندان می‌توانند ببینند"""
        return is_pure_admin(request.user) or is_employee(request.user)
    
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
        """نمایش نام کامل"""
        return f"{obj.first_name} {obj.last_name}"
    get_full_name.short_description = "نام و نام خانوادگی"
    
    def get_address_short(self, obj):
        """نمایش خلاصه آدرس"""
        if len(obj.address) > 50:
            return f"{obj.address[:47]}..."
        return obj.address
    get_address_short.short_description = "آدرس"


# ============================================
# 1. مجوزها (Licenses)
# ============================================

@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):
    """مدیریت مجوزها - ادمین و کارمندان"""
    list_display = (
        'service_title',
        'get_subcategory_colored',
        'get_identity_info',
        'get_amount_formatted',
        'get_created_by',
        'created_at'
    )
    list_filter = (
        'subcategory',
        ('created_at', JDateFieldListFilter),
        'created_by'
    )
    search_fields = (
        'service_title',
        'description',
        'identity_documents__first_name',
        'identity_documents__last_name',
        'identity_documents__national_id'
    )
    readonly_fields = (
        'created_at',
        'updated_at',
        'created_by'
    )
    
    fieldsets = (
        ('دسته‌بندی', {
            'fields': ('subcategory',)
        }),
        ('اطلاعات خدمت', {
            'fields': ('service_title',)
        }),
        ('مدارک و اطلاعات', {
            'fields': (
                'identity_documents',
                'contact_info'
            )
        }),
        ('مالی', {
            'fields': ('amount_received',)
        }),
        ('توضیحات', {
            'fields': ('description',)
        }),
        ('متاداده', {
            'fields': (
                'created_by',
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def has_module_permission(self, request):
        """ادمین و کارمندان می‌توانند این مدل را ببینند"""
        return is_pure_admin(request.user) or is_employee(request.user)
    
    def has_view_permission(self, request, obj=None):
        """ادمین می‌تواند همه را ببیند، کارمندان فقط خود را"""
        if is_pure_admin(request.user):
            return True
        if is_employee(request.user) and obj:
            return obj.created_by == request.user
        return False
    
    def has_add_permission(self, request):
        """ادمین و کارمندان می‌توانند اضافه کنند"""
        return is_pure_admin(request.user) or is_employee(request.user)
    
    def has_change_permission(self, request, obj=None):
        """ادمین می‌تواند همه را تغییر بدهد، کارمندان فقط خود را"""
        if is_pure_admin(request.user):
            return True
        if is_employee(request.user) and obj:
            return obj.created_by == request.user
        return False
    
    def has_delete_permission(self, request, obj=None):
        """ادمین می‌تواند همه را حذف کند، کارمندان فقط خود را"""
        if is_pure_admin(request.user):
            return True
        if is_employee(request.user) and obj:
            return obj.created_by == request.user
        return False
    
    def get_queryset(self, request):
        """تصفیه رکوردها بر اساس نقش کاربر"""
        qs = super().get_queryset(request)
        if is_pure_admin(request.user):
            return qs
        # کارمندان فقط می‌توانند رکوردهای خود را ببینند
        if is_employee(request.user):
            return qs.filter(created_by=request.user)
        return qs.none()
    
    def get_subcategory_colored(self, obj):
        """نمایش رنگی دسته‌بندی"""
        colors = {
            'household': '#3498db',      # آبی
            'professional': '#27ae60',   # سبز
            'other': '#95a5a6',          # خاکستری
        }
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
    
    def get_created_by(self, obj):
        """نمایش نام کاربر ایجادکننده"""
        return obj.created_by.get_full_name() if obj.created_by else "خودکار"
    get_created_by.short_description = "ایجادکننده"
    
    def get_amount_formatted(self, obj):
        """نمایش مبلغ با جدا‌کننده هزارگان"""
        return format_currency(obj.amount_received)
    get_amount_formatted.short_description = "مبلغ دریافتی"
    
    def save_model(self, request, obj, form, change):
        """ذخیره خودکار کاربر فعلی"""
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


# ============================================
# 2. بازرگانی - دریافت
# ============================================

@admin.register(TradeAcquisition)
class TradeAcquisitionAdmin(admin.ModelAdmin):
    """مدیریت دریافت بازرگانی - ادمین و کارمندان"""
    list_display = (
        'get_entity_type_colored',
        'acquisition_type',
        'check_category',
        'get_amount_formatted',
        'get_identity_info',
        'created_at'
    )
    list_filter = (
        'entity_type',
        'check_category',
        ('created_at', JDateFieldListFilter),
        'created_by'
    )
    search_fields = (
        'acquisition_type',
        'description',
        'identity_documents__national_id',
        'check_category'
    )
    readonly_fields = (
        'created_at',
        'updated_at',
        'created_by'
    )
    
    fieldsets = (
        ('دسته‌بندی', {
            'fields': ('entity_type',)
        }),
        ('اطلاعات دریافت', {
            'fields': ('acquisition_type',)
        }),
        ('مدارک و اطلاعات', {
            'fields': (
                'identity_documents',
                'contact_info'
            )
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
            'fields': (
                'created_by',
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def has_module_permission(self, request):
        """ادمین و کارمندان می‌توانند این مدل را ببینند"""
        return is_pure_admin(request.user) or is_employee(request.user)
    
    def has_view_permission(self, request, obj=None):
        """ادمین می‌تواند همه را ببیند، کارمندان فقط خود را"""
        if is_pure_admin(request.user):
            return True
        if is_employee(request.user) and obj:
            return obj.created_by == request.user
        return False
    
    def has_add_permission(self, request):
        """ادمین و کارمندان می‌توانند اضافه کنند"""
        return is_pure_admin(request.user) or is_employee(request.user)
    
    def has_change_permission(self, request, obj=None):
        """ادمین می‌تواند همه را تغییر بدهد، کارمندان فقط خود را"""
        if is_pure_admin(request.user):
            return True
        if is_employee(request.user) and obj:
            return obj.created_by == request.user
        return False
    
    def has_delete_permission(self, request, obj=None):
        """ادمین می‌تواند همه را حذف کند، کارمندان فقط خود را"""
        if is_pure_admin(request.user):
            return True
        if is_employee(request.user) and obj:
            return obj.created_by == request.user
        return False
    
    def get_queryset(self, request):
        """تصفیه رکوردها بر اساس نقش کاربر"""
        qs = super().get_queryset(request)
        if is_pure_admin(request.user):
            return qs
        # کارمندان فقط می‌توانند رکوردهای خود را ببینند
        if is_employee(request.user):
            return qs.filter(created_by=request.user)
        return qs.none()
    
    def get_entity_type_colored(self, obj):
        """نمایش رنگی نوع موجود"""
        colors = {
            'legal': '#e74c3c',      # قرمز
            'natural': '#27ae60',    # سبز
        }
        color = colors.get(obj.entity_type, '#34495e')
        text = obj.get_entity_type_display()
        return f'<span style="background-color: {color}; color: white; padding: 5px 10px; border-radius: 3px;">{text}</span>'
    get_entity_type_colored.short_description = "نوع موجود"
    get_entity_type_colored.allow_tags = True
    
    def get_identity_info(self, obj):
        """نمایش اطلاعات شخص"""
        doc = obj.identity_documents
        return f"{doc.first_name} {doc.last_name}"
    get_identity_info.short_description = "نام شخص"
    
    def get_amount_formatted(self, obj):
        """نمایش مبلغ با جدا‌کننده هزارگان"""
        return format_currency(obj.amount_received)
    get_amount_formatted.short_description = "مبلغ دریافتی"
    
    def save_model(self, request, obj, form, change):
        """ذخیره خودکار کاربر فعلی"""
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


# ============================================
# 2. بازرگانی - کارت بازرگانی
# ============================================

@admin.register(TradePartnership)
class TradePartnershipAdmin(admin.ModelAdmin):
    """مدیریت کارت بازرگانی - ادمین و کارمندان"""
    list_display = (
        'get_entity_type_colored',
        'card_year',
        'get_import_ceiling_formatted',
        'get_export_ceiling_formatted',
        'get_amount_formatted',
        'get_identity_info',
        'created_at'
    )
    list_filter = (
        'entity_type',
        'card_year',
        ('created_at', JDateFieldListFilter),
        'created_by'
    )
    search_fields = (
        'description',
        'identity_documents__national_id',
    )
    readonly_fields = (
        'created_at',
        'updated_at',
        'created_by'
    )
    
    fieldsets = (
        ('دسته‌بندی', {
            'fields': ('entity_type',)
        }),
        ('اطلاعات سال', {
            'fields': ('card_year',)
        }),
        ('سقف‌های تجاری', {
            'fields': (
                'import_ceiling',
                'export_ceiling'
            )
        }),
        ('مبالغ انجام‌شده', {
            'fields': (
                'import_amount',
                'export_amount'
            )
        }),
        ('مدارک و اطلاعات', {
            'fields': (
                'identity_documents',
                'contact_info'
            )
        }),
        ('مالی', {
            'fields': ('amount_received',)
        }),
        ('توضیحات', {
            'fields': ('description',)
        }),
        ('متاداده', {
            'fields': (
                'created_by',
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def has_module_permission(self, request):
        """ادمین و کارمندان می‌توانند این مدل را ببینند"""
        return is_pure_admin(request.user) or is_employee(request.user)
    
    def has_view_permission(self, request, obj=None):
        """ادمین می‌تواند همه را ببیند، کارمندان فقط خود را"""
        if is_pure_admin(request.user):
            return True
        if is_employee(request.user) and obj:
            return obj.created_by == request.user
        return False
    
    def has_add_permission(self, request):
        """ادمین و کارمندان می‌توانند اضافه کنند"""
        return is_pure_admin(request.user) or is_employee(request.user)
    
    def has_change_permission(self, request, obj=None):
        """ادمین می‌تواند همه را تغییر بدهد، کارمندان فقط خود را"""
        if is_pure_admin(request.user):
            return True
        if is_employee(request.user) and obj:
            return obj.created_by == request.user
        return False
    
    def has_delete_permission(self, request, obj=None):
        """ادمین می‌تواند همه را حذف کند، کارمندان فقط خود را"""
        if is_pure_admin(request.user):
            return True
        if is_employee(request.user) and obj:
            return obj.created_by == request.user
        return False
    
    def get_queryset(self, request):
        """تصفیه رکوردها بر اساس نقش کاربر"""
        qs = super().get_queryset(request)
        if is_pure_admin(request.user):
            return qs
        # کارمندان فقط می‌توانند رکوردهای خود را ببینند
        if is_employee(request.user):
            return qs.filter(created_by=request.user)
        return qs.none()
    
    def get_entity_type_colored(self, obj):
        """نمایش رنگی نوع موجود"""
        colors = {
            'natural': '#27ae60',       # سبز
            'legal': '#e74c3c',         # قرمز
            'productive': '#f39c12',    # نارنجی
        }
        color = colors.get(obj.entity_type, '#34495e')
        text = obj.get_entity_type_display()
        return f'<span style="background-color: {color}; color: white; padding: 5px 10px; border-radius: 3px;">{text}</span>'
    get_entity_type_colored.short_description = "نوع مشارکت"
    get_entity_type_colored.allow_tags = True
    
    def get_identity_info(self, obj):
        """نمایش اطلاعات شخص"""
        doc = obj.identity_documents
        return f"{doc.first_name} {doc.last_name}"
    get_identity_info.short_description = "نام شخص"
    
    def get_import_ceiling_formatted(self, obj):
        """نمایش سقف واردات با جدا‌کننده هزارگان"""
        return format_currency(obj.import_ceiling)
    get_import_ceiling_formatted.short_description = "سقف واردات"
    
    def get_export_ceiling_formatted(self, obj):
        """نمایش سقف صادرات با جدا‌کننده هزارگان"""
        return format_currency(obj.export_ceiling)
    get_export_ceiling_formatted.short_description = "سقف صادرات"
    
    def get_amount_formatted(self, obj):
        """نمایش مبلغ دریافتی با جدا‌کننده هزارگان"""
        return format_currency(obj.amount_received)
    get_amount_formatted.short_description = "مبلغ دریافتی"
    
    def save_model(self, request, obj, form, change):
        """ذخیره خودکار کاربر فعلی"""
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


# ============================================
# 3. شرکت‌ها
# ============================================

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    """مدیریت شرکت‌ها - ادمین و کارمندان"""
    list_display = (
        'company_name',
        'get_company_type_colored',
        'get_license_status',
        'get_amount_formatted',
        'created_at'
    )
    list_filter = (
        'company_type',
        'has_license',
        ('created_at', JDateFieldListFilter),
        'created_by'
    )
    search_fields = (
        'company_name',
        'description',
        'identity_documents__national_id',
    )
    readonly_fields = (
        'created_at',
        'updated_at',
        'created_by'
    )
    
    fieldsets = (
        ('اطلاعات شرکت', {
            'fields': (
                'company_name',
                'company_type'
            )
        }),
        ('مدارک و اطلاعات', {
            'fields': (
                'identity_documents',
                'contact_info'
            )
        }),
        ('مجوز', {
            'fields': (
                'has_license',
                'license_file'
            ),
            'description': 'فایل مجوز الزامی است اگر مجوز موجود باشد'
        }),
        ('مالی', {
            'fields': ('amount_received',)
        }),
        ('توضیحات', {
            'fields': ('description',)
        }),
        ('متاداده', {
            'fields': (
                'created_by',
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def has_module_permission(self, request):
        """ادمین و کارمندان می‌توانند این مدل را ببینند"""
        return is_pure_admin(request.user) or is_employee(request.user)
    
    def has_view_permission(self, request, obj=None):
        """ادمین می‌تواند همه را ببیند، کارمندان فقط خود را"""
        if is_pure_admin(request.user):
            return True
        if is_employee(request.user) and obj:
            return obj.created_by == request.user
        return False
    
    def has_add_permission(self, request):
        """ادمین و کارمندان می‌توانند اضافه کنند"""
        return is_pure_admin(request.user) or is_employee(request.user)
    
    def has_change_permission(self, request, obj=None):
        """ادمین می‌تواند همه را تغییر بدهد، کارمندان فقط خود را"""
        if is_pure_admin(request.user):
            return True
        if is_employee(request.user) and obj:
            return obj.created_by == request.user
        return False
    
    def has_delete_permission(self, request, obj=None):
        """ادمین می‌تواند همه را حذف کند، کارمندان فقط خود را"""
        if is_pure_admin(request.user):
            return True
        if is_employee(request.user) and obj:
            return obj.created_by == request.user
        return False
    
    def get_queryset(self, request):
        """تصفیه رکوردها بر اساس نقش کاربر"""
        qs = super().get_queryset(request)
        if is_pure_admin(request.user):
            return qs
        # کارمندان فقط می‌توانند رکوردهای خود را ببینند
        if is_employee(request.user):
            return qs.filter(created_by=request.user)
        return qs.none()
    
    def get_company_type_colored(self, obj):
        """نمایش رنگی نوع شرکت"""
        colors = {
            'limited_liability': '#3498db',  # آبی
            'joint_stock': '#27ae60',        # سبز
            'cooperative': '#9b59b6',        # بنفش
            'transport': '#f39c12',          # نارنجی
        }
        color = colors.get(obj.company_type, '#34495e')
        text = obj.get_company_type_display()
        return f'<span style="background-color: {color}; color: white; padding: 5px 10px; border-radius: 3px;">{text}</span>'
    get_company_type_colored.short_description = "نوع شرکت"
    get_company_type_colored.allow_tags = True
    
    def get_license_status(self, obj):
        """نمایش وضعیت مجوز"""
        if obj.has_license:
            if obj.license_file:
                return '✓ مجوز موجود (با فایل)'
            else:
                return '⚠ مجوز بدون فایل'
        return '✗ بدون مجوز'
    get_license_status.short_description = "وضعیت مجوز"
    
    def get_amount_formatted(self, obj):
        """نمایش مبلغ با جدا‌کننده هزارگان"""
        return format_currency(obj.amount_received)
    get_amount_formatted.short_description = "مبلغ دریافتی"
    
    def save_model(self, request, obj, form, change):
        """ذخیره خودکار کاربر فعلی و اعتبارسنجی"""
        if not obj.created_by:
            obj.created_by = request.user
        # اعتبارسنجی
        obj.full_clean()
        super().save_model(request, obj, form, change)


# سفارشی‌سازی Admin Site
admin.site.site_header = "⚖️ سیستم ثبتی خدمات Phonix"
admin.site.site_title = "Registry Admin"