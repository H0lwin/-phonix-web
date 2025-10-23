"""
Custom authentication backend برای ورود با کد ملی
"""
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from .models import UserProfile


class NationalIDBackend(ModelBackend):
    """
    Backend برای احراز هویت با استفاده از کد ملی
    """
    
    def authenticate(self, request, username=None, password=None):
        """
        کاربر می‌تواند با کد ملی و پسورد وارد شود
        """
        if not username or not password:
            return None
        
        try:
            # سعی کنیم کاربر را با کد ملی پیدا کنیم
            user_profile = UserProfile.objects.get(national_id=username)
            user = user_profile.user
            
            # بررسی کنیم پسورد درست است یا نه
            if user.check_password(password) and user.is_active:
                return user
        except UserProfile.DoesNotExist:
            pass
        
        return None
    
    def get_user(self, user_id):
        """
        دریافت کاربر بر اساس ID
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None