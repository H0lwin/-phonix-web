# راهنمای کامل استقرار پروژه Phonix روی هاست cPanel (برای مبتدی‌ها)

این راهنمای مرحله‌به‌مرحله مخصوص زمانی است که شما پروژه را کلون یا دانلود کرده‌اید و می‌خواهید آن را روی یک هاست لینوکسی با کنترل پنل cPanel در حالت تولید (production) اجرا کنید. این نسخه برای کاربرانی نوشته شده که دسترسی SSH ندارند ولی "Terminal" داخل cPanel فعال است.

---

## نکات مقدماتی قبل از شروع
- این راهنما فرض می‌کند شما دسترسی به cPanel، بخش File Manager، "Setup Python App"، "MySQL® Databases" و "SSL/TLS" یا AutoSSL را دارید.
- اگر هاست شما از Python App پشتیبانی نمی‌کند، می‌توان از روش Passenger (Passenger WSGI) یا پلن‌هایی که Python ندارند استفاده کرد — در ادامه راهنمای Passenger نیز آمده است.

---

## 0. جمع‌بندی کوتاه مراحل (آنچه قرار است انجام دهیم)
- آپلود فایل‌ها (یا Extract از ZIP) در cPanel
- ساخت دیتابیس MySQL و کاربر از طریق cPanel
- ساخت/پیکربندی اپ Python در "Setup Python App" (ایجاد virtualenv و نصب requirements)
- ساخت فایل `.env` و تنظیمات Django برای production
- اجرای migrate و collectstatic از داخل Terminal cPanel
- پیکربندی WSGI (Passenger / WSGI entry) و راه‌اندازی اپ
- فعال‌سازی SSL (AutoSSL یا Let's Encrypt از طریق cPanel)
- (اختیاری) راهنمای کامل برای استفاده از Nginx اگر خواستید روی VPS با دسترسی روت اجرا کنید

---

## 1. آماده‌سازی بسته پروژه و آپلود به cPanel

روش A — اگر پروژه را از گیت کلون نکرده‌اید (محلی روی سیستم شما):
1. در سیستم خودتان، پوشه پروژه را به‌صورت ZIP فشرده کنید (مگر اینکه بخواهید فایل‌ها را مستقیماً از گیت روی سرور کلون کنید).
2. از cPanel وارد **File Manager** شوید.
3. به مسیر دامنه یا پوشه‌ای که می‌خواهید اپ داخل آن قرار گیرد بروید (مثلاً `public_html` برای دامنه اصلی یا `domains/yourdomain.com/public_html`).
4. فایل ZIP را Upload کنید و سپس با استفاده از گزینه Extract آن را باز کنید.

روش B — اگر می‌خواهید از داخل cPanel با Git کار کنید:
1. در cPanel ببینید آیا بخش **Git Version Control** موجود است.
2. یک Repository جدید بسازید و URL `https://github.com/H0lwin/-phonix-web.git` را وارد کنید و سپس روی Clone کلیک کنید.
3. فایل‌ها در مسیر مشخص شده ظاهر می‌شوند.

توجه: پوشه `venv` را آپلود نکنید. virtualenv را در سرور می‌سازیم.

---

## 2. ساخت دیتابیس MySQL و کاربر (از طریق cPanel)

1. در cPanel وارد **MySQL® Databases** شوید.
2. در قسمت Create New Database یک نام مشخص (مثلاً `phonix_suite`) وارد کنید و Create را بزنید.
3. به پایین صفحه بروید و یک MySQL User جدید بسازید (مثلاً `phonix_user`) و رمزعبور قوی تنظیم کنید.
4. در بخش Add User To Database کاربر را به دیتابیس اضافه و تمام دسترسی‌ها (ALL PRIVILEGES) را بدهید.
5. نام دیتابیس و نام کاربر کامل شده را یادداشت کنید (گاهی cPanel پیشوند `username_` اضافه می‌کند؛ آن را دقیق کپی کنید).

---

## 3. ساخت Python App و virtualenv (با استفاده از Setup Python App در cPanel)

1. در cPanel وارد **Setup Python App** شوید.
2. Create Application را بزنید.
   - Python version: حداقل `3.11` یا نسخه‌ای که هاست پشتیبانی می‌کند را انتخاب کنید.
   - Application Root: مسیر پوشه پروژه که فایل‌های Django آن قرار دارد (مثلاً `phonix-dj` یا `public_html/phonix-dj`).
   - Application URL: دامنه یا زیرمسیر که می‌خواهید اپ در آن اجرا شود.
   - Passenger WSGI file: معمولاً `passenger_wsgi.py` را قرار می‌دهیم (در ادامه نمونه می‌نویسیم).
3. Create را بزنید تا اپ ساخته شود. این کار یک virtualenv برای شما می‌سازد و مسیر آن را نمایش می‌دهد (مثلاً `/home/username/virtualenv/phonix-dj/3.11/`).

بعد از ساخته شدن، در همان صفحه یک دستور pip برای نصب پکیج‌ها نمایش می‌دهد یا یک دکمه برای باز کردن یک Terminal مرتبط با آن محیط.

---

## 4. نصب وابستگی‌ها (بدون SSH، از Terminal داخل cPanel)

1. در صفحه Python App روی Open or Start Terminal (یا از بخش Terminal در cPanel) کلیک کنید تا یک ترمینال متصل به محیط مجازی باز شود.
2. در ترمینال به پوشه پروژه بروید:

```bash
cd $HOME/path/to/your/app    # یا مسیر نمایش‌داده‌شده در Setup Python App
```

3. نصب پکیج‌ها:

```bash
pip install -r requirements.txt
```

اگر خطا در نصب پکیج‌هایی مثل `mysqlclient` داشتید: بررسی کنید هاست پکیج‌های سیستمی مثل `python3-dev` و `libmysqlclient-dev` را نصب دارد یا از `mysql-connector-python` جایگزین استفاده کنید (در `requirements.txt` قرار بگیرید).

---

## 5. پیکربندی فایل `.env` و تنظیمات Django برای Production

1. در ریشه پروژه، یک فایل `.env` بسازید و این مقادیر را قرار دهید (مقادیر را با اطلاعات واقعی جایگزین کنید):

```env
DJANGO_SECRET_KEY=یک_کلید_خیلی_قوی
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DB_NAME=cpanel_db_name        # مثلا username_phonix_suite
DB_USER=cpanel_db_user        # مثلا username_phonix_user
DB_PASSWORD=the_db_password
DB_HOST=localhost
DB_PORT=3306
```

2. مطمئن شوید در `phonix/settings.py` یا فایل تنظیمات پروژه از این متغیرها خوانده می‌شود (پروژه در repo شما ظاهراً از `python-dotenv` استفاده می‌کند؛ اگر نه، از `django-environ` یا خواندن `os.environ` استفاده کنید).

3. مسیرهای Static و Media را ست کنید (در settings):

```python
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

---

## 6. اجرای مهاجرت‌ها و جمع‌آوری استاتیک از داخل cPanel Terminal

1. در Terminal که virtualenv فعال است، در ریشه پروژه اجرا کنید:

```bash
python manage.py migrate --noinput
python manage.py collectstatic --noinput
```

2. اگر خطا دریافت کردید، لاگ‌ها را بخوانید و خطای کامل را کپی کنید تا راهنمایی کنم.

---

## 7. پیکربندی WSGI برای cPanel (passenger_wsgi)

بیشتر cPanelها از Passenger برای اجرای اپ‌های Python استفاده می‌کنند. یک فایل `passenger_wsgi.py` در ریشه اپ بسازید یا ویرایش کنید:

```python
import sys
import os

# مسیر پروژه را به sys.path اضافه کنید
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ''))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'phonix.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

