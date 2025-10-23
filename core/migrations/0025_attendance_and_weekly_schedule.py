# Generated migration for Attendance status default and CompanySettings restructuring

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0024_notification'),
    ]

    operations = [
        # Add DayWorkSchedule model
        migrations.CreateModel(
            name='DayWorkSchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day_of_week', models.IntegerField(choices=[(0, 'شنبه'), (1, 'یکشنبه'), (2, 'دوشنبه'), (3, 'سه‌شنبه'), (4, 'چهارشنبه'), (5, 'پنج‌شنبه'), (6, 'جمعه')], verbose_name='روز هفته')),
                ('work_status', models.CharField(choices=[('open', 'باز'), ('closed', 'بسته')], default='open', max_length=10, verbose_name='وضعیت کاری')),
                ('work_start_range_start', models.TimeField(default='07:00', verbose_name='شروع بازه حضور (مثال: 7:00)')),
                ('work_start_range_end', models.TimeField(default='08:00', verbose_name='پایان بازه حضور (مثال: 8:00)')),
                ('work_end', models.TimeField(default='17:00', verbose_name='ساعت پایان کاری')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='آخرین به‌روزرسانی')),
                ('company_settings', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='day_schedules', to='core.companysettings', verbose_name='تنظیمات شرکت')),
            ],
            options={
                'verbose_name': 'جدول کاری روزانه',
                'verbose_name_plural': 'جداول کاری روزانه',
                'ordering': ['day_of_week'],
            },
        ),
        # Modify CompanySettings - Remove old fields
        migrations.RemoveField(
            model_name='companysettings',
            name='standard_work_start',
        ),
        migrations.RemoveField(
            model_name='companysettings',
            name='standard_work_end',
        ),
        migrations.RemoveField(
            model_name='companysettings',
            name='standard_work_hours',
        ),
        # Update Attendance default status
        migrations.AlterField(
            model_name='attendance',
            name='status',
            field=models.CharField(choices=[('present', 'حاضر'), ('absent', 'غایب'), ('leave', 'مرخصی'), ('late', 'تاخیر'), ('incomplete', 'ناقص'), ('early_leave', 'خروج زودهنگام')], default='absent', max_length=20, verbose_name='وضعیت'),
        ),
        # Add unique constraint to DayWorkSchedule
        migrations.AddConstraint(
            model_name='dayworkschedule',
            constraint=models.UniqueConstraint(fields=['company_settings', 'day_of_week'], name='unique_day_schedule'),
        ),
    ]