# Generated migration to populate missing data

from django.db import migrations
from datetime import datetime
import random


def generate_personnel_id():
    """تولید شماره پرسنلی 4 رقمی رندوم"""
    return str(random.randint(1000, 9999))


def populate_missing_fields(apps, schema_editor):
    """پر کردن فیلدهای خالی"""
    UserProfile = apps.get_model('core', 'UserProfile')
    
    # پر کردن national_id برای کاربران بدون national_id
    users_without_national_id = UserProfile.objects.filter(national_id__isnull=True) | UserProfile.objects.filter(national_id='')
    for idx, user in enumerate(users_without_national_id):
        # تولید یک کد ملی موقتی منحصر به‌فرد
        user.national_id = f"9999{str(idx).zfill(6)}"[-10:]
        user.save()
    
    # پر کردن display_name برای کاربران بدون display_name
    for user in UserProfile.objects.filter(display_name__isnull=True) | UserProfile.objects.filter(display_name=''):
        user.display_name = user.user.get_full_name() or user.user.username
        if not user.display_name:
            user.display_name = 'کاربر جدید'
        user.save()
    
    # پر کردن hire_date برای کاربران بدون hire_date
    for user in UserProfile.objects.filter(hire_date__isnull=True):
        # استفاده از تاریخ ایجاد یا یک تاریخ پیشفرض
        user.hire_date = user.created_at.date() if user.created_at else datetime.now().date()
        user.save()
    
    # پر کردن job_title برای کاربران بدون job_title
    for user in UserProfile.objects.filter(job_title__isnull=True) | UserProfile.objects.filter(job_title=''):
        user.job_title = 'کارمند'
        user.save()
    
    # پر کردن personnel_id برای کاربران بدون personnel_id
    for user in UserProfile.objects.filter(personnel_id__isnull=True) | UserProfile.objects.filter(personnel_id=''):
        while True:
            new_id = generate_personnel_id()
            if not UserProfile.objects.filter(personnel_id=new_id).exists():
                user.personnel_id = new_id
                break
        user.save()


def reverse_populate(apps, schema_editor):
    """بازگردانی تغییرات"""
    # این عملیات غیرقابل برگشت است
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0010_add_display_name_to_userprofile"),
    ]

    operations = [
        migrations.RunPython(populate_missing_fields, reverse_populate),
    ]