from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q, Count
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from datetime import datetime, timedelta, date
from decimal import Decimal
import json
from .models import (
    Income, Expense, LoanCreditor, LoanCreditorInstallment,
    Attendance, Employee, Leave, Loan, LoanBuyer, LoanBuyerStatusHistory
)
from vekalet.models import Consultation, CaseFile
from registry.models import TradeAcquisition, TradePartnership, Company, License
from .forms import LeaveRequestForm

def index(request):
    """صفحه اول - ریدایرکت به لاگین یا داشبورد"""
    # اگر کاربر لاگین شده باشد، به داشبورد مناسب ریدایرکت شود
    if request.user.is_authenticated:
        if hasattr(request.user, 'profile'):
            role = request.user.profile.role
            if role == 'admin':
                return redirect('admin:index')
            elif role == 'lawyer':
                return redirect('lawyer_admin:index')
            elif role == 'employee':
                return redirect('employee_admin:index')
        # اگر نقش پیدا نشود، به صفحه لاگین بروند
        return redirect('core:login')
    
    # اگر کاربر لاگین نشده باشد، به صفحه لاگین ریدایرکت شود
    return redirect('core:login')


@login_required(login_url='core:login')
def dashboard(request):
    """داشبورد - هدایت به رابط مدیریت"""
    return redirect('admin:index')


@login_required(login_url='core:login')
def financial_chart(request):
    """نمودار مالی - تحلیل درآمدها، هزینه‌ها، بستانکاری و سود وام فروخته شده (12 ماه)"""
    # فقط ادمین و کارمندان می‌توانند این صفحه را ببینند
    if not request.user.is_staff and not request.user.is_superuser:
        return redirect('core:dashboard')
    
    context = {
        'title': 'نمودار مالی - 12 ماه',
    }
    return render(request, 'financial_chart.html', context)


