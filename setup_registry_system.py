#!/usr/bin/env python
"""
سیستم ثبتی خدمات - تنظیم داده‌های نمونه
Registry System - Sample Data Setup
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'phonix.settings')
django.setup()

from registry.models import (
    IdentityDocuments,
    ContactInfo,
    License,
    TradeAcquisition,
    TradePartnership,
    Company,
)
from django.contrib.auth.models import User

def create_sample_documents():
    """ایجاد مدارک نمونه"""
    print("🔹 ایجاد مدارک هویتی نمونه...")
    
    docs = []
    sample_data = [
        {
            'first_name': 'علی',
            'last_name': 'احمدی',
            'national_id': '0012345671',
            'certificate_number': '123456',
            'birth_date': '1370-05-15',
            'birth_place': 'تهران',
        },
        {
            'first_name': 'فاطمه',
            'last_name': 'محمدی',
            'national_id': '0012345672',
            'certificate_number': '123457',
            'birth_date': '1372-03-20',
            'birth_place': 'اصفهان',
        },
        {
            'first_name': 'حسن',
            'last_name': 'علوی',
            'national_id': '0012345673',
            'certificate_number': '123458',
            'birth_date': '1368-07-10',
            'birth_place': 'شیراز',
        },
    ]
    
    for data in sample_data:
        doc, created = IdentityDocuments.objects.get_or_create(
            national_id=data['national_id'],
            defaults={
                'first_name': data['first_name'],
                'last_name': data['last_name'],
                'certificate_number': data['certificate_number'],
                'birth_date': data['birth_date'],
                'birth_place': data['birth_place'],
                'national_id_image': 'documents/sample.jpg',
            }
        )
        if created:
            print(f"   ✓ {data['first_name']} {data['last_name']} - {data['national_id']}")
        else:
            print(f"   ~ {data['first_name']} {data['last_name']} (موجود است)")
        docs.append(doc)
    
    return docs


def create_sample_contacts():
    """ایجاد اطلاعات تماس نمونه"""
    print("\n🔹 ایجاد اطلاعات تماس نمونه...")
    
    contacts = []
    sample_data = [
        {
            'نام': 'علی',
            'نام_خانوادگی': 'احمدی',
            'کد_ملی': '0012365671',
            'تلفن_موبایل': '09121234561',
            'تلفن_ثابت': '02188888881',
            'ایمیل': 'ali@example.com',
            'آدرس': 'تهران، خیابان ولیعصر، پلاک 10',
            'کد_پستی': '1234567890',
        },
        {
            'نام': 'فاطمه',
            'نام_خانوادگی': 'محمدی',
            'کد_ملی': '0012365672',
            'تلفن_موبایل': '09121234562',
            'تلفن_ثابت': '02188888882',
            'ایمیل': 'fateme@example.com',
            'آدرس': 'اصفهان، خیابان چاپاری، پلاک 20',
            'کد_پستی': '8765432109',
        },
        {
            'نام': 'حسن',
            'نام_خانوادگی': 'علوی',
            'کد_ملی': '0012365673',
            'تلفن_موبایل': '09121234563',
            'تلفن_ثابت': '02188888883',
            'ایمیل': 'hasan@example.com',
            'آدرس': 'شیراز، خیابان زند، پلاک 30',
            'کد_پستی': '5555555555',
        },
    ]
    
    for data in sample_data:
        contact, created = ContactInfo.objects.get_or_create(
            کد_ملی=data['کد_ملی'],
            defaults={
                'نام': data['نام'],
                'نام_خانوادگی': data['نام_خانوادگی'],
                'تلفن_موبایل': data['تلفن_موبایل'],
                'تلفن_ثابت': data['تلفن_ثابت'],
                'ایمیل': data['ایمیل'],
                'آدرس': data['آدرس'],
                'کد_پستی': data['کد_پستی'],
            }
        )
        if created:
            print(f"   ✓ {data['نام']} {data['نام_خانوادگی']} - {data['کد_ملی']}")
        else:
            print(f"   ~ {data['نام']} {data['نام_خانوادگی']} (موجود است)")
        contacts.append(contact)
    
    return contacts


def create_sample_licenses(admin_user, docs, contacts):
    """ایجاد مجوزهای نمونه"""
    print("\n🔹 ایجاد مجوزهای نمونه...")
    
    licenses = [
        {
            'subcategory': 'household',
            'service_title': 'مجوز فعالیت خانگی',
            'amount_received': 500000,
            'description': 'مجوز برای فعالیت خدماتی خانگی',
        },
        {
            'subcategory': 'professional',
            'service_title': 'مجوز فعالیت صنفی',
            'amount_received': 1000000,
            'description': 'مجوز برای فعالیت صنفی معتبر',
        },
    ]
    
    for i, data in enumerate(licenses):
        license_obj, created = License.objects.get_or_create(
            service_title=data['service_title'],
            defaults={
                'subcategory': data['subcategory'],
                'identity_documents': docs[i % len(docs)],
                'contact_info': contacts[i % len(contacts)],
                'amount_received': data['amount_received'],
                'description': data['description'],
                'created_by': admin_user,
            }
        )
        if created:
            print(f"   ✓ {data['service_title']}")
        else:
            print(f"   ~ {data['service_title']} (موجود است)")


def create_sample_acquisitions(admin_user, docs, contacts):
    """ایجاد دریافت‌های بازرگانی نمونه"""
    print("\n🔹 ایجاد دریافت‌های بازرگانی نمونه...")
    
    acquisitions = [
        {
            'entity_type': 'natural',
            'acquisition_type': 'دریافت حقیقی - واردات',
            'check_category': 'check_a',
            'amount_received': 2000000,
        },
        {
            'entity_type': 'legal',
            'acquisition_type': 'دریافت حقوقی - صادرات',
            'check_category': 'check_b',
            'amount_received': 3000000,
        },
    ]
    
    for i, data in enumerate(acquisitions):
        acq, created = TradeAcquisition.objects.get_or_create(
            acquisition_type=data['acquisition_type'],
            defaults={
                'entity_type': data['entity_type'],
                'identity_documents': docs[i % len(docs)],
                'contact_info': contacts[i % len(contacts)],
                'check_category': data['check_category'],
                'amount_received': data['amount_received'],
                'created_by': admin_user,
            }
        )
        if created:
            print(f"   ✓ {data['acquisition_type']}")
        else:
            print(f"   ~ {data['acquisition_type']} (موجود است)")


def create_sample_partnerships(admin_user, docs, contacts):
    """ایجاد کارت‌های بازرگانی نمونه"""
    print("\n🔹 ایجاد کارت‌های بازرگانی نمونه...")
    
    partnerships = [
        {
            'entity_type': 'natural',
            'card_year': 1403,
            'import_ceiling': 100000000,
            'export_ceiling': 50000000,
            'import_amount': 80000000,
            'export_amount': 40000000,
            'amount_received': 5000000,
        },
        {
            'entity_type': 'productive',
            'card_year': 1403,
            'import_ceiling': 200000000,
            'export_ceiling': 100000000,
            'import_amount': 150000000,
            'export_amount': 80000000,
            'amount_received': 7000000,
        },
    ]
    
    for i, data in enumerate(partnerships):
        key = f"{data['entity_type']}_{data['card_year']}"
        part, created = TradePartnership.objects.get_or_create(
            entity_type=data['entity_type'],
            card_year=data['card_year'],
            defaults={
                'identity_documents': docs[i % len(docs)],
                'contact_info': contacts[i % len(contacts)],
                'import_ceiling': data['import_ceiling'],
                'export_ceiling': data['export_ceiling'],
                'import_amount': data['import_amount'],
                'export_amount': data['export_amount'],
                'amount_received': data['amount_received'],
                'created_by': admin_user,
            }
        )
        if created:
            print(f"   ✓ کارت بازرگانی {data['entity_type']} - سال {data['card_year']}")
        else:
            print(f"   ~ کارت بازرگانی {data['entity_type']} (موجود است)")


def create_sample_companies(admin_user, docs, contacts):
    """ایجاد شرکت‌های نمونه"""
    print("\n🔹 ایجاد شرکت‌های نمونه...")
    
    companies = [
        {
            'company_type': 'limited_liability',
            'company_name': 'شرکت تولیدی الف',
            'amount_received': 10000000,
            'has_license': True,
        },
        {
            'company_type': 'joint_stock',
            'company_name': 'شرکت بازرگانی ب',
            'amount_received': 15000000,
            'has_license': False,
        },
        {
            'company_type': 'transport',
            'company_name': 'شرکت حمل‌ونقل ج',
            'amount_received': 8000000,
            'has_license': True,
        },
    ]
    
    for i, data in enumerate(companies):
        company, created = Company.objects.get_or_create(
            company_name=data['company_name'],
            defaults={
                'company_type': data['company_type'],
                'identity_documents': docs[i % len(docs)],
                'contact_info': contacts[i % len(contacts)],
                'amount_received': data['amount_received'],
                'has_license': data['has_license'],
                'license_file': 'documents/licenses/sample.pdf' if data['has_license'] else None,
                'created_by': admin_user,
            }
        )
        if created:
            print(f"   ✓ {data['company_name']}")
        else:
            print(f"   ~ {data['company_name']} (موجود است)")


def main():
    """برنامه اصلی"""
    print("=" * 60)
    print("🚀 سیستم ثبتی خدمات - تنظیم داده‌های نمونه")
    print("=" * 60)
    
    try:
        # دریافت کاربر Admin
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            print("⚠️  هیچ کاربر Super Admin یافت نشد!")
            return
        
        print(f"\n👤 کاربر Admin: {admin_user.username}")
        
        # ایجاد داده‌ها
        docs = create_sample_documents()
        contacts = create_sample_contacts()
        create_sample_licenses(admin_user, docs, contacts)
        create_sample_acquisitions(admin_user, docs, contacts)
        create_sample_partnerships(admin_user, docs, contacts)
        create_sample_companies(admin_user, docs, contacts)
        
        print("\n" + "=" * 60)
        print("✅ تمام داده‌های نمونه با موفقیت ایجاد شدند!")
        print("=" * 60)
        print("\n📊 آمار:")
        print(f"   • مدارک هویتی: {IdentityDocuments.objects.count()}")
        print(f"   • اطلاعات تماس: {ContactInfo.objects.count()}")
        print(f"   • مجوزها: {License.objects.count()}")
        print(f"   • دریافت‌های بازرگانی: {TradeAcquisition.objects.count()}")
        print(f"   • کارت‌های بازرگانی: {TradePartnership.objects.count()}")
        print(f"   • شرکت‌ها: {Company.objects.count()}")
        
    except Exception as e:
        print(f"\n❌ خطا: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()