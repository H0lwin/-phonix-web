from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from core.models import Employee, Attendance, CompanySettings, DayWorkSchedule
from datetime import datetime, time


class Command(BaseCommand):
    """
    دستور برای ایجاد خودکار رکوردهای حضور و غیاب روزانه
    
    کاربرد:
        python manage.py create_daily_attendance
        python manage.py create_daily_attendance --date=2024-01-15
    """
    
    help = 'ایجاد رکوردهای حضور و غیاب برای تمام کارمندان فعال'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=str,
            help='تاریخ برای ایجاد رکوردها (فرمت: YYYY-MM-DD)',
            default=None
        )
    
    def handle(self, *args, **options):
        # تعیین تاریخ
        if options['date']:
            try:
                target_date = datetime.strptime(options['date'], '%Y-%m-%d').date()
            except ValueError:
                self.stdout.write(self.style.ERROR('فرمت تاریخ نادرست است. از YYYY-MM-DD استفاده کنید.'))
                return
        else:
            target_date = timezone.now().date()
        
        # دریافت تنظیمات شرکت
        try:
            company_settings = CompanySettings.objects.first()
            if not company_settings:
                self.stdout.write(self.style.ERROR('تنظیمات شرکت یافت نشد!'))
                return
        except:
            self.stdout.write(self.style.ERROR('خطا در دریافت تنظیمات شرکت!'))
            return
        
        # دریافت روز هفته
        weekday = target_date.weekday()
        # تبدیل از Django weekday (0=دوشنبه) به Persian weekday (0=شنبه)
        persian_weekday = (weekday + 2) % 7
        
        # دریافت جدول کاری این روز
        day_schedule = company_settings.get_day_schedule(persian_weekday)
        
        if not day_schedule:
            self.stdout.write(
                self.style.WARNING(f'جدول کاری برای {target_date.strftime("%Y-%m-%d")} یافت نشد!')
            )
            return
        
        # اگر روز بسته باشد، هیچ رکوردی ایجاد نکن
        if day_schedule.work_status == 'closed':
            self.stdout.write(
                self.style.WARNING(f'{target_date.strftime("%Y-%m-%d")} روز بسته‌ای است.')
            )
            return
        
        # دریافت تمام کارمندان فعال
        active_employees = Employee.objects.filter(employment_status='active')
        
        created_count = 0
        updated_count = 0
        
        for employee in active_employees:
            try:
                # ایجاد یا دریافت رکورد حضور و غیاب
                attendance, created = Attendance.objects.get_or_create(
                    employee=employee,
                    date=target_date,
                    defaults={
                        'status': 'absent',  # پیش‌فرض غایب
                    }
                )
                
                if created:
                    # اگر رکورد جدید است، وضعیت را بر اساس ورود به‌روزرسانی کن
                    attendance.update_status_from_login()
                    attendance.save()
                    created_count += 1
                else:
                    updated_count += 1
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'خطا در ایجاد رکورد برای {employee}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'تکمیل شد! ایجاد شده: {created_count}، موجود: {updated_count}'
            )
        )