@login_required(login_url='core:login')
def financial_chart_api(request):
    """API endpoint برای دریافت داده‌های نمودار مالی - 12 ماه"""
    # فقط ادمین و کارمندان می‌توانند این API را استفاده کنند
    if not request.user.is_staff and not request.user.is_superuser:
        return JsonResponse({'error': 'Forbidden'}, status=403)
    
    # دریافت 12 ماه اخیر
    today = date.today()
    months_data = []
    labels = []
    
    # آرایه‌های داده برای هر ماه
    income_data = []
    consultation_income_data = []
    case_income_data = []
    registry_trade_acquisition_income_data = []  # درآمد بازرگانی اخذ
    registry_trade_partnership_income_data = []  # درآمد بازرگانی مشارکتی
    registry_company_income_data = []  # درآمد ثبت شرکت
    registry_license_income_data = []  # درآمد مجوزها
    expense_data = []
    creditor_paid_data = []
    creditor_unpaid_data = []
    net_profit_data = []
    loan_sale_profit_data = []  # سود فروش وام
    
    # شامل 12 ماه
    for i in range(11, -1, -1):
        # محاسبه ماه و سال
        current_date = today.replace(day=1) - timedelta(days=i*30)
        year = current_date.year
        month = current_date.month
        
        # محدوده زمانی ماه
        month_start = datetime(year, month, 1)
        if month == 12:
            month_end = datetime(year + 1, 1, 1)
        else:
            month_end = datetime(year, month + 1, 1)
        
        # نام ماه برای label
        month_name = ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
                      'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'][month - 1]
        labels.append(f'{month_name} {year}')
        
        # جمع درآمدها از Income مدل
        base_income = Income.objects.filter(
            registration_date__gte=month_start.date(),
            registration_date__lt=month_end.date()
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
        
        # اضافه کردن درآمد از هزینه مشاوره
        # 1. مشاورات پرداخت‌شده یا رایگان کامل
        consultation_income = Consultation.objects.filter(
            consultation_date__gte=month_start,
            consultation_date__lt=month_end,
            payment_status__in=['paid', 'free']  # فقط پرداخت‌شده یا رایگان
        ).aggregate(Sum('consultation_fee'))['consultation_fee__sum'] or Decimal('0')
        
        # 2. مبلغ پرداخت‌شده برای مشاورات جزئی
        partial_consultation_paid = Consultation.objects.filter(
            consultation_date__gte=month_start,
            consultation_date__lt=month_end,
            payment_status='partial'
        ).aggregate(Sum('amount_paid'))['amount_paid__sum'] or Decimal('0')
        
        consultation_income += partial_consultation_paid
        
        # اضافه کردن درآمد از مبلغ قرارداد پرونده‌ها
        case_income = CaseFile.objects.filter(
            case_start_date__gte=month_start.date(),
            case_start_date__lt=month_end.date()
        ).aggregate(Sum('contract_amount'))['contract_amount__sum'] or Decimal('0')
        
        # درآمدهای ثبتی (Registry)
        # 1. درآمد بازرگانی اخذ
        registry_trade_acquisition_income = TradeAcquisition.objects.filter(
            created_at__gte=month_start,
            created_at__lt=month_end
        ).aggregate(Sum('amount_received'))['amount_received__sum'] or Decimal('0')
        
        # 2. درآمد بازرگانی مشارکتی
        registry_trade_partnership_income = TradePartnership.objects.filter(
            created_at__gte=month_start,
            created_at__lt=month_end
        ).aggregate(Sum('amount_received'))['amount_received__sum'] or Decimal('0')
        
        # 3. درآمد شرکت‌ها
        registry_company_income = Company.objects.filter(
            created_at__gte=month_start,
            created_at__lt=month_end
        ).aggregate(Sum('amount_received'))['amount_received__sum'] or Decimal('0')
        
        # 4. درآمد مجوزها
        registry_license_income = License.objects.filter(
            created_at__gte=month_start,
            created_at__lt=month_end
        ).aggregate(Sum('amount_received'))['amount_received__sum'] or Decimal('0')
        
        # جمع کل درآمدهای ثبتی
        total_registry_income = (registry_trade_acquisition_income + 
                                registry_trade_partnership_income + 
                                registry_company_income + 
                                registry_license_income)
        
        # جمع کل درآمدها
        total_income = base_income + consultation_income + case_income + total_registry_income
        income_data.append(int(total_income))
        consultation_income_data.append(int(consultation_income))
        case_income_data.append(int(case_income))
        registry_trade_acquisition_income_data.append(int(registry_trade_acquisition_income))
        registry_trade_partnership_income_data.append(int(registry_trade_partnership_income))
        registry_company_income_data.append(int(registry_company_income))
        registry_license_income_data.append(int(registry_license_income))
        
        # جمع هزینه‌ها
        total_expense = Expense.objects.filter(
            registration_date__gte=month_start.date(),
            registration_date__lt=month_end.date()
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
        expense_data.append(int(total_expense))
        
        # بستانکاری پرداخت‌شده (پرداخت‌شده در این ماه)
        creditor_paid = LoanCreditorInstallment.objects.filter(
            payment_date__gte=month_start.date(),
            payment_date__lt=month_end.date(),
            payment_date__isnull=False
        ).aggregate(Sum('paid_amount'))['paid_amount__sum'] or Decimal('0')
        creditor_paid_data.append(int(creditor_paid))
        
        # بستانکاری پرداخت‌نشده (ایجاد شده در این ماه، هنوز پرداخت‌نشده)
        creditor_unpaid = LoanCreditorInstallment.objects.filter(
            created_at__gte=month_start,
            created_at__lt=month_end,
            payment_date__isnull=True
        ).aggregate(Sum('paid_amount'))['paid_amount__sum'] or Decimal('0')
        creditor_unpaid_data.append(int(creditor_unpaid))
        
        # سود فروش وام: قیمت فروش - قیمت خرید
        # فقط برای خریداران تکمیل‌شده (completed)
        loan_sale_profit = Decimal('0')
        completed_buyers = LoanBuyer.objects.filter(
            current_status='completed',
            created_at__gte=month_start,
            created_at__lt=month_end
        )
        for buyer in completed_buyers:
            if buyer.loan and buyer.loan.purchase_rate and buyer.sale_price:
                profit = buyer.sale_price - buyer.loan.purchase_rate
                loan_sale_profit += profit
        loan_sale_profit_data.append(int(loan_sale_profit))
        
        # سود خالص (شامل سود فروش وام)
        profit = int(total_income) + int(loan_sale_profit) - int(total_expense) - int(creditor_paid)
        net_profit_data.append(profit)
    
    # جمع کل 12 ماه
    total_income_12m = sum(income_data)
    total_consultation_income_12m = sum(consultation_income_data)
    total_case_income_12m = sum(case_income_data)
    total_registry_trade_acquisition_12m = sum(registry_trade_acquisition_income_data)
    total_registry_trade_partnership_12m = sum(registry_trade_partnership_income_data)
    total_registry_company_12m = sum(registry_company_income_data)
    total_registry_license_12m = sum(registry_license_income_data)
    total_expense_12m = sum(expense_data)
    total_creditor_paid_12m = sum(creditor_paid_data)
    total_creditor_unpaid_12m = sum(creditor_unpaid_data)
    total_loan_sale_profit_12m = sum(loan_sale_profit_data)
    total_net_profit_12m = sum(net_profit_data)
    
    return JsonResponse({
        'summary': {
            'total_income': total_income_12m,
            'total_consultation_income': total_consultation_income_12m,
            'total_case_income': total_case_income_12m,
            'total_registry_trade_acquisition': total_registry_trade_acquisition_12m,
            'total_registry_trade_partnership': total_registry_trade_partnership_12m,
            'total_registry_company': total_registry_company_12m,
            'total_registry_license': total_registry_license_12m,
            'total_expense': total_expense_12m,
            'total_creditor_paid': total_creditor_paid_12m,
            'total_creditor_unpaid': total_creditor_unpaid_12m,
            'total_loan_sale_profit': total_loan_sale_profit_12m,
            'net_profit': total_net_profit_12m,
            'period': '12 ماه اخیر'
        },
        'labels': labels,
        'datasets': [
            {
                'label': 'درآمدها (کل)',
                'data': income_data,
                'borderColor': 'rgba(46, 204, 113, 1)',
                'backgroundColor': 'rgba(46, 204, 113, 0.1)',
                'borderWidth': 2,
                'tension': 0.3,
                'fill': True,
                'pointRadius': 4,
                'pointHoverRadius': 6
            },
            {
                'label': 'درآمد مشاورات',
                'data': consultation_income_data,
                'borderColor': 'rgba(52, 211, 153, 1)',
                'backgroundColor': 'rgba(52, 211, 153, 0.1)',
                'borderWidth': 2,
                'tension': 0.3,
                'fill': False,
                'pointRadius': 3,
                'pointHoverRadius': 5,
                'borderDash': [5, 5]
            },
            {
                'label': 'درآمد پرونده‌ها',
                'data': case_income_data,
                'borderColor': 'rgba(34, 197, 94, 1)',
                'backgroundColor': 'rgba(34, 197, 94, 0.1)',
                'borderWidth': 2,
                'tension': 0.3,
                'fill': False,
                'pointRadius': 3,
                'pointHoverRadius': 5,
                'borderDash': [5, 5]
            },
            {
                'label': 'درآمد بازرگانی اخذ',
                'data': registry_trade_acquisition_income_data,
                'borderColor': 'rgba(230, 126, 34, 1)',
                'backgroundColor': 'rgba(230, 126, 34, 0.1)',
                'borderWidth': 2,
                'tension': 0.3,
                'fill': False,
                'pointRadius': 3,
                'pointHoverRadius': 5,
                'borderDash': [5, 5]
            },
            {
                'label': 'درآمد بازرگانی مشارکتی',
                'data': registry_trade_partnership_income_data,
                'borderColor': 'rgba(189, 195, 199, 1)',
                'backgroundColor': 'rgba(189, 195, 199, 0.1)',
                'borderWidth': 2,
                'tension': 0.3,
                'fill': False,
                'pointRadius': 3,
                'pointHoverRadius': 5,
                'borderDash': [5, 5]
            },
            {
                'label': 'درآمد شرکت‌ها',
                'data': registry_company_income_data,
                'borderColor': 'rgba(192, 57, 43, 1)',
                'backgroundColor': 'rgba(192, 57, 43, 0.1)',
                'borderWidth': 2,
                'tension': 0.3,
                'fill': False,
                'pointRadius': 3,
                'pointHoverRadius': 5,
                'borderDash': [5, 5]
            },
            {
                'label': 'درآمد مجوزها',
                'data': registry_license_income_data,
                'borderColor': 'rgba(127, 140, 141, 1)',
                'backgroundColor': 'rgba(127, 140, 141, 0.1)',
                'borderWidth': 2,
                'tension': 0.3,
                'fill': False,
                'pointRadius': 3,
                'pointHoverRadius': 5,
                'borderDash': [5, 5]
            },
            {
                'label': 'هزینه‌ها',
                'data': expense_data,
                'borderColor': 'rgba(231, 76, 60, 1)',
                'backgroundColor': 'rgba(231, 76, 60, 0.1)',
                'borderWidth': 2,
                'tension': 0.3,
                'fill': True,
                'pointRadius': 4,
                'pointHoverRadius': 6
            },
            {
                'label': 'بستانکاری پرداخت‌شده',
                'data': creditor_paid_data,
                'borderColor': 'rgba(52, 152, 219, 1)',
                'backgroundColor': 'rgba(52, 152, 219, 0.1)',
                'borderWidth': 2,
                'tension': 0.3,
                'fill': True,
                'pointRadius': 4,
                'pointHoverRadius': 6
            },
            {
                'label': 'بستانکاری معوق',
                'data': creditor_unpaid_data,
                'borderColor': 'rgba(241, 196, 15, 1)',
                'backgroundColor': 'rgba(241, 196, 15, 0.1)',
                'borderWidth': 2,
                'tension': 0.3,
                'fill': True,
                'pointRadius': 4,
                'pointHoverRadius': 6
            },
            {
                'label': 'سود فروش وام',
                'data': loan_sale_profit_data,
                'borderColor': 'rgba(155, 89, 182, 1)',
                'backgroundColor': 'rgba(155, 89, 182, 0.1)',
                'borderWidth': 2,
                'tension': 0.3,
                'fill': True,
                'pointRadius': 4,
                'pointHoverRadius': 6
            },
            {
                'label': 'سود خالص',
                'data': net_profit_data,
                'borderColor': 'rgba(26, 188, 156, 1)',
                'backgroundColor': 'rgba(26, 188, 156, 0.1)',
                'borderWidth': 2,
                'tension': 0.3,
                'fill': True,
                'pointRadius': 4,
                'pointHoverRadius': 6
            },
        ]
    })


@login_required(login_url='core:login')
@require_http_methods(["POST"])
def check_in(request):
    """ثبت ورود کارمند یا وکیل"""
    try:
        # فقط کارمند و وکیل می‌توانند ورود کنند
        if not hasattr(request.user, 'profile'):
            return JsonResponse({
                'success': False,
                'message': 'کاربر پروفایل ندارد'
            }, status=400)
        
        # پیدا کردن یا ایجاد کارمند
        try:
            employee, created = Employee.objects.get_or_create(user=request.user)
            # اگر نو ایجاد شد، اطلاعات را از UserProfile پر کنیم
            if created and hasattr(request.user, 'profile'):
                profile = request.user.profile
                employee.national_id = profile.national_id
                employee.phone = profile.phone
                employee.birth_date = profile.birth_date
                employee.gender = profile.gender
                employee.address = profile.address
                employee.branch = profile.branch
                employee.personnel_id = profile.personnel_id
                employee.job_title = 'lawyer' if profile.role == 'lawyer' else 'other'
                employee.contract_type = profile.contract_type
                employee.employment_status = profile.employment_status
                employee.hire_date = profile.hire_date
                employee.base_salary = profile.base_salary
                employee.benefits = profile.benefits
                employee.payment_method = profile.payment_method
                employee.bank_account_number = profile.bank_account_number
                employee.insurance_info = profile.insurance_info
                employee.education = profile.education
                employee.profile_picture = profile.profile_picture
                employee.save()
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'خطا در بارگذاری اطلاعات: {str(e)}'
            }, status=400)
        
        # چک کردن اینکه آیا امروز قبلاً ورود کرده است
        today = date.today()
        existing = Attendance.objects.filter(
            employee=employee,
            date=today
        ).first()
        
        if existing:
            if existing.check_out:
                # امروز ورود و خروج انجام داده است
                return JsonResponse({
                    'success': False,
                    'message': 'شما امروز قبلاً خروج کرده‌اید. فردا می‌توانید دوباره ورود کنید.'
                }, status=400)
            else:
                # ورود کرده‌ است ولی خروج نکرده است
                return JsonResponse({
                    'success': False,
                    'message': 'شما امروز قبلاً ورود کرده‌اید. ابتدا باید خروج کنید.'
                }, status=400)
        
        # ایجاد رکورد ورود جدید
        now = datetime.now()
        attendance = Attendance.objects.create(
            employee=employee,
            date=today,
            check_in=now.time()
        )
        
        return JsonResponse({
            'success': True,
            'message': '✅ ورود موفقیت‌آمیز!',
            'check_in': now.strftime('%H:%M:%S')
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'خطا: {str(e)}'
        }, status=500)


