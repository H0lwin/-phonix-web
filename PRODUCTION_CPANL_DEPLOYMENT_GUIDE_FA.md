# راهنمای استقرار پروژه Phonix روی هاست cPanel (Production)

این راهنما به شما کمک می‌کند پروژه Django خود را به بهترین شکل روی هاست cPanel (با دیتابیس MySQL) راه‌اندازی و اجرا کنید.

---

## پیش‌نیازها
- هاست لینوکسی با cPanel و دسترسی SSH (ترجیحاً)
- دامنه متصل به هاست
- دیتابیس MySQL ساخته شده در cPanel
- Python 3.11+ (در هاست)
- دسترسی به بخش **Setup Python App** در cPanel (برای هاست‌های اشتراکی)

---

## مراحل گام‌به‌گام

### 1. فشرده‌سازی و آپلود پروژه
1. کل پروژه را (بدون venv و __pycache__) در یک فایل ZIP قرار دهید.
2. وارد cPanel شوید و به بخش **File Manager** بروید.
3. به مسیر `home/username` یا پوشه مورد نظر (مثلاً `domains/yourdomain.com/`) بروید.
4. فایل ZIP را آپلود و Extract کنید.

### 2. ساخت دیتابیس و کاربر MySQL
1. وارد بخش **MySQL® Databases** شوید.
2. یک دیتابیس جدید بسازید (مثلاً: `phonix_suite`).
3. یک کاربر جدید بسازید و رمز قوی انتخاب کنید.
4. کاربر را به دیتابیس متصل و همه دسترسی‌ها را بدهید.

### 3. ساخت محیط مجازی Python (Virtualenv)
1. وارد بخش **Setup Python App** شوید.
2. نسخه Python را روی 3.11 یا بالاتر قرار دهید.
3. مسیر پروژه را به عنوان Root App Directory انتخاب کنید (مثلاً: `/home/username/phonix-dj`).
4. روی Create کلیک کنید.
5. پس از ساخت، دستور فعال‌سازی و مسیر محیط مجازی را یادداشت کنید.

### 4. نصب وابستگی‌ها
1. وارد **Terminal** یا **SSH** شوید (یا از بخش Python App → Open Terminal).
2. محیط مجازی را فعال کنید:
   ```bash
   source /home/username/virtualenv/phonix-dj/3.11/bin/activate
   ```
3. پکیج‌ها را نصب کنید:
   ```bash
   pip install -r requirements.txt
   ```

### 5. تنظیم متغیرهای محیطی (env)
1. یک فایل `.env` در ریشه پروژه بسازید و مقادیر زیر را قرار دهید:
   ```env
   DJANGO_SECRET_KEY=your-very-secret-key
   DEBUG=False
   ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   DB_NAME=phonix_suite
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   DB_HOST=localhost
   DB_PORT=3306
   ```
2. مطمئن شوید که `settings.py` پروژه از این متغیرها استفاده می‌کند (با python-dotenv).

### 6. تنظیمات Django برای Production
- `DEBUG = False`
- مقدار `ALLOWED_HOSTS` را به دامنه خود تغییر دهید.
- تنظیمات دیتابیس را از env بخوانید.
- مسیر static و media را مشخص کنید:
  ```python
  STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
  MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
  ```

### 7. اجرای Migrate و Collectstatic
1. در محیط مجازی:
   ```bash
   python manage.py migrate
   python manage.py collectstatic
   ```

### 8. تنظیم WSGI در cPanel
1. در **Setup Python App**، مسیر فایل `wsgi.py` را وارد کنید (مثلاً: `phonix/wsgi.py`).
2. اگر نیاز به تغییر دارید، فایل `passenger_wsgi.py` را به شکل زیر بسازید:
   ```python
   import sys
   import os
   sys.path.insert(0, '/home/username/phonix-dj')
   os.environ['DJANGO_SETTINGS_MODULE'] = 'phonix.settings'
   from django.core.wsgi import get_wsgi_application
   application = get_wsgi_application()
   ```
3. مسیر این فایل را در بخش Python App وارد کنید.

### 9. تنظیم دامنه و Static/Media
- در **File Manager**، پوشه‌های `staticfiles` و `media` را بسازید.
- در بخش **Domains** یا **Addon Domains**، دامنه را به پوشه پروژه متصل کنید.
- برای سرو کردن static/media، از **.htaccess** یا تنظیمات cPanel استفاده کنید:
  ```apache
  # .htaccess
  Alias /static /home/username/phonix-dj/staticfiles
  Alias /media /home/username/phonix-dj/media
  <Directory /home/username/phonix-dj/staticfiles>
      Require all granted
  </Directory>
  <Directory /home/username/phonix-dj/media>
      Require all granted
  </Directory>
  ```

### 10. راه‌اندازی و تست نهایی
1. اپلیکیشن را از بخش **Setup Python App** اجرا (Restart) کنید.
2. سایت را با دامنه تست کنید.
3. اگر خطا داشتید، لاگ‌ها را در بخش **Error Logs** یا **Terminal** بررسی کنید.

---

## نکات امنیتی و بهینه‌سازی
- حتماً `DEBUG=False` باشد.
- کلید Secret Key را امن نگه دارید.
- دسترسی پوشه‌ها را محدود کنید.
- از SSL (https) استفاده کنید.
- بکاپ منظم از دیتابیس و فایل‌ها تهیه کنید.

---

## منابع بیشتر
- [مستندات Django Deployment](https://docs.djangoproject.com/en/4.2/howto/deployment/)
- [راهنمای cPanel Python App](https://docs.cpanel.net/knowledge-base/web-services/how-to-install-a-python-wsgi-application/)

---

**تهیه و تنظیم: تیم توسعه Phonix**
