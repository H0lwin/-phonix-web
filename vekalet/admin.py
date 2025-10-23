from django import forms
from django.contrib import admin
from django.core.exceptions import PermissionDenied, ValidationError
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Q
from .models import CaseFile, CaseFileAttachment, ConsultationPrice, Consultation
from core.admin import lawyer_admin_site


# ============================================
# فرم‌های سفارشی
# ============================================

class CaseFileAttachmentForm(forms.ModelForm):
    """فرم سفارشی برای اعتبارسنجی پیوست‌ها"""
    
    class Meta:
        model = CaseFileAttachment
        fields = '__all__'
    
    def clean(self):
        """اعتبارسنجی برای اطمینان از انتخاب حداقل یک پرونده یا مشاوره"""
        cleaned_data = super().clean()
        case = cleaned_data.get('case')
        consultation = cleaned_data.get('consultation')
        
        if not case and not consultation:
            raise ValidationError('⚠️ لطفاً حداقل یک پرونده یا مشاوره انتخاب کنید')
        
        return cleaned_data


def is_admin(user):
    """بررسی کاربر ادمین است"""
    if user.is_superuser:
        return True
    if hasattr(user, 'profile') and user.profile.role == 'admin':
        return True
    return False


def is_pure_admin(user):
    """بررسی کاربر admin واقعی است (superuser یا role='admin')"""
    if user.is_superuser:
        return True
    if hasattr(user, 'profile') and user.profile.role == 'admin':
        return True
    return False


def is_lawyer(user):
    """بررسی کاربر وکیل است"""
    if hasattr(user, 'profile'):
        return user.profile.role == 'lawyer'
    return False


def is_non_admin(user):
    """بررسی کاربر کارمند یا وکیل است"""
    return is_lawyer(user)


# ============================================
# Inline برای پیوست‌های پرونده و مشاورات
# ============================================

class CaseFileAttachmentInline(admin.TabularInline):
    """مدیریت پیوست‌های پرونده در صفحه پرونده"""
    model = CaseFileAttachment
    extra = 1
    fields = ('attachment_type', 'title', 'description', 'file', 'uploaded_by', 'uploaded_at')
    readonly_fields = ('uploaded_by', 'uploaded_at')
    
    def get_queryset(self, request):
        """فقط پیوست‌های این پرونده نمایش داده شود"""
        qs = super().get_queryset(request)
        return qs.filter(case__isnull=False)
    
    def save_formset(self, request, form, formset, change):
        """تنظیم uploaded_by"""
        instances = formset.save(commit=False)
        for instance in instances:
            if not instance.uploaded_by:
                instance.uploaded_by = request.user
            # اطمینان از اینکه case تنظیم‌شده است
            if not instance.case and hasattr(form, 'instance'):
                instance.case = form.instance
        formset.save()


class ConsultationAttachmentInline(admin.TabularInline):
    """مدیریت پیوست‌های مشاوره در صفحه مشاوره"""
    model = CaseFileAttachment
    extra = 1
    fields = ('attachment_type', 'title', 'description', 'file', 'uploaded_by', 'uploaded_at')
    readonly_fields = ('uploaded_by', 'uploaded_at')
    
    def get_queryset(self, request):
        """فقط پیوست‌های این مشاوره نمایش داده شود"""
        qs = super().get_queryset(request)
        return qs.filter(consultation__isnull=False)
    
    def save_formset(self, request, form, formset, change):
        """تنظیم uploaded_by"""
        instances = formset.save(commit=False)
        for instance in instances:
            if not instance.uploaded_by:
                instance.uploaded_by = request.user
            # اطمینان از اینکه consultation تنظیم‌شده است
            if not instance.consultation and hasattr(form, 'instance'):
                instance.consultation = form.instance
        formset.save()


# ============================================
# مدیریت پرونده‌های حقوقی و قضایی
# ============================================