@login_required(login_url='core:login')
@require_http_methods(["POST"])
def check_out(request):
    """ثبت خروج کارمند یا وکیل"""
    try:
        # فقط کارمند و وکیل می‌توانند خروج کنند
        if not hasattr(request.user, 'profile'):
            return JsonResponse({
                'success': False,
                'message': 'کاربر پروفایل ندارد'
            }, status=400)
        
        # پیدا کردن یا ایجاد کارمند
        try:
            employee, created = Employee.objects.get_or_create(user=request.user)
            # اگر نو ایجاد شد، اطلاعات را از UserProfile پر کنیم
            if created and hasattr(request.user, 'profile'):
                profile = request.user.profile
                employee.national_id = profile.national_id
                employee.phone = profile.phone
                employee.birth_date = profile.birth_date
                employee.gender = profile.gender
                employee.address = profile.address
                employee.branch = profile.branch
                employee.personnel_id = profile.personnel_id
                employee.job_title = 'lawyer' if profile.role == 'lawyer' else 'other'
                employee.contract_type = profile.contract_type
                employee.employment_status = profile.employment_status
                employee.hire_date = profile.hire_date
                employee.base_salary = profile.base_salary
                employee.benefits = profile.benefits
                employee.payment_method = profile.payment_method
                employee.bank_account_number = profile.bank_account_number
                employee.insurance_info = profile.insurance_info
                employee.education = profile.education
                employee.profile_picture = profile.profile_picture
                employee.save()
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'خطا در بارگذاری اطلاعات: {str(e)}'
            }, status=400)
        
        # چک کردن رکورد امروز
        today = date.today()
        attendance = Attendance.objects.filter(
            employee=employee,
            date=today
        ).first()
        
        if not attendance:
            return JsonResponse({
                'success': False,
                'message': 'شما امروز ورود نکرده‌اید.'
            }, status=400)
        
        if attendance.check_out:
            return JsonResponse({
                'success': False,
                'message': 'شما امروز قبلاً خروج کرده‌اید.'
            }, status=400)
        
        # ثبت خروج
        now = datetime.now()
        attendance.check_out = now.time()
        attendance.calculate_work_duration()
        attendance.save()
        
        return JsonResponse({
            'success': True,
            'message': '✅ خروج موفقیت‌آمیز!',
            'check_out': now.strftime('%H:%M:%S'),
            'work_duration': attendance.get_work_duration_display(),
            'overtime': attendance.get_overtime_display()
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'خطا: {str(e)}'
        }, status=500)


