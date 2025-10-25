"""
سیستم جامع لاگ‌گیری خودکار فعالیت‌های سیستم
Automatic logging system for all system activities
"""
import json
import logging
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_login_failed, user_logged_in, user_logged_out
from django.utils.text import slugify

# Import models directly to avoid linter errors
from .models import ActivityLog, UserProfile, Employee, Attendance, Income, Expense, Loan, LoanBuyer, LoanCreditorInstallment, Branch

# Get logger for this module
logger = logging.getLogger('phonix')


def get_client_ip(request):
    """دریافت IP کاربر"""
    if request is None:
        return None
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def create_activity_log(user, action, model_name, object_id, description, details=None, request=None):
    """
    ایجاد رکورد لاگ فعالیت
    Create activity log record
    """
    try:
        log_data = {
            'user': user,
            'action': action,
            'content_type': model_name,
            'object_id': str(object_id) if object_id else None,
            'object_description': description,
            'details': json.dumps(details, ensure_ascii=False, default=str) if details else None,
            'ip_address': get_client_ip(request) if request else None,
        }
        ActivityLog.objects.create(**log_data)
    except Exception as e:
        logger.error(f"خطا در ایجاد لاگ فعالیت: {e}", exc_info=True)


# ============================================
# User (کاربر سیستم)
# ============================================

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """خودکار ایجاد UserProfile هنگام ایجاد User و تعیین دسترسی‌ها بر اساس نقش"""
    import jdatetime
    import random
    
    # Skip if explicitly requested
    if getattr(instance, '_skip_profile_creation', False):
        return
    
    # Skip if this is being called from admin (UserProfileInline handles it)
    if getattr(instance, '_saved_by_admin', False):
        return
        
    today = jdatetime.date.today()
    full_name = (f"{instance.first_name} {instance.last_name}".strip()) or instance.username
    
    # Check if profile already exists (possibly created by admin inline)
    try:
        profile = instance.profile
        profile_created = False
    except UserProfile.DoesNotExist:
        # Create new profile only if it doesn't exist
        defaults = {
            'hire_date': today,
            'display_name': full_name,
            'job_title': 'مدیر سیستم' if instance.is_superuser else 'کارمند',
            'department': '',
            'national_id': '',
        }
        desired_role = 'admin' if instance.is_superuser else 'employee'
        defaults['role'] = desired_role
        
        # Generate a unique national_id
        national_id = ''
        for _ in range(100):
            candidate = f"{random.randint(1000000000, 9999999999)}"
            if not UserProfile.objects.filter(national_id=candidate).exists():
                national_id = candidate
                break
        defaults['national_id'] = national_id
        
        profile = UserProfile.objects.create(user=instance, **defaults)
        profile_created = True
    
    # Update profile fields if needed
    updates = {}
    
    # Update national_id if empty
    if not profile.national_id:
        for _ in range(100):
            candidate = f"{random.randint(1000000000, 9999999999)}"
            if not UserProfile.objects.filter(national_id=candidate).exists():
                updates['national_id'] = candidate
                break
    
    # Update display_name if different
    if profile.display_name != full_name:
        updates['display_name'] = full_name
    
    # Update hire_date if empty
    if not profile.hire_date:
        updates['hire_date'] = today
    
    # Update role based on is_superuser status, but preserve admin role
    desired_role = 'admin' if instance.is_superuser else profile.role or 'employee'
    if desired_role == 'admin' or profile.role == 'admin':
        desired_role = 'admin' if instance.is_superuser else profile.role
    if profile.role != desired_role:
        updates['role'] = desired_role
    
    # Update job_title if empty
    if not profile.job_title:
        updates['job_title'] = 'مدیر سیستم' if instance.is_superuser else 'کارمند'
    
    # Save profile updates
    if updates:
        for field, value in updates.items():
            setattr(profile, field, value)
        profile.save()
    
    # Update user permissions based on profile role
    user_updates = {}
    if profile.role == 'admin':
        if not instance.is_staff:
            user_updates['is_staff'] = True
        if not instance.is_superuser:
            user_updates['is_superuser'] = True
    elif profile.role in ['lawyer', 'employee']:
        if not instance.is_staff:
            user_updates['is_staff'] = True
        if instance.is_superuser and profile.role != 'admin':
            user_updates['is_superuser'] = False
    
    # Save user updates
    if user_updates:
        for field, value in user_updates.items():
            setattr(instance, field, value)
        instance.save(update_fields=list(user_updates.keys()))


