# Data migration to populate DayWorkSchedule with initial data

from django.db import migrations
from datetime import time


def populate_day_schedules(apps, schema_editor):
    """پرکردن جداول کاری برای هر روز هفته"""
    CompanySettings = apps.get_model('core', 'CompanySettings')
    DayWorkSchedule = apps.get_model('core', 'DayWorkSchedule')
    
    # دریافت یا ایجاد تنظیمات شرکت
    settings, created = CompanySettings.objects.get_or_create(pk=1)
    
    # تعریف جدول کاری برای هر روز
    # روزهای کاری: شنبه تا چهارشنبه (0-4)
    # روزهای تعطیل: پنج‌شنبه و جمعه (5-6)
    days_config = [
        # (روز، وضعیت، شروع بازه، پایان بازه، پایان کاری)
        (0, 'open', time(7, 0), time(8, 0), time(17, 0)),   # شنبه
        (1, 'open', time(7, 0), time(8, 0), time(17, 0)),   # یکشنبه
        (2, 'open', time(7, 0), time(8, 0), time(17, 0)),   # دوشنبه
        (3, 'open', time(7, 0), time(8, 0), time(17, 0)),   # سه‌شنبه
        (4, 'open', time(7, 0), time(8, 0), time(17, 0)),   # چهارشنبه
        (5, 'closed', time(7, 0), time(8, 0), time(17, 0)), # پنج‌شنبه (تعطیل)
        (6, 'closed', time(7, 0), time(8, 0), time(17, 0)), # جمعه (تعطیل)
    ]
    
    for day_num, status, start_range, end_range, end_time in days_config:
        DayWorkSchedule.objects.get_or_create(
            company_settings=settings,
            day_of_week=day_num,
            defaults={
                'work_status': status,
                'work_start_range_start': start_range,
                'work_start_range_end': end_range,
                'work_end': end_time,
            }
        )


def reverse_populate_day_schedules(apps, schema_editor):
    """حذف داده‌های جدول کاری (برای reverse migration)"""
    DayWorkSchedule = apps.get_model('core', 'DayWorkSchedule')
    DayWorkSchedule.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0025_attendance_and_weekly_schedule'),
    ]

    operations = [
        migrations.RunPython(populate_day_schedules, reverse_populate_day_schedules),
    ]