@login_required(login_url='core:login')
@require_http_methods(["GET"])
def get_attendance_status(request):
    """دریافت وضعیت حضور و غیاب امروز"""
    try:
        # پیدا کردن یا ایجاد کارمند
        try:
            employee, created = Employee.objects.get_or_create(user=request.user)
            # اگر نو ایجاد شد، اطلاعات را از UserProfile پر کنیم
            if created and hasattr(request.user, 'profile'):
                profile = request.user.profile
                employee.national_id = profile.national_id
                employee.phone = profile.phone
                employee.birth_date = profile.birth_date
                employee.gender = profile.gender
                employee.address = profile.address
                employee.branch = profile.branch
                employee.personnel_id = profile.personnel_id
                employee.job_title = 'lawyer' if profile.role == 'lawyer' else 'other'
                employee.contract_type = profile.contract_type
                employee.employment_status = profile.employment_status
                employee.hire_date = profile.hire_date
                employee.base_salary = profile.base_salary
                employee.benefits = profile.benefits
                employee.payment_method = profile.payment_method
                employee.bank_account_number = profile.bank_account_number
                employee.insurance_info = profile.insurance_info
                employee.education = profile.education
                employee.profile_picture = profile.profile_picture
                employee.save()
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'خطا در بارگذاری اطلاعات: {str(e)}'
            }, status=400)
        
        today = date.today()
        attendance = Attendance.objects.filter(
            employee=employee,
            date=today
        ).first()
        
        # وضعیت دکمه‌ها
        show_check_in = True
        show_check_out = False
        status_text = '❌ شما هنوز ورود نکرده‌اید'
        
        if attendance:
            if attendance.check_out:
                # خروج کرده است
                show_check_in = False
                show_check_out = False
                status_text = f'✅ امروز کار تمام شد\nورود: {attendance.check_in}\nخروج: {attendance.check_out}\nکل ساعات: {attendance.get_work_duration_display()}'
            else:
                # ورود کرده ولی خروج نکرده است
                show_check_in = False
                show_check_out = True
                status_text = f'🔵 در حال کار\nورود: {attendance.check_in}\nمدت کار: محاسبه می‌شود...'
        
        return JsonResponse({
            'success': True,
            'show_check_in': show_check_in,
            'show_check_out': show_check_out,
            'status_text': status_text,
            'has_attendance': attendance is not None
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'خطا: {str(e)}'
        }, status=500)


