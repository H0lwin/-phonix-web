from django.urls import path
from . import views
from .auth_views import employee_login, employee_logout

app_name = 'core'

urlpatterns = [
    # Public views
    path('', views.index, name='index'),
    path('login/', employee_login, name='login'),
    path('logout/', employee_logout, name='logout'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('financial-chart/', views.financial_chart, name='financial_chart'),
    path('api/financial-chart/', views.financial_chart_api, name='financial_chart_api'),
    
    # Pages - Attendance & Leave (سابق روت‌ها برای سازگاری)
    path('attendance/', views.attendance_page, name='attendance_page'),
    path('leave-request/', views.leave_request_page, name='leave_request_page'),
    
    # Pages - Attendance & Leave (روت‌های جدید داخل Admin)
    path('lawyer-admin/attendance/', views.attendance_page, name='lawyer_attendance'),
    path('lawyer-admin/leave-request/', views.leave_request_page, name='lawyer_leave_request'),
    path('employee-admin/attendance/', views.attendance_page, name='employee_attendance'),
    path('employee-admin/leave-request/', views.leave_request_page, name='employee_leave_request'),
    
    # API - Attendance
    path('api/check-in/', views.check_in, name='check_in'),
    path('api/check-out/', views.check_out, name='check_out'),
    path('api/attendance-status/', views.get_attendance_status, name='attendance_status'),
    path('api/attendance-history/', views.get_attendance_history, name='attendance_history'),
    
    # API - Health
    path('api/health/', views.health_check, name='health_check'),
]