"""
صفحات ورود سفارشی برای ورود با کد ملی
"""
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.http import HttpResponse
import os
from django.conf import settings

@require_http_methods(["GET", "POST"])
def employee_login(request):
    """
    صفحه ورود کارمندان با کد ملی
    ریدایرکت به داشبورد مناسب بر اساس نقش کاربر
    """
    if request.method == 'POST':
        national_id = request.POST.get('national_id', '')
        password = request.POST.get('password', '')
        
        if not national_id or not password:
            messages.error(request, 'لطفاً کد ملی و پسورد را وارد کنید')
            return render(request, 'login.html', {
                'national_id': national_id,
                'error_message': 'لطفاً کد ملی و پسورد را وارد کنید'
            })
        
        # احراز هویت با کد ملی و پسورد
        user = authenticate(request, username=national_id, password=password)
        
        if user is not None:
            # ورود کاربر
            login(request, user)
            
            # تعیین مقصد بر اساس نقش کاربر
            if hasattr(user, 'profile'):
                role = user.profile.role
                messages.success(request, f'خوش آمدید {user.profile.display_name or user.first_name}')
                
                # ریدایرکت بر اساس نقش (دسترسی‌ها در signals مدیریت می‌شوند)
                if role == 'admin':
                    return redirect('admin:index')
                elif role == 'lawyer':
                    return redirect('lawyer_admin:index')
                elif role == 'employee':
                    return redirect('employee_admin:index')
            
            # مقصد پیش‌فرض - اگر نقش پیدا نشود
            messages.warning(request, 'نقش کاربر تعریف نشده است')
            return redirect('core:index')
        else:
            messages.error(request, 'کد ملی یا پسورد اشتباه است')
            return render(request, 'login.html', {
                'national_id': national_id,
                'error_message': 'کد ملی یا پسورد اشتباه است'
            })
    
    # صفحه ورود (GET)
    return render(request, 'login.html', {
        'title': 'ورود به سیستم'
    })


@login_required(login_url='core:login')
def employee_logout(request):
    """
    خروج از سیستم
    """
    logout(request)
    messages.success(request, 'با موفقیت از سیستم خارج شدید')
    return redirect('core:login')