@login_required(login_url='core:login')
@require_http_methods(["GET"])
def get_attendance_history(request):
    """دریافت تاریخچه حضور ۷ روز اخیر"""
    try:
        # پیدا کردن یا ایجاد کارمند
        try:
            employee, created = Employee.objects.get_or_create(user=request.user)
            # اگر نو ایجاد شد، اطلاعات را از UserProfile پر کنیم
            if created and hasattr(request.user, 'profile'):
                profile = request.user.profile
                employee.national_id = profile.national_id
                employee.phone = profile.phone
                employee.birth_date = profile.birth_date
                employee.gender = profile.gender
                employee.address = profile.address
                employee.branch = profile.branch
                employee.personnel_id = profile.personnel_id
                employee.job_title = 'lawyer' if profile.role == 'lawyer' else 'other'
                employee.contract_type = profile.contract_type
                employee.employment_status = profile.employment_status
                employee.hire_date = profile.hire_date
                employee.base_salary = profile.base_salary
                employee.benefits = profile.benefits
                employee.payment_method = profile.payment_method
                employee.bank_account_number = profile.bank_account_number
                employee.insurance_info = profile.insurance_info
                employee.education = profile.education
                employee.profile_picture = profile.profile_picture
                employee.save()
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'خطا در بارگذاری اطلاعات: {str(e)}'
            }, status=400)
        
        # ۷ روز اخیر
        today = date.today()
        start_date = today - timedelta(days=7)
        
        records = Attendance.objects.filter(
            employee=employee,
            date__gte=start_date,
            date__lte=today
        ).order_by('-date')
        
        # محاسبه آمار
        total_days = records.exclude(check_in__isnull=True).count()
        total_work_minutes = records.aggregate(Sum('work_duration'))['work_duration__sum'] or 0
        total_overtime_minutes = records.aggregate(Sum('overtime_duration'))['overtime_duration__sum'] or 0
        
        total_hours = total_work_minutes // 60
        total_mins = total_work_minutes % 60
        overtime_hours = total_overtime_minutes // 60
        overtime_mins = total_overtime_minutes % 60
        
        # فرمت کردن داده‌ها
        data = []
        for record in records:
            status = '❌ ناقص'
            if record.check_out:
                status = '✅ تکمیل'
            elif record.check_in:
                status = '🔵 در حال کار'
            
            data.append({
                'date': record.date.strftime('%Y-%m-%d'),
                'check_in': record.check_in.strftime('%H:%M') if record.check_in else '-',
                'check_out': record.check_out.strftime('%H:%M') if record.check_out else '-',
                'work_duration': record.get_work_duration_display(),
                'overtime': record.get_overtime_display(),
                'status': status
            })
        
        return JsonResponse({
            'success': True,
            'records': data,
            'stats': {
                'total_days': total_days,
                'total_hours': f'{total_hours:02d}:{total_mins:02d}',
                'total_overtime': f'{overtime_hours:02d}:{overtime_mins:02d}'
            }
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'خطا: {str(e)}'
        }, status=500)


