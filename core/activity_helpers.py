"""
راهنمای ایجاد گزارش‌های فعالیت خودکار
Helper functions for automatic activity reporting
"""
from django.utils import timezone
from django.db.models import Count, Q
from .models import ActivityLog
from datetime import timedelta


def get_user_activity_summary(user, days=7):
    """
    خلاصه فعالیت کاربر برای تعداد روز معین
    Get user activity summary for last N days
    """
    start_date = timezone.now() - timedelta(days=days)
    
    activities = ActivityLog.objects.filter(
        user=user,
        timestamp__gte=start_date
    ).values('action').annotate(count=Count('id'))
    
    summary = {
        'total_actions': sum(item['count'] for item in activities),
        'by_action': {item['action']: item['count'] for item in activities},
        'period_days': days,
        'start_date': start_date,
        'end_date': timezone.now(),
    }
    
    return summary


def get_system_activity_stats(days=7):
    """
    آمار کلی فعالیت سیستم
    Get overall system activity statistics
    """
    start_date = timezone.now() - timedelta(days=days)
    
    logs = ActivityLog.objects.filter(
        timestamp__gte=start_date
    )
    
    stats = {
        'total_actions': logs.count(),
        'by_action': dict(logs.values('action').annotate(count=Count('id')).values_list('action', 'count')),
        'by_model': dict(logs.values('content_type').annotate(count=Count('id')).values_list('content_type', 'count')),
        'by_user': dict(logs.filter(user__isnull=False).values('user__username').annotate(count=Count('id')).values_list('user__username', 'count')),
        'period_days': days,
    }
    
    return stats


def get_employee_daily_activity(employee, date):
    """
    دریافت فعالیت روزانه کارمند
    Get daily activity for specific employee
    """
    user = employee.user
    
    activities = ActivityLog.objects.filter(
        user=user,
        timestamp__date=date
    ).order_by('-timestamp')
    
    formatted_activities = []
    for activity in activities:
        formatted_activities.append({
            'action': activity.get_action_display(),
            'action_key': activity.action,
            'model': activity.content_type,
            'description': activity.object_description,
            'time': activity.timestamp.strftime('%H:%M:%S'),
            'details': activity.details,
        })
    
    return {
        'employee': employee,
        'date': date,
        'activities': formatted_activities,
        'total_actions': len(formatted_activities),
    }


def get_model_changes_today(model_name):
    """
    دریافت تمام تغییرات یک مدل در امروز
    Get all changes to a model today
    """
    today = timezone.now().date()
    
    changes = ActivityLog.objects.filter(
        content_type=model_name,
        timestamp__date=today
    ).order_by('-timestamp')
    
    formatted_changes = []
    for change in changes:
        formatted_changes.append({
            'action': change.get_action_display(),
            'user': change.user.get_full_name() if change.user else 'سیستم',
            'record': change.object_description,
            'time': change.timestamp.strftime('%H:%M:%S'),
            'details': change.details,
        })
    
    return formatted_changes


def get_critical_activities():
    """
    دریافت فعالیت‌های حساس (حذف، تغییر بزرگ)
    Get critical activities (deletions, major changes)
    """
    today = timezone.now().date()
    
    # فعالیت‌های حذف
    deletions = ActivityLog.objects.filter(
        action='delete',
        timestamp__date=today
    ).order_by('-timestamp')
    
    activities = []
    for deletion in deletions:
        activities.append({
            'type': 'حذف',
            'severity': 'high',
            'model': deletion.content_type,
            'record': deletion.object_description,
            'user': deletion.user.get_full_name() if deletion.user else 'نامشخص',
            'time': deletion.timestamp.strftime('%Y/%m/%d %H:%M:%S'),
        })
    
    return activities


def generate_daily_activity_report(date=None):
    """
    ایجاد گزارش فعالیت روزانه
    Generate daily activity report
    """
    if date is None:
        date = timezone.now().date()
    
    activities = ActivityLog.objects.filter(
        timestamp__date=date
    ).order_by('-timestamp')
    
    report = {
        'date': date,
        'total_activities': activities.count(),
        'by_action': {},
        'by_user': {},
        'by_model': {},
        'activities': []
    }
    
    # آماری‌گیری
    for activity in activities:
        # by action
        action_key = activity.get_action_display()
        report['by_action'][action_key] = report['by_action'].get(action_key, 0) + 1
        
        # by user
        user_name = activity.user.get_full_name() if activity.user else 'سیستم'
        report['by_user'][user_name] = report['by_user'].get(user_name, 0) + 1
        
        # by model
        model_name = activity.content_type
        report['by_model'][model_name] = report['by_model'].get(model_name, 0) + 1
    
    # فعالیت‌های تفصیلی
    for activity in activities[:50]:  # آخرین 50 فعالیت
        report['activities'].append({
            'time': activity.timestamp.strftime('%H:%M:%S'),
            'user': activity.user.get_full_name() if activity.user else 'سیستم',
            'action': activity.get_action_display(),
            'model': activity.content_type,
            'record': activity.object_description,
            'ip': activity.ip_address,
        })
    
    return report