# ============================================
# ورود و خروج کاربر (Login/Logout)
# ============================================

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """ثبت ورود کاربر"""
    create_activity_log(
        user=user,
        action='login',
        model_name='User',
        object_id=user.id,
        description=f'کاربر {user.get_full_name() or user.username} وارد سیستم شد',
        request=request
    )


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """ثبت خروج کاربر"""
    create_activity_log(
        user=user,
        action='logout',
        model_name='User',
        object_id=user.id,
        description=f'کاربر {user.get_full_name() or user.username} از سیستم خارج شد',
        request=request
    )


@receiver(user_login_failed)
def log_failed_login(sender, credentials, request, **kwargs):
    """ثبت تلاش‌های ناموفق ورود"""
    username = credentials.get('username', 'نامشخص')
    try:
        ActivityLog.objects.create(
            action='login',
            content_type='User',
            object_description=f'تلاش ناموفق برای ورود با نام‌کاربری: {username}',
            ip_address=get_client_ip(request),
            details=json.dumps({'status': 'failed', 'username': username})
        )
    except:
        pass


# ============================================
# Employee (کارمند)
# ============================================

@receiver(post_save, sender=Employee)
def log_employee_change(sender, instance, created, **kwargs):
    """ثبت ایجاد و تغییر کارمند"""
    action = 'create' if created else 'update'
    
    try:
        create_activity_log(
            user=None,
            action=action,
            model_name='Employee',
            object_id=instance.id,
            description=f'کارمند {instance.user.get_full_name()} ({instance.personnel_id})',
            details={
                'name': instance.user.get_full_name(),
                'job_title': instance.job_title,
                'branch': str(instance.branch) if instance.branch else None,
                'status': instance.employment_status
            }
        )
    except Exception as e:
        logger.error(f"خطا در لاگ‌گیری Employee: {e}", exc_info=True)


@receiver(post_delete, sender=Employee)
def log_employee_delete(sender, instance, **kwargs):
    """ثبت حذف کارمند"""
    try:
        create_activity_log(
            user=None,
            action='delete',
            model_name='Employee',
            object_id=instance.id,
            description=f'کارمند {instance.user.get_full_name()} ({instance.personnel_id}) حذف شد'
        )
    except Exception as e:
        logger.error(f"خطا در لاگ‌گیری حذف Employee: {e}", exc_info=True)


# ============================================
# Attendance (حضور و غیاب)
# ============================================

@receiver(post_save, sender=Attendance)
def log_attendance_change(sender, instance, created, **kwargs):
    """ثبت ایجاد و تغییر حضور و غیاب"""
    action = 'create' if created else 'update'
    
    try:
        create_activity_log(
            user=None,
            action=action,
            model_name='Attendance',
            object_id=instance.id,
            description=f'حضور و غیاب {instance.employee.user.get_full_name()} در تاریخ {instance.date}',
            details={
                'employee': str(instance.employee),
                'date': str(instance.date),
                'status': instance.status,
                'notes': instance.notes[:100] if instance.notes else None
            }
        )
    except Exception as e:
        logger.error(f"خطا در لاگ‌گیری Attendance: {e}", exc_info=True)


# ============================================
# Income (درآمد)
# ============================================

@receiver(post_save, sender=Income)
def log_income_change(sender, instance, created, **kwargs):
    """ثبت ایجاد و تغییر درآمد"""
    action = 'create' if created else 'update'
    
    try:
        create_activity_log(
            user=None,
            action=action,
            model_name='Income',
            object_id=instance.id,
            description=f'درآمد "{instance.title}" - {instance.amount:,.0f}',
            details={
                'title': instance.title,
                'amount': float(instance.amount),
                'category': instance.category,
                'payment_status': instance.payment_status,
                'branch': str(instance.branch) if instance.branch else None
            }
        )
    except Exception as e:
        logger.error(f"خطا در لاگ‌گیری Income: {e}", exc_info=True)


@receiver(post_delete, sender=Income)
def log_income_delete(sender, instance, **kwargs):
    """ثبت حذف درآمد"""
    try:
        create_activity_log(
            user=None,
            action='delete',
            model_name='Income',
            object_id=instance.id,
            description=f'درآمد "{instance.title}" - {instance.amount:,.0f} حذف شد'
        )
    except Exception as e:
        logger.error(f"خطا در لاگ‌گیری حذف Income: {e}", exc_info=True)


# ============================================
# Expense (هزینه)
# ============================================

@receiver(post_save, sender=Expense)
def log_expense_change(sender, instance, created, **kwargs):
    """ثبت ایجاد و تغییر هزینه"""
    action = 'create' if created else 'update'
    
    try:
        create_activity_log(
            user=None,
            action=action,
            model_name='Expense',
            object_id=instance.id,
            description=f'هزینه "{instance.title}" - {instance.amount:,.0f}',
            details={
                'title': instance.title,
                'amount': float(instance.amount),
                'category': instance.category,
                'payment_status': instance.payment_status,
                'branch': str(instance.branch) if instance.branch else None
            }
        )
    except Exception as e:
        logger.error(f"خطا در لاگ‌گیری Expense: {e}", exc_info=True)


