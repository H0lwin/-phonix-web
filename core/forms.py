from django import forms
from .models import Leave, Employee


class LeaveRequestForm(forms.ModelForm):
    """فرم درخواست مرخصی برای وکیلا و کارمندان - ساعتی و روزانه"""
    
    class Meta:
        model = Leave
        fields = ['leave_type', 'duration_type', 'start_date', 'end_date', 'date', 'start_time', 'end_time', 'reason']
        widgets = {
            'leave_type': forms.Select(attrs={
                'class': 'form-control',
            }),
            'duration_type': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_duration_type',
                'onchange': 'updateLeaveFields()',
            }),
            'start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'id': 'id_start_date',
            }),
            'end_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'id': 'id_end_date',
            }),
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'id': 'id_date',
                'style': 'display:none;',
            }),
            'start_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control',
                'id': 'id_start_time',
                'style': 'display:none;',
            }),
            'end_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control',
                'id': 'id_end_time',
                'style': 'display:none;',
            }),
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'دلیل و توضیحات مرخصی',
            }),
        }
        labels = {
            'leave_type': 'نوع مرخصی',
            'duration_type': 'نوع مدت',
            'start_date': 'تاریخ شروع (روزانه)',
            'end_date': 'تاریخ پایان (روزانه)',
            'date': 'تاریخ مرخصی (ساعتی)',
            'start_time': 'ساعت شروع',
            'end_time': 'ساعت پایان',
            'reason': 'دلیل/توضیحات',
        }
    
    def clean(self):
        """اعتبارسنجی فرم"""
        cleaned_data = super().clean()
        duration_type = cleaned_data.get('duration_type')
        
        if duration_type == 'daily':
            start_date = cleaned_data.get('start_date')
            end_date = cleaned_data.get('end_date')
            
            if not start_date or not end_date:
                raise forms.ValidationError("برای مرخصی روزانه باید تاریخ شروع و پایان را وارد کنید.")
            
            if end_date < start_date:
                raise forms.ValidationError("تاریخ پایان نمی‌تواند قبل از تاریخ شروع باشد.")
        
        elif duration_type == 'hourly':
            date = cleaned_data.get('date')
            start_time = cleaned_data.get('start_time')
            end_time = cleaned_data.get('end_time')
            
            if not date or not start_time or not end_time:
                raise forms.ValidationError("برای مرخصی ساعتی باید تاریخ و ساعت شروع/پایان را وارد کنید.")
            
            if end_time <= start_time:
                raise forms.ValidationError("ساعت پایان باید بعد از ساعت شروع باشد.")
        
        return cleaned_data