@require_http_methods(["GET"])
def health_check(request):
    """بررسی سلامت سیستم"""
    return JsonResponse({
        'status': 'موفق',
        'message': 'سرور فونیکس در حال اجراست!'
    })

def page_not_found(request, exception):
    """صفحه 404"""
    return render(request, 'error.html', {'error': 'صفحه یافت نشد', 'status_code': 404}, status=404)

def server_error(request):
    """صفحه خطای سرور"""
    return render(request, 'error.html', {'error': 'خطای سرور', 'status_code': 500}, status=500)


# ============================================
# صفحات حضور و غیاب و مرخصی برای وکیل/کارمند
# ============================================

@login_required(login_url='core:login')
def attendance_page(request):
    """صفحه حضور و غیاب - نمایش وضعیت و دکمه‌های ورود/خروج"""
    try:
        # بررسی دسترسی - فقط وکیل و کارمند (بدون ادمین)
        if request.user.is_superuser:
            messages.error(request, 'ادمین به حضور و غیاب نیاز ندارد.')
            return redirect('admin:index')
        
        if not hasattr(request.user, 'profile') or request.user.profile.role not in ['lawyer', 'employee']:
            messages.error(request, 'دسترسی رد شد.')
            return redirect('admin:index')
        
        # پیدا کردن یا ایجاد کارمند برای وکیل و کارمند
        try:
            employee, created = Employee.objects.get_or_create(user=request.user)
            # اگر نو ایجاد شد، اطلاعات را از UserProfile پر کنیم
            if created and hasattr(request.user, 'profile'):
                profile = request.user.profile
                employee.national_id = profile.national_id
                employee.phone = profile.phone
                employee.birth_date = profile.birth_date
                employee.gender = profile.gender
                employee.address = profile.address
                employee.branch = profile.branch
                employee.personnel_id = profile.personnel_id
                employee.job_title = 'lawyer' if profile.role == 'lawyer' else 'other'
                employee.contract_type = profile.contract_type
                employee.employment_status = profile.employment_status
                employee.hire_date = profile.hire_date
                employee.base_salary = profile.base_salary
                employee.benefits = profile.benefits
                employee.payment_method = profile.payment_method
                employee.bank_account_number = profile.bank_account_number
                employee.insurance_info = profile.insurance_info
                employee.education = profile.education
                employee.profile_picture = profile.profile_picture
                employee.save()
        except Exception as e:
            messages.error(request, f'خطا در بارگذاری اطلاعات: {str(e)}')
            return redirect('admin:index')
        
        today = date.today()
        
        # بررسی وضعیت امروز
        attendance = Attendance.objects.filter(
            employee=employee,
            date=today
        ).first()
        
        # جدول ۳۰ روز اخیر
        thirty_days_ago = today - timedelta(days=30)
        attendance_history = Attendance.objects.filter(
            employee=employee,
            date__gte=thirty_days_ago
        ).order_by('-date')
        
        # وضعیت دکمه‌ها
        can_check_in = True
        can_check_out = False
        
        if attendance:
            if attendance.check_in and not attendance.check_out:
                # ورود کرده ولی خروج نکرده
                can_check_in = False
                can_check_out = True
            elif attendance.check_in and attendance.check_out:
                # خروج کرده - نمی‌تواند دوباره ورود کند
                can_check_in = False
                can_check_out = False
        
        context = {
            'title': 'حضور و غیاب',
            'employee': employee,
            'today': today,
            'attendance': attendance,
            'attendance_history': attendance_history,
            'can_check_in': can_check_in,
            'can_check_out': can_check_out,
        }
        
        return render(request, 'attendance_page.html', context)
    
    except Exception as e:
        messages.error(request, f'خطا: {str(e)}')
        return redirect('admin:index')


