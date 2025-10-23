"""
Django management command برای ایجاد ادمین با کد ملی
"""
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from core.models import Employee, Branch, UserProfile
import jdatetime


class Command(BaseCommand):
    help = 'ایجاد ادمین با کد ملی 3510670310'

    def add_arguments(self, parser):
        parser.add_argument(
            '--national-id',
            type=str,
            default='3510670310',
            help='کد ملی ادمین (پیش‌فرض: 3510670310)'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='admin@123',
            help='پسورد ادمین (پیش‌فرض: admin@123)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='بروزرسانی ادمین اگر قبلاً وجود داشته باشد'
        )

    def handle(self, *args, **options):
        national_id = options['national_id']
        password = options['password']
        force = options['force']
        
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 60))
        self.stdout.write(self.style.SUCCESS('🔐 ایجاد ادمین سیستم'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        
        # بررسی آیا ادمین قبلاً وجود دارد
        admin_exists = User.objects.filter(username='admin').exists()
        
        if admin_exists and not force:
            admin_user = User.objects.get(username='admin')
            self.stdout.write(self.style.WARNING(f'\n⚠️  کاربر "admin" قبلاً وجود دارد!'))
            self.stdout.write(f'   نام: {admin_user.first_name} {admin_user.last_name}')
            self.stdout.write(f'   ایمیل: {admin_user.email}')
            
            if hasattr(admin_user, 'employee_profile'):
                employee = admin_user.employee_profile
                self.stdout.write(f'   کد ملی فعلی: {employee.national_id}')
            
            self.stdout.write(self.style.ERROR('\n💡 برای بروزرسانی از --force استفاده کنید'))
            return
        
        try:
            if admin_exists and force:
                # بروزرسانی ادمین موجود
                admin_user = User.objects.get(username='admin')
                self.stdout.write('\n📝 بروزرسانی ادمین موجود...')
                admin_user.set_password(password)
                admin_user.save()
                
                # بروزرسانی Employee
                if hasattr(admin_user, 'employee_profile'):
                    employee = admin_user.employee_profile
                    employee.national_id = national_id
                    employee.save()
                    self.stdout.write(self.style.SUCCESS(f'✅ کد ملی به‌روزرسانی شد: {national_id}'))
            else:
                # ایجاد ادمین جدید
                self.stdout.write('\n📝 ایجاد ادمین جدید...')
                
                admin_user = User.objects.create_superuser(
                    username='admin',
                    email='admin@phonix.ir',
                    password=password,
                    first_name='سیستم',
                    last_name='ادمین'
                )
                
                self.stdout.write(self.style.SUCCESS('✅ کاربر "admin" ایجاد شد'))
                
                # ایجاد UserProfile
                profile, _ = UserProfile.objects.get_or_create(
                    user=admin_user,
                    defaults={'role': 'admin'}
                )
                
                # ایجاد شعبه اصلی
                branch, created = Branch.objects.get_or_create(
                    name='دفتر مرکزی',
                    defaults={
                        'code': 'HQ001',
                        'branch_type': 'headquarters',
                        'address': 'تهران - ایران',
                        'city': 'تهران',
                        'province': 'تهران',
                        'phone': '02100000000',
                        'status': 'active'
                    }
                )
                
                if created:
                    self.stdout.write(self.style.SUCCESS('✅ شعبه "دفتر مرکزی" ایجاد شد'))
                
                # ایجاد Employee
                today = jdatetime.date.today()
                employee = Employee.objects.create(
                    user=admin_user,
                    national_id=national_id,
                    branch=branch,
                    job_title='manager',
                    hire_date=today,
                    phone='09000000000',
                    employment_status='active',
                    contract_type='full_time'
                )
                
                self.stdout.write(self.style.SUCCESS('✅ Employee ایجاد شد'))
            
            # نمایش اطلاعات نهایی
            self.stdout.write(self.style.SUCCESS('\n' + '=' * 60))
            self.stdout.write(self.style.SUCCESS('📋 اطلاعات ورود به سیستم:'))
            self.stdout.write(self.style.SUCCESS('=' * 60))
            self.stdout.write(self.style.WARNING(f'کد ملی: {national_id}'))
            self.stdout.write(self.style.WARNING(f'پسورد: {password}'))
            self.stdout.write(self.style.WARNING(f'URL ورود: http://localhost:8000/admin/'))
            self.stdout.write(self.style.SUCCESS('=' * 60))
            self.stdout.write(self.style.SUCCESS('\n✨ ادمین با موفقیت آماده است!\n'))
            
        except Exception as e:
            raise CommandError(f'❌ خطا: {str(e)}')