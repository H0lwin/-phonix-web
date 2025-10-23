from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
    verbose_name = "سیستم اصلی"
    
    def ready(self):
        """بارگذاری سیگنال‌ها هنگام آغاز برنامه"""
        import core.signals  # noqa
