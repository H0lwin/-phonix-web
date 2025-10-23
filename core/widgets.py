"""
ویجت‌های سفارشی برای فرم‌ها
Custom widgets for forms
"""
from django import forms
from django.utils.html import format_html
from django.utils.numberformat import format as django_format


class CurrencyInput(forms.TextInput):
    """
    ویجت ورودی ارز با فرمت‌سازی خودکار
    Currency input widget with automatic formatting
    """
    template_name = 'widgets/currency_input.html'
    
    def format_value(self, value):
        """
        فرمت‌سازی مقدار برای نمایش
        Format value for display
        """
        if value is None or value == '':
            return value
        
        try:
            formatted = django_format(
                float(value),
                decimal_sep='.',
                thousand_sep='٬',
                force_grouping=True
            )
            return formatted
        except (ValueError, TypeError):
            return value
    
    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['attrs']['class'] = context['widget']['attrs'].get('class', '') + ' currency-input'
        return context


class CurrencyDisplay(forms.TextInput):
    """
    ویجت نمایش ارز (فقط خواندنی)
    Currency display widget (read-only)
    """
    def __init__(self, attrs=None):
        super().__init__(attrs)
        self.attrs['readonly'] = True
        self.attrs['class'] = self.attrs.get('class', '') + ' currency-display'
    
    def format_value(self, value):
        """
        فرمت‌سازی مقدار برای نمایش
        Format value for display
        """
        if value is None or value == '':
            return value
        
        try:
            formatted = django_format(
                float(value),
                decimal_sep='.',
                thousand_sep='٬',
                force_grouping=True
            )
            return formatted
        except (ValueError, TypeError):
            return value


class NumberInput(forms.NumberInput):
    """
    ویجت ورودی عدد با فرمت‌سازی
    Number input widget with formatting
    """
    def format_value(self, value):
        """
        فرمت‌سازی مقدار برای نمایش
        Format value for display
        """
        if value is None or value == '':
            return value
        
        try:
            # فقط برای نمایش فرمت‌سازی می‌کنیم
            formatted = django_format(
                int(float(value)),
                thousand_sep='٬',
                force_grouping=True
            )
            return formatted
        except (ValueError, TypeError):
            return value