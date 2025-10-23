"""
ابزارهای فرمت‌سازی و نمایش داده‌های سیستم
Formatting and display utilities for the system
"""
from django.utils.numberformat import format as django_format
from decimal import Decimal


def format_toman(value):
    """
    فرمت‌سازی مقادیر پولی به تومان با جدا‌کننده هزارگان
    بدون اعشار اگر عدد صحیح باشد
    
    Formats currency values in Toman with thousand separator
    Removes decimals if the value is a whole number
    
    Example:
        format_toman(25000000.0) -> '۲۵٬۰۰۰٬۰۰۰ ریال'
        format_toman(25000000.50) -> '۲۵٬۰۰۰٬۰۰۰.۵ ریال'
    """
    if value is None or value == '':
        return '-'
    
    try:
        # تبدیل به Decimal برای دقیق‌تری بهتر
        decimal_value = Decimal(str(value))
        
        # اگر عدد صحیح است، اعشار حذف کن
        if decimal_value % 1 == 0:
            value_to_format = int(decimal_value)
        else:
            # اگر اعشار دارد، ۲ رقم اعشار نگه دار
            value_to_format = float(decimal_value)
        
        # استفاده از تابع فرمت‌سازی Django برای جداکنندگی هزارگان
        formatted = django_format(
            value_to_format,
            decimal_sep='.',
            thousand_sep='٬',
            force_grouping=True
        )
        
        return f"{formatted} تومان"
    except (ValueError, TypeError, ArithmeticError):
        return str(value)


def format_amount_toman(value, include_currency=True):
    """
    فرمت‌سازی مبلغ به تومان
    فقط مقدار عددی بدون نام واحد
    
    Formats amount in Toman (only numeric value)
    """
    if value is None or value == '':
        return '-'
    
    try:
        decimal_value = Decimal(str(value))
        
        # اگر عدد صحیح است
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
        
        if include_currency:
            return f"{formatted} تومان"
        return formatted
    except (ValueError, TypeError, ArithmeticError):
        return str(value)


def format_currency(value):
    """
    فرمت‌سازی اعداد مالی با جدا کننده هزارگان
    Formats currency/amount with thousand separator
    
    Example:
        format_currency(1500000.5) -> '۱٬۵۰۰٬۰۰۰.۵۰'
    """
    return format_toman(value)


def format_amount_display(value, decimal_places=0):
    """
    فرمت‌سازی مبلغ برای نمایش بدون اعشار
    Formats amount for display without decimals (Toman)
    """
    if value is None or value == '':
        return '-'
    
    try:
        decimal_value = Decimal(str(value))
        value_to_format = int(decimal_value)
        
        return django_format(
            value_to_format,
            decimal_sep='.',
            thousand_sep='٬',
            force_grouping=True
        )
    except (ValueError, TypeError, ArithmeticError):
        return str(value)


def format_number_with_thousand_sep(value):
    """
    فرمت‌سازی اعداد با جدا کننده هزارگان
    Formats numbers with Persian thousand separator (٬)
    
    Example:
        format_number_with_thousand_sep(1500000.50) -> '۱٬۵۰۰٬۰۰۰.۵'
    """
    if value is None:
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
        return str(value)