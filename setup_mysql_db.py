#!/usr/bin/env python
"""
اسکریپت برای ایجاد دیتابیس MySQL و کاربر
"""
import mysql.connector
from mysql.connector import Error

# اطلاعات MySQL
MYSQL_HOST = "127.0.0.1"
MYSQL_PORT = 3306
MYSQL_ROOT_USER = "root"  # یوزرنیم root MySQL
MYSQL_ROOT_PASSWORD = "Shayan.1400"  # پسورد root MySQL

# اطلاعات پروژه
DB_NAME = "Phonix_suite"
DB_USER = "H0lwin"
DB_PASSWORD = "Shayan.1400"

def setup_database():
    """ایجاد دیتابیس و کاربر"""
    try:
        # اتصال به MySQL به عنوان root
        print("🔌 در حال اتصال به MySQL...")
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_ROOT_USER,
            password=MYSQL_ROOT_PASSWORD
        )
        
        cursor = connection.cursor()
        
        # ایجاد دیتابیس
        print(f"📊 در حال ایجاد دیتابیس '{DB_NAME}'...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        print(f"✓ دیتابیس '{DB_NAME}' ایجاد شد!")
        
        # ایجاد کاربر و اختصاص دسترسی‌ها
        print(f"👤 در حال ایجاد کاربر '{DB_USER}'...")
        cursor.execute(f"DROP USER IF EXISTS '{DB_USER}'@'%';")
        cursor.execute(f"CREATE USER '{DB_USER}'@'%' IDENTIFIED BY '{DB_PASSWORD}';")
        print(f"✓ کاربر '{DB_USER}' ایجاد شد!")
        
        # اختصاص تمام دسترسی‌ها
        print(f"🔐 در حال اختصاص دسترسی‌ها...")
        cursor.execute(f"GRANT ALL PRIVILEGES ON {DB_NAME}.* TO '{DB_USER}'@'%';")
        cursor.execute("FLUSH PRIVILEGES;")
        print(f"✓ دسترسی‌ها اختصاص داده شدند!")
        
        connection.commit()
        cursor.close()
        connection.close()
        
        print("\n" + "="*60)
        print("✅ تنظیمات MySQL با موفقیت انجام شد!")
        print("="*60)
        print(f"نام دیتابیس: {DB_NAME}")
        print(f"یوزرنیم:     {DB_USER}")
        print(f"پسورد:      {DB_PASSWORD}")
        print(f"Host:        {MYSQL_HOST}")
        print(f"Port:        {MYSQL_PORT}")
        print("="*60 + "\n")
        
        return True
        
    except Error as err:
        if err.errno == 2003:
            print("\n❌ خطا: MySQL Server در حال اجرا نیست!")
            print("لطفاً MySQL Server را شروع کنید.\n")
            print("برای Windows:")
            print("  • XAMPP Control Panel → شروع Apache و MySQL")
            print("  • یا cmd: net start MySQL80\n")
        elif err.errno == 1045:
            print("\n❌ خطا: نام کاربری یا پسورد MySQL root غلط است!")
            print("لطفاً کد را تصحیح کنید (خطوط 13-14)\n")
        else:
            print(f"\n❌ خطای MySQL: {err}\n")
        return False

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🔥 Phonix - راه‌اندازی دیتابیس MySQL")
    print("="*60 + "\n")
    
    if setup_database():
        print("💡 گام بعدی: python manage.py migrate\n")
    else:
        print("⚠️  لطفاً مشکل را حل کنید و دوباره تلاش کنید.\n")