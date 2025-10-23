from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import CaseFile


def is_admin(user):
    """بررسی کاربر ادمین است"""
    if user.is_superuser:
        return True
    if hasattr(user, 'profile') and user.profile.role == 'admin':
        return True
    return False


def is_lawyer(user):
    """بررسی کاربر وکیل است"""
    if hasattr(user, 'profile'):
        return user.profile.role == 'lawyer'
    return False


@login_required
def vekalet_dashboard(request):
    """داشبورد وکالت"""
    if not (is_admin(request.user) or is_lawyer(request.user)):
        raise PermissionDenied("شما اجازه دسترسی به این بخش را ندارید")
    
    if is_admin(request.user):
        cases = CaseFile.objects.all()
    else:
        cases = CaseFile.objects.filter(created_by=request.user)
    
    context = {
        'cases': cases,
        'total_cases': cases.count(),
        'pending_cases': cases.filter(status='pending').count(),
        'in_progress_cases': cases.filter(status='in_progress').count(),
        'completed_cases': cases.filter(status='completed').count(),
        'closed_cases': cases.filter(status='closed').count(),
    }
    
    return render(request, 'vekalet/dashboard.html', context)