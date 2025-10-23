#!/usr/bin/env python
"""
اسکریپت تعاملی برای ایجاد و مدیریت کاربر ادمین
سازگار با محیط تولید (Production)
"""
import os
import sys
import django
import getpass
from pathlib import Path

# Django سیٹ اپ
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'phonix.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import UserProfile, Branch, Employee
import jdatetime


class AdminInitializer:
    """کلاس برای مدیریت ایجاد ادمین"""
    
    def __init__(self):
        self.username = None
        self.email = None
        self.password = None
        self.national_id = None
        self.first_name = None
        self.last_name = None
    
    def print_header(self, title):
        """نمایش عنوان"""
        print("\n" + "=" * 70)
        print(f"🔐 {title}")
        print("=" * 70)
    
    def print_success(self, msg):
        """پیام موفقیت"""
        print(f"✅ {msg}")
    
    def print_error(self, msg):
        """پیام خطا"""
        print(f"❌ {msg}")
    
    def print_warning(self, msg):
        """پیام هشدار"""
        print(f"⚠️  {msg}")
    
    def print_info(self, msg):
        """پیام اطلاعات"""
        print(f"ℹ️  {msg}")
    
    def get_input(self, prompt, required=True, default=None, is_password=False):
        """دریافت ورودی از کاربر"""
        while True:
            if default:
                display_prompt = f"➜ {prompt} [{default}]: "
            else:
                display_prompt = f"➜ {prompt}: "
            
            if is_password:
                value = getpass.getpass(display_prompt)
            else:
                value = input(display_prompt).strip()
            
            # استفاده از مقدار پیشفرض
            if not value and default:
                return default
            
            # بررسی فیلد الزامی
            if not value and required:
                self.print_error("این فیلد الزامی است!")
                continue
            
            return value if value else None
    
    def get_yes_no(self, prompt):
        """دریافت پاسخ بله/خیر"""
        while True:
            response = input(f"❓ {prompt} (بله/خیر) [n]: ").strip().lower()
            if response in ['بله', 'yes', 'y']:
                return True
            elif response in ['خیر', 'no', 'n', '']:
                return False
            else:
                self.print_error("لطفاً بله یا خیر وارد کنید")
    
    def check_existing_admin(self):
        """بررسی ادمین موجود"""
        if User.objects.filter(username=self.username).exists():
            user = User.objects.get(username=self.username)
            self.print_warning(f"کاربر '{self.username}' قبلاً وجود دارد")
            print(f"   نام: {user.first_name} {user.last_name}")
            print(f"   ایمیل: {user.email}")
            
            if hasattr(user, 'userprofile'):
                print(f"   نقش: {user.userprofile.get_role_display()}")
            
            return user
        return None
    
    def create_or_update_branch(self):
        """ایجاد یا بازیابی شعبه مرکزی"""
        branch, created = Branch.objects.get_or_create(
            code='HQ-001',
            defaults={
                'name': 'دفتر مرکزی',
                'branch_type': 'headquarters',
                'address': 'تهران - ایران',
                'city': 'تهران',
                'province': 'تهران',
                'postal_code': '0000000000',
                'phone': '02100000000',
                'status': 'active',
                'description': 'دفتر مرکزی شرکت',
            }
        )
        if created:
            self.print_success("شعبه مرکزی ایجاد شد")
        return branch
    
    def create_user(self):
        """ایجاد کاربر جدید"""
        self.print_info("ایجاد کاربر جدید...")
        
        # بررسی نام کاربری
        while True:
            username = self.get_input("نام کاربری", required=True)
            if User.objects.filter(username=username).exists():
                self.print_error(f"کاربر '{username}' قبلاً وجود دارد")
                continue
            self.username = username
            break
        
        # دریافت دیگر اطلاعات
        self.email = self.get_input("ایمیل", required=True)
        self.first_name = self.get_input("نام", required=False, default="سیستم")
        self.last_name = self.get_input("نام خانوادگی", required=False, default="ادمین")
        self.national_id = self.get_input("کد ملی (10 رقم)", required=True)
        
        # دریافت رمز عبور
        while True:
            self.password = self.get_input(
                "رمز عبور (حداقل 8 کاراکتر)",
                required=True,
                is_password=True
            )
            if len(self.password) < 8:
                self.print_error("رمز عبور باید حداقل 8 کاراکتر باشد")
                continue
            
            password_confirm = self.get_input(
                "تایید رمز عبور",
                required=True,
                is_password=True
            )
            if self.password != password_confirm:
                self.print_error("رمز عبورها منطبق نیستند")
                continue
            break
        
        # ایجاد کاربر
        try:
            user = User.objects.create_superuser(
                username=self.username,
                email=self.email,
                password=self.password,
                first_name=self.first_name,
                last_name=self.last_name,
            )
            self.print_success(f"کاربر '{self.username}' ایجاد شد")
            return user
        except Exception as e:
            self.print_error(f"خطا در ایجاد کاربر: {str(e)}")
            return None
    
    def create_profile(self, user):
        """ایجاد یا بروزرسانی پروفایل کاربری"""
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'role': 'admin',
                'national_id': self.national_id,
                'display_name': f"{self.first_name} {self.last_name}",
                'job_title': 'مدیر سیستم',
                'hire_date': jdatetime.date.today().isoformat(),
            }
        )
        
        if created:
            self.print_success("پروفایل کاربری ایجاد شد")
        else:
            profile.national_id = self.national_id
            profile.save()
            self.print_success("پروفایل کاربری بروزرسانی شد")
        
        return profile
    
    def create_employee(self, user, branch):
        """ایجاد یا بروزرسانی رکورد کارمند"""
        employee, created = Employee.objects.get_or_create(
            user=user,
            defaults={
                'national_id': self.national_id,
                'branch': branch,
                'job_title': 'مدیر سیستم',
                'hire_date': jdatetime.date.today(),
                'phone': '09000000000',
                'employment_status': 'active',
                'contract_type': 'full_time',
            }
        )
        
        if created:
            self.print_success("رکورد کارمند ایجاد شد")
        else:
            employee.national_id = self.national_id
            employee.save()
            self.print_success("رکورد کارمند بروزرسانی شد")
        
        return employee
    
    def display_credentials(self, user):
        """نمایش اطلاعات ورود"""
        print("\n" + "=" * 70)
        print("📋 اطلاعات ورود به سیستم")
        print("=" * 70)
        print(f"نام کاربری:  {user.username}")
        print(f"رمز عبور:    {self.password}")
        print(f"ایمیل:       {user.email}")
        print(f"کد ملی:      {self.national_id}")
        print(f"نام:         {user.first_name} {user.last_name}")
        print("=" * 70)
        print("💡 توجه: این اطلاعات را در جایی امن ذخیره کنید")
        print("=" * 70)
    
    def run(self):
        """اجرای برنامه"""
        self.print_header("سیستم مدیریت ادمین - Phonix")
        
        print("""
گزینه‌ها:
  1. ایجاد ادمین جدید
  2. بروزرسانی ادمین موجود
  3. خروج
        """)
        
        choice = self.get_input("انتخاب خود را وارد کنید", required=True)
        
        if choice == '1':
            self._create_new()
        elif choice == '2':
            self._update_existing()
        elif choice == '3':
            print("\n👋 خروج...")
            sys.exit(0)
        else:
            self.print_error("انتخاب نامعتبر است")
            self.run()
    
    def _create_new(self):
        """ایجاد ادمین جدید"""
        self.print_header("ایجاد ادمین جدید")
        
        # ایجاد کاربر
        user = self.create_user()
        if not user:
            return
        
        # ایجاد شعبه
        branch = self.create_or_update_branch()
        
        # ایجاد پروفایل
        self.create_profile(user)
        
        # ایجاد کارمند
        self.create_employee(user, branch)
        
        # نمایش اطلاعات
        self.display_credentials(user)
        
        print("\n✨ ادمین با موفقیت ایجاد شد!")
        
        if self.get_yes_no("آیا می‌خواهید ادمین دیگری ایجاد کنید؟"):
            self.run()
    
    def _update_existing(self):
        """بروزرسانی ادمین موجود"""
        self.print_header("بروزرسانی ادمین موجود")
        
        username = self.get_input("نام کاربری ادمین", required=True)
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.print_error(f"کاربر '{username}' پیدا نشد")
            return
        
        print(f"\n📋 اطلاعات فعلی کاربر '{username}':")
        print(f"   نام: {user.first_name} {user.last_name}")
        print(f"   ایمیل: {user.email}")
        
        # دریافت اطلاعات جدید
        self.username = username
        self.first_name = self.get_input(
            "نام جدید (برای بدون تغییر Enter بزنید)",
            required=False,
            default=user.first_name
        )
        self.last_name = self.get_input(
            "نام خانوادگی جدید (برای بدون تغییر Enter بزنید)",
            required=False,
            default=user.last_name
        )
        self.email = self.get_input(
            "ایمیل جدید (برای بدون تغییر Enter بزنید)",
            required=False,
            default=user.email
        )
        self.national_id = self.get_input(
            "کد ملی جدید (برای بدون تغییر Enter بزنید)",
            required=False,
            default=None
        )
        
        # رمز عبور اختیاری
        if self.get_yes_no("آیا می‌خواهید رمز عبور را تغییر دهید؟"):
            while True:
                self.password = self.get_input(
                    "رمز عبور جدید (حداقل 8 کاراکتر)",
                    required=True,
                    is_password=True
                )
                if len(self.password) < 8:
                    self.print_error("رمز عبور باید حداقل 8 کاراکتر باشد")
                    continue
                
                password_confirm = self.get_input(
                    "تایید رمز عبور",
                    required=True,
                    is_password=True
                )
                if self.password != password_confirm:
                    self.print_error("رمز عبورها منطبق نیستند")
                    continue
                break
            
            user.set_password(self.password)
        
        # بروزرسانی کاربر
        user.first_name = self.first_name
        user.last_name = self.last_name
        user.email = self.email
        user.save()
        self.print_success("اطلاعات کاربر بروزرسانی شد")
        
        # بروزرسانی پروفایل
        if hasattr(user, 'userprofile'):
            profile = user.userprofile
            if self.national_id:
                profile.national_id = self.national_id
            profile.display_name = f"{self.first_name} {self.last_name}"
            profile.save()
            self.print_success("پروفایل بروزرسانی شد")
        
        # نمایش اطلاعات
        if self.password:
            self.display_credentials(user)
        else:
            print("\n" + "=" * 70)
            print("📋 اطلاعات کاربر بروزرسانی شد")
            print("=" * 70)
            print(f"نام کاربری:  {user.username}")
            print(f"ایمیل:       {user.email}")
            print(f"نام:         {user.first_name} {user.last_name}")
            print("=" * 70)
        
        print("\n✨ ادمین با موفقیت بروزرسانی شد!")
        
        if self.get_yes_no("آیا می‌خواهید عملیات دیگری انجام دهید؟"):
            self.run()


def main():
    """تابع اصلی"""
    try:
        initializer = AdminInitializer()
        initializer.run()
    except KeyboardInterrupt:
        print("\n\n👋 عملیات لغو شد")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ خطای غیرمنتظره: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()