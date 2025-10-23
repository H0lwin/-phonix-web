# Generated migration for adding hourly leave support

from django.db import migrations, models
import django_jalali.db.models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0022_leave"),
    ]

    operations = [
        # اضافه کردن فیلد duration_type
        migrations.AddField(
            model_name='leave',
            name='duration_type',
            field=models.CharField(
                choices=[('hourly', 'ساعتی'), ('daily', 'روزانه')],
                default='daily',
                max_length=10,
                verbose_name='نوع مدت'
            ),
        ),
        
        # تغییر نام duration به duration_days
        migrations.RenameField(
            model_name='leave',
            old_name='duration',
            new_name='duration_days',
        ),
        
        # اضافه کردن فیلدهای ساعتی
        migrations.AddField(
            model_name='leave',
            name='date',
            field=django_jalali.db.models.jDateField(
                verbose_name='تاریخ مرخصی',
                blank=True,
                null=True
            ),
        ),
        migrations.AddField(
            model_name='leave',
            name='start_time',
            field=models.TimeField(
                verbose_name='ساعت شروع',
                blank=True,
                null=True
            ),
        ),
        migrations.AddField(
            model_name='leave',
            name='end_time',
            field=models.TimeField(
                verbose_name='ساعت پایان',
                blank=True,
                null=True
            ),
        ),
        migrations.AddField(
            model_name='leave',
            name='duration_hours',
            field=models.FloatField(
                verbose_name='مدت (ساعت)',
                blank=True,
                null=True
            ),
        ),
        
        # تغییر start_date و end_date به اختیاری
        migrations.AlterField(
            model_name='leave',
            name='start_date',
            field=django_jalali.db.models.jDateField(
                verbose_name='تاریخ شروع',
                blank=True,
                null=True
            ),
        ),
        migrations.AlterField(
            model_name='leave',
            name='end_date',
            field=django_jalali.db.models.jDateField(
                verbose_name='تاریخ پایان',
                blank=True,
                null=True
            ),
        ),
    ]