در صفحه Setup Python App آدرس این فایل را تنظیم کنید (اگر از همان صفحه Passenger استفاده می‌شود، معمولاً به صورت اتوماتیک تنظیم می‌شود).

---

## 8. راه‌اندازی برنامه (Restart) و تست

1. در صفحه **Setup Python App**، اپ را Restart کنید (دکمه Restart Application).
2. آدرس دامنه یا URL اپ را باز کنید و ببینید صفحه بارگذاری می‌شود.
3. در صورت خطا، لاگ خطا را از بخش **Error Logs** در cPanel یا از Terminal بررسی کنید.

---

## 9. فعال‌سازی SSL (Public) در cPanel

روش آسان و معمول: استفاده از AutoSSL یا SSL رایگان Let's Encrypt که اکثر cPanelها از آن پشتیبانی می‌کنند.

1. در cPanel به بخش **SSL/TLS** یا **Let's Encrypt** یا **SSL/TLS Status** بروید.
2. اگر AutoSSL فعال است، برای دامنه‌تان گزینه Run AutoSSL یا Renew را انتخاب کنید تا گواهی صادر شود.
3. اگر هاست شما ابزار Let's Encrypt دارد، از آن برای نصب گواهی روی دامنه استفاده کنید.
4. پس از نصب، مطمئن شوید در تنظیمات دامنه `https://` کار می‌کند.

