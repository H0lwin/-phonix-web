# 🔥 Phonix - پروژه Django

یک پروژه Django کامل با فرانت‌اند HTML/CSS/JavaScript

## 📋 اطلاعات پروژه

- **نام پروژه:** Phonix
- **فریم‌ورک:** Django 4.2.7
- **Python:** 3.11+
- **دیتابیس:** SQLite (قابل تغییر به PostgreSQL)
- **ساختار:** MVC/MVT

## 🚀 شروع کار

### ۱. فعال کردن محیط مجازی

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# یا macOS/Linux
source venv/bin/activate
```

### ۲. نصب وابستگی‌ها

```bash
pip install -r requirements.txt
```

### ۳. راه‌اندازی

```bash
# مایگریشن‌ها
python manage.py migrate

# ایجاد کاربر ادمین (اختیاری)
python manage.py createsuperuser

# شروع سرور
python manage.py runserver
```

## 👤 ایجاد کاربر ادمین

برای ایجاد یک کاربر ادمین جدید و ایمن:

```bash
# روش ۱: استفاده از اسکریپت تعاملی (توصیه شده)
python init_admin.py

# روش ۲: استفاده از دستور Django
python manage.py createsuperuser
```

**توجه:** هرگز credentials خود را در کد یا documentation عمومی قرار ندهید!

**دسترسی:** http://localhost:8000/admin/ (بعد از ورود)

## 📁 ساختار پروژه

```
phonix-dj/
├── phonix/              # تنظیمات اصلی پروژه
│   ├── settings.py      # تنظیمات Django
│   ├── urls.py          # URLs اصلی
│   └── wsgi.py          # WSGI
├── core/                # اپلیکیشن اصلی
│   ├── models.py        # مدل‌های دیتابیس
│   ├── views.py         # ویو‌ها
│   └── urls.py          # URLs App
├── templates/           # فایل‌های HTML
├── static/              # فایل‌های استاتیک
│   ├── css/
│   ├── js/
│   └── images/
├── manage.py            # دستورات Django
└── requirements.txt     # وابستگی‌های پروژه
```

## 🎨 فرانت‌اند

### صفحات موجود:
- **صفحه اول** (`/`) - صفحه خوش‌آمد
- **ادمین** (`/admin/`) - پنل ادمین Django

### فایل‌های CSS/JS:
- `static/css/style.css` - طراحی کلی
- `static/js/main.js` - JavaScript اصلی

## 📚 مستندات مفید

- [Django Documentation](https://docs.djangoproject.com/)
- [Django ORM](https://docs.djangoproject.com/en/4.2/topics/db/models/)
- [Django REST Framework](https://www.django-rest-framework.org/)

## 🔄 اتصال PostgreSQL (اختیاری)

اگر می‌خواهید از PostgreSQL استفاده کنید:

1. PostgreSQL را نصب کنید
2. دیتابیس `Phonix_suite` را ایجاد کنید:
```sql
CREATE DATABASE Phonix_suite;
CREATE USER H0lwin WITH PASSWORD 'Shayan.1400';
ALTER ROLE H0lwin SET client_encoding TO 'utf8';
ALTER ROLE H0lwin SET default_transaction_isolation TO 'read committed';
ALTER ROLE H0lwin SET default_transaction_deferrable TO on;
ALTER ROLE H0lwin SET timezone TO 'Asia/Tehran';
GRANT ALL PRIVILEGES ON DATABASE Phonix_suite TO H0lwin;
```

3. تنظیمات Django را تغییر دهید:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'Phonix_suite',
        'USER': 'H0lwin',
        'PASSWORD': 'Shayan.1400',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

4. مجدد مایگریشن کنید:
```bash
python manage.py migrate
```

## 🛠️ دستورات مفید

```bash
# ایجاد اپلیکیشن جدید
python manage.py startapp myapp

# مایگریشن‌های جدید
python manage.py makemigrations
python manage.py migrate

# شل Django
python manage.py shell

# جمع‌آوری فایل‌های استاتیک
python manage.py collectstatic

# تست‌ها
python manage.py test
```

## 📝 نکات نکات مهم

- 🔒 در Production، `DEBUG=False` را تنظیم کنید
- 🔑 `SECRET_KEY` را تغییر دهید
- 🗄️ دیتابیس را backup کنید
- 📦 وابستگی‌ها را به‌روز نگاه دارید

## 📞 تماس و پشتیبانی

برای سؤالات و مشکلات:
- **ایمیل:** shayanqasmy88@gmail.com
- **پروژه:** Phonix

---

**ساخته شده با ❤️ استفاده از Django**