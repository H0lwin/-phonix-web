"""
تگ‌های قالب برای فرمت‌سازی ارز و اعداد
Template tags for currency and number formatting
"""
from django import template
from django.utils.numberformat import format as django_format
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from decimal import Decimal

register = template.Library()


@register.filter
def currency(value):
    """
    فرمت‌سازی مبلغ با جدا کننده هزارگان فارسی
    Format amount with Persian thousand separator
    
    Usage in template:
        {{ price|currency }}
    """
    if value is None or value == '':
        return '-'
    
    try:
        formatted = django_format(
            float(value),
            decimal_sep='.',
            thousand_sep='٬',
            force_grouping=True
        )
        return formatted
    except (ValueError, TypeError):
        return conditional_escape(value)


@register.filter
def currency_display(value, arg=2):
    """
    فرمت‌سازی مبلغ برای نمایش با تعداد مشخصی اعشار
    Format amount for display with specified decimal places
    
    Usage in template:
        {{ price|currency_display }}
        {{ price|currency_display:0 }}
    """
    if value is None or value == '':
        return '-'
    
    try:
        decimal_places = int(arg) if arg else 2
        formatted = django_format(
            float(value),
            decimal_sep='.',
            thousand_sep='٬',
            force_grouping=True
        )
        return formatted
    except (ValueError, TypeError):
        return conditional_escape(value)


@register.filter
def format_number(value):
    """
    فرمت‌سازی عدد با جدا کننده هزارگان
    Format number with thousand separator
    
    Usage in template:
        {{ quantity|format_number }}
    """
    if value is None or value == '':
        return '-'
    
    try:
        formatted = django_format(
            int(value),
            thousand_sep='٬',
            force_grouping=True
        )
        return formatted
    except (ValueError, TypeError):
        return conditional_escape(value)


@register.filter
def as_currency_html(value):
    """
    فرمت‌سازی ارز به صورت HTML با کلاس‌های مناسب
    Format currency as HTML with appropriate classes
    
    Usage in template:
        {{ price|as_currency_html }}
    """
    if value is None or value == '':
        return '<span class="currency-value">-</span>'
    
    try:
        formatted = django_format(
            float(value),
            decimal_sep='.',
            thousand_sep='٬',
            force_grouping=True
        )
        return mark_safe(f'<span class="currency-value">{formatted}</span>')
    except (ValueError, TypeError):
        return mark_safe(f'<span class="currency-value">{conditional_escape(value)}</span>')


@register.filter
def toman(value):
    """
    فرمت‌سازی مقادیر پولی به تومان با جدا‌کننده هزارگان
    بدون اعشار اگر عدد صحیح باشد
    
    Formats currency values in Toman with thousand separator
    Removes decimals if the value is a whole number
    
    Usage in template:
        {{ price|toman }}
    
    Example:
        {{ 25000000|toman }} -> '۲۵٬۰۰۰٬۰۰۰ تومان'
        {{ 25000000.50|toman }} -> '۲۵٬۰۰۰٬۰۰۰.۵ تومان'
    """
    if value is None or value == '':
        return '-'
    
    try:
        decimal_value = Decimal(str(value))
        
        # اگر عدد صحیح است، اعشار حذف کن
        if decimal_value % 1 == 0:
            value_to_format = int(decimal_value)
        else:
            value_to_format = float(decimal_value)
        
        formatted = django_format(
            value_to_format,
            decimal_sep='.',
            thousand_sep='٬',
            force_grouping=True
        )
        return f"{formatted} تومان"
    except (ValueError, TypeError, ArithmeticError):
        return conditional_escape(value)


@register.filter
def toman_number(value):
    """
    فرمت‌سازی به تومان (فقط مقدار عددی بدون نام واحد)
    
    Formats currency value without currency name
    
    Usage in template:
        {{ price|toman_number }}
    
    Example:
        {{ 25000000|toman_number }} -> '۲۵٬۰۰۰٬۰۰۰'
    """
    if value is None or value == '':
        return '-'
    
    try:
        decimal_value = Decimal(str(value))
        
        if decimal_value % 1 == 0:
            value_to_format = int(decimal_value)
        else:
            value_to_format = float(decimal_value)
        
        formatted = django_format(
            value_to_format,
            decimal_sep='.',
            thousand_sep='٬',
            force_grouping=True
        )
        return formatted
    except (ValueError, TypeError, ArithmeticError):
        return conditional_escape(value)


@register.filter
def toman_html(value):
    """
    فرمت‌سازی مقادیر تومان به صورت HTML
    
    Formats Toman values as HTML with appropriate classes
    
    Usage in template:
        {{ price|toman_html }}
    """
    if value is None or value == '':
        return '<span class="toman-value">-</span>'
    
    try:
        decimal_value = Decimal(str(value))
        
        if decimal_value % 1 == 0:
            value_to_format = int(decimal_value)
        else:
            value_to_format = float(decimal_value)
        
        formatted = django_format(
            value_to_format,
            decimal_sep='.',
            thousand_sep='٬',
            force_grouping=True
        )
        return mark_safe(f'<span class="toman-value">{formatted} <span class="currency-unit">تومان</span></span>')
    except (ValueError, TypeError, ArithmeticError):
        return mark_safe(f'<span class="toman-value">{conditional_escape(value)}</span>')