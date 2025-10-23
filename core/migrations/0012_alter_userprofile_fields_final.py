# Generated migration to alter UserProfile fields

from django.db import migrations, models
import core.models
import django_jalali.db.models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0011_populate_missing_userprofile_data"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userprofile",
            name="hire_date",
            field=django_jalali.db.models.jDateField(verbose_name="تاریخ استخدام"),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="job_title",
            field=models.CharField(max_length=100, verbose_name="سمت/شغل"),
        ),
        migrations.AlterField(
            model_name="userprofile",
            name="personnel_id",
            field=models.CharField(
                default=core.models.get_unique_personnel_id,
                editable=False,
                max_length=4,
                unique=True,
                verbose_name="شماره پرسنلی",
            ),
        ),
    ]