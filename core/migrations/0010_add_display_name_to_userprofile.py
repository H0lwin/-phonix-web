# Generated migration to add display_name field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0009_userprofile_address_userprofile_bank_account_number_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="display_name",
            field=models.CharField(
                default="کاربر جدید", max_length=200, verbose_name="نام و نام خانوادگی"
            ),
        ),
    ]