@login_required(login_url='core:login')
def leave_request_page(request):
    """صفحه درخواست مرخصی"""
    try:
        # بررسی دسترسی - فقط وکیل و کارمند (بدون ادمین)
        if request.user.is_superuser:
            messages.error(request, 'ادمین به درخواست مرخصی نیاز ندارد.')
            return redirect('admin:index')
        
        if not hasattr(request.user, 'profile') or request.user.profile.role not in ['lawyer', 'employee']:
            messages.error(request, 'دسترسی رد شد.')
            return redirect('admin:index')
        
        # پیدا کردن یا ایجاد کارمند برای وکیل و کارمند
        try:
            employee, created = Employee.objects.get_or_create(user=request.user)
            # اگر نو ایجاد شد، اطلاعات را از UserProfile پر کنیم
            if created and hasattr(request.user, 'profile'):
                profile = request.user.profile
                employee.national_id = profile.national_id
                employee.phone = profile.phone
                employee.birth_date = profile.birth_date
                employee.gender = profile.gender
                employee.address = profile.address
                employee.branch = profile.branch
                employee.personnel_id = profile.personnel_id
                employee.job_title = 'lawyer' if profile.role == 'lawyer' else 'other'
                employee.contract_type = profile.contract_type
                employee.employment_status = profile.employment_status
                employee.hire_date = profile.hire_date
                employee.base_salary = profile.base_salary
                employee.benefits = profile.benefits
                employee.payment_method = profile.payment_method
                employee.bank_account_number = profile.bank_account_number
                employee.insurance_info = profile.insurance_info
                employee.education = profile.education
                employee.profile_picture = profile.profile_picture
                employee.save()
        except Exception as e:
            messages.error(request, f'خطا در بارگذاری اطلاعات: {str(e)}')
            return redirect('admin:index')
        
        # دریافت درخواست‌های مرخصی خودش
        leaves = Leave.objects.filter(employee=employee).order_by('-created_at')
        
        if request.method == 'POST':
            form = LeaveRequestForm(request.POST)
            if form.is_valid():
                leave = form.save(commit=False)
                leave.employee = employee
                leave.save()
                messages.success(request, '✅ درخواست مرخصی با موفقیت ثبت شد. منتظر تایید ادمین باشید.')
                return redirect('core:leave_request_page')
        else:
            form = LeaveRequestForm()
        
        context = {
            'title': 'درخواست مرخصی',
            'form': form,
            'leaves': leaves,
            'employee': employee,
        }
        
        return render(request, 'leave_request_page.html', context)
    
    except Exception as e:
        messages.error(request, f'خطا: {str(e)}')
        return redirect('admin:index')
