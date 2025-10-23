#!/usr/bin/env python
"""
اسکریپت ایجاد کاربران نمونه برای تست
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'phonix.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import UserProfile

# حذف کاربران قدیمی (اختیاری)
# User.objects.all().delete()

# ادمین
admin_user, created = User.objects.get_or_create(
    username='H0lwin',
    defaults={
        'email': 'shayanqasmy88@gmail.com',
        'first_name': 'شایان',
        'last_name': 'قاسمی',
        'is_staff': True,
        'is_superuser': True,
    }
)
if created:
    admin_user.set_password('Shayan.1400')
    admin_user.save()

admin_profile, _ = UserProfile.objects.get_or_create(
    user=admin_user,
    defaults={
        'role': 'admin',
        'phone': '09123456789',
        'department': 'مدیریت',
        'bio': 'مدیر کل سیستم',
    }
)

# وکیل
lawyer_user, created = User.objects.get_or_create(
    username='lawyer_1',
    defaults={
        'email': 'lawyer@phonix.com',
        'first_name': 'علی',
        'last_name': 'محمدی',
    }
)
if created:
    lawyer_user.set_password('Lawyer@123')
    lawyer_user.save()

lawyer_profile, _ = UserProfile.objects.get_or_create(
    user=lawyer_user,
    defaults={
        'role': 'lawyer',
        'phone': '09121234567',
        'department': 'حقوقی',
        'bio': 'وکیل دادگستری',
    }
)

# وکیل دوم
lawyer_user2, created = User.objects.get_or_create(
    username='lawyer_2',
    defaults={
        'email': 'lawyer2@phonix.com',
        'first_name': 'فاطمه',
        'last_name': 'احمدی',
    }
)
if created:
    lawyer_user2.set_password('Lawyer@123')
    lawyer_user2.save()

lawyer_profile2, _ = UserProfile.objects.get_or_create(
    user=lawyer_user2,
    defaults={
        'role': 'lawyer',
        'phone': '09129876543',
        'department': 'حقوقی',
        'bio': 'وکیل دادگستری',
    }
)

# کارمند
employee_user, created = User.objects.get_or_create(
    username='employee_1',
    defaults={
        'email': 'employee@phonix.com',
        'first_name': 'رضا',
        'last_name': 'حسنی',
    }
)
if created:
    employee_user.set_password('Employee@123')
    employee_user.save()

employee_profile, _ = UserProfile.objects.get_or_create(
    user=employee_user,
    defaults={
        'role': 'employee',
        'phone': '09131111111',
        'department': 'اداری',
        'bio': 'کارمند اداری',
    }
)

# کارمند دوم
employee_user2, created = User.objects.get_or_create(
    username='employee_2',
    defaults={
        'email': 'employee2@phonix.com',
        'first_name': 'مریم',
        'last_name': 'عزیزی',
    }
)
if created:
    employee_user2.set_password('Employee@123')
    employee_user2.save()

employee_profile2, _ = UserProfile.objects.get_or_create(
    user=employee_user2,
    defaults={
        'role': 'employee',
        'phone': '09132222222',
        'department': 'اداری',
        'bio': 'کارمند اداری',
    }
)

print("✅ کاربران با موفقیت ایجاد شدند!")
print("\n" + "="*60)
print("📋 اطلاعات ورود کاربران:")
print("="*60)
print("\n👨‍💼 ادمین:")
print(f"  یوزرنیم: H0lwin")
print(f"  پسورد: Shayan.1400")
print(f"  لینک: http://127.0.0.1:8000/admin/")
print("\n👨‍⚖️ وکیل 1:")
print(f"  یوزرنیم: lawyer_1")
print(f"  پسورد: Lawyer@123")
print("\n👩‍⚖️ وکیل 2:")
print(f"  یوزرنیم: lawyer_2")
print(f"  پسورد: Lawyer@123")
print("\n👨‍💻 کارمند 1:")
print(f"  یوزرنیم: employee_1")
print(f"  پسورد: Employee@123")
print("\n👩‍💻 کارمند 2:")
print(f"  یوزرنیم: employee_2")
print(f"  پسورد: Employee@123")
print("\n" + "="*60)