@receiver(post_delete, sender=Expense)
def log_expense_delete(sender, instance, **kwargs):
    """ثبت حذف هزینه"""
    try:
        create_activity_log(
            user=None,
            action='delete',
            model_name='Expense',
            object_id=instance.id,
            description=f'هزینه "{instance.title}" - {instance.amount:,.0f} حذف شد'
        )
    except Exception as e:
        logger.error(f"خطا در لاگ‌گیری حذف Expense: {e}", exc_info=True)


# ============================================
# Loan (وام)
# ============================================

@receiver(post_save, sender=Loan)
def log_loan_change(sender, instance, created, **kwargs):
    """ثبت ایجاد و تغییر وام"""
    action = 'create' if created else 'update'
    
    try:
        create_activity_log(
            user=None,
            action=action,
            model_name='Loan',
            object_id=instance.id,
            description=f'وام {instance.bank_name} - {instance.amount:,.0f}',
            details={
                'bank_name': instance.bank_name,
                'loan_type': instance.loan_type,
                'amount': float(instance.amount),
                'status': instance.status
            }
        )
    except Exception as e:
        logger.error(f"خطا در لاگ‌گیری Loan: {e}", exc_info=True)


# ============================================
# LoanBuyer (خریدار وام)
# ============================================

@receiver(post_save, sender=LoanBuyer)
def log_loanbuy_change(sender, instance, created, **kwargs):
    """ثبت ایجاد و تغییر خریدار وام"""
    action = 'create' if created else 'update'
    
    try:
        create_activity_log(
            user=None,
            action=action,
            model_name='LoanBuyer',
            object_id=instance.id,
            description=f'خریدار وام {instance.get_full_name()} - {instance.requested_amount:,.0f}',
            details={
                'name': instance.get_full_name(),
                'national_id': instance.national_id,
                'status': instance.current_status
            }
        )
    except Exception as e:
        logger.error(f"خطا در لاگ‌گیری LoanBuyer: {e}", exc_info=True)


# ============================================
# Branch (شعبه)
# ============================================

@receiver(post_save, sender=Branch)
def log_branch_change(sender, instance, created, **kwargs):
    """ثبت ایجاد و تغییر شعبه"""
    action = 'create' if created else 'update'
    
    try:
        create_activity_log(
            user=None,
            action=action,
            model_name='Branch',
            object_id=instance.id,
            description=f'شعبه "{instance.name}" ({instance.code})',
            details={
                'name': instance.name,
                'city': instance.city,
                'status': instance.status
            }
        )
    except Exception as e:
        logger.error(f"خطا در لاگ‌گیری Branch: {e}", exc_info=True)


# ============================================
# LoanCreditorInstallment (قسط‌های بستانکار)
# ============================================

@receiver(post_save, sender=LoanCreditorInstallment)
def update_creditor_on_installment_save(sender, instance, created, **kwargs):
    """هنگام ذخیره قسط، مبلغ پرداخت‌شده و وضعیت تسویه بستانکار را بروزرسانی کنید"""
    try:
        creditor = instance.creditor
        # ذخیره بستانکار تا منطق save() اجرا شود
        creditor.save()
        
        # ثبت لاگ
        create_activity_log(
            user=None,
            action='update' if not created else 'create',
            model_name='LoanCreditorInstallment',
            object_id=instance.id,
            description=f'قسط {instance.installment_number} - {instance.creditor.first_name} {instance.creditor.last_name}',
            details={
                'creditor_id': instance.creditor.id,
                'installment_number': instance.installment_number,
                'paid_amount': float(instance.paid_amount),
                'status': instance.status
            }
        )
    except Exception as e:
        logger.error(f"خطا در بروزرسانی بستانکار: {e}", exc_info=True)


@receiver(post_delete, sender=LoanCreditorInstallment)
def update_creditor_on_installment_delete(sender, instance, **kwargs):
    """هنگام حذف قسط، مبلغ پرداخت‌شده و وضعیت تسویه بستانکار را بروزرسانی کنید"""
    try:
        creditor = instance.creditor
        # ذخیره بستانکار تا منطق save() اجرا شود
        creditor.save()
        
        # ثبت لاگ
        create_activity_log(
            user=None,
            action='delete',
            model_name='LoanCreditorInstallment',
            object_id=instance.id,
            description=f'قسط {instance.installment_number} - {instance.creditor.first_name} {instance.creditor.last_name} حذف شد'
        )
    except Exception as e:
        print(f"خطا در بروزرسانی بستانکار پس از حذف قسط: {e}")