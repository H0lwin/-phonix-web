# 🌍 راه‌اندازی Environment - Phonix

## 🚀 شروع سریع

### 1. فایل `.env` را ایجاد کنید

```bash
# Windows PowerShell
Copy-Item .env.example .env
```

یا دستی:
```bash
cp .env.example .env
```

### 2. تنظیمات `.env` را ویرایش کنید

**برای Development:**
```env
DEBUG=True
SECRET_KEY=your-dev-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_ENGINE=django.db.backends.mysql
DATABASE_NAME=Phonix_suite
DATABASE_USER=your_db_user
DATABASE_PASSWORD=your_db_password
DATABASE_HOST=127.0.0.1
DATABASE_PORT=3306
```

**برای Production:**
```env
DEBUG=False
SECRET_KEY=generate-a-long-random-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_ENGINE=django.db.backends.mysql
DATABASE_NAME=phonix_production
DATABASE_USER=prod_user
DATABASE_PASSWORD=strong-secure-password
DATABASE_HOST=your-db-server.com
DATABASE_PORT=3306
```

---

## 🔐 تولید SECRET_KEY محفوظ

### روش 1: استفاده از Django Shell

```bash
python manage.py shell
```

```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

Output را کپی کنید و در `.env` تنظیم کنید.

### روش 2: استفاده از Python

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### روش 3: استفاده از OpenSSL

```bash
openssl rand -base64 32
```

---

## 📝 متغیرهای محیطی پشتیبانی شده

| متغیر | مقدار پیش‌فرض | توضیح |
|-------|--------------|-------|
| `DEBUG` | `False` | فعال کردن debug mode |
| `SECRET_KEY` | dev-key | Django secret key |
| `ALLOWED_HOSTS` | localhost,127.0.0.1 | میزبان‌های مجاز |
| `DATABASE_ENGINE` | mysql | Database backend |
| `DATABASE_NAME` | Phonix_suite | نام database |
| `DATABASE_USER` | `` | کاربر database |
| `DATABASE_PASSWORD` | `` | رمز database |
| `DATABASE_HOST` | 127.0.0.1 | Host database |
| `DATABASE_PORT` | 3306 | Port database |

---

## ✅ Verification

بعد از تنظیم `.env`:

```bash
# 1. فعال کردن Virtual Environment
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate      # Linux/Mac

# 2. نصب dependencies
pip install -r requirements.txt

# 3. تست database connection
python manage.py check

# 4. Migration
python manage.py migrate

# 5. تولید superuser (optional)
python manage.py createsuperuser

# 6. راه‌اندازی سرور
python manage.py runserver
```

---

## 🔍 بررسی تنظیمات

برای مشاهده تنظیمات active:

```bash
python manage.py shell
```

```python
from django.conf import settings

# بررسی DEBUG
print(f"DEBUG: {settings.DEBUG}")

# بررسی ALLOWED_HOSTS
print(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")

# بررسی Database
print(f"Database: {settings.DATABASES['default']}")

# بررسی Security
print(f"SESSION_COOKIE_SECURE: {settings.SESSION_COOKIE_SECURE}")
print(f"SESSION_COOKIE_HTTPONLY: {settings.SESSION_COOKIE_HTTPONLY}")
```

---

## ⚠️ مشکل‌های عام و حل‌ها

### 1. "No module named 'dotenv'"

**حل:**
```bash
pip install python-dotenv
```

### 2. "Database connection refused"

**بررسی:**
- [ ] MySQL server در حال اجرا است؟
- [ ] DATABASE_HOST صحیح است؟
- [ ] DATABASE_USER و PASSWORD صحیح هستند؟

**راه‌حل:**
```bash
# تست MySQL connection
mysql -u your_user -p -h 127.0.0.1 Phonix_suite
```

### 3. "ALLOWED_HOSTS error"

**مشکل:** شما از یک host دسترسی می‌کنید که در ALLOWED_HOSTS نیست

**حل:** اضافه کنید به `.env`:
```env
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com
```

### 4. "Settings module not found"

**بررسی:**
```bash
python manage.py shell
```

اگر خطا داد، بررسی کنید که نام فایل settings صحیح است.

---

## 🔒 Security Best Practices

### ✅ کاری که باید کنید:

1. **`.env` را git commit نکنید**
   ```bash
   # بررسی .gitignore
   cat .gitignore | grep env
   ```

2. **Strong SECRET_KEY استفاده کنید**
   ```python
   # نه اینطور (خطرناک):
   SECRET_KEY = "debug-key"
   
   # اینطور (امن):
   SECRET_KEY = "django-insecure-a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z"
   ```

3. **Production credentials محفوظ نگه دارید**
   - از `/dev/random` یا key manager استفاده کنید
   - هرگز production keys را share نکنید

4. **Secrets rotation**
   - هر 90 روز SECRET_KEY تغییر دهید
   - Database passwords هر 6 ماه تغییر دهید

### ❌ کاری که نباید کنید:

1. ❌ `.env` را در GitHub commit کنید
2. ❌ در plaintext logs قرار دهید
3. ❌ Email یا chat shared کنید
4. ❌ Production credentials در development استفاده کنید
5. ❌ Simple/obvious keys استفاده کنید

---

## 🎯 Environment-Specific Configuration

### Development Setup

```env
DEBUG=True
SECRET_KEY=dev-key-insecure-for-testing-only
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_ENGINE=django.db.backends.sqlite3
DATABASE_NAME=db.sqlite3
```

### Testing Setup

```env
DEBUG=False
SECRET_KEY=test-key-change-before-production
ALLOWED_HOSTS=test.example.com
DATABASE_ENGINE=django.db.backends.sqlite3
DATABASE_NAME=test_db.sqlite3
```

### Production Setup

```env
DEBUG=False
SECRET_KEY=very-long-random-secure-key-generated-by-openssl
ALLOWED_HOSTS=example.com,www.example.com
DATABASE_ENGINE=django.db.backends.mysql
DATABASE_NAME=phonix_prod
DATABASE_USER=prod_user_secure
DATABASE_PASSWORD=extremely-strong-password-changed-regularly
DATABASE_HOST=prod-db.example.com
DATABASE_PORT=3306
```

---

## 📊 Deployment Checklist

- [ ] `.env` فایل ایجاد شده است
- [ ] `DEBUG=False` تنظیم شده است
- [ ] `SECRET_KEY` تغییر داده شده است
- [ ] `ALLOWED_HOSTS` بر اساس domain شما
- [ ] Database credentials صحیح تنظیم شده‌اند
- [ ] HTTPS certificate installed
- [ ] Database backups scheduled
- [ ] Logging configured
- [ ] Monitoring setup
- [ ] `.env` in `.gitignore`

---

## 🚀 راه‌اندازی نهایی

```bash
# 1. Environment setup
.\venv\Scripts\Activate.ps1

# 2. Dependencies
pip install -r requirements.txt

# 3. Database
python manage.py migrate

# 4. Static files
python manage.py collectstatic

# 5. Start server
python manage.py runserver 0.0.0.0:8000
```

---

## 📞 Support

اگر مشکلی دارید:

1. بررسی کنید `.env` موجود است
2. تمام required fields را پر کنید
3. `python manage.py check` اجرا کنید
4. Log files را بررسی کنید

**احتمال مشکل: بیشتر مشکلات مربوط به `.env` configuration هستند!**