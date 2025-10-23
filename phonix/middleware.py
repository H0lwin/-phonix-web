"""
Middleware برای Phonix - هدایت‌های خودکار و کنترل دسترسی
کنترل جامع سطح دسترسی بر اساس نقش کاربر
"""
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from django.contrib.auth import logout
from django.utils.deprecation import MiddlewareMixin
from datetime import datetime


class RoleBasedAccessMiddleware:
    """
    کنترل دسترسی جامع بر اساس نقش کاربر:
    - ادمین: دسترسی کامل به /admin/
    - وکیل: دسترسی فقط به /lawyer-admin/
    - کارمند: دسترسی فقط به /employee-admin/
    
    هر کاربری که سعی کند از مسیری دسترسی ناشناخته استفاده کند، ریدایرکت می‌شود
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # اگر کاربر وارد شده است
        if request.user.is_authenticated:
            if hasattr(request.user, 'profile'):
                role = request.user.profile.role
                path = request.path
                
                # ===== کنترل دسترسی ادمین =====
                if role == 'admin':
                    # ادمین‌ها فقط می‌توانند به /admin/ بروند
                    if path.startswith('/employee-admin/'):
                        return redirect('/admin/')
                    if path.startswith('/lawyer-admin/'):
                        return redirect('/admin/')
                
                # ===== کنترل دسترسی وکیل =====
                elif role == 'lawyer':
                    # وکلا فقط می‌توانند به /lawyer-admin/ بروند
                    if path.startswith('/admin/'):
                        return redirect('/lawyer-admin/')
                    if path.startswith('/employee-admin/'):
                        return redirect('/lawyer-admin/')
                
                # ===== کنترل دسترسی کارمند =====
                elif role == 'employee':
                    # کارمندان فقط می‌توانند به /employee-admin/ بروند
                    if path.startswith('/admin/'):
                        return redirect('/employee-admin/')
                    if path.startswith('/lawyer-admin/'):
                        return redirect('/employee-admin/')
        
        response = self.get_response(request)
        return response


class SessionTimeoutMiddleware(MiddlewareMixin):
    """
    میان‌افزار برای اجرای Timeout Session
    اگر کاربر بیش از SESSION_COOKIE_AGE بدون فعالیت بماند، logout می‌شود
    """
    
    def process_request(self, request):
        # فقط برای کاربران لاگین شده
        if request.user.is_authenticated:
            # آخرین زمان فعالیت را از session دریافت کن
            if '_last_activity' in request.session:
                # بررسی زمان
                from django.conf import settings
                import time
                
                last_activity = request.session['_last_activity']
                current_time = time.time()
                session_timeout = getattr(settings, 'SESSION_COOKIE_AGE', 1800)
                
                # اگر timeout گذشته باشد
                if current_time - last_activity > session_timeout:
                    logout(request)
                    return redirect('core:login')
            
            # زمان فعالیت را به روز کن
            import time
            request.session['_last_activity'] = time.time()
        
        return None