پی‌نوشت برای مسیرها: اگر از Passenger استفاده می‌کنید، Nginx/Apache داخل cPanel بصورت پیش‌فرض گواهی را مدیریت می‌کند و لازم نیست فایل‌های .pem را دستکاری کنید.

---

## 10. (اختیاری) اگر خواستید Nginx را بعداً استفاده کنید

توضیح مهم: روی هاست‌های اشتراکی cPanel معمولاً امکان نصب یا مدیریت Nginx را ندارید مگر VPS یا سرور اختصاصی با دسترسی روت. اگر به Nginx نیاز دارید، بهتر است سرور VPS تهیه کنید. در آن صورت مراحل کلی:

- نصب و اجرای Gunicorn در virtualenv
- پیکربندی Nginx برای پروکسی به Gunicorn
- استفاده از Certbot برای گرفتن گواهی Let's Encrypt و فعال‌سازی HTTPS

اگر خواستید راهنمای کامل Nginx/Gunicorn را هم برای VPS آماده کنم، بگویید تا یک راهنمای جداگانه و دقیق بنویسم.

---

## 11. دسترسی‌ها، نگهداری و نکات امنیتی

- Always: `DEBUG = False` در production.
- کلید `DJANGO_SECRET_KEY` را محرمانه نگه دارید و آن را داخل `.env` نگه دارید.
- دسترسی فایل‌ها: پوشه‌ها را با دسترسی مناسب 755/644 تنظیم کنید؛ فایل‌های حساس را در public_html قرار ندهید.
- بکاپ منظم از دیتابیس و فولدر `media` داشته باشید.
- بررسی لاگ‌ها (Error Logs, Access Logs) در cPanel به‌صورت دوره‌ای.

---

## 12. عیب‌یابی سریع (Troubleshooting)

- خطای 500 بعد از Deploy: در لاگ خطا دنبال Traceback بگردید؛ معمولاً مشکل از Missing dependency یا خطای اتصال دیتابیس است.
- مشکل اتصال به MySQL: نام دیتابیس و نام کاربری را چک کنید. در cPanel اغلب نام‌ها شامل prefix می‌شوند (مثال: `username_phonix_suite`).
- خطاهای مربوط به mysqlclient: از `mysql-connector-python` استفاده کنید یا از پشتیبانی هاست بخواهید بسته‌های توسعه‌ای لازم را نصب کند.

---

## مثال‌های مفید از دستورات (برای کپی در Terminal داخل cPanel)

```bash
# رفتن به پوشه پروژه
cd $HOME/path/to/phonix-dj

# فعال بودن virtualenv (معمولاً توسط cPanel فعال می‌شود اما اگر لازم بود)
source /home/username/virtualenv/phonix-dj/3.11/bin/activate

# نصب پکیج‌ها
pip install -r requirements.txt

# اجرای مهاجرت‌ها
python manage.py migrate --noinput

# جمع‌آوری فایل‌های استاتیک
python manage.py collectstatic --noinput

# ری‌استارت اپ (از Setup Python App یا با دستور در ترمینال بسته به هاست)
# اگر cPanel دکمه Restart دارد، آن را بزنید
```

---

## جمع‌بندی و گام‌های بعدی

- فایل‌ها را آپلود یا از Git کلون کنید.
- دیتابیس را در cPanel بسازید.
- Python App را بسازید و پکیج‌ها را نصب کنید.
- `.env` را تنظیم کنید و migrate/collectstatic را اجرا کنید.
- اپ را Restart کنید و SSL را فعال کنید.

اگر در هر مرحله خطا یا سوال داشتید، خطا را کپی کنید و ارسال کنید؛ من دقیق‌تر کمک می‌کنم (مثلاً لاگ خطاها، خروجی pip install یا خروجی migrate).

**تهیه و تنظیم: تیم توسعه Phonix**