class CaseFileAdmin(admin.ModelAdmin):
    """مدیریت پرونده‌های حقوقی و قضایی - وکلا و ادمین"""
    inlines = [CaseFileAttachmentInline]
    
    list_display = ('case_number', 'title', 'get_case_type_display', 'client_name', 
                   'assigned_lawyer', 'get_priority_display', 'status', 'get_payment_status', 'created_at')
    list_filter = ('case_type', 'status', 'priority', 'case_start_date', 
                  'assigned_lawyer', 'created_at')
    search_fields = ('case_number', 'title', 'client_name', 'client_national_id', 
                    'description', 'court_case_number')
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'get_remaining_amount', 'get_amount_info')
    date_hierarchy = 'case_start_date'
    
    fieldsets = (
        ('🔖 شناسایی پرونده', {
            'fields': ('case_number', 'title', 'case_type')
        }),
        ('👤 اطلاعات مراجع/موکل', {
            'fields': ('client_name', 'client_national_id', 'client_phone', 'client_address')
        }),
        ('📋 جزئیات پرونده', {
            'fields': ('description', 'case_details')
        }),
        ('⚖️ مشخصات قانونی', {
            'fields': ('legal_basis', 'court_name', 'court_case_number', 'judge_name'),
            'classes': ('collapse',)
        }),
        ('📅 زمان‌بندی', {
            'fields': ('case_start_date', 'case_end_date', 'next_hearing_date')
        }),
        ('💰 اطلاعات مالی', {
            'fields': ('contract_amount', 'paid_amount', 'get_remaining_amount')
        }),
        ('🏷️ وضعیت و اولویت', {
            'fields': ('status', 'priority')
        }),
        ('👨‍⚖️ اختصاص و مسئولیت', {
            'fields': ('assigned_lawyer', 'co_lawyers')
        }),
        ('📝 یادداشت‌ها', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('📊 اطلاعات سیستمی', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_module_permission(self, request):
        """وکلا و ادمین می‌توانند این مدل را ببینند"""
        return is_admin(request.user) or is_lawyer(request.user)
    
    def has_view_permission(self, request, obj=None):
        """وکلا و ادمین می‌توانند ببینند"""
        if is_admin(request.user):
            return True
        return is_lawyer(request.user)
    
    def has_add_permission(self, request):
        """وکلا و ادمین می‌توانند اضافه کنند"""
        return is_admin(request.user) or is_lawyer(request.user)
    
    def has_change_permission(self, request, obj=None):
        """ادمین همه، وکلا فقط خود یا واگذار‌شده را می‌توانند تغییر دهند"""
        if is_admin(request.user):
            return True
        if is_lawyer(request.user) and obj:
            return obj.created_by == request.user or obj.assigned_lawyer == request.user
        return False
    
    def has_delete_permission(self, request, obj=None):
        """ادمین همه، وکلا فقط خود را می‌توانند حذف کنند"""
        if is_admin(request.user):
            return True
        if is_lawyer(request.user) and obj:
            return obj.created_by == request.user
        return False
    
    def get_queryset(self, request):
        """تصفیه پرونده‌ها بر اساس نقش کاربر"""
        qs = super().get_queryset(request).prefetch_related('co_lawyers', 'attachments')
        if is_admin(request.user):
            return qs
        # وکلا می‌توانند پرونده‌های خود یا واگذار‌شده را ببینند
        if is_lawyer(request.user):
            return qs.filter(Q(created_by=request.user) | Q(assigned_lawyer=request.user))
        return qs.none()
    
    def save_model(self, request, obj, form, change):
        """ذخیره‌سازی مدل - تنظیم created_by برای رکوردهای جدید"""
        if not change:  # اگر رکورد جدید است
            obj.created_by = request.user
        # تنظیم assigned_lawyer اگر تنها وکیل است
        if not obj.assigned_lawyer and is_lawyer(request.user):
            obj.assigned_lawyer = request.user
        super().save_model(request, obj, form, change)
    
    def get_created_by(self, obj):
        """نمایش ایجاد‌کننده"""
        if obj.created_by:
            return obj.created_by.profile.display_name if hasattr(obj.created_by, 'profile') else obj.created_by.username
        return '-'
    get_created_by.short_description = "ایجاد‌کننده"
    
    def get_case_type_display(self, obj):
        """نمایش نوع پرونده با رنگ"""
        if obj.case_type == 'legal':
            return format_html('<span style="color: blue;"><strong>حقوقی</strong></span>')
        elif obj.case_type == 'judicial':
            return format_html('<span style="color: red;"><strong>قضایی</strong></span>')
        else:
            return format_html('<span style="color: gray;"><strong>سایر</strong></span>')
    get_case_type_display.short_description = "نوع پرونده"
    
    def get_priority_display(self, obj):
        """نمایش اولویت با رنگ"""
        colors = {
            'low': 'green',
            'medium': 'blue',
            'high': 'orange',
            'urgent': 'red'
        }
        labels = {
            'low': 'کم',
            'medium': 'متوسط',
            'high': 'بالا',
            'urgent': 'فوری'
        }
        color = colors.get(obj.priority, 'gray')
        label = labels.get(obj.priority, obj.priority)
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, label)
    get_priority_display.short_description = "اولویت"
    
    def get_payment_status(self, obj):
        """نمایش وضعیت پرداخت پرونده"""
        remaining = obj.get_remaining_amount()
        if remaining > 0:
            percentage = (obj.paid_amount / obj.contract_amount * 100) if obj.contract_amount > 0 else 0
            return format_html(
                '<span style="color: orange;"><strong>جزئی:</strong> {:.0f}%</span>',
                percentage
            )
        elif remaining == 0:
            return format_html('<span style="color: green;"><strong>✓ پرداخت شده</strong></span>')
        return '-'
    get_payment_status.short_description = "وضعیت پرداخت"
    
    def get_amount_info(self, obj):
        """نمایش جزئیات مالی پرونده"""
        remaining = obj.get_remaining_amount()
        if remaining > 0:
            return format_html(
                '<strong>قرارداد:</strong> {} تومان<br/>'
                '<strong>پرداخت‌شده:</strong> {} تومان<br/>'
                '<span style="color: red;"><strong>باقی‌مانده:</strong> {} تومان</span>',
                f'{obj.contract_amount:,.0f}',
                f'{obj.paid_amount:,.0f}',
                f'{remaining:,.0f}'
            )
        elif remaining == 0:
            return format_html(
                '<span style="color: green;"><strong>✓ تمام مبلغ پرداخت‌شده است</strong></span>'
            )
        return '-'
    get_amount_info.short_description = "وضعیت مالی"
    
    def get_remaining_amount(self, obj):
        """نمایش مبلغ باقی‌مانده"""
        remaining = obj.get_remaining_amount()
        if remaining > 0:
            return format_html(
                '<strong>قرارداد:</strong> {} تومان<br/>'
                '<strong>پرداخت‌شده:</strong> {} تومان<br/>'
                '<span style="color: red;"><strong>باقی‌مانده:</strong> {} تومان</span>',
                f'{obj.contract_amount:,.0f}',
                f'{obj.paid_amount:,.0f}',
                f'{remaining:,.0f}'
            )
        elif remaining == 0:
            return format_html(
                '<span style="color: green;"><strong>✓ تمام مبلغ پرداخت‌شده است</strong></span>'
            )
        return '-'
    get_remaining_amount.short_description = "وضعیت مالی"


# ============================================
# مدیریت پیوست‌های پرونده
# ============================================

class CaseFileAttachmentAdmin(admin.ModelAdmin):
    """مدیریت پیوست‌های پرونده و مشاورات"""
    form = CaseFileAttachmentForm
    
    list_display = ('title', 'get_related_object', 'attachment_type', 'get_file_name', 'uploaded_by', 'uploaded_at')
    list_filter = ('attachment_type', 'uploaded_at', 'case', 'consultation')
    search_fields = ('title', 'description', 'case__case_number', 'consultation__client_name')
    readonly_fields = ('uploaded_by', 'uploaded_at', 'get_file_size', 'get_related_object')
    date_hierarchy = 'uploaded_at'
    
    fieldsets = (
        ('متعلق به', {
            'fields': ('case', 'consultation'),
            'description': '⚠️ حداقل یکی از پرونده یا مشاوره را انتخاب کنید'
        }),
        ('مشخصات پیوست', {
            'fields': ('attachment_type', 'title', 'description')
        }),
        ('فایل', {
            'fields': ('file', 'get_file_size')
        }),
        ('اطلاعات سیستمی', {
            'fields': ('uploaded_by', 'uploaded_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_module_permission(self, request):
        """وکلا و ادمین می‌توانند این مدل را ببینند"""
        return is_admin(request.user) or is_lawyer(request.user)
    
    def has_view_permission(self, request, obj=None):
        """وکلا و ادمین می‌توانند ببینند"""
        if is_admin(request.user):
            return True
        return is_lawyer(request.user)
    
    def has_add_permission(self, request):
        """وکلا و ادمین می‌توانند اضافه کنند"""
        return is_admin(request.user) or is_lawyer(request.user)
    
    def has_change_permission(self, request, obj=None):
        """ادمین همه، وکلا اپلودکننده"""
        if is_admin(request.user):
            return True
        if is_lawyer(request.user) and obj:
            return obj.uploaded_by == request.user
        return False
    
    def has_delete_permission(self, request, obj=None):
        """ادمین همه، وکلا اپلودکننده"""
        if is_admin(request.user):
            return True
        if is_lawyer(request.user) and obj:
            return obj.uploaded_by == request.user
        return False
    
    def get_queryset(self, request):
        """تصفیه پیوست‌ها بر اساس نقش کاربر"""
        qs = super().get_queryset(request).select_related('case', 'consultation')
        if is_admin(request.user):
            return qs
        # وکلا فقط می‌توانند پیوست‌های پرونده‌ها و مشاوراتی که خود ایجاد کردند را ببینند
        if is_lawyer(request.user):
            return qs.filter(
                Q(case__created_by=request.user) | 
                Q(case__assigned_lawyer=request.user) |
                Q(consultation__created_by=request.user) | 
                Q(consultation__assigned_lawyer=request.user)
            )
        return qs.none()
    
    def save_model(self, request, obj, form, change):
        """ذخیره‌سازی مدل - تنظیم uploaded_by"""
        if not obj.uploaded_by:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)
    
    def get_related_object(self, obj):
        """نمایش پرونده یا مشاوره"""
        if obj.case:
            return format_html(
                '<span style="color: blue;"><strong>📋 پرونده:</strong> {}</span>',
                obj.case.case_number
            )
        elif obj.consultation:
            return format_html(
                '<span style="color: green;"><strong>💬 مشاوره:</strong> {}</span>',
                obj.consultation.client_name
            )
        return format_html('<span style="color: red;">❌ نامشخص</span>')
    get_related_object.short_description = "متعلق به"
    
    def get_file_name(self, obj):
        """نمایش نام فایل"""
        if obj.file:
            return obj.file.name.split('/')[-1]
        return '-'
    get_file_name.short_description = "نام فایل"
    
    def get_file_size(self, obj):
        """نمایش اندازه فایل"""
        size_kb = obj.get_file_size_kb()
        if size_kb > 1024:
            size_mb = round(size_kb / 1024, 2)
            return f"{size_mb} MB"
        return f"{size_kb} KB"
    get_file_size.short_description = "اندازه فایل"


# ============================================
# مدیریت قیمت‌های خدمات
# ============================================

class ConsultationForm(forms.ModelForm):
    """فرم سفارشی برای مشاورات - فیلد مبلغ پرداخت شده فقط برای پرداخت جزئی"""
    
    class Meta:
        model = Consultation
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # اگر payment_status جزئی نیست، amount_paid غیرفعال باشد
        if self.instance.pk:
            if self.instance.payment_status != 'partial':
                self.fields['amount_paid'].widget.attrs['disabled'] = True
                self.fields['amount_paid'].help_text = 'فقط برای پرداخت‌های جزئی فعال است'
    
    def clean(self):
        """اعتبارسنجی"""
        cleaned_data = super().clean()
        payment_status = cleaned_data.get('payment_status')
        amount_paid = cleaned_data.get('amount_paid')
        consultation_fee = cleaned_data.get('consultation_fee')
        
        # اگر payment_status جزئی بود، amount_paid باید پر باشد و کمتر از consultation_fee
        if payment_status == 'partial':
            if amount_paid is None or amount_paid == 0:
                raise ValidationError('برای پرداخت جزئی، مبلغ پرداخت‌شده باید وارد شود')
            if amount_paid >= consultation_fee:
                raise ValidationError(f'مبلغ پرداخت‌شده ({amount_paid:,.0f}) باید کمتر از هزینه مشاوره ({consultation_fee:,.0f}) باشد')
        
        return cleaned_data


class ConsultationPriceAdmin(admin.ModelAdmin):
    """مدیریت قیمت‌های خدمات - فقط ادمین"""
    list_display = ('get_service_name', 'get_formatted_price', 'is_active', 'updated_at')
    list_filter = ('is_active', 'service_type')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('نوع خدمت', {
            'fields': ('service_type', 'description')
        }),
        ('قیمت‌گذاری', {
            'fields': ('price', 'is_active'),
            'description': 'قیمت را بر حسب تومان وارد کنید. برای خدمات رایگان، مقدار 0 را وارد کنید.'
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
        """فقط ادمین"""
        return is_pure_admin(request.user)
    
    def has_add_permission(self, request):
        """فقط ادمین"""
        return is_pure_admin(request.user)
    
    def has_change_permission(self, request, obj=None):
        """فقط ادمین"""
        return is_pure_admin(request.user)
    
    def has_delete_permission(self, request, obj=None):
        """فقط ادمین"""
        return is_pure_admin(request.user)
    
    def get_service_name(self, obj):
        """نمایش نام خدمت"""
        return obj.get_service_type_display()
    get_service_name.short_description = "خدمت"
    
    def get_formatted_price(self, obj):
        """نمایش قیمت با رنگ"""
        if obj.price == 0:
            return format_html('<span style="color: green;"><strong>رایگان</strong></span>')
        return format_html('<span style="color: blue;"><strong>{}</strong> تومان</span>', f'{obj.price:,.0f}')
    get_formatted_price.short_description = "قیمت"


# ============================================
# مدیریت مشاورات
# ============================================

class ConsultationAdmin(admin.ModelAdmin):
    """مدیریت مشاورات - وکلا و ادمین"""
    form = ConsultationForm
    inlines = [ConsultationAttachmentInline]
    
    list_display = ('client_name', 'consultation_subject', 'consultation_date', 'assigned_lawyer', 
                   'status', 'get_fee_display', 'payment_status', 'get_payment_info', 'created_at')
    list_filter = ('status', 'payment_status', 'consultation_date', 'assigned_lawyer', 'created_at')
    search_fields = ('client_name', 'client_phone', 'client_national_id', 'consultation_subject')
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'get_fee_difference_display', 'get_remaining_fee')
    date_hierarchy = 'consultation_date'
    
    fieldsets = (
        ('اطلاعات مراجع', {
            'fields': ('client_name', 'client_phone', 'client_national_id', 'client_email', 'client_address')
        }),
        ('مشخصات مشاوره', {
            'fields': ('consultation_date', 'consultation_subject', 'consultation_details', 'assigned_lawyer')
        }),
        ('هزینه و پرداخت', {
            'fields': ('consultation_fee', 'payment_status', 'amount_paid', 'get_remaining_fee', 'get_fee_difference_display'),
            'description': 'هزینه مشاوره را به تومان وارد کنید. برای مشاورات رایگان، 0 را وارد کنید. مبلغ پرداخت‌شده فقط برای پرداخت‌های جزئی فعال است.'
        }),
        ('تبدیل به پرونده', {
            'fields': ('status', 'converted_to_case', 'conversion_date', 'final_contract_amount', 'conversion_notes'),
            'description': 'اگر این مشاوره به قرارداد تبدیل شد، اطلاعات را وارد کنید',
            'classes': ('collapse',)
        }),
        ('یادداشت‌های عمومی', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('اطلاعات سیستمی', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_module_permission(self, request):
        """وکلا و ادمین می‌توانند این مدل را ببینند"""
        return is_admin(request.user) or is_lawyer(request.user)
    
    def has_view_permission(self, request, obj=None):
        """وکلا و ادمین می‌توانند ببینند"""
        if is_admin(request.user):
            return True
        return is_lawyer(request.user)
    
    def has_add_permission(self, request):
        """وکلا و ادمین می‌توانند اضافه کنند"""
        return is_admin(request.user) or is_lawyer(request.user)
    
    def has_change_permission(self, request, obj=None):
        """ادمین همه، وکلا فقط خود را می‌توانند تغییر دهند"""
        if is_admin(request.user):
            return True
        if is_lawyer(request.user) and obj:
            return obj.created_by == request.user or obj.assigned_lawyer == request.user
        return False
    
    def has_delete_permission(self, request, obj=None):
        """ادمین همه، وکلا فقط خود را می‌توانند حذف کنند"""
        if is_admin(request.user):
            return True
        if is_lawyer(request.user) and obj:
            return obj.created_by == request.user
        return False
    
    def get_queryset(self, request):
        """تصفیه مشاورات بر اساس نقش کاربر"""
        qs = super().get_queryset(request)
        if is_admin(request.user):
            return qs
        # وکلا فقط می‌توانند مشاوراتی که خود ایجاد کردند یا به آن‌ها واگذار شده ببینند
        if is_lawyer(request.user):
            return qs.filter(Q(created_by=request.user) | Q(assigned_lawyer=request.user))
        return qs.none()
    
    def save_model(self, request, obj, form, change):
        """ذخیره‌سازی مدل - تنظیم created_by و assigned_lawyer"""
        if not change:  # اگر رکورد جدید است
            obj.created_by = request.user
        
        # تنظیم assigned_lawyer اگر تنها وکیل است
        if not obj.assigned_lawyer and is_lawyer(request.user):
            obj.assigned_lawyer = request.user
        
        super().save_model(request, obj, form, change)
    
    def get_fee_display(self, obj):
        """نمایش هزینه با رنگ"""
        if obj.consultation_fee == 0:
            return format_html('<span style="color: green;"><strong>رایگان</strong></span>')
        return format_html('<span style="color: blue;"><strong>{}</strong> تومان</span>', f'{obj.consultation_fee:,.0f}')
    get_fee_display.short_description = "هزینه مشاوره"
    
    def get_payment_info(self, obj):
        """نمایش وضعیت پرداخت"""
        if obj.payment_status == 'paid':
            return format_html('<span style="color: green;"><strong>✓ پرداخت شده</strong></span>')
        elif obj.payment_status == 'partial':
            remaining = obj.consultation_fee - obj.amount_paid
            return format_html(
                '<span style="color: orange;"><strong>جزئی:</strong> {}/{} تومان</span>',
                f'{obj.amount_paid:,.0f}',
                f'{obj.consultation_fee:,.0f}'
            )
        elif obj.payment_status == 'unpaid':
            return format_html('<span style="color: red;"><strong>✗ پرداخت نشده</strong></span>')
        elif obj.payment_status == 'free':
            return format_html('<span style="color: blue;"><strong>رایگان</strong></span>')
        return '-'
    get_payment_info.short_description = "وضعیت پرداخت"
    
    def get_remaining_fee(self, obj):
        """نمایش مبلغ باقی‌مانده برای پرداخت جزئی"""
        if obj.payment_status == 'partial':
            remaining = obj.consultation_fee - obj.amount_paid
            return format_html(
                '<strong>باقی‌مانده:</strong> <span style="color: red;">{} تومان</span>',
                f'{remaining:,.0f}'
            )
        return '-'
    get_remaining_fee.short_description = "مبلغ باقی‌مانده"
    
    def get_fee_difference_display(self, obj):
        """نمایش اختلاف هزینه برای پرداخت جزئی یا تبدیل به قرارداد"""
        if obj.payment_status == 'partial':
            # برای پرداخت جزئی نمایش مبلغ پرداخت شده و باقی‌مانده
            remaining = obj.consultation_fee - obj.amount_paid
            return format_html(
                '<strong>هزینه کل:</strong> {}<br/>'
                '<strong>پرداخت شده:</strong> {}<br/>'
                '<span style="color: red;"><strong>باقی‌مانده:</strong> {} تومان</span>',
                f'{obj.consultation_fee:,.0f}',
                f'{obj.amount_paid:,.0f}',
                f'{remaining:,.0f}'
            )
        elif obj.final_contract_amount:
            # برای تبدیل به قرارداد
            difference = obj.get_fee_difference()
            if difference > 0:
                return format_html(
                    '<strong>هزینه مشاوره:</strong> {}<br/>'
                    '<strong>مبلغ قرارداد:</strong> {}<br/>'
                    '<span style="color: orange;"><strong>اختلاف:</strong> {} تومان</span>',
                    f'{obj.consultation_fee:,.0f}',
                    f'{obj.final_contract_amount:,.0f}',
                    f'{difference:,.0f}'
                )
            return format_html(
                '<strong>هزینه مشاوره:</strong> {}<br/>'
                '<strong>مبلغ قرارداد:</strong> {}',
                f'{obj.consultation_fee:,.0f}',
                f'{obj.final_contract_amount:,.0f}'
            )
        return '-'
    get_fee_difference_display.short_description = "جزئیات مالی"


# ============================================
# ثبت مدل‌ها در سیستم وکالت
# ============================================
lawyer_admin_site.register(CaseFile, CaseFileAdmin)
lawyer_admin_site.register(CaseFileAttachment, CaseFileAttachmentAdmin)
lawyer_admin_site.register(ConsultationPrice, ConsultationPriceAdmin)
lawyer_admin_site.register(Consultation, ConsultationAdmin)