"""
صفحات ورود سفارشی برای ورود با کد ملی
"""
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
import os

# Fallback login template as string for production environments
LOGIN_TEMPLATE_FALLBACK = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ورود به سیستم - شهر راز</title>
    <style>
        body {
            font-family: Vazirmatn, Tahoma, sans-serif;
            direction: rtl;
            text-align: center;
            padding: 50px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 400px;
            margin: 0 auto;
            padding: 2rem;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            background: white;
        }
        .form-group {
            margin-bottom: 1rem;
            text-align: right;
        }
        label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: bold;
        }
        input {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 1rem;
            box-sizing: border-box;
        }
        button {
            width: 100%;
            padding: 0.75rem;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 4px;
            font-size: 1rem;
            cursor: pointer;
        }
        button:hover {
            background-color: #0056b3;
        }
        .error {
            color: #dc3545;
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
            padding: 0.75rem;
            border-radius: 4px;
            margin-bottom: 1rem;
        }
        .logo {
            color: #007bff;
            margin-bottom: 1rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            <h1>شهر راز</h1>
            <p>ورود به سیستم کارکنان</p>
        </div>
        
        {% if error_message %}
        <div class="error">
            {{ error_message }}
        </div>
        {% endif %}
        
        <form method="post">
            {% csrf_token %}
            <div class="form-group">
                <label for="national_id">کد ملی:</label>
                <input type="text" id="national_id" name="national_id" value="{{ national_id|default:'' }}" required>
            </div>
            
            <div class="form-group">
                <label for="password">رمز عبور:</label>
                <input type="password" id="password" name="password" required>
            </div>
            
            <button type="submit">ورود</button>
        </form>
    </div>
</body>
</html>
"""

@require_http_methods(["GET", "POST"])
def employee_login(request):
    """
    صفحه ورود کارمندان با کد ملی
    ریدایرکت به داشبورد مناسب بر اساس نقش کاربر
    """
    try:
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
    except TemplateDoesNotExist:
        # If template doesn't exist, render the fallback template directly
        from django.template import Context, Template
        
        # Process template with Django template engine
        template = Template(LOGIN_TEMPLATE_FALLBACK)
        context = Context({
            'national_id': getattr(request, 'national_id', ''),
            'error_message': getattr(request, 'error_message', ''),
            'title': 'ورود به سیستم'
        })
        
        html_content = template.render(context)
        return HttpResponse(html_content.encode('utf-8'), content_type="text/html; charset=utf-8")


@login_required(login_url='core:login')
def employee_logout(request):
    """
    خروج از سیستم
    """
    logout(request)
    messages.success(request, 'با موفقیت از سیستم خارج شدید')
    return redirect('core:login')