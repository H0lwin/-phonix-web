# راهنمای배포 پروداکشن - Phonix

## 📋 فهرست مطالب
1. [پیش‌نیازها](#پیش‌نیازها)
2. [نصب و راه‌اندازی](#نصب-و-راه‌اندازی)
3. [تنظیمات امنیتی](#تنظیمات-امنیتی)
4. [دیتابیس](#دیتابیس)
5. [Static Files](#static-files)
6. [Web Server](#web-server)
7. [Monitoring & Maintenance](#monitoring--maintenance)

---

## پیش‌نیازها

### نرم‌افزار مورد نیاز
- **Python**: 3.11+
- **MySQL/MariaDB**: 5.7+
- **Web Server**: Nginx یا Apache
- **Application Server**: Gunicorn یا uWSGI

### متغیرهای محیطی مورد نیاز
```bash
# تنظیمات اصلی
DEBUG=False
SECRET_KEY=<یک کلید محرمانه قوی بسازید>
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# دیتابیس
DATABASE_ENGINE=django.db.backends.mysql
DATABASE_NAME=Phonix_suite
DATABASE_USER=<کاربر>
DATABASE_PASSWORD=<رمز عبور>
DATABASE_HOST=<آدرس سرور>
DATABASE_PORT=3306

# سرور
SERVER_PORT=8000
SERVER_HOST=0.0.0.0
```

---

## نصب و راه‌اندازی

### 1. محیط virtual
```bash
# ایجاد محیط مجازی
python -m venv venv

# فعال‌سازی (Windows)
venv\Scripts\activate

# فعال‌سازی (Linux/Mac)
source venv/bin/activate
```

### 2. نصب Dependencies
```bash
pip install -r requirements.txt

# برای production، باید gunicorn و دیگر ابزارها نصب شوند:
pip install gunicorn psycopg2-binary
```

### 3. تنظیمات Django
```bash
# جمع‌آوری Static Files
python manage.py collectstatic --noinput

# اجرای Migrations
python manage.py migrate

# ایجاد ادمین (تعاملی)
python init_admin.py
```

### 4. بررسی تنظیمات پروداکشن
```bash
python manage.py check --deploy
```

---

## تنظیمات امنیتی

### .env فایل
```bash
# قوی و منحصر به‌فرد باشد
SECRET_KEY=<generated-key-here>

# فقط در پروداکشن False کنید
DEBUG=False

# دامنه‌های مجاز را فقط اضافه کنید
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### Django Security Settings
تمام تنظیمات امنیتی در `phonix/settings.py` تنظیم شده است:
- ✅ HTTPS enforcement
- ✅ HSTS headers
- ✅ CSRF protection
- ✅ Session security
- ✅ XSS filter

### دیتابیس
```bash
# رمز عبور قوی برای کاربر دیتابیس استفاده کنید
# Backups منظم انجام دهید
mysqldump -u user -p database_name > backup.sql

# Permissions را محدود کنید
GRANT SELECT, INSERT, UPDATE, DELETE ON database.* TO 'user'@'localhost';
```

---

## دیتابیس

### 1. دیتابیس را آماده کنید
```bash
# کاربر دیتابیس ایجاد کنید
CREATE USER 'phonix_user'@'localhost' IDENTIFIED BY 'strong_password';
CREATE DATABASE Phonix_suite CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
GRANT ALL PRIVILEGES ON Phonix_suite.* TO 'phonix_user'@'localhost';
FLUSH PRIVILEGES;
```

### 2. Migrations را اعمال کنید
```bash
python manage.py migrate
```

### 3. Static Content مدیریت کنید
```bash
# جمع‌آوری Static Files
python manage.py collectstatic --noinput
```

---

## Static Files

### Nginx Configuration
```nginx
location /static/ {
    alias /path/to/phonix-dj/staticfiles/;
    expires 30d;
    add_header Cache-Control "public, immutable";
}

location /media/ {
    alias /path/to/phonix-dj/media/;
    expires 7d;
}
```

### Apache Configuration
```apache
<Directory /path/to/phonix-dj/staticfiles>
    Header set Cache-Control "max-age=2592000, public"
</Directory>
```

---

## Web Server

### Gunicorn (توصیه شده)

#### 1. نصب
```bash
pip install gunicorn
```

#### 2. Systemd Service
```ini
# /etc/systemd/system/phonix.service
[Unit]
Description=Phonix Django Application
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/path/to/phonix-dj
ExecStart=/path/to/phonix-dj/venv/bin/gunicorn \
    --workers=4 \
    --worker-class=sync \
    --bind=127.0.0.1:8000 \
    --timeout=30 \
    phonix.wsgi:application
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 3. فعال‌سازی
```bash
sudo systemctl daemon-reload
sudo systemctl enable phonix
sudo systemctl start phonix
```

### Nginx Configuration
```nginx
upstream phonix {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL Certificates
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    
    # Static Files
    location /static/ {
        alias /path/to/phonix-dj/staticfiles/;
        expires 30d;
    }
    
    location /media/ {
        alias /path/to/phonix-dj/media/;
    }
    
    # Django Application
    location / {
        proxy_pass http://phonix;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Monitoring & Maintenance

### Logs
```bash
# Django Logs
tail -f /var/log/phonix/django.log

# Nginx Logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# Systemd Logs
journalctl -u phonix -f
```

### Database Backups
```bash
# روزانه backup بگیرید
0 2 * * * /usr/bin/mysqldump -u user -p'password' Phonix_suite > /backups/phonix_$(date +\%Y\%m\%d).sql
```

### Performance Monitoring
```bash
# CPU و Memory
htop

# Disk Usage
df -h

# Database Performance
SHOW PROCESSLIST;
SHOW TABLE STATUS;
```

### Health Check
```bash
# Application
curl -I https://yourdomain.com/admin/

# Database
mysql -u user -p -e "SELECT 1;"
```

---

## Troubleshooting

### 1. Static Files Not Loading
```bash
# دوباره جمع‌آوری کنید
python manage.py collectstatic --clear --noinput

# اجازه‌ها را بررسی کنید
ls -la staticfiles/
```

### 2. Database Connection Error
```bash
# اتصال را تست کنید
mysql -h host -u user -p database_name

# تنظیمات .env را بررسی کنید
cat .env | grep DATABASE
```

### 3. Permission Denied
```bash
# مالک و دسترسی‌ها را بررسی کنید
ls -la /path/to/phonix-dj
chown -R www-data:www-data /path/to/phonix-dj
chmod -R 755 /path/to/phonix-dj
```

### 4. High Memory Usage
```bash
# Gunicorn workers را کاهش دهید
# استفاده از Nginx caching بیشتر شود
```

---

## Pre-Deployment Checklist

- [ ] `.env` فایل با تنظیمات پروداکشن آماده است
- [ ] `DEBUG=False` تنظیم شده است
- [ ] `SECRET_KEY` منحصر به فرد و قوی است
- [ ] دیتابیس ایجاد و مهاجرت شد
- [ ] Static Files جمع‌آوری شدند
- [ ] ادمین ایجاد شد (`python init_admin.py`)
- [ ] `python manage.py check --deploy` پاس کرد
- [ ] Web Server (Nginx/Apache) تنظیم شد
- [ ] SSL Certificates نصب شد
- [ ] Backups منظم تنظیم شدند
- [ ] Monitoring و Logging تنظیم شدند
- [ ] Email Configuration تنظیم شد (اختیاری)

---

## تماس و پشتیبانی

برای هر سوال یا مسئله، مستندات Django و پروژه را بررسی کنید:
- Django Documentation: https://docs.djangoproject.com/
- Gunicorn Documentation: https://gunicorn.org/
- Nginx Documentation: https://nginx.org/

**تاریخ آخرین بروزرسانی:** 1403